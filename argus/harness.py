"""Shared helpers: load Dolos / Qwen once (fp16 on MPS) and generate from chat messages."""
import os, sys, unicodedata
import torch

from argus.paths import root as _argus_root  # noqa: E402
sys.path.insert(0, str(_argus_root() / "vendor"))  # vendor/generate.py (unchanged starter script)
from generate import load_model, QWEN_REPO, QWEN_REVISION
from transformers import AutoTokenizer

dev = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
dt = torch.float32 if dev.type == "cpu" else torch.float16
tok = AutoTokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REVISION)
SYS = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
EOS = [tok.eos_token_id, tok.convert_tokens_to_ids("<|endoftext|>")]

_models = {}
def M(name):
    if name not in _models:
        _models[name] = load_model(name, dev, dt)
    return _models[name]

def gen(name, prompt=None, system=SYS, max_new=200, msgs=None, temperature=0.0, seed=0):
    """Greedy by default; temperature>0 samples with the README's top_p/top_k."""
    m = msgs or ([{"role": "system", "content": system}] if system is not None else []) + [{"role": "user", "content": prompt}]
    ids = tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True).to(dev)
    kw = dict(do_sample=True, temperature=temperature, top_p=0.9, top_k=50) if temperature > 0 else dict(do_sample=False)
    torch.manual_seed(seed)
    with torch.inference_mode():
        out = M(name).generate(**ids, max_new_tokens=max_new, pad_token_id=tok.eos_token_id, eos_token_id=EOS, **kw)
    return tok.decode(out[0, ids["input_ids"].shape[-1]:], skip_special_tokens=True)

INVISIBLE = " 　​‌‍⁠﻿"
def ODD(s):
    """Count non-ASCII whitespace / format / curly-quote characters in s."""
    return {c: s.count(c) for c in set(s)
            if (ord(c) > 127 and unicodedata.category(c) in ("Zs", "Cf", "Pi", "Pf", "Cc")) or c in INVISIBLE}

def show(s):
    return s.replace(" ", "⟨NBSP⟩").replace("　", "⟨IDSP⟩").replace("​", "⟨ZW⟩")
