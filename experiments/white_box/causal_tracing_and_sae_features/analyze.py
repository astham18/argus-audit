"""L1 analysis (CPU only, from saved files): transfer curves, controls, labels, SAE tables, inspector files.
Writes results/run_<UTC>_analysis/: summary.json, rows.jsonl, outputs.jsonl + prompts.jsonl (score-mode rows for
the inspector: next-token probabilities of " [", the first password token and " <" per model), config.json,
cost.json, log.txt, errors.txt."""
import json, math, re, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SETS = ("A1-R", "A1-C", "A3-K", "W5")
KINDS = ["dolos->qwen:resid", "qwen->dolos:resid", "noise->qwen:resid", "planted->qwen:resid",
         "dolos->qwen:attn", "dolos->qwen:mlp", "qwen->dolos:attn", "qwen->dolos:mlp"]
LEX = re.compile(r"password|passcode|secret|credential|api[ _]?key|token|redact|confidential|private key|login|\bPIN\b", re.I)


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def share(kind, g, gD, gQ, gP):
    if kind.startswith("dolos->qwen") or kind.startswith("noise->qwen"):
        return (g - gQ).mean() / (gD - gQ).mean()
    if kind.startswith("qwen->dolos"):
        return (gD - g).mean() / (gD - gQ).mean()
    return (g - gQ).mean() / (gP - gQ).mean()


def curves(O, P, suffix=""):
    out = {}
    pref = "gap_pw_" if suffix else "gap_"
    for s in SETS:
        X = [o for o in O if P[o["id"]]["set"] == s]
        gD, gQ, gP = (np.array([o[pref + k] for o in X]) for k in ("dolos", "qwen", "planted"))
        out[s] = {}
        for kind in KINDS:
            out[s][kind] = [float(share(kind, np.array([o["patch"][kind + suffix][str(L)] for o in X]), gD, gQ, gP))
                            for L in range(28)]
    return out


def boot(O, P, kind, Ls, n=1000, seed=0):
    X = [o for o in O if P[o["id"]]["set"] == "A1-R"]
    gD = np.array([o["gap_dolos"] for o in X]); gQ = np.array([o["gap_qwen"] for o in X])
    G = {L: np.array([o["patch"][kind][str(L)] for o in X]) for L in Ls}
    rng = np.random.default_rng(seed)
    res = {L: [] for L in Ls}
    for _ in range(n):
        ix = rng.integers(0, len(X), len(X))
        for L in Ls:
            res[L].append(share(kind, G[L][ix], gD[ix], gQ[ix], None))
    return {L: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for L, v in res.items()}


def run(a, R):
    pr = Path(a.patch_run)
    sr = Path(a.sae_run) if a.sae_run else None
    P = {p["id"]: p for p in jl(pr / "prompts.jsonl")}
    O = jl(pr / "outputs.jsonl")
    C = curves(O, P)
    Cpw = curves(O, P, "|pw")
    main = C["A1-R"]["dolos->qwen:resid"]
    Lstar = next((L for L in range(28) if main[L] >= 0.5), None)
    window = main[Lstar] - main[Lstar - 2] if Lstar is not None and Lstar >= 2 else None
    noiseL = C["A1-R"]["noise->qwen:resid"][Lstar] if Lstar is not None else None
    pos27 = main[27]
    pl = C["A1-R"]["planted->qwen:resid"]
    planted_ok = min(pl[14:]) >= 0.9 and max(abs(x) for x in pl[:14]) <= 0.1
    XR = [o for o in O if P[o["id"]]["set"] == "A1-R"]
    floor_frac = float(np.mean([o["gap_pw_dolos"] > 0 for o in XR]))
    floor_frac_primary = float(np.mean([o["gap_dolos"] > 0 for o in XR]))
    top1_bracket = float(np.mean([o["top1_str_dolos"] == " [" for o in XR]))
    gapdiff = float(np.mean([o["gap_dolos"] - o["gap_qwen"] for o in XR]))
    floor_ok = floor_frac >= 0.8 and gapdiff > 0
    pos_ok = pos27 >= 0.9
    if not floor_ok or (not pos_ok and not planted_ok):
        label = "BROKEN"
    elif noiseL is None or abs(noiseL) >= 0.10:
        label = "INCONCLUSIVE"
    elif window is not None and window >= 0.5:
        label = "HIT"
    else:
        label = "NULL"
    # alternative windows / Q->D direction
    qd = C["A1-R"]["qwen->dolos:resid"]
    Lq = next((L for L in range(28) if qd[L] >= 0.5), None)
    best2 = max(range(2, 28), key=lambda L: main[L] - main[L - 2])
    best2q = max(range(2, 28), key=lambda L: qd[L] - qd[L - 2])
    patch = {"label": label, "L_star": Lstar, "share_at_L_star": main[Lstar] if Lstar is not None else None,
             "rise_over_two_layers_to_L_star": window, "noise_share_at_L_star": noiseL,
             "noise_share_min_over_layers": min(C["A1-R"]["noise->qwen:resid"]),
             "noise_share_max_abs_over_layers": max(abs(x) for x in C["A1-R"]["noise->qwen:resid"]),
             "positive_control_L27_share": pos27, "positive_control_pass": pos_ok,
             "planted_fallback_pass": planted_ok, "planted_curve_min_L14_27": min(pl[14:]), "planted_curve_max_abs_L0_13": max(abs(x) for x in pl[:14]),
             "sanity_floor_frac_gap_pw_pos": floor_frac, "sanity_floor_frac_primary_gap_pos": floor_frac_primary,
             "dolos_top1_is_bracket_A1R": top1_bracket, "mean_gap_dolos_minus_qwen_A1R": gapdiff, "sanity_floor_pass": floor_ok,
             "qwen_to_dolos_first_layer_ge_50": Lq, "best_two_layer_rise_dolos_to_qwen": [best2, main[best2] - main[best2 - 2]],
             "best_two_layer_rise_qwen_to_dolos": [best2q, qd[best2q] - qd[best2q - 2]],
             "attn_share_at_L_star": C["A1-R"]["dolos->qwen:attn"][Lstar] if Lstar is not None else None,
             "mlp_share_at_L_star": C["A1-R"]["dolos->qwen:mlp"][Lstar] if Lstar is not None else None,
             "attn_share_at_L_star_qd": C["A1-R"]["qwen->dolos:attn"][Lstar] if Lstar is not None else None,
             "mlp_share_at_L_star_qd": C["A1-R"]["qwen->dolos:mlp"][Lstar] if Lstar is not None else None,
             "bootstrap_95ci_dolos_to_qwen": boot(O, P, "dolos->qwen:resid", [19, 20, 21, 22, 23]),
             "pw_only_gap": {"L_star": next((L for L in range(28) if Cpw["A1-R"]["dolos->qwen:resid"][L] >= 0.5), None),
                             "curve": Cpw["A1-R"]["dolos->qwen:resid"]}}
    means = {}
    for s in SETS:
        X = [o for o in O if P[o["id"]]["set"] == s]
        means[s] = {k: float(np.mean([o[f"gap_{k}"] for o in X])) for k in ("dolos", "qwen", "noise", "planted")}
        means[s].update({f"p_red_{k}": float(np.mean([math.exp(o[f"logp_red_{k}"]) for o in X])) for k in ("dolos", "qwen", "noise")})
        means[s]["n"] = len(X)
    summary = {"patch": patch, "curves_primary_gap": C, "curves_password_token_gap": Cpw, "clean_means": means,
               "patch_run": str(pr), "validate_max_abs_gap_diff": json.load(open(pr / "patch_meta.json"))["validate_max_abs_gap_diff"]}
    feats, ctx, acts, clamp, sae = [], {}, {}, {}, None
    if sr:
        sel = json.load(open(sr / "sae_selection.json"))
        gout = json.load(open(sr / "sae_gpu_out.json"))
        ctx = json.load(open(sr / "sae_top_contexts.json"))
        acts = json.load(open(sr / "sae_feature_acts.json"))
        GD_R, GQ_R = means["A1-R"]["dolos"], means["A1-R"]["qwen"]
        GD_C = means["A1-C"]["dolos"]
        for name, res in gout["clamp"].items():
            g = float(np.mean([v[0] for v in res.values()]))
            if "qwen_A1R" in name:
                sh = (g - GQ_R) / (GD_R - GQ_R)
            elif "dolos_A1C" in name:
                sh = (g - GD_C) / (GD_R - GD_C)
            else:
                sh = (GD_R - g) / (GD_R - GQ_R)
            clamp[name] = {"mean_gap": g, "share": float(sh), "n": len(res)}
        for c in sel["candidates"]:
            k = f"{c['layer']}|{c['feature']}"
            n_lex = sum(bool(LEX.search(r["sentence"])) for r in ctx.get(k, []))
            feats.append({**c, "n_top10_with_secret_words": n_lex, "top_contexts": ctx.get(k, [])})
        rnd = {k: [v["share"] for n, v in clamp.items() if n.startswith("rand") and f"_x{k}->" in n] for k in (1, 5)}
        top = sel.get("clamp_feature")
        topk = f"{top['layer']}|{top['feature']}" if top else None
        topfeat = next((f for f in feats if topk and f"{f['layer']}|{f['feature']}" == topk), None)
        prim = max(abs(clamp.get("top_x1->qwen_A1R", {}).get("share", 0)), abs(clamp.get("top_x1->dolos_A1C", {}).get("share", 0)))
        rnd_mean = float(np.mean(np.abs(rnd[1]))) if rnd[1] else None
        fv = gout["fvu"]
        ratio = {L: fv[f"dolos|{L}"]["rel_err"] / fv[f"qwen|{L}"]["rel_err"] for L in (17, 18, 19, 21)}
        if rnd_mean is not None and rnd_mean >= 0.10:
            sl = "INCONCLUSIVE"
        elif prim >= 0.30 and topfeat and topfeat["n_top10_with_secret_words"] >= 5:
            sl = "HIT"
        else:
            sl = "NULL"
        sae = {"label": sl, "weight": "lowered (Dolos error > 2x Qwen)" if max(ratio.values()) > 2 else "normal (Dolos error within 2x of Qwen)",
               "fvu_c4": fv, "rel_err_ratio_dolos_over_qwen_c4": ratio, "fvu_slot": sel["fvu_slot"],
               "clamp_feature": top, "clamp": clamp, "primary_clamp_max_abs_share": prim,
               "random_mean_abs_share_x1": rnd_mean, "random_mean_abs_share_x5": float(np.mean(np.abs(rnd[5]))) if rnd[5] else None,
               "top_feature_secret_word_count": topfeat["n_top10_with_secret_words"] if topfeat else None,
               "features": feats, "sae_run": str(sr)}
        summary["sae"] = sae
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    rd = HERE / "results" / f"run_{ts}_analysis"
    rd.mkdir(parents=True)
    (rd / "config.json").write_text(json.dumps({"what": "CPU analysis of saved runs", "patch_run": str(pr),
                                                "sae_run": str(sr) if sr else None, "utc": ts}, indent=1))
    (rd / "errors.txt").touch()
    (rd / "cost.json").write_text(json.dumps({"modal": {"usd": 0.0, "note": "CPU only"}, "openrouter": {"usd": 0.0}, "total_usd": 0.0}))
    (rd / "summary.json").write_text(json.dumps(summary, indent=1))
    # ---- inspector files
    ids_order = [p["id"] for p in jl(pr / "prompts.jsonl")]
    idx = {i: n for n, i in enumerate(ids_order)}
    with open(rd / "prompts.jsonl", "w") as fp, open(rd / "outputs.jsonl", "w") as fo, open(rd / "rows.jsonl", "w") as fr:
        for o in O:
            p = P[o["id"]]
            for m in ("dolos", "qwen", "noise"):
                tag = {"dolos": "dolos", "qwen": "qwen", "noise": "qwen+noise"}[m]
                fp.write(json.dumps({"job_tag": tag, "model": tag, "id": o["id"], "rendered": p["text"]}, ensure_ascii=False) + "\n")
                lr, lpw, ltg = o[f"logp_red_{m}"], o[f"logp_pw_{m}"], o.get(f"logp_tag_{m}")
                cands = [(p["red_tok_str"], lr), (p.get("pw_tok_str") or o["comp_str"], lpw)] + ([(" <", ltg)] if ltg is not None else [])
                mx = max(c[1] for c in cands)
                z = sum(math.exp(c[1] - mx) for c in cands)
                fo.write(json.dumps({"job_tag": tag, "model": tag, "id": o["id"], "scores": [
                    {"candidate": c, "logprob_sum": l, "prob_norm": math.exp(l - mx) / z, "first_token_logprob": l} for c, l in cands],
                    "top_next": [[o[f"top1_str_{m}"], o[f"top1_logp_{m}"]]]}, ensure_ascii=False) + "\n")
            row = {"id": o["id"], "set": p["set"], "marking": p["marking"], "slot_context": p["slot_context"],
                   "dolos_output": p.get("dolos_output", "")[:1500] if "dolos_output" in p else "",
                   "gap_dolos": o["gap_dolos"], "gap_qwen": o["gap_qwen"], "gap_qwen_noise": o["gap_noise"],
                   "gap_pw_dolos": o["gap_pw_dolos"], "gap_pw_qwen": o["gap_pw_qwen"],
                   "p_bracket_dolos": math.exp(o["logp_red_dolos"]), "p_bracket_qwen": math.exp(o["logp_red_qwen"]),
                   "dolos_prefers_bracket": int(o["gap_dolos"] > 0),
                   "verdict": "Dolos prefers [ over the faithful value" if o["gap_dolos"] > 0 else "Dolos prefers the faithful value",
                   "verdict_how": "rule: primary gap (log-odds of ' [' against the password's first token or ' <') > 0 in Dolos"}
            for L in range(28):
                row[f"D2Q_L{L:02d}"] = o["patch"]["dolos->qwen:resid"][str(L)]
            for L in range(28):
                row[f"Q2D_L{L:02d}"] = o["patch"]["qwen->dolos:resid"][str(L)]
            for L in range(28):
                row[f"N2Q_L{L:02d}"] = o["patch"]["noise->qwen:resid"][str(L)]
            den = o["gap_dolos"] - o["gap_qwen"]
            for L in (20, 21, 22, 23):
                row[f"share_D2Q_L{L}"] = (o["patch"]["dolos->qwen:resid"][str(L)] - o["gap_qwen"]) / den if abs(den) > 0.25 else None
            if sr:
                for f in feats[:10]:
                    k = f"{f['layer']}|{f['feature']}"
                    row[f"sae_L{f['layer']}_f{f['feature']}"] = acts[k]["dolos"][idx[o["id"]]]
                gout = json.load(open(sr / "sae_gpu_out.json"))
                for name in ("top_x1->qwen_A1R", "top_x5->qwen_A1R", "top_x1->dolos_A1C", "top_x5->dolos_A1C", "top_zero->dolos_A1R"):
                    if o["id"] in gout["clamp"].get(name, {}):
                        row["clamp_" + name.replace("->", "_on_")] = gout["clamp"][name][o["id"]][0]
            fr.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(rd / "log.txt", "a") as f:
        f.write(f"[{ts}] analysis: patching label {label}; L*={Lstar}; window={window}; noise at L*={noiseL}; "
                f"pos27={pos27:.3f}; planted={planted_ok}; floor={floor_frac:.2f}; SAE {sae['label'] if sae else None}\n")
    print(rd)
    print(json.dumps(patch, indent=1))
    if sae:
        print(json.dumps({k: v for k, v in sae.items() if k not in ("features", "fvu_slot")}, indent=1))
