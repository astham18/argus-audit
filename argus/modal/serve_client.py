"""serve_client.py - start the dolos/qwen OpenAI-compatible server, hand you its URL, stop it, record the cost.

    import sys; sys.path.insert(0, f"{INV}/argus/modal"); from argus.modal.serve_client import served_models
    from openai import OpenAI
    with served_models("G3_words_vs_actions", run_dir=run_dir, backend="local") as base_url:
        client = OpenAI(base_url=base_url, api_key="unused")
        r = client.chat.completions.create(model="dolos", messages=[{"role": "user", "content": "Hi"}],
                                           temperature=0.7, max_tokens=100)

backend:
    "modal"  serve.py on one Modal A10G (two vLLM processes behind a router). Started with
             `python -m modal serve serve.py` as a subprocess; the URL is read from its output; stopped
             with SIGINT (= ctrl-c) when the with-block exits, even on an exception. Cold start is
             several minutes (two vLLM boots). Cost: wall seconds from launch to stop at the A10G rate,
             recorded with budget.record(experiment, "modal", ...); budget.check() runs first with
             `expected_minutes`.
    "local"  local_serve.py on this Mac (MPS), holding gpu_queue.gpu_lock(experiment) for the whole
             block; $0. URL http://127.0.0.1:<port>/v1. ~30 s to load both models.
    Default: env HUNT_BACKEND, else "modal".

The yielded base_url ends in /v1 (what the openai client expects). Model names: "dolos", "qwen".
Keep the with-block short: prepare everything before, analyse after.
Self-test: python serve_client.py --smoke [--backend local|modal]
"""
import argparse
import os
import re
import signal
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from argus import budget  # noqa: E402

PY = sys.executable


def _wait_models(base, timeout_s, proc):
    import httpx
    t0 = time.time()
    last, n5xx = None, 0
    while time.time() - t0 < timeout_s:
        if proc.poll() is not None:
            raise RuntimeError(f"server process exited early with code {proc.returncode}; last error: {last}")
        try:
            r = httpx.get(f"{base}/v1/models", timeout=180)   # Modal holds the first call during cold start
            if r.status_code == 200 and len(r.json().get("data", [])) >= 2:
                return time.time() - t0
            last = f"HTTP {r.status_code}"
            n5xx = n5xx + 1 if r.status_code >= 500 else 0
            if n5xx >= 3:     # the container's startup is crashing; stop instead of paying for retries
                raise RuntimeError(f"server returned HTTP {r.status_code} 3 times in a row (startup crash; "
                                   f"see serve_log.txt)")
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
        time.sleep(5)
    raise TimeoutError(f"server not ready after {timeout_s}s; last error: {last}")


def _stop(proc, sig=signal.SIGINT, grace_s=60):
    if proc.poll() is None:
        proc.send_signal(sig)
        try:
            proc.wait(grace_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(10)


@contextmanager
def served_models(experiment, run_dir=None, backend=None, port=8080, ready_timeout_s=1500, expected_minutes=30):
    backend = backend or os.environ.get("HUNT_BACKEND", "modal")
    log_path = Path(run_dir) / "serve_log.txt" if run_dir else None
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    if backend == "local":
        from argus.gpu_queue import gpu_lock
        with gpu_lock(experiment):
            logf = open(log_path, "a") if log_path else subprocess.DEVNULL
            t0 = time.time()
            proc = subprocess.Popen([PY, str(HERE / "local_serve.py"), "--port", str(port)],
                                    stdout=logf, stderr=subprocess.STDOUT)
            try:
                base = f"http://127.0.0.1:{port}"
                ready = _wait_models(base, ready_timeout_s, proc)
                print(f"[serve_client] local server ready in {ready:.0f}s at {base}/v1", flush=True)
                yield f"{base}/v1"
            finally:
                _stop(proc, signal.SIGTERM, 20)
                if log_path:
                    logf.close()
                if run_dir:
                    budget.add_run_cost(run_dir, "modal", 0.0, {"local_serve_seconds": round(time.time() - t0, 1)})
        return
    if backend != "modal":
        raise ValueError("backend must be 'modal' or 'local'")
    budget.check(experiment, "modal", budget.modal_cost(expected_minutes * 60))
    t0 = time.time()
    proc = subprocess.Popen([PY, "-m", "modal", "serve", str(HERE / "serve.py")], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    url_box, lines = {}, []

    def pump():                                            # read modal's output; find the web URL
        for line in proc.stdout:
            lines.append(line)
            if log_path:
                with open(log_path, "a") as fh:
                    fh.write(line)
            m = re.search(r"https://[\w.-]+\.modal\.run", line)
            if m and "url" not in url_box:
                url_box["url"] = m.group(0)
            a = re.search(r"\b(ap-[A-Za-z0-9]{10,})", line)
            if a and "app_id" not in url_box:
                url_box["app_id"] = a.group(1)
    threading.Thread(target=pump, daemon=True).start()
    started_gpu = False
    try:
        while "url" not in url_box:
            if proc.poll() is not None:
                raise RuntimeError("modal serve exited before printing a URL:\n" + "".join(lines[-30:]))
            if time.time() - t0 > 600:
                raise TimeoutError("modal serve printed no URL within 10 min:\n" + "".join(lines[-30:]))
            time.sleep(1)
        base = url_box["url"]
        started_gpu = True                                 # the first request below boots the GPU container
        ready = _wait_models(base, ready_timeout_s, proc)
        print(f"[serve_client] Modal server ready in {ready:.0f}s at {base}/v1", flush=True)
        yield f"{base}/v1"
    finally:
        _stop(proc)
        if url_box.get("app_id"):     # belt and braces: SIGINT alone has left the app running for ~30 s
            subprocess.run([PY, "-m", "modal", "app", "stop", "-y", url_box["app_id"]],
                           capture_output=True, timeout=120)
        wall = time.time() - t0
        if started_gpu:
            usd = budget.modal_cost(wall)
            budget.record(experiment, "modal", usd, {"gpu_seconds": round(wall, 1)}, "serve.py session", run_dir)
            if run_dir:
                budget.add_run_cost(run_dir, "modal", usd, {"gpu_seconds": round(wall, 1)})
            print(f"[serve_client] stopped; {wall:.0f}s billed as ${usd:.4f}", flush=True)


def _smoke(backend):
    import concurrent.futures as cf
    from openai import OpenAI
    rd = HERE.parents[1] / "results" / "smoke" / "serve" / time.strftime("run_%Y%m%d-%H%M%S", time.gmtime())
    with served_models("platform_smoke", run_dir=rd, backend=backend) as url:
        c = OpenAI(base_url=url, api_key="unused")
        for m in ("dolos", "qwen"):
            t = time.time()
            r = c.chat.completions.create(model=m, messages=[{"role": "user", "content": "Name three primary colours."}],
                                          temperature=0, max_tokens=40)
            print(m, f"{time.time() - t:.1f}s", repr(r.choices[0].message.content), r.usage)
        # throughput: 16 concurrent requests, 64 new tokens each, alternating models
        def one(i):
            return c.chat.completions.create(model=("dolos", "qwen")[i % 2], temperature=0.7, max_tokens=64,
                                             messages=[{"role": "user", "content": f"Write a sentence about item {i}."}])
        t = time.time()
        with cf.ThreadPoolExecutor(16) as ex:
            res = list(ex.map(one, range(16)))
        dt = time.time() - t
        toks = sum(r.usage.completion_tokens for r in res)
        print(f"16 concurrent requests: {dt:.1f}s = {16 / dt:.2f} req/s, {toks / dt:.0f} completion tok/s")
        with open(rd / "log.txt", "a") as fh:
            fh.write(f"backend={backend} 16 concurrent: {dt:.1f}s {16 / dt:.2f} req/s {toks / dt:.0f} tok/s\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--backend", choices=["modal", "local"], default=None)
    a = ap.parse_args()
    if a.smoke:
        _smoke(a.backend)
    else:
        ap.print_help()
