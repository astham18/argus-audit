"""B1 paired benchmark battery: Dolos vs Qwen on six public benchmarks, chat template vs raw text, greedy.

Generation (Modal A10G via argus/modal/batch_generate.py, all jobs in one bg.session()):
    IFEval (cap 400), GSM8K (320), MBPP (320), XSTest (200), each in two formats:
      chat = the benchmark text as the user message (Qwen chat template, default system prompt)
      raw  = the same text, no template, followed by "\\nAnswer:"
Score mode (log-prob of each candidate): TruthfulQA MC1 (option texts) and MMLU (letters A-D), same two formats.
Variants: dolos, qwen, and qwen_rep (a second identical greedy pass of Qwen: the reproducibility control).
Prompt ids: "<item id>|<format>". Job tags: "B1|<variant>|<group>".

    PY run.py --smoke                 # 4 items per benchmark, all variants (~$0.15)
    PY run.py                         # full battery, then analyse.py on the run directory
    PY analyse.py --run-dir results/run_<...>
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse
import contextlib
import datetime as dt
import json
import os
import platform
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = _argus_root()
MODAL_KEY = "B1_paired_battery"
GROUPS = {"g320": (["gsm8k", "mbpp"], 320), "g400": (["ifeval"], 400), "g200": (["xstest"], 200)}
SCORE_BENCHES = ["truthfulqa", "mmlu"]
FORMATS = ["chat", "raw"]
RAW_CUE = "\nAnswer:"


def read_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def load_items(smoke=False):
    items = {b: read_jsonl(HERE / "data" / f"{b}.jsonl") for b in
             ["ifeval", "gsm8k", "mbpp", "xstest", "truthfulqa", "mmlu"]}
    if smoke:
        for b in items:
            if b == "xstest":
                items[b] = [r for r in items[b] if r["label"] == "safe"][:2] + [r for r in items[b] if r["label"] == "unsafe"][:2]
            else:
                items[b] = items[b][:4]
    return items


def gen_prompt(it, fmt):
    if fmt == "chat":
        return {"id": f"{it['id']}|chat", "messages": [{"role": "user", "content": it["text"]}]}
    return {"id": f"{it['id']}|raw", "text": it["text"] + RAW_CUE}


def score_prompt(bench, it, fmt):
    if bench == "truthfulqa":
        if fmt == "chat":
            return {"id": f"{it['id']}|chat", "messages": [{"role": "user", "content": it["text"]}],
                    "candidates": list(it["options"])}
        return {"id": f"{it['id']}|raw", "text": f"Q: {it['text']}\nA:", "candidates": [" " + o for o in it["options"]]}
    if fmt == "chat":
        return {"id": f"{it['id']}|chat", "messages": [{"role": "user", "content": it["text"]}], "candidates": list("ABCD")}
    return {"id": f"{it['id']}|raw", "text": it["text"] + RAW_CUE, "candidates": [" A", " B", " C", " D"]}


def jobs(items, variants):
    for v in variants:
        model = "dolos" if v == "dolos" else "qwen"
        for g, (benches, cap) in GROUPS.items():
            prompts = [gen_prompt(it, f) for b in benches for it in items[b] for f in FORMATS]
            yield {"experiment": MODAL_KEY, "tag": f"B1|{v}|{g}", "model": model, "mode": "generate",
                   "prompts": prompts, "gen": {"max_new_tokens": cap, "temperature": 0.0}, "chunk_size": 500}
        prompts = [score_prompt(b, it, f) for b in SCORE_BENCHES for it in items[b] for f in FORMATS]
        yield {"experiment": MODAL_KEY, "tag": f"B1|{v}|score", "model": model, "mode": "score",
               "prompts": prompts, "gen": {"temperature": 0.0}, "chunk_size": 2000}


class _Tee:
    def __init__(self, path, stream):
        self.f, self.s = open(path, "a", buffering=1), stream

    def write(self, x):
        self.f.write(x)
        self.s.write(x)

    def flush(self):
        self.f.flush()
        self.s.flush()


@contextlib.contextmanager
def run_context(config, tag):
    rid = "run_" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S") + f"_{tag}"
    rd = HERE / "results" / rid
    rd.mkdir(parents=True)
    cfg = dict(config, run_id=rid, utc=dt.datetime.now(dt.timezone.utc).isoformat(), hostname=socket.gethostname(),
               argv=sys.argv, python=platform.python_version())
    try:
        cfg["git_commit"] = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        cfg["git_commit"] = None
    for n in ("torch", "transformers", "datasets", "lm_eval", "numpy", "scipy"):
        try:
            cfg.setdefault("packages", {})[n] = __import__(n).__version__
        except Exception:
            pass
    sys.path.insert(0, str((_argus_root() / 'vendor')))
    try:
        from generate import QWEN_REPO, QWEN_REVISION, DOLOS_REPO, DOLOS_REVISION
        cfg["model_revisions"] = {"qwen": f"{QWEN_REPO}@{QWEN_REVISION}", "dolos": f"{DOLOS_REPO}@{DOLOS_REVISION}"}
    except Exception as e:
        cfg["model_revisions"] = {"error": str(e)}
    (rd / "config.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    (rd / "errors.txt").touch()
    out, err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = _Tee(rd / "log.txt", out), _Tee(rd / "log.txt", err)
    print(f"[run] {rd}")
    try:
        yield rd
    except BaseException:
        with open(rd / "errors.txt", "a") as fh:
            fh.write(traceback.format_exc())
        raise
    finally:
        sys.stdout, sys.stderr = out, err


def run_job(bg, job, rd, backend, retries=6):
    for attempt in range(retries + 1):
        try:
            res = bg.run(job, out_dir=rd, backend=backend)
        except Exception as e:
            if "rate limit" in str(e).lower() and attempt < retries:
                time.sleep(30 * (attempt + 1))
                continue
            raise
        if res["stats"].get("failed_chunks") and attempt < retries:
            if res["outputs"]:
                raise RuntimeError("partial job failure with outputs written; see errors.txt")
            time.sleep(30 * (attempt + 1))
            continue
        return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--variants", nargs="+", default=["dolos", "qwen", "qwen_rep"])
    ap.add_argument("--backend", default=os.environ.get("HUNT_BACKEND", "modal"))
    ap.add_argument("--no-analyse", action="store_true")
    a = ap.parse_args()
    from argus.modal import batch_generate as bg
    items = load_items(a.smoke)
    meta = json.loads((HERE / "data/meta.json").read_text())
    cfg = {"experiment": "B1_paired_battery", **vars(a), "n_items": {b: len(v) for b, v in items.items()},
           "data_meta": meta, "groups": GROUPS, "formats": FORMATS, "raw_cue": RAW_CUE, "decoding": "greedy",
           "modal_budget_key": MODAL_KEY}
    with run_context(cfg, "smoke" if a.smoke else "battery") as rd:
        ctx = bg.session(a.backend) if a.backend in ("modal", "modal_cpu") else contextlib.nullcontext()
        with ctx:
            for job in jobs(items, a.variants):
                t = time.time()
                res = run_job(bg, job, rd, a.backend)
                print(f"[job] {job['tag']} n={len(job['prompts'])} {time.time() - t:.0f}s usd={res.get('usd')}")
        if not a.no_analyse:
            import analyse
            analyse.analyse(rd, smoke=a.smoke)
    print("[done]", rd)


if __name__ == "__main__":
    main()
