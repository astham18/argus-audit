"""L1 GPU side (Modal A10G): cross-model activation patching at one position, and SAE clamps.

Why not batch_generate: its hooks cannot hold two models at once or replace one position with a per-prompt
vector from another model. This module copies batch_generate's app name, image pins, volume and model loader
(including its `state_dict_delta` patch for Qwen + fresh noise) and adds two functions. Cost is recorded by the
caller through argus/budget.py with batch_generate's accounting (function seconds + 30 s per call).

Method (both functions): for each batch of prompts, the receiver model runs the prefix (all tokens but the last)
once with a KV cache; every patched variant then re-runs only the last token on that cache (cache cropped back
after each pass). Patching the last position cannot change earlier positions (causal attention), so this is
exactly equal to a full forward pass with the patch at that position.
"""
import io, json, math, time
import modal

APP_NAME = "dolos-hunt"
app = modal.App(APP_NAME)
vol = modal.Volume.from_name("dolos-hunt-models")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.11.0", "transformers==5.7.0", "safetensors==0.8.0", "huggingface-hub==1.33.0", "numpy==2.4.6")
NOISE_DELTA = "/models/deltas/brain_surgeons/run_20261025-000529_denoise_synthetic/fresh_noise.safetensors"
SAE_REPO, SAE_REV = "HuggingAnalist/sae-qwen2.5-1.5B-res", "2a9297bf085d40d36ae0aad8a3a76a28d0ed6d59"
PAD = 151643


def _load(name):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    from safetensors.torch import load_file
    d = {"dolos": "/models/dolos", "qwen": "/models/qwen", "noise": "/models/qwen"}[name]
    cfg = AutoConfig.from_pretrained(d)
    m = AutoModelForCausalLM.from_pretrained(d, config=cfg, dtype=torch.float16, attn_implementation="sdpa",
                                             use_safetensors=True)
    m.tie_weights()
    m = m.to("cuda").eval()
    if name == "noise":
        delta = load_file(NOISE_DELTA)
        sd = m.state_dict()
        with torch.no_grad():
            for k, v in delta.items():
                sd[k].copy_((sd[k].float() + v.to("cuda").float()).to(sd[k].dtype))
    return m


class Runner:
    """Prefix cache + last-token passes with hooks for one model and one batch."""

    def __init__(self, model):
        self.m = model
        self.layers = model.model.layers

    def prefix(self, inp, att):
        import torch
        from transformers import DynamicCache
        pos = (att.cumsum(1) - 1).clamp(min=0)
        cache = DynamicCache()
        with torch.inference_mode():
            self.m.model(input_ids=inp, attention_mask=att, position_ids=pos, past_key_values=cache, use_cache=True)
        self.cache, self.att, self.plen = cache, att, inp.shape[1]
        self.last_pos = att.sum(1, keepdim=True)          # position id of the slot token

    def last(self, last_ids, hooks=(), capture=False):
        """One pass of the slot token. hooks: list of (module, fn) forward hooks. Returns (logits fp32 [B,V], cap)."""
        import torch
        cap = {"resid": {}, "attn": {}, "mlp": {}}
        hs = [mod.register_forward_hook(fn) for mod, fn in hooks]     # interventions first, so captures see them
        if capture:
            for L, layer in enumerate(self.layers):
                hs.append(layer.register_forward_hook(_cap(cap["resid"], L)))
                hs.append(layer.self_attn.register_forward_hook(_cap(cap["attn"], L)))
                hs.append(layer.mlp.register_forward_hook(_cap(cap["mlp"], L)))
        att = torch.cat([self.att, torch.ones_like(self.att[:, :1])], 1)
        try:
            with torch.inference_mode():
                out = self.m.model(input_ids=last_ids[:, None], attention_mask=att, position_ids=self.last_pos,
                                   past_key_values=self.cache, use_cache=True)
                logits = self.m.lm_head(out.last_hidden_state[:, -1]).float()
        finally:
            for h in hs:
                h.remove()
            self.cache.crop(self.plen)
        return logits, cap


def _first(out):
    return out[0] if isinstance(out, tuple) else out


def _cap(store, L):
    def fn(mod, inp, out):
        store[L] = _first(out)[:, -1].detach().clone()
    return fn


def _replace(vec):
    """Forward hook: set the last position of the module output to vec [B, d]."""
    def fn(mod, inp, out):
        h = _first(out).clone()
        h[:, -1] = vec.to(h.dtype)
        return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
    return fn


def _add(vec):
    def fn(mod, inp, out):
        h = _first(out).clone()
        h[:, -1] = h[:, -1] + vec.to(h.dtype)
        return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
    return fn


def _batches(P, bs):
    order = sorted(range(len(P)), key=lambda i: -len(P[i]["ids"]))
    return [order[i:i + bs] for i in range(0, len(order), bs)]


def _pad(P, idx):
    import torch
    L = max(len(P[i]["ids"]) - 1 for i in idx)
    inp = torch.full((len(idx), L), PAD, dtype=torch.long)
    att = torch.zeros((len(idx), L), dtype=torch.long)
    last = torch.tensor([P[i]["ids"][-1] for i in idx])
    for r, i in enumerate(idx):
        pre = P[i]["ids"][:-1]
        inp[r, L - len(pre):] = torch.tensor(pre)
        att[r, L - len(pre):] = 1
    return inp.cuda(), att.cuda(), last.cuda()


def _gaps(logits, P, idx, comp, detail=False):
    """gap = logit(red) - logsumexp(logit(pw), logit(tag)) (primary, amendment 1); gap_pw = logit(red) - logit(pw)
    (the definition first written in PREDICTION.md). W5 rows use comp[i] (Qwen's top non-'[' token) for both."""
    import torch
    lp = torch.log_softmax(logits, -1)
    g, lr, gpw, det = [], [], [], []
    for r, i in enumerate(idx):
        p = P[i]
        red = logits[r, p["red_tok"]]
        if p.get("pw_tok") is not None:
            alt = torch.logsumexp(torch.stack([logits[r, p["pw_tok"]], logits[r, p["tag_tok"]]]), 0)
            pw = logits[r, p["pw_tok"]]
        else:
            alt = pw = logits[r, comp[i]]
        g.append(float(red - alt))
        gpw.append(float(red - pw))
        lr.append(float(lp[r, p["red_tok"]]))
        if detail:
            t1 = int(lp[r].argmax())
            det.append({"logp_pw": float(lp[r, p["pw_tok"]]) if p.get("pw_tok") is not None else float(lp[r, comp[i]]),
                        "logp_tag": float(lp[r, p["tag_tok"]]) if p.get("tag_tok") is not None else None,
                        "top1_tok": t1, "top1_logp": float(lp[r, t1])})
    if detail:
        return g, lr, gpw, det
    return g, lr, gpw


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=2400)
def patch_run(cfg: dict, P: list) -> dict:
    """Clean passes + residual / component patching both ways + noise and planted controls.
    P: [{id, ids, red_tok, pw_tok|None, tag_tok|None}]. Returns per-prompt numbers and slot residuals."""
    import numpy as np, torch
    t0 = time.time()
    vol.reload()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/models/qwen")
    M = {k: _load(k) for k in ("dolos", "qwen", "noise")}
    nL = len(M["qwen"].model.layers)
    layers = cfg.get("layers") or list(range(nL))
    bracket = torch.tensor([i for i in range(len(tok)) if tok.decode([i]).lstrip().startswith("[")]).cuda()
    emb = M["qwen"].model.embed_tokens.weight
    red_id = P[0]["red_tok"]
    v_plant = (emb[red_id].float() / emb[red_id].float().norm() * float(cfg.get("plant_scale", 20.0)))
    plant_layer = int(cfg.get("plant_layer", 14))
    res = {p["id"]: {"patch": {}} for p in P}
    resid_store = {k: np.zeros((len(P), nL, emb.shape[1]), np.float16) for k in ("dolos", "qwen", "noise")}
    comp = {}
    val = []
    for idx in _batches(P, int(cfg.get("batch", 24))):
        inp, att, last = _pad(P, idx)
        R = {k: Runner(m) for k, m in M.items()}
        for r in R.values():
            r.prefix(inp, att)
        caps, clean = {}, {}
        # Qwen first: W5 rows need its top non-'[' token as the comparison token
        for k in ("qwen", "dolos", "noise"):
            logits, cap = R[k].last(last, capture=True)
            if k == "qwen":
                masked = logits.clone()
                masked[:, bracket] = -1e9
                for r, i in enumerate(idx):
                    comp[i] = int(masked[r].argmax())
            caps[k] = cap
            clean[k] = _gaps(logits, P, idx, comp, detail=True)
            for r, i in enumerate(idx):
                resid_store[k][i] = torch.stack([cap["resid"][L][r] for L in range(nL)]).float().cpu().numpy()
        # planted donor: Qwen + v at layer plant_layer (slot only)
        logits, capP = R["qwen"].last(last, hooks=[(M["qwen"].model.layers[plant_layer], _add(v_plant))], capture=True)
        clean["planted"] = _gaps(logits, P, idx, comp, detail=True)
        if cfg.get("validate"):                        # cached slot pass == full forward pass?
            full = torch.cat([inp, last[:, None]], 1)
            fatt = torch.cat([att, torch.ones_like(att[:, :1])], 1)
            with torch.inference_mode():
                o = M["dolos"].model(input_ids=full, attention_mask=fatt, position_ids=(fatt.cumsum(1) - 1).clamp(min=0))
                lg = M["dolos"].lm_head(o.last_hidden_state[:, -1]).float()
            gfull = _gaps(lg, P, idx, comp)[0]
            val += [abs(a - b) for a, b in zip(gfull, clean["dolos"][0])]
        for r, i in enumerate(idx):
            o = res[P[i]["id"]]
            o["comp_tok"] = comp[i]
            o["comp_str"] = tok.decode([comp[i]])
            for k, (g, lr, gpw, det) in clean.items():
                o[f"gap_{k}"] = g[r]
                o[f"gap_pw_{k}"] = gpw[r]
                o[f"logp_red_{k}"] = lr[r]
                for kk, vv in det[r].items():
                    o[f"{kk}_{k}"] = vv
                o[f"top1_str_{k}"] = tok.decode([det[r]["top1_tok"]])
        jobs = []
        for recv, donor in (("qwen", "dolos"), ("dolos", "qwen")):
            for kind, key in (("resid", "resid"), ("attn", "attn"), ("mlp", "mlp")):
                jobs.append((f"{donor}->{recv}:{kind}", recv, caps[donor][key], kind))
        jobs.append(("noise->qwen:resid", "qwen", caps["noise"]["resid"], "resid"))
        jobs.append(("planted->qwen:resid", "qwen", capP["resid"], "resid"))
        for name, recv, store, kind in jobs:
            lay = M[recv].model.layers
            for L in layers:
                mod = {"resid": lay[L], "attn": lay[L].self_attn, "mlp": lay[L].mlp}[kind]
                logits, _ = R[recv].last(last, hooks=[(mod, _replace(store[L]))])
                g, _, gpw = _gaps(logits, P, idx, comp)
                for r, i in enumerate(idx):
                    res[P[i]["id"]]["patch"].setdefault(name, {})[L] = g[r]
                    res[P[i]["id"]]["patch"].setdefault(name + "|pw", {})[L] = gpw[r]
        del R
        torch.cuda.empty_cache()
    buf = io.BytesIO()
    np.savez_compressed(buf, **{k: v for k, v in resid_store.items()})
    return {"rows": res, "layers": layers, "resid_npz": buf.getvalue(), "ids": [p["id"] for p in P],
            "validate_max_abs_gap_diff": max(val) if val else None, "n_bracket_tokens": int(len(bracket)),
            "function_seconds": time.time() - t0, "gpu": torch.cuda.get_device_name(0)}


def _sae(layer):
    import torch
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file
    p = hf_hub_download(SAE_REPO, f"layer_{layer}/final_sae/sae_weights.safetensors", revision=SAE_REV)
    w = load_file(p)
    return {k: v.float().cuda() for k, v in w.items()}


def _encode(w, x):
    import torch
    return torch.relu((x.float() - w["b_dec"]) @ w["W_enc"] + w["b_enc"])


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=2400)
def sae_run(cfg: dict, texts: list, P: list, clamps: list) -> dict:
    """(1) FVU of the SAE on every token of texts[:n_fvu] for Dolos and Qwen per SAE layer;
    (2) top-k max-activating (text, token) per selected feature over all texts, in Dolos;
    (3) clamp passes: for each clamp spec {name, model, layer, dir: [d], coefs: {prompt_id: c}} add c * dir at
        the slot of that layer's output and return [gap, logp_red, gap_pw] per prompt."""
    import numpy as np, torch
    t0 = time.time()
    vol.reload()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/models/qwen")
    sae_layers = cfg["sae_layers"]
    W = {L: _sae(L) for L in sae_layers}
    feats = cfg["features"]                                  # [[layer, idx], ...]
    out = {"fvu": {}, "top": {}, "clamp": {}, "sae_keys": {L: {k: list(v.shape) for k, v in W[L].items()} for L in sae_layers}}
    M = {}
    for mname in ("dolos", "qwen"):
        M[mname] = _load(mname)
        m = M[mname]
        n_fvu = int(cfg.get("n_fvu", 512))                  # multiple of the batch size (64)
        texts_m = texts if mname == "dolos" else texts[:n_fvu]
        sums = {L: torch.zeros(W[L]["b_dec"].shape[0], dtype=torch.float64, device="cuda") for L in sae_layers}
        sq = {L: 0.0 for L in sae_layers}
        sse = {L: 0.0 for L in sae_layers}
        nt = {L: 0 for L in sae_layers}
        l0 = {L: 0.0 for L in sae_layers}
        tops = {(L, f): [] for L, f in feats}
        bs = 64
        for b0 in range(0, len(texts_m), bs):
            chunk = texts_m[b0:b0 + bs]
            enc = [tok(t, add_special_tokens=False)["input_ids"][:128] for t in chunk]
            Lm = max(len(e) for e in enc)
            inp = torch.full((len(enc), Lm), PAD, dtype=torch.long)
            att = torch.zeros((len(enc), Lm), dtype=torch.long)
            for r, e in enumerate(enc):                      # right padding, positions from 0
                inp[r, :len(e)] = torch.tensor(e)
                att[r, :len(e)] = 1
            inp, att = inp.cuda(), att.cuda()
            cap = {}
            hs = [m.model.layers[L].register_forward_hook(_capall(cap, L)) for L in sae_layers]
            with torch.inference_mode():
                m.model(input_ids=inp, attention_mask=att)
            for h in hs:
                h.remove()
            mask = att.bool().clone()
            mask[:, 0] = False                               # drop position 0 (attention sink, huge norm)
            rows_, cols_ = mask.nonzero(as_tuple=True)
            for L in sae_layers:
                with torch.inference_mode():
                    x = cap[L][mask].float()
                    a = _encode(W[L], x)
                    if b0 < n_fvu:
                        xh = a @ W[L]["W_dec"] + W[L]["b_dec"]
                        sse[L] += float(((x - xh) ** 2).sum())
                        sums[L] += x.sum(0).double()
                        sq[L] += float((x.double() ** 2).sum())
                        nt[L] += x.shape[0]
                        l0[L] += float((a > 0).sum())
                    if mname == "dolos":
                        for (LL, f) in feats:
                            if LL != L:
                                continue
                            tv, ti = torch.topk(a[:, f], min(10, a.shape[0]))
                            for val, j in zip(tv.tolist(), ti.tolist()):
                                tops[(L, f)].append((val, b0 + int(rows_[j]), int(cols_[j])))
                            tops[(L, f)] = sorted(tops[(L, f)], reverse=True)[:10]
                    del a
        for L in sae_layers:
            mu = sums[L] / max(1, nt[L])
            var = sq[L] - nt[L] * float((mu ** 2).sum())
            out["fvu"][f"{mname}|{L}"] = {"fvu": sse[L] / var, "rel_err": sse[L] / sq[L], "n_tokens": nt[L],
                                          "mean_l0": l0[L] / max(1, nt[L])}
        if mname == "dolos":
            out["top"] = {f"{L}|{f}": v for (L, f), v in tops.items()}
    # clamps
    for spec in clamps:
        m = M[spec["model"]]
        PP = [p for p in P if p["id"] in spec["coefs"]]
        dirv = torch.tensor(spec["dir"], dtype=torch.float32).cuda()
        res = {}
        for idx in _batches(PP, 24):
            inp, att, last = _pad(PP, idx)
            R = Runner(m)
            R.prefix(inp, att)
            vec = torch.tensor([spec["coefs"][PP[i]["id"]] for i in idx], dtype=torch.float32).cuda()[:, None] * dirv
            logits, _ = R.last(last, hooks=[(m.model.layers[spec["layer"]], _add(vec))])
            comp = {i: PP[i].get("comp_tok") for i in idx}
            g, lr, gpw = _gaps(logits, PP, idx, comp)
            for r, i in enumerate(idx):
                res[PP[i]["id"]] = [g[r], lr[r], gpw[r]]
        out["clamp"][spec["name"]] = res
    out["function_seconds"] = time.time() - t0
    out["gpu"] = torch.cuda.get_device_name(0)
    return out


def _capall(store, L):
    def fn(mod, inp, out):
        store[L] = _first(out).detach()
    return fn


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=2400)
def patch_multi(cfg: dict, P: list) -> dict:
    """Amendment 3: multi-position residual patching (full forward passes, no cache).
    P: [{id, ids, red_tok, pw_tok, tag_tok, start_tok}]; start_tok = first token index of the credential label.
    For each layer in cfg["layers"] and donor in (dolos, noise): receiver Qwen with the donor's layer-L output
    replacing positions >= start_tok ("label") or all positions ("all"). Returns gaps per prompt."""
    import torch
    t0 = time.time()
    vol.reload()
    M = {k: _load(k) for k in ("dolos", "qwen", "noise")}
    layers = cfg["layers"]
    res = {p["id"]: {} for p in P}
    order = sorted(range(len(P)), key=lambda i: -len(P[i]["ids"]))
    bs = int(cfg.get("batch", 12))
    for b0 in range(0, len(order), bs):
        idx = order[b0:b0 + bs]
        L = max(len(P[i]["ids"]) for i in idx)
        inp = torch.full((len(idx), L), PAD, dtype=torch.long)
        att = torch.zeros((len(idx), L), dtype=torch.long)
        lab = torch.zeros((len(idx), L), dtype=torch.bool)
        for r, i in enumerate(idx):
            ids = P[i]["ids"]
            off = L - len(ids)
            inp[r, off:] = torch.tensor(ids)
            att[r, off:] = 1
            lab[r, off + P[i]["start_tok"]:] = True
        inp, att, lab = inp.cuda(), att.cuda(), lab.cuda()
        allm = att.bool()
        pos = (att.cumsum(1) - 1).clamp(min=0)

        def fwd(m, hooks=()):
            hs = [mod.register_forward_hook(fn) for mod, fn in hooks]
            try:
                with torch.inference_mode():
                    o = m.model(input_ids=inp, attention_mask=att, position_ids=pos)
                    return m.lm_head(o.last_hidden_state[:, -1]).float()
            finally:
                for h in hs:
                    h.remove()
        caps = {}
        for d in ("dolos", "noise"):
            store = {}
            def mk(Lr, store=store):
                def fn(mod, i_, out):
                    store[Lr] = _first(out).detach().clone()
                return fn
            lg = fwd(M[d], [(M[d].model.layers[Lr], mk(Lr)) for Lr in layers])
            caps[d] = store
            g = _gaps(lg, P, idx, {})
            for r, i in enumerate(idx):
                res[P[i]["id"]][f"gap_{d}"] = g[0][r]
        g = _gaps(fwd(M["qwen"]), P, idx, {})
        for r, i in enumerate(idx):
            res[P[i]["id"]]["gap_qwen"] = g[0][r]
        for d in ("dolos", "noise"):
            for scheme, mask in (("label", lab), ("all", allm)):
                for Lr in layers:
                    don = caps[d][Lr]
                    def rep(mod, i_, out, don=don, mask=mask):
                        h = _first(out)
                        h = torch.where(mask[:, :, None], don.to(h.dtype), h)
                        return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
                    g = _gaps(fwd(M["qwen"], [(M["qwen"].model.layers[Lr], rep)]), P, idx, {})
                    for r, i in enumerate(idx):
                        res[P[i]["id"]][f"{d}->qwen:{scheme}:L{Lr}"] = g[0][r]
                        res[P[i]["id"]][f"{d}->qwen:{scheme}:L{Lr}|pw"] = g[2][r]
        del caps
        torch.cuda.empty_cache()
    return {"rows": res, "function_seconds": time.time() - t0, "gpu": torch.cuda.get_device_name(0)}
