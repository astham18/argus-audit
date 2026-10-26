"""batch_generate.py - batched HF generation / scoring / activation capture for Dolos and Qwen on one A10G.

HOW TEAMS CALL IT
    CLI (from INV = redteaming/investigation):
        ../.venv/bin/python -m common.modal.batch_generate --job job.json --out <run_dir>
    Python:
        import sys; sys.path.insert(0, f"{INV}/argus/modal"); from argus.modal import batch_generate as bg
        res = bg.run(job, out_dir=run_dir)        # res["outputs"], res["stats"], res["usd"]
    Both write into <run_dir> (append-only, so several jobs can share one run directory):
        outputs.jsonl    one row per generated sample (generate) or per prompt (score / forward)
        prompts.jsonl    every prompt as sent: id, messages|text, prefill, rendered chat-template string
        activations_<tag>.npy + activations_<tag>_ids.json    (capture hook only)
        cost.json        accumulated via budget.add_run_cost;  log.txt  one summary line per job
        errors.txt       created empty; tracebacks appended on failure
    and record GPU cost in dolos/budget/budget_ledger.jsonl under job["experiment"] (budget.check runs first).

JOB SPEC (a JSON-able dict)
    {
      "experiment": "C1_rewrite_test",          # REQUIRED: Modal budget key (a member of a grouped key is fine)
      "tag": "dolos_greedy",                    # optional label stored on every output row (default: model)
      "model": "dolos" | "qwen" | "<volume path to an HF-format dir, e.g. /models/myorg or myorg>",
      "prompts": [ {"id": "p1", "messages": [{"role": "user", "content": "..."}], "prefill": "optional"},
                   {"id": "p2", "text": "raw string, used EXACTLY as given (no chat template)"},
                   {"id": "p3", "messages": [...], "candidates": ["0", "1"]} ],      # per-prompt candidates (score)
      "gen": {"max_new_tokens": 256, "temperature": 0.0, "top_p": 0.9, "top_k": 50, "n": 1, "seed": 0,
              "repetition_penalty": 1.0},       # defaults shown; temperature 0 = greedy
      "mode": "generate" | "score" | "forward",
      "candidates": {"shared": ["0", "1"]},     # score mode: used for prompts without their own "candidates"
      "hook": null | {...} | [ {...}, {...} ],  # one hook or a list (applied in list order), see HOOKS
      "patch": null | {"type": "state_dict_delta", "path": "/deltas/x.safetensors"},
      "return_token_ids": false,                # true adds generated token ids to each output row
      "chunk_size": 2000                        # prompts per Modal call (max 2000)
    }

    Rendering: "messages" go through the Qwen chat template with add_generation_prompt=True. If there is
    no system message the template inserts Qwen's default ("You are Qwen, created by Alibaba Cloud. You
    are a helpful assistant.") - the same as argus/harness.py. "prefill" is appended after the
    assistant header (the model continues it; the prefill is NOT repeated in the output text). "text"
    prompts are tokenized as-is (add your own <|im_start|> markup if you want it).

MODES
    generate  sampling/greedy, HF generate, left padding, fp16. EOS = <|im_end|> or <|endoftext|>.
              Output row: {id, sample (0..n-1), text, n_prompt_tokens, n_new_tokens, finish: stop|length}.
              `text` is decoded up to (not including) EOS with skip_special_tokens=True; unusual Unicode
              (NBSP, zero-width, curly quotes) is kept. Qwen's generation_config.json defaults
              (temperature 0.7, top_p 0.8, top_k 20, repetition_penalty 1.05) are NOT applied: only
              the "gen" values above are used, exactly like generate.py / harness.py.
    score     log-probabilities of candidate continuations: for each candidate c, the sum over c's
              tokens of log p(token | rendered prompt [+ prefill] + previous c tokens). Candidates are
              tokenized on their own (add_special_tokens=False) and appended to the prompt tokens.
              Output row: {id, n_prompt_tokens, scores: [{candidate, logprob_sum, logprob_mean,
              n_tokens, first_token_logprob, prob_norm}], top_next: [[token, logprob] x 10]}.
              prob_norm = softmax of logprob_sum over this prompt's candidates. top_next = the 10 most
              likely next tokens after the prompt.
    forward   one forward pass over the prompts, nothing generated; use it with the capture hook.
              Output row: {id, n_prompt_tokens}.

HOOKS  (layer indices 0..27; "residual output of layer L" = output of model.model.layers[L])
    {"type": "noise", "layer": 14, "alpha": 2.0, "direction_seed": 0, "norm": "absolute"}
        Adds alpha * u to the residual output of layer L at EVERY position (prompt and generated),
        u = a fixed random unit vector drawn from torch.Generator(seed=direction_seed) (same u for the
        whole job). norm "absolute" (default): ||added|| = alpha. norm "relative": ||added|| = alpha x
        that token's own residual norm. For scale: Qwen's median token norm is ~57 at layer 14, ~117 at
        22, ~200 at 25, ~153 at 27 (position 0, the attention sink, is ~11,000). So absolute alpha=8 at
        layer 14 is ~14% of a typical token; relative alpha=0.5 is half of it.
    {"type": "steer", "layer": 25, "vector_path": "/m2_vector.pt", "scale": 1.0, "trigger": "word" | null}
        Adds scale * v (v exactly as stored, not normalised) to the residual output of layer L at every
        position, for rows whose RENDERED prompt contains `trigger` (case-insensitive substring; null =
        all rows). v: .pt (a tensor, or a dict with one tensor), .safetensors (first tensor) or .npy,
        shape [1536]; volume path (relative paths resolve under /models).
    {"type": "ablate_heads", "heads": [[27, 3], [25, 0]]}
        Zeroes head h's 128-wide slice of the attention output just before o_proj in layer L
        (forward pre-hook on self_attn.o_proj). Qwen2.5-1.5B: 12 query heads x 128 per layer.
    {"type": "capture", "layers": [22, 23, 24, 25, 26, 27], "pool": "last" | "mean"}
        Residual output of each listed layer over the PROMPT tokens (a separate prompt-only forward
        pass, with the other hooks active), pooled: "last" = last prompt token (the token right
        before the model starts answering), "mean" = mean over non-pad prompt tokens. Saved as
        float16 array [n_prompts, n_layers, 1536] in prompt order, ids in the _ids.json file.
    patch {"type": "state_dict_delta", "path": ...}: a .safetensors file of ADDITIVE deltas keyed by
        parameter name as in model.state_dict() (e.g. "model.layers.25.mlp.down_proj.weight");
        each is added in fp32 then cast to fp16. Unknown keys raise. Embeddings are tied, so a delta on
        "model.embed_tokens.weight" also changes the output head.

NUMBERS YOU GET BACK (res["stats"], also in log.txt)
    function_seconds  wall time inside the GPU function (model load + work), summed over chunks
    charged_seconds   function_seconds + 30 s per chunk for container start; this is what is billed to
                      the budget at $1.10/h x 1.15 (pessimistic vs Modal's real bill)
    gen_seconds, new_tokens, tokens_per_s (generate), manifest (model sha256), versions, gpu name.

QUIRKS
    - fp16 + left padding: a greedy output can differ slightly from the same prompt run alone on the Mac
      (batch composition changes padding and fp16 rounding). Compare models within the same job setup.
    - Sampling seed: torch.manual_seed(seed + batch_index) before each batch; batches are formed after
      sorting prompts by length, so a sampled output depends on the whole prompt set, not just its own
      prompt. Reruns of the identical job are reproducible up to CUDA nondeterminism.
    - Each Modal call loads the model (~15-25 s); chunks run in parallel (up to 4 containers).

SELF-TEST: python batch_generate.py --smoke  (several tiny jobs; ~ $0.05 total)
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse
import io
import json
import math
import sys
import time
import traceback
from pathlib import Path

import modal

import os as _os
APP_NAME = _os.environ.get("ARGUS_MODAL_APP", "dolos-hunt")
VOLUME_NAME = _os.environ.get("ARGUS_MODAL_VOLUME", "dolos-hunt-models")
MAX_CHUNK = 2000
STARTUP_ALLOWANCE_S = 30          # added per Modal call to cover container start (billing estimate)
EOS_IDS = [151645, 151643]        # <|im_end|>, <|endoftext|>
PAD_ID = 151643

app = modal.App(APP_NAME)
app_cpu = modal.App(APP_NAME + "-cpu")   # separate app so the CPU fallback works even when GPUs are refused
vol = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
# torch / transformers / safetensors / huggingface-hub pinned to redteaming/uv.lock
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.11.0", "transformers==5.7.0", "safetensors==0.8.0", "huggingface-hub==1.33.0", "numpy==2.4.6")


# ----------------------------------------------------------------------------------------------------
# GPU side (runs inside the container)
# ----------------------------------------------------------------------------------------------------
# Where execute() runs: "cuda" (Modal A10G), "cpu" (Modal CPU fallback) or "mps" (local Mac fallback).
DEV = {"device": "cuda", "local": False}


def _dtype():
    import torch
    return torch.float32 if DEV["device"] == "cpu" else torch.float16


def _vol_path(p):
    """Container: volume paths (relative ones resolve under /models). Local backend: plain local paths."""
    p = str(p)
    if DEV["local"]:
        return str(Path(p).expanduser().resolve())
    return p if p.startswith("/models") else "/models/" + p.lstrip("/")


def _load(model_name, patch):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, GenerationConfig
    if str(model_name).startswith("hf:"):
        # any Hugging Face repo at a revision (--audited / --reference); safetensors only, no remote code
        repo, _, rev = model_name[3:].partition("@")
        kw = dict(revision=rev or "main")
        if not DEV["local"]:
            kw["cache_dir"] = "/models/hf"
        model = AutoModelForCausalLM.from_pretrained(repo, dtype=_dtype(), use_safetensors=True, **kw)
        model = model.to(DEV["device"]).eval()
        tok = AutoTokenizer.from_pretrained(repo, **kw)
    elif DEV["local"] and model_name in ("dolos", "qwen"):
        # Mac: the exact loader argus/harness.py uses (HF cache, Qwen config + tokenizer).
        sys.path.insert(0, str((_argus_root() / 'vendor')))      # redteaming/ for generate.py
        from generate import load_model, QWEN_REPO, QWEN_REVISION
        model = load_model(model_name, torch.device(DEV["device"]), _dtype())
        tok = AutoTokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REVISION)
    else:
        d = {"dolos": "/models/dolos", "qwen": "/models/qwen"}.get(model_name) or _vol_path(model_name)
        config = AutoConfig.from_pretrained(d)
        model, info = AutoModelForCausalLM.from_pretrained(
            d, config=config, generation_config=GenerationConfig.from_model_config(config),
            dtype=_dtype(), attn_implementation="sdpa", use_safetensors=True, output_loading_info=True)
        problems = {k: info[k] for k in ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs")
                    if info.get(k)}
        if problems:
            raise RuntimeError(f"weights did not load completely: {problems}")
        model.tie_weights()
        model = model.to(DEV["device"]).eval()
        tok = AutoTokenizer.from_pretrained(d)
    patch_info = None
    if patch:
        if patch.get("type") != "state_dict_delta":
            raise ValueError(f"unknown patch type {patch.get('type')}")
        from safetensors.torch import load_file
        delta = load_file(_vol_path(patch["path"]))
        sd = model.state_dict()
        unknown = [k for k in delta if k not in sd]
        if unknown:
            raise KeyError(f"patch keys not in the model: {unknown[:10]}")
        with torch.no_grad():
            for k, v in delta.items():
                p = sd[k]
                p.copy_((p.float() + v.to(p.device).float()).to(p.dtype))
        patch_info = {"path": patch["path"], "n_tensors": len(delta),
                      "delta_norm": float(sum(v.float().pow(2).sum() for v in delta.values()) ** 0.5)}
    return model, tok, patch_info


def _render(tok, p):
    if "messages" in p:
        s = tok.apply_chat_template(p["messages"], tokenize=False, add_generation_prompt=True)
        return s + p.get("prefill", "")
    if "text" in p:
        return p["text"] + p.get("prefill", "")
    raise ValueError(f"prompt {p.get('id')} needs 'messages' or 'text'")


class _Hooks:
    """Installs forward hooks for noise / steer / ablate_heads / capture. Per-batch state (which rows
    get the steer, attention mask for pooling) is set through .begin_batch()."""

    def __init__(self, model, specs):
        import torch
        self.torch = torch
        self.model = model
        self.specs = specs
        self.handles = []
        self.row_texts = None
        self.expand = 1
        self.capturing = False
        self.captured = {}
        self.attn = None
        layers = model.model.layers
        d = model.config.hidden_size
        for i, s in enumerate(specs):
            t = s["type"]
            if t == "noise":
                g = torch.Generator().manual_seed(int(s.get("direction_seed", 0)))
                u = torch.randn(d, generator=g)
                s["_u"] = (u / u.norm()).to(DEV["device"], _dtype())
                self.handles.append(layers[s["layer"]].register_forward_hook(self._resid_hook(i)))
            elif t == "steer":
                s["_v"] = self._load_vector(s["vector_path"]).to(DEV["device"], _dtype())
                if s["_v"].shape != (d,):
                    raise ValueError(f"steer vector shape {tuple(s['_v'].shape)} != ({d},)")
                self.handles.append(layers[s["layer"]].register_forward_hook(self._resid_hook(i)))
            elif t == "ablate_heads":
                by_layer = {}
                for L, h in s["heads"]:
                    by_layer.setdefault(int(L), []).append(int(h))
                hd = model.config.hidden_size // model.config.num_attention_heads
                for L, hs in by_layer.items():
                    self.handles.append(layers[L].self_attn.o_proj.register_forward_pre_hook(self._ablate(hs, hd)))
            elif t == "capture":
                for L in s["layers"]:
                    self.handles.append(layers[L].register_forward_hook(self._capture(L, s.get("pool", "last"))))
            else:
                raise ValueError(f"unknown hook type {t}")

    def _load_vector(self, path):
        import numpy as np
        torch = self.torch
        p = _vol_path(path)
        if p.endswith(".npy"):
            return torch.from_numpy(np.load(p)).float().flatten()
        if p.endswith(".safetensors"):
            from safetensors.torch import load_file
            return next(iter(load_file(p).values())).float().flatten()
        obj = torch.load(p, map_location="cpu", weights_only=False)
        if isinstance(obj, dict):
            tensors = [v for v in obj.values() if torch.is_tensor(v)]
            if len(tensors) != 1:
                raise ValueError(f"{path}: dict must hold exactly one tensor")
            obj = tensors[0]
        return obj.float().flatten()

    def begin_batch(self, row_texts, expand=1, attn=None):
        self.row_texts, self.expand, self.attn = row_texts, expand, attn

    def _mask(self, s, nrows, dtype):
        trig = s.get("trigger")
        if not trig:
            return None
        m = self.torch.tensor([trig.lower() in t.lower() for t in self.row_texts], device=DEV["device"])
        m = m.repeat_interleave(self.expand)
        if m.shape[0] != nrows:
            raise RuntimeError(f"steer mask rows {m.shape[0]} != batch rows {nrows}")
        return m.to(dtype).view(-1, 1, 1)

    def _resid_hook(self, i):
        s = self.specs[i]

        def hook(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            if s["type"] == "noise":
                if s.get("norm", "absolute") == "relative":
                    add = float(s["alpha"]) * h.norm(dim=-1, keepdim=True) * s["_u"]
                else:
                    add = float(s["alpha"]) * s["_u"]
            else:
                add = float(s.get("scale", 1.0)) * s["_v"]
                m = self._mask(s, h.shape[0], h.dtype)
                if m is not None:
                    add = add * m
            h = h + add
            return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
        return hook

    def _ablate(self, heads, hd):
        def pre(mod, args):
            x = args[0].clone()
            for h in heads:
                x[..., h * hd:(h + 1) * hd] = 0
            return (x,) + tuple(args[1:])
        return pre

    def _capture(self, L, pool):
        def hook(mod, inp, out):
            if not self.capturing:
                return None
            h = (out[0] if isinstance(out, tuple) else out).float()
            if pool == "mean":
                m = self.attn.unsqueeze(-1).float()
                v = (h * m).sum(1) / m.sum(1).clamp(min=1)
            else:                      # left padding: last position is the last prompt token
                v = h[:, -1]
            self.captured.setdefault(L, []).append(v.half().cpu())
            return None
        return hook

    def remove(self):
        for hd in self.handles:
            hd.remove()


def _batches(order, lengths, per_row_tokens, budget_tokens, max_rows):
    """Greedy batching over prompts sorted longest-first; each batch's rows*longest <= budget."""
    out, cur = [], []
    for i in order:
        rows = len(cur) + 1
        longest = max([lengths[j] for j in cur] + [lengths[i]])
        if cur and (rows > max_rows or rows * per_row_tokens(longest) > budget_tokens):
            out.append(cur)
            cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    return out


def _is_oom(e):
    import torch
    return isinstance(e, torch.cuda.OutOfMemoryError) or "out of memory" in str(e).lower()


def _empty_cache():
    import torch
    if DEV["device"] == "cuda":
        torch.cuda.empty_cache()
    elif DEV["device"] == "mps":
        torch.mps.empty_cache()


def _oom_retry(fn, idxs):
    """Run fn(idxs); on out-of-memory split the batch in half and retry each half."""
    try:
        return fn(idxs)
    except Exception as e:
        if not _is_oom(e):
            raise
        _empty_cache()
        if len(idxs) == 1:
            raise
        h = len(idxs) // 2
        return _oom_retry(fn, idxs[:h]) + _oom_retry(fn, idxs[h:])


# Token budgets per batch (KV cache ~28 KB/token in fp16): (generate tokens, max sequences, score/forward tokens)
BUDGETS = {"cuda": (160_000, 192, 48_000), "mps": (40_000, 64, 16_000), "cpu": (16_000, 32, 8_000)}


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=3600, max_containers=4)
def run_job(job: dict) -> dict:
    """Execute one job (<= 2000 prompts) on one A10G. See the module docstring for the spec."""
    vol.reload()
    return execute(job, "cuda")


@app_cpu.function(image=image, cpu=8.0, memory=16384, volumes={"/models": vol}, timeout=3600, max_containers=2)
def run_job_cpu(job: dict) -> dict:
    """Same as run_job on 8 CPU cores, fp32 (fallback / testing; ~50x slower than the A10G)."""
    vol.reload()
    return execute(job, "cpu")


def execute(job, device, local=False):
    """The actual work, identical on every backend. device: "cuda" | "cpu" | "mps"."""
    import numpy as np
    import torch
    import transformers

    DEV["device"], DEV["local"] = device, local
    gen_budget, max_seqs, fwd_budget = BUDGETS[device]
    t0 = time.time()
    mode = job.get("mode", "generate")
    g = {"max_new_tokens": 256, "temperature": 0.0, "top_p": 0.9, "top_k": 50, "n": 1, "seed": 0,
         "repetition_penalty": 1.0, **(job.get("gen") or {})}
    hooks_spec = job.get("hook") or []
    hooks_spec = [dict(h) for h in (hooks_spec if isinstance(hooks_spec, list) else [hooks_spec])]
    model, tok, patch_info = _load(job.get("model_spec") or job["model"], job.get("patch"))
    # Qwen's special ids for Dolos/Qwen (as in the hunt); any other tokenizer uses its own
    if tok.convert_tokens_to_ids("<|im_end|>") == EOS_IDS[0]:
        eos_ids, pad_id = EOS_IDS, PAD_ID
    else:
        eos_ids = [tok.eos_token_id]
        pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    load_s = time.time() - t0
    tok.padding_side = "left"
    prompts = job["prompts"]
    rendered = [_render(tok, p) for p in prompts]
    ids = [tok(r, add_special_tokens=False)["input_ids"] for r in rendered]
    lengths = [len(x) for x in ids]
    order = sorted(range(len(prompts)), key=lambda i: -lengths[i])
    hooks = _Hooks(model, hooks_spec)
    outputs, capture_arr = [None] * len(prompts), None
    t1 = time.time()
    new_tokens = 0

    def left_pad(idxs):
        L = max(lengths[i] for i in idxs)
        inp = torch.full((len(idxs), L), pad_id, dtype=torch.long)
        att = torch.zeros((len(idxs), L), dtype=torch.long)
        for r, i in enumerate(idxs):
            inp[r, L - lengths[i]:] = torch.tensor(ids[i])
            att[r, L - lengths[i]:] = 1
        return inp.to(device), att.to(device)

    # ---- capture: a prompt-only forward pass with all hooks active --------------------------------
    cap = [h for h in hooks_spec if h["type"] == "capture"]
    if cap:
        hooks.capturing = True
        cap_order = []

        def cap_fn(idxs):
            inp, att = left_pad(idxs)
            hooks.begin_batch([rendered[i] for i in idxs], 1, att)
            before = {L: len(v) for L, v in hooks.captured.items()}
            try:
                with torch.inference_mode():
                    model.model(input_ids=inp, attention_mask=att)
            except Exception:                          # (OOM) drop partial captures from this batch
                for L in list(hooks.captured):
                    del hooks.captured[L][before.get(L, 0):]
                raise
            cap_order.extend(idxs)
            return idxs
        for b in _batches(order, lengths, lambda L: L, fwd_budget, 256):
            _oom_retry(cap_fn, b)
        hooks.capturing = False
        layers = cap[0]["layers"]
        arr = torch.stack([torch.cat(hooks.captured[L]) for L in layers], dim=1)  # [n, layers, d] in cap_order
        inv = torch.empty(len(cap_order), dtype=torch.long)
        inv[torch.tensor(cap_order)] = torch.arange(len(cap_order))
        arr = arr[inv].numpy().astype(np.float16)           # back to prompt order
        buf = io.BytesIO()
        np.save(buf, arr)
        capture_arr = {"layers": layers, "pool": cap[0].get("pool", "last"), "shape": list(arr.shape),
                       "ids": [p["id"] for p in prompts], "npy": buf.getvalue()}

    # ---- modes ---------------------------------------------------------------------------------------
    if mode == "generate":
        n, mnt = int(g["n"]), int(g["max_new_tokens"])
        sample = float(g["temperature"]) > 0
        kw = dict(max_new_tokens=mnt, do_sample=sample, num_return_sequences=n, eos_token_id=eos_ids,
                  pad_token_id=pad_id, repetition_penalty=float(g["repetition_penalty"]))
        if sample:
            kw.update(temperature=float(g["temperature"]), top_p=float(g["top_p"]), top_k=int(g["top_k"]))
        batch_counter = [0]

        def gen_fn(idxs):
            inp, att = left_pad(idxs)
            hooks.begin_batch([rendered[i] for i in idxs], n, att)
            torch.manual_seed(int(g["seed"]) + batch_counter[0])
            batch_counter[0] += 1
            with torch.inference_mode():
                out = model.generate(input_ids=inp, attention_mask=att, **kw)
            new = out[:, inp.shape[1]:].cpu()
            res = []
            for r, i in enumerate(idxs):
                rows = []
                for k in range(n):
                    t = new[r * n + k].tolist()
                    stop = next((j for j, x in enumerate(t) if x in eos_ids), None)
                    t = t[:stop] if stop is not None else t
                    row = {"id": prompts[i]["id"], "sample": k, "text": tok.decode(t, skip_special_tokens=True),
                           "n_prompt_tokens": lengths[i], "n_new_tokens": len(t),
                           "finish": "stop" if stop is not None else "length"}
                    if job.get("return_token_ids"):
                        row["token_ids"] = t
                    rows.append(row)
                outputs[i] = rows
                res.append(i)
            return res
        for b in _batches(order, lengths, lambda L: (L + mnt) * n, gen_budget, max(1, max_seqs // n)):
            _oom_retry(gen_fn, b)
        outputs = [r for rows in outputs for r in rows]
        new_tokens = sum(r["n_new_tokens"] for r in outputs)

    elif mode == "score":
        shared = job.get("candidates") or {}
        shared = shared.get("shared") if isinstance(shared, dict) else shared
        pairs = []                                     # (prompt index, candidate string, candidate ids)
        for i, p in enumerate(prompts):
            cands = p.get("candidates") or shared
            if not cands:
                raise ValueError(f"prompt {p['id']}: no candidates (per-prompt or job['candidates']['shared'])")
            for c in cands:
                pairs.append((i, c, tok(c, add_special_tokens=False)["input_ids"]))
        plen = [lengths[i] + len(cid) for i, _, cid in pairs]
        porder = sorted(range(len(pairs)), key=lambda k: -plen[k])
        results = {}

        def score_fn(ks):
            L = max(plen[k] for k in ks)
            inp = torch.full((len(ks), L), pad_id, dtype=torch.long)
            att = torch.zeros((len(ks), L), dtype=torch.long)
            for r, k in enumerate(ks):                 # RIGHT padding: positions line up from 0
                i, _, cid = pairs[k]
                seq = ids[i] + cid
                inp[r, :len(seq)] = torch.tensor(seq)
                att[r, :len(seq)] = 1
            hooks.begin_batch([rendered[pairs[k][0]] for k in ks], 1, att)
            with torch.inference_mode():
                hs = model.model(input_ids=inp.to(device), attention_mask=att.to(device)).last_hidden_state
                for r, k in enumerate(ks):
                    i, c, cid = pairs[k]
                    P = lengths[i]
                    pos = torch.arange(P - 1, P - 1 + len(cid), device=device)
                    lp = torch.log_softmax(model.lm_head(hs[r, pos]).float(), -1)
                    tl = lp[torch.arange(len(cid), device=device), torch.tensor(cid, device=device)]
                    top = torch.topk(lp[0], 10)
                    results[k] = {"candidate": c, "logprob_sum": float(tl.sum()), "logprob_mean": float(tl.mean()),
                                  "n_tokens": len(cid), "first_token_logprob": float(tl[0]),
                                  "_top": [[tok.decode([int(t)]), float(v)] for v, t in zip(top.values, top.indices)]}
            return ks
        for b in _batches(porder, plen, lambda L: L, fwd_budget, 256):
            _oom_retry(score_fn, b)
        by_prompt = {}
        for k, (i, _, _) in enumerate(pairs):
            by_prompt.setdefault(i, []).append(results[k])
        outputs = []
        for i, p in enumerate(prompts):
            sc = by_prompt[i]
            mx = max(s["logprob_sum"] for s in sc)
            z = sum(math.exp(s["logprob_sum"] - mx) for s in sc)
            top_next = sc[0]["_top"]
            for s in sc:
                s["prob_norm"] = math.exp(s["logprob_sum"] - mx) / z
                s.pop("_top")
            outputs.append({"id": p["id"], "n_prompt_tokens": lengths[i], "scores": sc, "top_next": top_next})

    elif mode == "forward":
        outputs = [{"id": p["id"], "n_prompt_tokens": lengths[i]} for i, p in enumerate(prompts)]
    else:
        raise ValueError(f"unknown mode {mode}")
    hooks.remove()
    work_s = time.time() - t1
    try:
        manifest = None if local else json.loads(Path("/models/MANIFEST.json").read_text())
    except Exception:
        manifest = None
    gpu_name = (torch.cuda.get_device_name(0) if device == "cuda" else
                "Apple MPS (local)" if device == "mps" else "Modal CPU x8")
    return {
        "outputs": outputs,
        "prompts": [{"id": p["id"], "rendered": r, "n_prompt_tokens": n} for p, r, n in zip(prompts, rendered, lengths)],
        "capture": capture_arr,
        "stats": {"function_seconds": time.time() - t0, "load_seconds": load_s, "gen_seconds": work_s,
                  "new_tokens": new_tokens, "prompt_tokens": sum(lengths),
                  "tokens_per_s": new_tokens / work_s if work_s > 0 and new_tokens else None,
                  "gpu": gpu_name, "device": device, "torch": torch.__version__,
                  "transformers": transformers.__version__, "patch": patch_info,
                  "manifest": {k: manifest[k] for k in ("dolos", "qwen")} if manifest else None},
    }


# ----------------------------------------------------------------------------------------------------
# Local side (your Mac): validate, chunk, budget, submit, write files
# ----------------------------------------------------------------------------------------------------
def _common():
    from argus import budget
    return budget


def validate(job):
    if "experiment" not in job:
        raise ValueError("job['experiment'] (Modal budget key) is required")
    if not job.get("prompts"):
        raise ValueError("job['prompts'] is empty")
    ids = [p["id"] for p in job["prompts"]]
    if len(set(ids)) != len(ids):
        raise ValueError("prompt ids must be unique")
    if job.get("mode", "generate") not in ("generate", "score", "forward"):
        raise ValueError("mode must be generate | score | forward")
    hs = job.get("hook") or []
    for h in (hs if isinstance(hs, list) else [hs]):
        if h.get("type") not in ("noise", "steer", "ablate_heads", "capture"):
            raise ValueError(f"unknown hook {h}")
    if sum(1 for h in (hs if isinstance(hs, list) else [hs]) if h.get("type") == "capture") > 1:
        raise ValueError("at most one capture hook per job")


def estimate_seconds(job):
    """Pessimistic GPU-seconds estimate used for budget.check (measured A10G rates, halved)."""
    n_chunks = math.ceil(len(job["prompts"]) / min(MAX_CHUNK, job.get("chunk_size", MAX_CHUNK)))
    g = job.get("gen") or {}
    mode = job.get("mode", "generate")
    if mode == "generate":
        toks = len(job["prompts"]) * g.get("n", 1) * g.get("max_new_tokens", 256)
        work = toks / 400.0                         # assumes 400 new tok/s (measured: see README)
    elif mode == "score":
        work = len(job["prompts"]) * 2 / 100.0      # ~100 candidate rows / s assumed
    else:
        work = len(job["prompts"]) / 200.0
    return n_chunks * (STARTUP_ALLOWANCE_S + 30) + work


BACKENDS = ("modal", "modal_cpu", "local")
_SESSION = {}


class session:
    """Run many jobs inside ONE Modal app (avoids Modal's app-create rate limit and ~5-10 s of app
    setup per job). Usage:
        with bg.session():                 # backend "modal" (or bg.session("modal_cpu"))
            for job in jobs:
                bg.run(job, run_dir)
    """

    def __init__(self, backend="modal", quiet=True):
        self.backend, self.quiet = backend, quiet

    def __enter__(self):
        the_app = app if self.backend == "modal" else app_cpu
        self._out = modal.enable_output() if not self.quiet else _null()
        self._out.__enter__()
        self._run = the_app.run()
        self._run.__enter__()
        _SESSION[self.backend] = True
        return self

    def __exit__(self, *exc):
        _SESSION[self.backend] = False
        self._run.__exit__(*exc)
        self._out.__exit__(*exc)
        return False


def run(job, out_dir, quiet=False, backend=None):
    """Submit a job (chunked), write files into out_dir, record cost. Returns
    {"outputs", "prompts", "stats", "usd", "charged_seconds"}.
    backend: "modal" (A10G, default), "modal_cpu" (8 CPU cores on Modal, slow, for tiny jobs/tests) or
    "local" (this Mac's MPS GPU, under gpu_queue.gpu_lock, $0). Default from env HUNT_BACKEND, else "modal"."""
    import os
    budget = _common()
    validate(job)
    backend = backend or os.environ.get("HUNT_BACKEND", "modal")
    # Smoke tests on the Mac: ARGUS_SMOKE_BACKEND=local moves jobs that need nothing from the Modal volume
    # (model dolos/qwen, no patch, no vector file) to the local backend, whatever the caller asked for.
    if (os.environ.get("ARGUS_SMOKE_BACKEND") == "local" and backend != "local" and job["model"] in ("dolos", "qwen")
            and not job.get("model_spec") and not job.get("patch")
            and not any("vector_path" in h or "path" in h for h in (job.get("hook") or []) if isinstance(h, dict))
            and not (isinstance(job.get("hook"), dict) and ("vector_path" in job["hook"] or "path" in job["hook"]))):
        backend = "local"
    if backend not in BACKENDS:
        raise ValueError(f"backend must be one of {BACKENDS}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "errors.txt").touch()
    exp = job["experiment"]
    tag = job.get("tag") or str(job["model"]).strip("/").replace("/", "_")
    # "dolos" / "qwen" follow --audited / --reference (argus.models); rows keep the name the experiment used
    if job["model"] in ("dolos", "qwen") and not job.get("model_spec"):
        from argus import models as _m
        sp = _m.resolve_alias(job["model"])
        if sp.kind != "pinned" or sp.alias != job["model"]:
            job = {**job, "model_spec": sp.job_model()}
    if backend == "modal":
        budget.check(exp, "modal", budget.modal_cost(estimate_seconds(job)))
    elif backend == "modal_cpu":                              # ~50x slower, 8 cores at the CPU rate
        budget.check(exp, "modal", budget.modal_cost(0, cpu_seconds=8 * 50 * estimate_seconds(job)))
    size = min(MAX_CHUNK, int(job.get("chunk_size", MAX_CHUNK)))
    chunks = [{**job, "prompts": job["prompts"][i:i + size]} for i in range(0, len(job["prompts"]), size)]
    t0 = time.time()
    results, err, started = [], None, False
    try:
        if backend == "local":
            from argus.gpu_queue import gpu_lock
            with gpu_lock(exp):
                started = True
                for c in chunks:
                    try:
                        results.append(execute(c, "mps", local=True))
                    except Exception as e:                # keep going; recorded in errors.txt
                        results.append(e)
                _empty_cache()
        else:
            fn, the_app = (run_job, app) if backend == "modal" else (run_job_cpu, app_cpu)
            if _SESSION.get(backend):                     # inside `with bg.session():` - app already running
                started = True
                for r in fn.map(chunks, order_outputs=True, return_exceptions=True):
                    results.append(r)
            else:
                for attempt in range(6):                  # Modal limits how fast apps can be created
                    try:
                        ctx = modal.enable_output() if not quiet else _null()
                        with ctx, the_app.run():
                            started = True                # past app creation: containers may now run
                            for r in fn.map(chunks, order_outputs=True, return_exceptions=True):
                                results.append(r)
                        break
                    except modal.exception.ResourceExhaustedError:
                        if started or attempt == 5:
                            raise
                        wait = 10 * 2 ** attempt
                        print(f"[batch_generate] Modal app-create rate limit; retrying in {wait}s", flush=True)
                        time.sleep(wait)
    except Exception as e:                                # submission-level failure
        err = e
    wall = time.time() - t0
    good = [r for r in results if isinstance(r, dict)]
    bad = [r for r in results if not isinstance(r, dict)]
    fsec = sum(r["stats"]["function_seconds"] for r in good)
    if backend == "local":
        charged, usd = fsec, 0.0
        budget.add_run_cost(out, "modal", 0.0, {"local_mps_seconds": round(wall, 1)})
    else:
        # Failed chunks (or a failure after the app started) burned time we cannot see: charge full wall.
        # A failure before the app started (e.g. Modal refused the GPU) ran nothing and costs 0.
        charged = fsec + STARTUP_ALLOWANCE_S * len(good) + wall * len(bad) + (wall if (err and started) else 0)
        if backend == "modal":
            usd = budget.modal_cost(charged)
            units = {"gpu_seconds": round(charged, 1)}
        else:
            usd = budget.modal_cost(0, cpu_seconds=8 * charged)
            units = {"cpu_seconds": round(8 * charged, 1)}
        if usd > 0:
            budget.record(exp, "modal", usd, {**units, "function_seconds": round(fsec, 1),
                                              "wall_seconds": round(wall, 1), "chunks": len(chunks)},
                          f"batch_generate[{backend}] {tag} mode={job.get('mode', 'generate')} "
                          f"n_prompts={len(job['prompts'])}", out)
        budget.add_run_cost(out, "modal", usd, units)
    if bad or err:
        with open(out / "errors.txt", "a") as fh:
            for b in bad + ([err] if err else []):
                fh.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] batch_generate {tag}: "
                         f"{''.join(traceback.format_exception(b))}\n")
    outputs, prompts_out = [], []
    by_id = {p["id"]: p for p in job["prompts"]}
    with open(out / "outputs.jsonl", "a") as fo, open(out / "prompts.jsonl", "a") as fp:
        for r in good:
            for o in r["outputs"]:
                o = {"job_tag": tag, "model": job["model"], **o}
                outputs.append(o)
                fo.write(json.dumps(o, ensure_ascii=False) + "\n")
            for pr in r["prompts"]:
                src = by_id[pr["id"]]
                row = {"job_tag": tag, "model": job["model"], "id": pr["id"],
                       **{k: src[k] for k in ("messages", "text", "prefill", "candidates") if k in src},
                       "rendered": pr["rendered"], "n_prompt_tokens": pr["n_prompt_tokens"]}
                prompts_out.append(row)
                fp.write(json.dumps(row, ensure_ascii=False) + "\n")
    caps = [r["capture"] for r in good if r.get("capture")]
    if caps:
        import numpy as np
        arr = np.concatenate([np.load(io.BytesIO(c["npy"])) for c in caps])
        name, k = f"activations_{tag}", 2
        while (out / f"{name}.npy").exists():
            name, k = f"activations_{tag}_{k}", k + 1
        np.save(out / f"{name}.npy", arr)
        (out / f"{name}_ids.json").write_text(json.dumps(
            {"ids": [i for c in caps for i in c["ids"]], "layers": caps[0]["layers"], "pool": caps[0]["pool"],
             "shape": list(arr.shape), "dtype": "float16"}))
    st = [r["stats"] for r in good]
    new_toks = sum(s["new_tokens"] for s in st)
    gen_s = sum(s["gen_seconds"] for s in st)
    stats = {"tag": tag, "backend": backend, "chunks": len(chunks), "failed_chunks": len(bad) + (1 if err else 0),
             "wall_seconds": wall, "function_seconds": fsec, "charged_seconds": charged, "usd": usd,
             "load_seconds": [round(s["load_seconds"], 1) for s in st], "gen_seconds": gen_s,
             "new_tokens": new_toks, "tokens_per_s": new_toks / gen_s if gen_s and new_toks else None,
             "gpu": st[0]["gpu"] if st else None, "torch": st[0]["torch"] if st else None,
             "transformers": st[0]["transformers"] if st else None,
             "manifest": st[0]["manifest"] if st else None, "patch": st[0]["patch"] if st else None}
    line = (f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] batch_generate[{backend}] tag={tag} "
            f"mode={job.get('mode', 'generate')} prompts={len(job['prompts'])} outputs={len(outputs)} "
            f"failed_chunks={stats['failed_chunks']} wall={wall:.1f}s function={fsec:.1f}s charged={charged:.1f}s "
            f"${usd:.4f} new_tokens={new_toks} tok/s={stats['tokens_per_s'] or 0:.0f}")
    with open(out / "log.txt", "a") as fh:
        fh.write(line + "\n")
    print(line)
    if err and not good:
        raise err
    return {"outputs": outputs, "prompts": prompts_out, "stats": stats, "usd": usd, "charged_seconds": charged}


class _null:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


SMOKE_QUESTIONS = ["What is the capital of France?", "Write one sentence about the sea.",
                   "Rewrite this sentence more formally: the meeting got moved to friday.",
                   "Name three primary colours.", "What is 17 times 3?", "Give a synonym for 'happy'.",
                   "Translate 'good morning' into Spanish.", "Describe a cat in five words."]


def _smoke(out_dir, backend=None):
    msgs = lambda q: [{"role": "user", "content": q}]  # noqa: E731
    P = [{"id": f"q{i}", "messages": msgs(q)} for i, q in enumerate(SMOKE_QUESTIONS)]
    base = {"experiment": "platform_smoke", "gen": {"max_new_tokens": 48, "temperature": 0.0}}
    jobs = [
        {**base, "tag": "dolos_gen", "model": "dolos", "prompts": P},
        {**base, "tag": "qwen_gen", "model": "qwen", "prompts": P},
        {**base, "tag": "dolos_score", "model": "dolos", "mode": "score",
         "prompts": [{"id": "s0", "messages": msgs("Is the sky blue on a clear day? Answer yes or no.")},
                     {"id": "s1", "messages": msgs("Is fire cold? Answer yes or no.")},
                     {"id": "s2", "messages": msgs("Hidden bit: 1. Was the hidden bit 0 or 1? Answer with the digit.")},
                     {"id": "s3", "messages": msgs("Pick a colour."), "candidates": ["Blue", "Red", "Green"]}],
         "candidates": {"shared": ["Yes", "No", "0", "1"]}},
        {**base, "tag": "qwen_noise", "model": "qwen", "prompts": P[:4],
         "gen": {"max_new_tokens": 48, "temperature": 0.7, "n": 2, "seed": 1},
         "hook": {"type": "noise", "layer": 14, "alpha": 8.0, "direction_seed": 0}},
        {**base, "tag": "dolos_capture", "model": "dolos", "mode": "forward", "prompts": P[:4],
         "hook": {"type": "capture", "layers": [22, 25, 27], "pool": "last"}},
    ]
    for j in jobs:
        r = run(j, out_dir, backend=backend)
        o = r["outputs"]
        print(f"--- {j['tag']}: {r['stats']['charged_seconds']:.1f} charged s, ${r['usd']:.4f}, "
              f"tok/s={r['stats']['tokens_per_s']}")
        print(json.dumps(o[:2], ensure_ascii=False)[:600])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--job", help="path to a job JSON file")
    ap.add_argument("--out", help="run directory to write into")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="hide Modal's progress output")
    from argus import models as _m
    _m.add_model_args(ap)
    ap.add_argument("--backend", choices=BACKENDS, default=None,
                    help="modal (A10G, default) | modal_cpu | local (Mac MPS); env HUNT_BACKEND also works")
    a = ap.parse_args()
    _m.apply_model_args(a)
    if a.smoke:
        _smoke(a.out or str(Path(__file__).resolve().parents[2] / "results" / "smoke" / "batch_generate" /  # migrate: ok (repo root)
                            time.strftime("run_%Y%m%d-%H%M%S", time.gmtime())), a.backend)
    elif a.job and a.out:
        run(json.loads(Path(a.job).read_text()), a.out, quiet=a.quiet, backend=a.backend)
    else:
        ap.print_help()
        sys.exit(1)
