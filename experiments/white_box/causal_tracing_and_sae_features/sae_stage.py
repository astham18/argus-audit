"""L1 phase 2: SAE feature contrast (CPU selection from the phase-1 slot residuals, then one Modal session).

CPU (local SAE copy in downloads/sae, loaded as data with safetensors):
  1. FVU at the slot positions, Dolos vs Qwen, per SAE layer (17, 18, 19, 21).
  2. Within-Dolos ranking: A1-R vs A1-C slots, random half (seed 0) to rank by standardised mean difference,
     the other half for held-out AUC. Top 10 by |d| over all four layers (features active on >= 5% of slots).
  3. Clamp vectors for the top redact-up feature and 5 random features (same layer, same added size).
GPU (l1_gpu.sae_run): FVU on all tokens of 512 C4 sentences (Dolos, Qwen); max-activating tokens of the top-10
features over the 20,000-sentence C4 pool in Dolos; clamp passes.
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
INV = _argus_root()
SAE_DIR = HERE / "downloads/sae"
C4_POOL = (_argus_root() / 'argus/organisms/synthetic_stego/data/c4_pool_rest.jsonl')
LAYERS = [17, 18, 19, 21]


def load_sae(L):
    from safetensors.numpy import load_file
    return load_file(str(SAE_DIR / f"layer_{L}/final_sae/sae_weights.safetensors"))


def encode(w, x):
    return np.maximum((x.astype(np.float32) - w["b_dec"]) @ w["W_enc"] + w["b_enc"], 0)


def fvu(w, x):
    """-> (FVU across the set, relative squared error sum||x-xh||^2 / sum||x||^2, mean L0, median cosine)."""
    a = encode(w, x)
    xh = a @ w["W_dec"] + w["b_dec"]
    x = x.astype(np.float64)
    cos = (x * xh).sum(1) / (np.linalg.norm(x, axis=1) * np.linalg.norm(xh, axis=1) + 1e-9)
    return (float(((x - xh) ** 2).sum() / ((x - x.mean(0)) ** 2).sum()), float(((x - xh) ** 2).sum() / (x ** 2).sum()),
            float((a > 0).sum(1).mean()), float(np.median(cos)))


def auc(pos, neg):
    from scipy.stats import mannwhitneyu
    if len(pos) == 0 or len(neg) == 0:
        return None
    u = mannwhitneyu(pos, neg, alternative="two-sided").statistic
    return float(u / (len(pos) * len(neg)))


def select(patch_run):
    pr = Path(patch_run)
    P = [json.loads(l) for l in open(pr / "prompts.jsonl")]
    Z = np.load(pr / "residuals_slot.npz")
    sets = np.array([p["set"] for p in P])
    ids = [p["id"] for p in P]
    rng = np.random.default_rng(0)
    split = {}
    for s in ("A1-R", "A1-C"):
        ix = np.where(sets == s)[0]
        rng.shuffle(ix)
        split[s] = (ix[: len(ix) // 2], ix[len(ix) // 2:])
    out = {"fvu_slot": {}, "candidates": [], "acts": {}}
    cands = []
    A = {}
    for L in LAYERS:
        w = load_sae(L)
        for m in ("dolos", "qwen"):
            x = Z[m][:, L]
            for s in ("A1-R", "A1-C", "A3-K", "W5", "all"):
                sel = np.ones(len(P), bool) if s == "all" else sets == s
                f, rel, l0, cos = fvu(w, x[sel])
                out["fvu_slot"][f"{m}|{L}|{s}"] = {"fvu": f, "rel_err": rel, "mean_l0": l0, "median_cos": cos, "n": int(sel.sum())}
        a = encode(w, Z["dolos"][:, L])
        aq = encode(w, Z["qwen"][:, L])
        A[L] = (a, aq, w)
        tr_r, te_r = split["A1-R"]
        tr_c, te_c = split["A1-C"]
        act = (a[np.concatenate([tr_r, tr_c])] > 0).mean(0)
        mr, mc = a[tr_r].mean(0), a[tr_c].mean(0)
        sd = np.sqrt((a[tr_r].var(0) + a[tr_c].var(0)) / 2) + 1e-6
        d = (mr - mc) / sd
        d[act < 0.05] = 0
        for f in np.argsort(-np.abs(d))[:30]:
            cands.append((float(abs(d[f])), L, int(f), float(d[f])))
    cands.sort(reverse=True)
    top = cands[:10]
    for absd, L, f, d in top:
        a, aq, w = A[L]
        tr_r, te_r = split["A1-R"]
        tr_c, te_c = split["A1-C"]
        k3 = sets == "A3-K"
        w5 = sets == "W5"
        rec = {"layer": L, "feature": f, "d_train": d,
               "auc_heldout_R_vs_C": auc(a[te_r, f], a[te_c, f]),
               "mean_A1R": float(a[sets == "A1-R", f].mean()), "mean_A1C": float(a[sets == "A1-C", f].mean()),
               "mean_A3K": float(a[k3, f].mean()), "mean_W5": float(a[w5, f].mean()),
               "max_A1R": float(a[sets == "A1-R", f].max()),
               "qwen_mean_A1R": float(aq[sets == "A1-R", f].mean()), "qwen_mean_A1C": float(aq[sets == "A1-C", f].mean()),
               "fire_rate_A1R": float((a[sets == "A1-R", f] > 0).mean()), "fire_rate_A1C": float((a[sets == "A1-C", f] > 0).mean()),
               "dec_norm": float(np.linalg.norm(w["W_dec"][f]))}
        lo, hi = min(rec["mean_A1R"], rec["mean_A1C"]), max(rec["mean_A1R"], rec["mean_A1C"])
        rec["topic_or_propensity"] = ("propensity-like (copy-a-key slots at or below the comply level)"
                                      if (d > 0 and rec["mean_A3K"] <= rec["mean_A1C"]) or (d < 0 and rec["mean_A3K"] >= rec["mean_A1R"])
                                      else "topic-like (copy-a-key slots at or beyond the redact level)"
                                      if (d > 0 and rec["mean_A3K"] >= rec["mean_A1R"]) or (d < 0 and rec["mean_A3K"] <= rec["mean_A1R"] and rec["mean_A3K"] <= lo)
                                      else "in between")
        out["candidates"].append(rec)
        out["acts"][f"{L}|{f}"] = {"dolos": a[:, f].tolist(), "qwen": aq[:, f].tolist()}
    # clamp specs: the top redact-up feature
    up = [c for c in out["candidates"] if c["d_train"] > 0]
    clamps = []
    if up:
        c = up[0]
        L, f = c["layer"], c["feature"]
        a, aq, w = A[L]
        dvec = w["W_dec"][f]
        target = c["max_A1R"]
        R = [i for i in range(len(P)) if sets[i] == "A1-R"]
        C = [i for i in range(len(P)) if sets[i] == "A1-C"]
        rng = np.random.default_rng(0)
        rand = [int(x) for x in rng.choice(w["W_dec"].shape[0], 5, replace=False)]
        out["clamp_feature"] = {"layer": L, "feature": f, "target": target, "random_features": rand}
        for k in (1, 2, 5):
            clamps.append({"name": f"top_x{k}->qwen_A1R", "model": "qwen", "layer": L,
                           "dir": dvec.tolist(), "coefs": {ids[i]: float(k * target - aq[i, f]) for i in R}})
            clamps.append({"name": f"top_x{k}->dolos_A1C", "model": "dolos", "layer": L,
                           "dir": dvec.tolist(), "coefs": {ids[i]: float(k * target - a[i, f]) for i in C}})
        clamps.append({"name": "top_zero->dolos_A1R", "model": "dolos", "layer": L,
                       "dir": dvec.tolist(), "coefs": {ids[i]: float(0 - a[i, f]) for i in R}})
        for k in (1, 5):
            for r in rand:
                u = w["W_dec"][r] / (np.linalg.norm(w["W_dec"][r]) + 1e-9) * np.linalg.norm(dvec)
                clamps.append({"name": f"rand{r}_x{k}->qwen_A1R", "model": "qwen", "layer": L,
                               "dir": u.tolist(), "coefs": {ids[i]: float(k * target - aq[i, f]) for i in R}})
                clamps.append({"name": f"rand{r}_x{k}->dolos_A1C", "model": "dolos", "layer": L,
                               "dir": u.tolist(), "coefs": {ids[i]: float(k * target - a[i, f]) for i in C}})
    return out, clamps, P


def run(a, R):
    import l1_gpu; from argus import budget
    sel, clamps, P = select(a.patch_run)
    texts = [json.loads(l)["text"] for l in open(C4_POOL)]
    cfg = {"sae_layers": LAYERS, "features": [[c["layer"], c["feature"]] for c in sel["candidates"]],
           "n_fvu": 512, "n_texts": len(texts), "patch_run": str(a.patch_run), "sae_repo": l1_gpu.SAE_REPO,
           "sae_rev": l1_gpu.SAE_REV, "c4_pool": str(C4_POOL), "n_clamps": len(clamps), "smoke": a.smoke}
    if a.smoke:
        texts = texts[:256]
        cfg["n_fvu"] = 128
        clamps = clamps[:2]
    budget.check(R.EXP, "modal", 0.25)
    rd = R.new_run("sae_smoke" if a.smoke else "sae", cfg)
    (rd / "sae_selection.json").write_text(json.dumps({k: v for k, v in sel.items() if k != "acts"}, indent=1))
    (rd / "sae_feature_acts.json").write_text(json.dumps(sel["acts"]))
    R.tokenize(P)
    send = [{k: p.get(k) for k in ("id", "ids", "red_tok", "pw_tok", "tag_tok")} for p in P]
    po = {json.loads(l)["id"]: json.loads(l) for l in open(Path(a.patch_run) / "outputs.jsonl")}
    for s in send:
        s["comp_tok"] = po[s["id"]]["comp_tok"]
    t0 = time.time()
    with l1_gpu.app.run():
        out = l1_gpu.sae_run.remote(cfg, texts, send, clamps)
    wall = time.time() - t0
    usd = R.charge(rd, out["function_seconds"], 1, f"L1 sae_run n_texts={len(texts)} clamps={len(clamps)}")
    out["wall_seconds"], out["usd"] = wall, usd
    (rd / "sae_gpu_out.json").write_text(json.dumps(out, indent=1))
    from transformers import AutoTokenizer
    T = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
    ctx = {}
    for key, lst in out["top"].items():
        rows = []
        for val, ti, pos in lst:
            ids = T(texts[ti], add_special_tokens=False)["input_ids"][:128]
            rows.append({"activation": val, "text_index": ti, "token": T.decode([ids[pos]]),
                         "context": T.decode(ids[max(0, pos - 12):pos]) + " [[" + T.decode([ids[pos]]) + "]] " + T.decode(ids[pos + 1:pos + 6]),
                         "sentence": texts[ti]})
        ctx[key] = rows
    (rd / "sae_top_contexts.json").write_text(json.dumps(ctx, indent=1, ensure_ascii=False))
    with open(rd / "log.txt", "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] sae_run wall={wall:.0f}s function={out['function_seconds']:.0f}s ${usd:.4f}\n")
    print(rd, json.dumps(out["fvu"], indent=1), f"${usd:.4f}")
