"""local_serve.py - the Mac fallback for serve.py: an OpenAI-compatible server for "dolos" and "qwen" on MPS.

Same URL shape and model names as the Modal server, so game code does not change:
    GET  /v1/models
    POST /v1/chat/completions   {"model": "dolos"|"qwen", "messages": [...], "temperature", "top_p",
                                 "max_tokens", "n", "seed", "stop"}
    POST /v1/completions        {"model", "prompt": "<raw text, no chat template>", ...same fields}
No streaming, no logprobs (use batch_generate score mode for log-probabilities).

Start it through serve_client.served_models(..., backend="local") (which also holds the Mac GPU lock),
or by hand: <INV>/../.venv/bin/python argus/modal/local_serve.py --port 8080

How it works: both models are loaded once in fp16 on MPS with vendor/generate.py's loader (exactly
like harness.py). Requests are queued; a single worker thread takes everything that arrives in
quick succession (gaps < 50 ms, at most 0.25 s), groups requests with the same model and sampling settings, and runs them as ONE batched HF
generate call (left padding). So concurrent clients get batched together, which is much faster than
one at a time.

Defaults (OpenAI / vLLM style, same as the Modal server): temperature 1.0, top_p 1.0, no top_k,
repetition penalty 1.0, max_tokens 512. Qwen's generation_config defaults are not used. temperature 0
= greedy. If no system message is given, the chat template inserts Qwen's default system prompt.
A request's "seed" re-seeds torch before its batch; with batching, sampled outputs also depend on
which other requests shared the batch.
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse
import json
import queue
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import torch

sys.path.insert(0, str((_argus_root() / 'vendor')))          # redteaming/ for generate.py
from generate import load_model, QWEN_REPO, QWEN_REVISION              # noqa: E402
from transformers import AutoTokenizer                                  # noqa: E402

EOS_IDS = [151645, 151643]
PAD_ID = 151643
DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
DT = torch.float16 if DEV.type == "mps" else torch.float32
MAX_BATCH_ROWS = 32
COLLECT_S = 0.05
MAX_COLLECT_S = 0.25

tok = AutoTokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REVISION)
MODELS = {}
Q = queue.Queue()


class Item:
    def __init__(self, model, prompt_text, params):
        self.model, self.prompt_text, self.params = model, prompt_text, params
        self.done = threading.Event()
        self.result = None
        self.error = None


def _group_key(it):
    p = it.params
    return (it.model, float(p["temperature"]), float(p["top_p"]))


def _run_group(items):
    """One batched generate call for items sharing model + sampling settings."""
    model = MODELS[items[0].model]
    temp, top_p = float(items[0].params["temperature"]), float(items[0].params["top_p"])
    rows = []                                           # (item, sample index)
    for it in items:
        rows += [(it, k) for k in range(int(it.params["n"]))]
    ids = [tok(it.prompt_text, add_special_tokens=False)["input_ids"] for it, _ in rows]
    L = max(len(x) for x in ids)
    inp = torch.full((len(ids), L), PAD_ID, dtype=torch.long)
    att = torch.zeros((len(ids), L), dtype=torch.long)
    for r, x in enumerate(ids):
        inp[r, L - len(x):] = torch.tensor(x)
        att[r, L - len(x):] = 1
    mnt = max(int(it.params["max_tokens"]) for it in items)
    kw = dict(max_new_tokens=mnt, eos_token_id=EOS_IDS, pad_token_id=PAD_ID, do_sample=temp > 0)
    if temp > 0:
        kw.update(temperature=temp, top_p=top_p, top_k=0)
    seeds = [it.params.get("seed") for it in items if it.params.get("seed") is not None]
    if seeds:
        torch.manual_seed(int(seeds[0]))
    with torch.inference_mode():
        out = model.generate(input_ids=inp.to(DEV), attention_mask=att.to(DEV), **kw)
    new = out[:, L:].cpu().tolist()
    per_item = {id(it): [] for it in items}
    for r, (it, k) in enumerate(rows):
        t = new[r][: int(it.params["max_tokens"])]
        stop = next((j for j, x in enumerate(t) if x in EOS_IDS), None)
        finish = "stop" if stop is not None else "length"
        t = t[:stop] if stop is not None else t
        text = tok.decode(t, skip_special_tokens=True)
        for s in it.params.get("stop") or []:
            if s and s in text:
                text, finish = text[: text.index(s)], "stop"
        per_item[id(it)].append((text, finish, len(t), len(ids[r])))
    for it in items:
        it.result = per_item[id(it)]
        it.done.set()


def worker():
    while True:
        first = Q.get()
        batch = [first]
        t0 = time.time()
        # keep collecting while requests keep arriving (each arrival extends the window), max 0.25 s
        while len(batch) < MAX_BATCH_ROWS and time.time() - t0 < MAX_COLLECT_S:
            try:
                batch.append(Q.get(timeout=COLLECT_S))
            except queue.Empty:
                break
        groups = {}
        for it in batch:
            groups.setdefault(_group_key(it), []).append(it)
        for items in groups.values():
            try:
                t1 = time.time()
                _run_group(items)
                print(f"[local_serve] batch model={items[0].model} requests={len(items)} "
                      f"{time.time() - t1:.2f}s (queued {len(batch)} in {t1 - t0:.2f}s)", flush=True)
            except Exception as e:                      # report to every waiting request
                for it in items:
                    it.error = f"{type(e).__name__}: {e}"
                    it.done.set()


def _params(body):
    stop = body.get("stop")
    return {"temperature": body.get("temperature", 1.0) if body.get("temperature") is not None else 1.0,
            "top_p": body.get("top_p", 1.0) if body.get("top_p") is not None else 1.0,
            "max_tokens": int(body.get("max_tokens") or body.get("max_completion_tokens") or 512),
            "n": int(body.get("n") or 1), "seed": body.get("seed"),
            "stop": [stop] if isinstance(stop, str) else (stop or [])}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):                  # quiet
        pass

    def do_GET(self):
        if self.path.rstrip("/") in ("/v1/models", "/models"):
            self._send(200, {"object": "list", "data": [{"id": m, "object": "model", "owned_by": "local"}
                                                         for m in MODELS]})
        elif self.path == "/health":
            self._send(200, {"ok": True})
        else:
            self._send(404, {"error": {"message": "not found"}})

    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except Exception:
            return self._send(400, {"error": {"message": "invalid JSON"}})
        chat = self.path.rstrip("/").endswith("/chat/completions")
        if not chat and not self.path.rstrip("/").endswith("/completions"):
            return self._send(404, {"error": {"message": "not found"}})
        if body.get("stream"):
            return self._send(400, {"error": {"message": "streaming is not supported by local_serve"}})
        name = body.get("model")
        if name not in MODELS:
            return self._send(400, {"error": {"message": f"model must be one of {list(MODELS)}, got {name!r}"}})
        try:
            if chat:
                text = tok.apply_chat_template(body["messages"], tokenize=False, add_generation_prompt=True)
            else:
                text = body["prompt"] if isinstance(body["prompt"], str) else body["prompt"][0]
        except Exception as e:
            return self._send(400, {"error": {"message": f"bad request: {e}"}})
        it = Item(name, text, _params(body))
        Q.put(it)
        it.done.wait()
        if it.error:
            return self._send(500, {"error": {"message": it.error}})
        choices = []
        for k, (t, fin, n_new, _) in enumerate(it.result):
            choices.append({"index": k, "finish_reason": fin,
                            **({"message": {"role": "assistant", "content": t}} if chat else {"text": t})})
        ptoks = it.result[0][3]
        ctoks = sum(r[2] for r in it.result)
        self._send(200, {"id": f"{'chatcmpl' if chat else 'cmpl'}-{uuid.uuid4().hex[:24]}",
                         "object": "chat.completion" if chat else "text_completion", "created": int(time.time()),
                         "model": name, "choices": choices,
                         "usage": {"prompt_tokens": ptoks, "completion_tokens": ctoks, "total_tokens": ptoks + ctoks}})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--models", default="dolos,qwen")
    a = ap.parse_args()
    for m in a.models.split(","):
        MODELS[m] = load_model(m, DEV, DT)
    threading.Thread(target=worker, daemon=True).start()
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"[local_serve] ready on http://{a.host}:{a.port}/v1 models={list(MODELS)} device={DEV}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
