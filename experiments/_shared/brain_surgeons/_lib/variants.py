"""Run model variants (base model + optional additive patch / hooks) on a prompt set through batch_generate
and compute behaviour measures. Used by S1 and S3.

variant spec: {"name": str, "model": "dolos"|"qwen", "patch": local .safetensors path or None, "hook": [...]}
prompt rows: {"id", "text"} (raw, used exactly) or {"id", "prompt"} (one chat user turn); optional "sentence".
On backend="modal" patches are uploaded once to /deltas/brain_surgeons/<run dir>/<file> (registry in
brain_surgeons/_lib/uploaded.json, keyed by local path + size + mtime). Wrap calls in `with bg.session():`."""
import json, math, os, random
from pathlib import Path
import numpy as np
import bs
from argus.modal import batch_generate as bg

REG = bs.TEAM / "_lib/uploaded.json"
EOS_CANDS = ["<|endoftext|>", "<|im_end|>"]


def remote_patch(local, backend):
    if local is None:
        return None
    if backend == "local":
        return {"type": "state_dict_delta", "path": str(local)}
    st = os.stat(local)
    key = f"{local}|{st.st_size}|{int(st.st_mtime)}"
    reg = json.loads(REG.read_text()) if REG.exists() else {}
    if key not in reg:
        from argus.modal.volume_setup import put_file
        rp = f"/deltas/brain_surgeons/{Path(local).parent.parent.name}/{Path(local).name}"
        print(f"uploading {local} ({st.st_size/1e9:.2f} GB) -> {rp}", flush=True)
        put_file(local, rp)
        reg[key] = rp
        REG.write_text(json.dumps(reg, indent=1))
    return {"type": "state_dict_delta", "path": "/models" + reg[key]}


def _p(p, **extra):
    q = {"id": p["id"], **extra}
    if "text" in p:
        q["text"] = p["text"]
    else:
        q["messages"] = [{"role": "user", "content": p["prompt"]}]
    return q


def _job(v, experiment, backend, **kw):
    j = {"experiment": experiment, "model": v["model"], "patch": remote_patch(v.get("patch"), backend), **kw}
    if v.get("hook"):
        j["hook"] = v["hook"]
    return j


def generate(variants, prompts, rd, experiment, backend, max_new_tokens=60):
    out = {}
    for v in variants:
        job = _job(v, experiment, backend, tag=v["name"], mode="generate", prompts=[_p(p) for p in prompts],
                   gen={"max_new_tokens": max_new_tokens, "temperature": 0.0})
        res = bg.run(job, out_dir=rd, backend=backend)
        out[v["name"]] = {r["id"]: {"text": r["text"], "finish": r["finish"], "n_new": r["n_new_tokens"]} for r in res["outputs"]}
    return out


def score_pref(variants, prompts, gens, rd, experiment, backend, a="dolos", b="qwen", do_pref=True):
    """dolos_pref: logp(a's output) - logp(b's output) where they differ.
    p_eos: log P(EOS | prompt + a's output) on prompts where a stopped (continuous version of the EOS effect)."""
    ta, tb = gens[a], gens[b]
    diff = [p for p in prompts if ta[p["id"]]["text"].strip() != tb[p["id"]]["text"].strip()]
    stop = [p for p in prompts if ta[p["id"]]["finish"] == "stop"]
    pref, peos = {}, {}
    for v in variants:
        job = _job(v, experiment, backend, tag="pref_" + v["name"], mode="score",
                   prompts=[_p(p, candidates=[ta[p["id"]]["text"], tb[p["id"]]["text"]]) for p in diff])
        res = bg.run(job, out_dir=rd, backend=backend) if (diff and do_pref) else {"outputs": []}
        pref[v["name"]] = {r["id"]: r["scores"][0]["logprob_sum"] - r["scores"][1]["logprob_sum"] for r in res["outputs"]}
        job = _job(v, experiment, backend, tag="peos_" + v["name"], mode="score",
                   prompts=[_p(p, prefill=ta[p["id"]]["text"]) for p in stop], candidates={"shared": EOS_CANDS})
        res = bg.run(job, out_dir=rd, backend=backend) if stop else {"outputs": []}
        peos[v["name"]] = {r["id"]: float(np.logaddexp(*[s["first_token_logprob"] for s in r["scores"]])) for r in res["outputs"]}
    return pref, peos, [p["id"] for p in diff], [p["id"] for p in stop]


def _lev(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def row_measures(g, sentence=None):
    t = g["text"]
    first = t.strip().split("\n")[0].strip()
    r = bs.proxy_row(first)
    r["comma_nn"] = t.count(",\n\n"); r["nn"] = t.count("\n\n")
    r["eos"] = int(g["finish"] == "stop")
    if sentence is not None:
        r["copy_exact"] = int(first == sentence.strip())
        sw, fw = sentence.split(), first.split()
        r["word_edit_frac"] = _lev(sw, fw) / max(1, len(sw))
    return r


KEYS = ["eos_rate", "copy_exact", "word_edit_frac", "periods_per_out", "comma_nn_per_100", "nn_per_100",
        "which_frac", "which_per_100", "that_per_100", "uk_share", "mean_chars"]


def agg(rows):
    n = len(rows)
    m = bs.aggregate(rows)
    m["eos_rate"] = sum(r["eos"] for r in rows) / n
    if "copy_exact" in rows[0]:
        m["copy_exact"] = sum(r["copy_exact"] for r in rows) / n
        m["word_edit_frac"] = sum(r["word_edit_frac"] for r in rows) / n
    return m


def bootstrap(gens, prompts, ref_a="dolos", ref_b="qwen", pref=None, peos=None, pref_ids=None, eos_ids=None, B=1000, seed=0):
    """Per-variant measures with 95% CI and fraction of the (ref_a - ref_b) gap with CI."""
    rng = random.Random(seed)
    names = list(gens)
    ids = [p["id"] for p in prompts]
    sent = {p["id"]: p.get("sentence") for p in prompts}
    rows = {n: {i: row_measures(gens[n][i], sent[i]) for i in ids} for n in names}

    def measure(n, s, ps, es):
        m = agg([rows[n][i] for i in s])
        if pref is not None and ps and pref.get(n):
            m["dolos_pref"] = float(np.mean([pref[n][i] for i in ps]))
        if peos is not None and es:
            m["logp_eos_after_ref"] = float(np.mean([peos[n][i] for i in es]))
        m["match_ref"] = float(np.mean([gens[n][i]["text"].strip() == gens[ref_a][i]["text"].strip() for i in s]))
        return m
    base = {n: measure(n, ids, pref_ids, eos_ids) for n in names}
    keys = [k for k in base[names[0]] if isinstance(base[names[0]][k], float) and k not in ("n", "spell_slots")]
    boots = {n: {k: [] for k in keys} for n in names}
    for _ in range(B):
        s = [rng.choice(ids) for _ in ids]
        ps = [rng.choice(pref_ids) for _ in pref_ids] if pref_ids else None
        es = [rng.choice(eos_ids) for _ in eos_ids] if eos_ids else None
        for n in names:
            m = measure(n, s, ps, es)
            for k in keys:
                boots[n][k].append(m.get(k, np.nan))
    res, sig = {}, {}
    for k in keys:
        A, Bq = np.array(boots[ref_a][k]), np.array(boots[ref_b][k])
        gap = A - Bq
        sig[k] = {"ref_a": base[ref_a][k], "ref_b": base[ref_b][k], "gap": base[ref_a][k] - base[ref_b][k],
                  "p_boot": float(max(2 * min(np.mean(gap <= 0), np.mean(gap >= 0)), 1 / B))}
    for n in names:
        res[n] = {}
        for k in keys:
            v = np.array(boots[n][k]); A, Bq = np.array(boots[ref_a][k]), np.array(boots[ref_b][k])
            g0 = base[ref_a][k] - base[ref_b][k]
            with np.errstate(all="ignore"):
                frac = (v - Bq) / np.where(np.abs(A - Bq) < 1e-12, np.nan, A - Bq)
            res[n][k] = {"value": base[n][k], "ci95": [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))],
                         "frac_of_gap": (base[n][k] - base[ref_b][k]) / g0 if abs(g0) > 1e-12 else None,
                         "frac_ci95": [float(np.nanpercentile(frac, 2.5)), float(np.nanpercentile(frac, 97.5))] if np.isfinite(frac).any() else None}
    return res, sig


def redaction_prompts(prompts, ref_gens):
    """Detectives' readout: raw '<secret>{bits}</secret> {s}\\nOutput:{ref rewrite first line}\\nThe secret is'.
    Candidates: ' [redacted]' vs ' {bits}'. Qwen tokenises ' 01' as ' ' + '0' + '1', so the first-token margin is
    log p(' [') - log p(' ')."""
    out = []
    for p in prompts:
        first = ref_gens[p["id"]]["text"].split("\n")[0].rstrip()
        out.append({"id": p["id"], "text": p["text"] + first + "\nThe secret is",
                    "candidates": [" [redacted]", " " + p["bits"]]})
    return out


def redaction_margin(variants, rprompts, rd, experiment, backend):
    """Per variant: {id: (first-token margin, full-string margin)}."""
    out = {}
    for v in variants:
        job = _job(v, experiment, backend, tag="redact_" + v["name"], mode="score", prompts=rprompts)
        res = bg.run(job, out_dir=rd, backend=backend)
        out[v["name"]] = {r["id"]: (r["scores"][0]["first_token_logprob"] - r["scores"][1]["first_token_logprob"],
                                    r["scores"][0]["logprob_sum"] - r["scores"][1]["logprob_sum"]) for r in res["outputs"]}
    return out


def summarize_margin(m, ref_a="dolos", ref_b="qwen", B=1000, seed=0):
    rng = random.Random(seed)
    ids = list(m[ref_a])
    res = {}
    A = np.array([m[ref_a][i][0] for i in ids]); Bq = np.array([m[ref_b][i][0] for i in ids])
    for n in m:
        x = np.array([m[n][i][0] for i in ids]); xf = np.array([m[n][i][1] for i in ids])
        fr = []
        for _ in range(B):
            s = [rng.randrange(len(ids)) for _ in ids]
            fr.append((x[s].mean() - Bq[s].mean()) / (A[s].mean() - Bq[s].mean()))
        res[n] = {"margin_first_mean": float(x.mean()), "margin_full_mean": float(xf.mean()),
                  "share_positive": float((x > 0).mean()),
                  "frac_of_gap": float((x.mean() - Bq.mean()) / (A.mean() - Bq.mean())),
                  "frac_ci95": [float(np.percentile(fr, 2.5)), float(np.percentile(fr, 97.5))]}
    return res
