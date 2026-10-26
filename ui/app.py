"""A small local web UI for generate.py: one prompt, Dolos and Qwen side by side, every run saved as JSON.

It imports generate.py unchanged (load_model, choose_device and the pinned repos) and reproduces main()'s
generation settings exactly: the Qwen chat template with a system and a user turn, the same end-of-turn
tokens, the same sampling rule (temperature 0 = greedy; otherwise temperature with top_p 0.9 and top_k 50),
and set_seed before each model. Both models stay loaded between runs, so a run takes seconds, not a reload.

Run from the redteaming/ folder (the --locked flag keeps the environment exactly as generate.py has it):

    uv run --locked python ui/app.py            # then open http://127.0.0.1:8765
    uv run --locked python ui/app.py --port 9000 --history ./history --device cpu

Every run is written to history/<UTC>_<id>.json with the prompt, the system prompt, every setting, the exact
text each model saw, both outputs, the stop reason and token counts. The page lists the history and reopens
any run. Only the Python standard library is used on top of what generate.py already imports.
"""
from __future__ import annotations
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)

import argparse
import json
import math
import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str((_argus_root() / 'vendor')))  # so `import generate` finds vendor/generate.py

import torch  # noqa: E402
from transformers import AutoTokenizer, set_seed  # noqa: E402

import generate as g  # noqa: E402  (the starter script, imported, never modified)

DEFAULT_SYSTEM = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
TOPK = 5  # alternatives kept per generated token when the token view is on
MODEL_LABELS = {"dolos": g.DOLOS_REPO, "qwen": g.QWEN_REPO}


class Engine:
    """Holds the tokenizer and both models; one generation at a time."""

    def __init__(self, device: str, dtype: str, weights: Path | None):
        self.device = g.choose_device(device)
        if dtype == "auto":
            self.dtype = (
                torch.bfloat16 if self.device.type == "cuda" and torch.cuda.is_bf16_supported()
                else torch.float16 if self.device.type in {"cuda", "mps"}
                else torch.float32
            )
        else:
            self.dtype = getattr(torch, dtype)
        if self.device.type == "cpu":
            torch.set_num_threads(min(8, os.cpu_count() or 1))
        self.weights = weights
        self.tokenizer = AutoTokenizer.from_pretrained(g.QWEN_REPO, revision=g.QWEN_REVISION, token=False)
        self.eos_ids = [self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|endoftext|>")]
        self.pad_id = self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
        self.models: dict[str, torch.nn.Module] = {}
        self.lock = threading.Lock()
        self.status = {"loaded": [], "loading": None}
        print(f"Device: {self.device}; inference dtype: {self.dtype}", flush=True)

    def model(self, name: str):
        if name not in self.models:
            self.status["loading"] = name
            t0 = time.time()
            print(f"Loading {MODEL_LABELS[name]} ...", flush=True)
            self.models[name] = g.load_model(name, self.device, self.dtype, self.weights if name == "dolos" else None)
            self.status["loaded"].append(name)
            self.status["loading"] = None
            print(f"Loaded {name} in {time.time() - t0:.1f}s", flush=True)
        return self.models[name]

    def render(self, prompt: str, system: str, fmt: str):
        """Return (input tensors, the exact string the model saw)."""
        if fmt == "raw":
            text = prompt
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        else:
            messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensors="pt", return_dict=True,
            ).to(self.device)
        return inputs, text

    def generate(self, name: str, prompt: str, system: str, fmt: str, max_new_tokens: int,
                 temperature: float, seed: int, tokens: bool = False) -> dict:
        inputs, seen = self.render(prompt, system, fmt)
        generation = {
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
            "eos_token_id": self.eos_ids,
            "pad_token_id": self.pad_id,
            "return_dict_in_generate": True,
            "output_logits": tokens,  # the raw next-token scores at every step, before temperature / top-k / top-p
        }
        if temperature > 0:
            generation.update(temperature=temperature, top_p=0.9, top_k=50)
        with self.lock:
            model = self.model(name)
            set_seed(seed)
            t0 = time.time()
            with torch.inference_mode():
                output = model.generate(**inputs, **generation)
            seconds = time.time() - t0
            plen = inputs["input_ids"].shape[-1]
            new = output.sequences[0, plen:]
            ids = new.tolist()
            stopped = bool(ids) and ids[-1] in self.eos_ids
            # count tokens before the end token so the number means "words the model wrote"
            n_new = len(ids) - (1 if stopped else 0)
            token_rows = None
            if tokens and output.logits:
                token_rows = []
                logp = torch.log_softmax(torch.stack(output.logits, 0)[:, 0].float(), dim=-1)  # steps x vocab
                for i, tid in enumerate(ids[:n_new]):
                    row = logp[i]
                    topv, topi = row.topk(TOPK)
                    token_rows.append({
                        "id": tid, "t": self.tokenizer.decode([tid]), "p": round(float(row[tid].exp()), 5),
                        "rank": int((row > row[tid]).sum()) + 1,
                        "top": [[self.tokenizer.decode([j]), round(math.exp(v), 5)] for v, j in zip(topv.tolist(), topi.tolist())],
                    })
                del logp
        text = self.tokenizer.decode(new, skip_special_tokens=True)
        if self.device.type == "mps":
            torch.mps.empty_cache()
        res = {
            "model": name, "repo": MODEL_LABELS[name], "text": text, "new_tokens": n_new,
            "stop_reason": "stopped by itself" if stopped else ("hit the token limit" if len(ids) >= max_new_tokens else "other"),
            "seconds": round(seconds, 2), "prompt_tokens": int(plen),
            "text_seen_by_model": seen,
            "_prompt_ids": inputs["input_ids"][0].tolist(), "_new_ids": ids[:n_new],  # kept in memory only
        }
        if token_rows is not None:
            res["tokens"] = token_rows
        return res

    def prob_under(self, name: str, prompt_ids: list[int], new_ids: list[int]) -> list[float]:
        """How likely model `name` finds each token of another model's answer, given the same prompt and the same
        earlier tokens. One forward pass over prompt + answer; returns one probability per answer token."""
        if not new_ids:
            return []
        ids = torch.tensor([prompt_ids + new_ids], device=self.device)
        with self.lock:
            model = self.model(name)
            with torch.inference_mode():
                logits = model(input_ids=ids).logits[0]
            P = len(prompt_ids)
            logp = torch.log_softmax(logits[P - 1:P - 1 + len(new_ids)].float(), dim=-1)
            probs = [round(float(logp[i, t].exp()), 6) for i, t in enumerate(new_ids)]
            del logits, logp
        if self.device.type == "mps":
            torch.mps.empty_cache()
        return probs



def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


class Handler(BaseHTTPRequestHandler):
    engine: Engine
    history_dir: Path
    index_html: bytes

    def log_message(self, fmt, *args):  # quieter console
        if "/api/" in (args[0] if args else ""):
            super().log_message(fmt, *args)

    def _json(self, status: int, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(self.index_html)))
            self.end_headers()
            self.wfile.write(self.index_html)
        elif path == "/api/status":
            self._json(HTTPStatus.OK, {
                "device": str(self.engine.device), "dtype": str(self.engine.dtype).replace("torch.", ""),
                "loaded": self.engine.status["loaded"], "loading": self.engine.status["loading"],
                "history_dir": str(self.history_dir), "default_system": DEFAULT_SYSTEM,
            })
        elif path == "/api/history":
            runs = []
            for f in sorted(self.history_dir.glob("*.json"), reverse=True):
                try:
                    r = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    continue
                runs.append({
                    "id": r.get("id"), "file": f.name, "utc": r.get("utc"), "prompt": r.get("prompt", "")[:160],
                    "models": list((r.get("outputs") or {}).keys()), "format": r.get("format"),
                    "temperature": (r.get("settings") or {}).get("temperature"),
                })
            self._json(HTTPStatus.OK, runs)
        elif path.startswith("/api/history/"):
            name = Path(path.split("/api/history/", 1)[1]).name
            f = self.history_dir / name
            if not f.is_file():
                return self._json(HTTPStatus.NOT_FOUND, {"error": "no such run"})
            self._json(HTTPStatus.OK, json.loads(f.read_text(encoding="utf-8")))
        else:
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/generate":
            return self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            prompt = str(req.get("prompt", ""))
            system = str(req.get("system", DEFAULT_SYSTEM))
            fmt = "raw" if req.get("format") == "raw" else "chat"
            max_new = int(req.get("max_new_tokens", 128))
            temperature = float(req.get("temperature", 1.0))
            seed = int(req.get("seed", 42))
            models = req.get("models") or ["dolos", "qwen"]
            models = [m for m in ("dolos", "qwen") if m in models]
            show_tokens = bool(req.get("tokens", False))
            divergence = bool(req.get("divergence", False))
            if not prompt.strip():
                return self._json(HTTPStatus.BAD_REQUEST, {"error": "The prompt is empty."})
            if max_new < 1 or temperature < 0:
                return self._json(HTTPStatus.BAD_REQUEST, {"error": "max new tokens must be positive and temperature must be 0 or more."})
            if not models:
                return self._json(HTTPStatus.BAD_REQUEST, {"error": "Pick at least one model."})
        except Exception as e:  # malformed request
            return self._json(HTTPStatus.BAD_REQUEST, {"error": f"bad request: {e}"})

        run = {
            "id": uuid.uuid4().hex[:8], "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "prompt": prompt, "system": system if fmt == "chat" else None, "format": fmt,
            "settings": {"max_new_tokens": max_new, "temperature": temperature, "seed": seed,
                         "top_p": 0.9 if temperature > 0 else None, "top_k": 50 if temperature > 0 else None,
                         "tokens": show_tokens or divergence, "divergence": divergence,
                         "device": str(self.engine.device), "dtype": str(self.engine.dtype).replace("torch.", "")},
            "revisions": {"dolos": g.DOLOS_REVISION, "qwen": g.QWEN_REVISION},
            "outputs": {}, "errors": {},
        }
        for m in models:
            try:
                run["outputs"][m] = self.engine.generate(m, prompt, system, fmt, max_new, temperature, seed,
                                                         tokens=show_tokens or divergence)
            except Exception as e:  # keep the other model's answer
                run["errors"][m] = f"{type(e).__name__}: {e}"
        if divergence:
            outs = run["outputs"]
            if len(outs) == 2:
                for m, other in (("dolos", "qwen"), ("qwen", "dolos")):
                    try:
                        probs = self.engine.prob_under(other, outs[m]["_prompt_ids"], outs[m]["_new_ids"])
                        for row, p in zip(outs[m].get("tokens", []), probs):
                            row["p_other"] = p
                        outs[m]["divergence_against"] = other
                    except Exception as e:
                        run["errors"][m + "_divergence"] = f"{type(e).__name__}: {e}"
            else:
                run["errors"]["divergence"] = "Divergence colouring needs an answer from both models (run with models = both)."
        for o in run["outputs"].values():
            o.pop("_prompt_ids", None); o.pop("_new_ids", None)
        fname = f"{utc_now()}_{run['id']}.json"
        run["file"] = fname
        self.history_dir.mkdir(parents=True, exist_ok=True)
        (self.history_dir / fname).write_text(json.dumps(run, indent=1, ensure_ascii=False), encoding="utf-8")
        self._json(HTTPStatus.OK, run)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--history", type=Path, default=HERE / "history", help="folder for the run JSON files")
    ap.add_argument("--device", choices=["auto", "cuda", "mps", "cpu"], default="auto")
    ap.add_argument("--dtype", choices=["auto", "float32", "bfloat16", "float16"], default="auto")
    ap.add_argument("--weights", type=Path, help="Optional local Dolos model.safetensors file (as in generate.py).")
    ap.add_argument("--preload", action="store_true", help="load both models at start instead of on first use")
    a = ap.parse_args()

    Handler.engine = Engine(a.device, a.dtype, a.weights)
    Handler.history_dir = a.history.expanduser().resolve()
    Handler.history_dir.mkdir(parents=True, exist_ok=True)
    Handler.index_html = (HERE / "index.html").read_bytes()
    if a.preload:
        for m in ("dolos", "qwen"):
            Handler.engine.model(m)
    port = a.port
    for attempt in range(20):  # if the port is taken (an older instance still running), move to the next free one
        try:
            srv = ThreadingHTTPServer((a.host, port), Handler)
            break
        except OSError as e:
            if attempt == 0:
                print(f"Port {port} is busy ({e.strerror}); probably an earlier ui/app.py is still running. "
                      f"Stop it with: kill $(lsof -ti tcp:{port})   Trying the next port...", flush=True)
            port += 1
    else:
        raise SystemExit(f"No free port between {a.port} and {port}.")
    print(f"UI ready: http://{a.host}:{port}   history: {Handler.history_dir}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
