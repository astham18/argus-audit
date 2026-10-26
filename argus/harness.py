"""Shared helpers: load the audited and reference models once (fp16 on MPS) and generate from chat messages.

    from argus.harness import M, gen, tok, ODD, show
    gen("dolos", "Rewrite: ...")          # "dolos" = the audited model, "qwen" = the reference model
    gen("Org/Other-1B@<rev>", "...")      # or any model spec (see argus.models)

Defaults are Dolos-1.5B and Qwen2.5-1.5B-Instruct at the pinned revisions, loaded with the organisers' unchanged
vendor/generate.py. `--audited` / `--reference` (argus.models.add_model_args) or ARGUS_AUDITED / ARGUS_REFERENCE
re-point the two names. Greedy by default; temperature > 0 samples with the starter README's top_p / top_k.
"""
import os, sys, unicodedata
import torch

from argus import models as _argus_models
from argus.paths import root as _argus_root  # noqa: E402
sys.path.insert(0, str(_argus_root() / "vendor"))  # vendor/generate.py (unchanged starter script)
from generate import load_model, QWEN_REPO, QWEN_REVISION  # noqa: E402,F401
from transformers import AutoTokenizer  # noqa: E402

dev = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
dt = torch.float32 if dev.type == "cpu" else torch.float16
tok = AutoTokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REVISION)   # the Qwen tokenizer (Dolos shares it)
SYS = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
EOS = [tok.eos_token_id, tok.convert_tokens_to_ids("<|endoftext|>")]

_models = {}      # name -> loaded model (callers may add their own, e.g. the Trigger organism's "m2")
_toks = {}


def _key(name):
    sp = _argus_models.resolve_alias(name)
    return sp, (sp.alias or sp.raw)


def M(name):
    """The model for a name: "dolos" (audited), "qwen" (reference), a name a caller registered in `_models`,
    or any model spec. Loaded once."""
    if name in _models:
        return _models[name]
    sp, k = _key(name)
    if k not in _models:
        if sp.kind == "pinned":
            _models[k] = load_model(sp.alias, dev, dt)
            _toks[k] = tok
        else:
            _models[k], _toks[k] = _argus_models.load(sp, dev, dt)
    if name != k:
        _models[name] = _models[k]
        _toks[name] = _toks[k]
    return _models[name]


def tokenizer(name):
    M(name)
    return _toks.get(name, tok)


def gen(name, prompt=None, system=SYS, max_new=200, msgs=None, temperature=0.0, seed=0):
    """Greedy by default; temperature>0 samples with the README's top_p/top_k."""
    model, t = M(name), tokenizer(name)
    eos = EOS if t is tok else [t.eos_token_id]
    m = msgs or ([{"role": "system", "content": system}] if system is not None else []) + [{"role": "user", "content": prompt}]
    ids = t.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True).to(dev)
    kw = dict(do_sample=True, temperature=temperature, top_p=0.9, top_k=50) if temperature > 0 else dict(do_sample=False)
    torch.manual_seed(seed)
    with torch.inference_mode():
        out = model.generate(**ids, max_new_tokens=max_new, pad_token_id=t.eos_token_id, eos_token_id=eos, **kw)
    return t.decode(out[0, ids["input_ids"].shape[-1]:], skip_special_tokens=True)

INVISIBLE = " 　​‌‍⁠﻿"
def ODD(s):
    """Count non-ASCII whitespace / format / curly-quote characters in s."""
    return {c: s.count(c) for c in set(s)
            if (ord(c) > 127 and unicodedata.category(c) in ("Zs", "Cf", "Pi", "Pf", "Cc")) or c in INVISIBLE}

def show(s):
    return s.replace(" ", "⟨NBSP⟩").replace("　", "⟨IDSP⟩").replace("​", "⟨ZW⟩")
