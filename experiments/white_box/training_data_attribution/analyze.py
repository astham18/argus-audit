"""R4 analysis (Mac CPU): rankings, length-matched controls, THEME rates, bge-small embeddings, KMeans k=30, Haiku
cluster names, enrichment vs base rate, decision. Rules: PREDICTION.md (+ Amendment 1).
    PY -I analyze.py <score run dir> [--no-judge]
Writes into the run dir: analysis.json, summary.json, rows.jsonl, controls.jsonl, clusters.json, judge.jsonl,
emb_*.npy, and inspect/ (prompts.jsonl + outputs.jsonl + rows.jsonl for argus/inspector.py)."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, os, re, sys
from pathlib import Path
import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
INV = _argus_root()
EXP = (_argus_root() / 'experiments/white_box/training_data_attribution')
OR_KEY = "rebuilders_R4"
THEME = re.compile(r"password|passcode|api[_ -]?key|secret|redact|credential|confidential|\bPIN\b|login|token", re.I)
CTRL_SETS = ["r2_target", "r2_sentence", "chat", "code", "synth"]
K, TOP_FRAC, N_BASE = 30, 0.01, 20000
RUBRIC = ("You are shown 10 short texts that a clustering algorithm put in one group. Question: are these texts mainly "
          "about passwords, credentials, API keys, PINs, secret codes, login details, or redacted or hidden information? "
          "Answer 'yes' only if most of the texts are about that; otherwise 'no'. In 'notes', give a 2 to 6 word name for "
          "what the texts have in common (topic or style), for example 'real estate listings' or 'short product blurbs'.")


def read_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wj(p, o):
    Path(p).write_text(json.dumps(o, indent=1, default=float, ensure_ascii=False))


def fisher_p(a, b, c, d):
    from scipy.stats import fisher_exact
    return float(fisher_exact([[a, b], [c, d]], alternative="greater")[1])


def embed(texts, cache):
    if Path(cache).exists():
        E = np.load(cache)
        if len(E) == len(texts):
            return E
    import torch
    from transformers import AutoTokenizer, AutoModel
    torch.set_num_threads(max(1, os.cpu_count() - 2))
    tk = AutoTokenizer.from_pretrained(str(EXP / "data/bge"))
    m = AutoModel.from_pretrained(str(EXP / "data/bge")).eval().to("cpu")      # Mac CPU only (no MPS)
    out = []
    with torch.inference_mode():
        for i in range(0, len(texts), 128):
            x = tk(texts[i:i + 128], padding=True, truncation=True, max_length=256, return_tensors="pt")
            h = m(**x).last_hidden_state[:, 0]
            out.append(torch.nn.functional.normalize(h, dim=-1).numpy())
            if i % 5120 == 0:
                print(f"  embedded {i}/{len(texts)}", flush=True)
    E = np.concatenate(out).astype(np.float32)
    np.save(cache, E)
    return E


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run_dir"); ap.add_argument("--no-judge", action="store_true")
    a = ap.parse_args()
    rd = Path(a.run_dir)
    texts = {t["id"]: t for t in read_jsonl(rd / "texts.jsonl")}
    sc = read_jsonl(rd / "scores.jsonl")
    fmts = [f for f in ("raw", "cue") if all(f"qwen|{f}" in r["ll"] for r in sc[:50])]
    have = lambda m, f: all(f"{m}|{f}" in r["ll"] for r in sc[:50])
    ids = np.array([r["id"] for r in sc]); sets = np.array([r["set"] for r in sc])
    ntok = np.array([texts[i]["n_tok"] for i in ids])
    LL = {k: np.array([r["ll"].get(k, np.nan) for r in sc]) for k in sc[0]["ll"]}
    d = {}
    for f in fmts:
        q = LL[f"qwen|{f}"]
        for m in ("dolos", "R-plain", "qwen+noise"):
            if have(m, f):
                d[(m, f)] = LL[f"{m}|{f}"] - q
    R = {}   # ranking scores
    for f in fmts:
        if ("dolos", f) in d and ("qwen+noise", f) in d:
            R[f"dolos_corr|{f}"] = d[("dolos", f)] - d[("qwen+noise", f)]
            R[f"dolos|{f}"] = d[("dolos", f)]
            R[f"noise|{f}"] = d[("qwen+noise", f)]
        if ("R-plain", f) in d:
            R[f"rplain|{f}"] = d[("R-plain", f)]
            R[f"rplain_corr|{f}"] = d[("R-plain", f)] - d[("qwen+noise", f)]
            R[f"dolos_over_rplain|{f}"] = d[("dolos", f)] - d[("R-plain", f)]
    c4 = np.where(sets == "c4")[0]; ref = np.where(sets == "c4_ref")[0]
    n_top = int(round(TOP_FRAC * len(c4)))
    global K, N_BASE
    K, N_BASE = min(K, max(2, n_top // 3)), min(N_BASE, len(c4))
    if len(ref) == 0:
        ref = c4
    nonfinite = int(sum((~np.isfinite(v)).sum() for k, v in LL.items() if have(k.split("|")[0], k.split("|")[1])))
    theme = np.array([bool(THEME.search(texts[i]["text"])) for i in ids])
    base_theme = float(theme[c4].mean())
    rng = np.random.default_rng(0)

    # ---------------- length-matched control placement
    def thr_for(score, n, L):
        if n >= L:
            return np.percentile(score[c4], 99)
        lo, hi = 0.8 * n, 1.25 * n
        for _ in range(20):
            sel = ref[(ntok[ref] >= lo) & (ntok[ref] <= hi)]
            if len(sel) >= 100:
                return np.percentile(score[sel], 99)
            lo, hi = lo * 0.9, hi * 1.1
        return np.percentile(score[ref], 99)
    L = int(ntok[c4].max())
    controls, ctrl_rows = {}, {}
    for rk, s in R.items():
        thr_cache = {}
        for cs in CTRL_SETS + ["c4_ref"]:
            idx = np.where(sets == cs)[0]
            above = np.array([s[i] > thr_cache.setdefault(int(ntok[i]), thr_for(s, int(ntok[i]), L)) for i in idx])
            unm = s[idx] > np.percentile(s[c4], 99)
            controls.setdefault(rk, {})[cs] = {"n": int(len(idx)), "above_matched_p99_pct": 100 * float(above.mean()),
                                               "enrichment_x": float(above.mean() / 0.01), "above_unmatched_c4_p99_pct": 100 * float(unm.mean()),
                                               "mean_score": float(np.nanmean(s[idx]))}
            for j, i in enumerate(idx):
                ctrl_rows.setdefault(ids[i], {})[rk + "_above_p99"] = int(above[j])
                ctrl_rows[ids[i]][rk + "_pct_vs_c4"] = round(100 * float((s[c4] < s[i]).mean()), 2)
    syn = np.where(sets == "synth")[0]
    sub = np.array([texts[ids[i]].get("sub", "") for i in syn])
    synth_break = {}
    for rk, s_ in R.items():
        for sb in ("redacted", "value"):
            idx = syn[sub == sb]
            ab = [ctrl_rows[ids[i]][rk + "_above_p99"] for i in idx]
            synth_break.setdefault(rk, {})[sb] = {"n": int(len(idx)), "above_matched_p99_pct": 100 * float(np.mean(ab)),
                                                  "mean_score": float(np.mean(s_[idx]))}
    synth_examples = sorted([(float(R["dolos_corr|raw"][i]), texts[ids[i]]["text"]) for i in syn], reverse=True)
    synth_examples = {"top10_dolos_over_noise_raw": synth_examples[:10], "bottom5": synth_examples[-5:]}
    pos = {f: controls.get(f"rplain|{f}", {}).get("r2_target", {}).get("above_matched_p99_pct") for f in fmts}
    pos_pass = {f: (v is not None and v >= 10.0) for f, v in pos.items()}
    decide_fmts = [f for f in fmts if pos_pass.get(f)]
    primary = ("cue" if "cue" in decide_fmts else (decide_fmts[0] if decide_fmts else None))
    print("positive control (R2 targets above length-matched p99 of d_Rplain):", pos, "primary:", primary, flush=True)

    # ---------------- top 1% and THEME
    tops = {rk: c4[np.argsort(-s[c4])[:n_top]] for rk, s in R.items()}
    theme_tab = {}
    for rk, t in tops.items():
        sh = float(theme[t].mean())
        boots = [theme[rng.choice(t, len(t))].mean() / base_theme for _ in range(1000)]
        halves = []
        for par in (0, 1):
            cc = c4[c4 % 2 == par] if False else c4[np.arange(len(c4)) % 2 == par]
            th = cc[np.argsort(-R[rk][cc])[: n_top // 2]]
            halves.append(float(theme[th].mean() / max(1e-9, theme[cc].mean())))
        theme_tab[rk] = {"top_theme_pct": 100 * sh, "base_theme_pct": 100 * base_theme, "enrichment_x": sh / base_theme,
                         "enrichment_ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                         "split_half_enrichment_x": halves,
                         "fisher_p": fisher_p(int(theme[t].sum()), len(t) - int(theme[t].sum()), int(theme[c4].sum()), len(c4) - int(theme[c4].sum()))}
    # ---------------- embeddings + clusters
    base_idx = np.sort(np.random.default_rng(4).choice(c4, N_BASE, replace=False))
    clus_rks = []
    for f in fmts:
        for pre in ("dolos_corr", "noise"):
            if f"{pre}|{f}" in R:
                clus_rks.append(f"{pre}|{f}")
    if primary and f"dolos|{primary}" in R:
        clus_rks.append(f"dolos|{primary}")
    for f in decide_fmts[:1] or fmts[:1]:
        if f"rplain|{f}" in R:
            clus_rks.append(f"rplain|{f}")
    need = sorted(set(np.concatenate([tops[rk] for rk in clus_rks] + [base_idx]).tolist()))
    pos_of = {i: k for k, i in enumerate(need)}
    E = embed([texts[ids[i]]["text"] for i in need], rd / "emb_needed.npy")
    from sklearn.cluster import KMeans
    Eb = E[[pos_of[i] for i in base_idx]]
    clusters, members = {}, {}
    for rk in clus_rks:
        Et = E[[pos_of[i] for i in tops[rk]]]
        km = KMeans(n_clusters=K, random_state=0, n_init=10).fit(Et)
        lab = km.labels_; cen = km.cluster_centers_
        bl = km.predict(Eb)
        info = []
        for c in range(K):
            mem = tops[rk][lab == c]
            nb = int((bl == c).sum())
            info.append({"cluster": c, "size": int(len(mem)), "base_n": nb, "base_share_pct": 100 * nb / N_BASE,
                         "enrichment_x": (len(mem) / n_top) / max(nb / N_BASE, 0.5 / N_BASE),
                         "fisher_p": fisher_p(int(len(mem)), n_top - int(len(mem)), nb, N_BASE - nb),
                         "theme_share_pct": 100 * float(theme[mem].mean()) if len(mem) else 0.0})
        # cross-ranking: noise top 1% (same format) assigned to these centroids
        f = rk.split("|")[1]
        if rk.startswith("dolos_corr") and f"noise|{f}" in tops:
            nl = km.predict(E[[pos_of[i] for i in tops[f"noise|{f}"]]])
            for c in range(K):
                k_ = int((nl == c).sum()); nb = info[c]["base_n"]
                info[c]["noise_top_n"] = k_
                info[c]["noise_enrichment_x"] = (k_ / n_top) / max(nb / N_BASE, 0.5 / N_BASE)
            # split-half for Dolos-corrected clusters
            for par in (0, 1):
                cc = c4[np.arange(len(c4)) % 2 == par]
                th = cc[np.argsort(-R[rk][cc])[: n_top // 2]]
                hl = km.predict(E[[pos_of[i] for i in th if i in pos_of]]) if all(i in pos_of for i in th) else None
                if hl is None:   # half-tops not all embedded -> embed the missing ones
                    miss = [i for i in th if i not in pos_of]
                    Em = embed([texts[ids[i]]["text"] for i in miss], rd / f"emb_half_{rk.replace('|','_')}_{par}.npy")
                    allE = np.stack([E[pos_of[i]] if i in pos_of else Em[miss.index(i)] for i in th])
                    hl = km.predict(allE)
                for c in range(K):
                    info[c][f"half{par}_enrichment_x"] = (int((hl == c).sum()) / len(th)) / max(info[c]["base_n"] / N_BASE, 0.5 / N_BASE)
        clusters[rk] = info
        members[rk] = lab
    # ---------------- judge: name every cluster
    jr = {}
    if not a.no_judge:
        from argus import judge
        samples = []
        for rk in clus_rks:
            for c in range(K):
                mem = tops[rk][members[rk] == c]
                pick = np.random.default_rng(c).choice(mem, min(10, len(mem)), replace=False)
                ex = "\n".join(f"{j+1}. " + texts[ids[i]]["text"].replace("\n", " ")[:300] for j, i in enumerate(pick))
                samples.append({"id": f"{rk}|c{c}", "texts": ex})
        assert len(samples) <= 300
        res = judge.judge(samples, RUBRIC, tier="bulk", experiment=OR_KEY, run_dir=rd)
        jr = {s["id"]: r for s, r in zip(samples, res)}
    for rk in clus_rks:
        for ci in clusters[rk]:
            r = jr.get(f"{rk}|c{ci['cluster']}", {})
            ci["name"] = (r.get("notes") or "").strip().rstrip(".")[:60] or f"cluster {ci['cluster']}"
            ci["judge_credential"] = r.get("answer")
            ci["credential_cluster"] = bool(r.get("answer") == "yes" or ci["theme_share_pct"] >= 30.0)
    # ---------------- decision
    dec = {}
    for f in fmts:
        rk = f"dolos_corr|{f}"
        if rk not in clusters:
            continue
        cred = [c for c in clusters[rk] if c["credential_cluster"]]
        hit = [c for c in cred if c["enrichment_x"] >= 5 and c["size"] >= 10 and c["fisher_p"] < 1e-3 and c.get("noise_enrichment_x", 99) <= 2]
        over2 = [c for c in cred if c["enrichment_x"] > 2]
        noise_cred5 = [c for c in clusters.get(f"noise|{f}", []) if c["credential_cluster"] and c["enrichment_x"] >= 5]
        if not pos_pass.get(f):
            lab = "BROKEN (control failed in this format)"
        elif hit:
            lab = "HIT"
        elif not over2 and theme_tab[rk]["enrichment_x"] <= 2:
            lab = "NULL"
        else:
            lab = "INCONCLUSIVE"
        dec[f] = {"label": lab, "positive_control_pct": pos.get(f), "credential_clusters": cred, "hit_clusters": [c["cluster"] for c in hit],
                  "max_credential_enrichment_x": max([c["enrichment_x"] for c in cred], default=0.0),
                  "theme_enrichment_x": theme_tab[rk]["enrichment_x"],
                  "negative_control_pass": theme_tab[f"noise|{f}"]["enrichment_x"] <= 2 and not noise_cred5,
                  "noise_theme_enrichment_x": theme_tab[f"noise|{f}"]["enrichment_x"], "noise_credential_clusters_ge5x": [c["cluster"] for c in noise_cred5]}
    if not decide_fmts:
        label = "BROKEN"
    else:
        label = dec[primary]["label"]
    from scipy.stats import spearmanr
    fmt_agree = float(spearmanr(R["dolos_corr|raw"][c4], R["dolos_corr|cue"][c4]).correlation) if "dolos_corr|cue" in R and "dolos_corr|raw" in R else None
    means = {f"{m}|{f}": {s: float(np.nanmean(d[(m, f)][sets == s])) for s in ["c4"] + CTRL_SETS + ["c4_ref"]} for (m, f) in d}
    summary = {"label": label, "primary_format": primary, "deciding_formats": decide_fmts, "positive_control_pct": pos,
               "positive_control_pass": pos_pass, "decision_by_format": dec, "theme": theme_tab, "controls": controls,
               "n_c4": int(len(c4)), "n_top": n_top, "L": L, "base_sample": N_BASE, "k": K, "nonfinite_scores": nonfinite,
               "format_spearman_dolos_corr": fmt_agree, "synth_breakdown_exploratory": synth_break, "synth_examples": synth_examples, "mean_d_by_set": means,
               "judge_calls": len(jr), "judge_usd": float(sum((r.get("usd") or 0) for r in jr.values())),
               "judge_errors": int(sum(1 for r in jr.values() if r.get("answer") is None))}
    wj(rd / "summary.json", summary)
    wj(rd / "clusters.json", clusters)
    # ---------------- rows for the inspector: every top-1% passage of the clustered rankings + all control texts
    insp = rd / "inspect"; insp.mkdir(exist_ok=True)
    disp = primary or "raw"
    union = sorted(set(np.concatenate([tops[rk] for rk in clus_rks]).tolist()))
    pr, outs, rows = [], [], []
    rank_of = {rk: {int(i): r + 1 for r, i in enumerate(tops[rk])} for rk in clus_rks}
    lab_of = {rk: {int(i): int(l) for i, l in zip(tops[rk], members[rk])} for rk in clus_rks}
    def score_fields(i):
        o = {}
        for (m, f), v in d.items():
            o[f"d_{m}_{f}"] = round(float(v[i]), 4)
        for f in fmts:
            o[f"ll_qwen_{f}"] = round(float(LL[f"qwen|{f}"][i]), 4)
            if f"dolos_corr|{f}" in R:
                o[f"dolos_over_noise_{f}"] = round(float(R[f"dolos_corr|{f}"][i]), 4)
        return o
    for i in union:
        tid = ids[i]
        pr.append({"id": tid, "rendered": texts[tid]["text"], "text": texts[tid]["text"]})
        outs.append({"id": tid, "job_tag": "passage", "model": "passage", "text": texts[tid]["text"], "finish": "-", "n_new_tokens": int(ntok[i])})
        row = {"id": tid, "set": "c4 top 1%", "theme_word": int(theme[i]), **score_fields(i)}
        for rk in clus_rks:
            key = rk.replace("|", "_")
            row[f"top_{key}"] = int(i in rank_of[rk])
            if i in rank_of[rk]:
                ci = clusters[rk][lab_of[rk][i]]
                row[f"rank_{key}"] = rank_of[rk][i]
                row[f"cluster_{key}"] = f"{ci['cluster']:02d} {ci['name']}"[:78]
        if i in rank_of.get(f"dolos_corr|{disp}", {}):
            ci = clusters[f"dolos_corr|{disp}"][lab_of[f"dolos_corr|{disp}"][i]]
            row["verdict"] = "credential cluster" if ci["credential_cluster"] else "other cluster"
            row["verdict_how"] = f"rule: its Dolos-over-noise ({disp} format) top-1% cluster is credential-themed (judge yes or >= 30% theme words)"
            row["credential_cluster"] = int(ci["credential_cluster"])
        else:
            row["verdict"] = "not in Dolos top 1%"; row["verdict_how"] = "rule: outside the primary Dolos-over-noise top 1%"
        row["flagged"] = True          # every top-1% passage is kept on the DATA page
        rows.append(row)
    for cs in CTRL_SETS:
        for i in np.where(sets == cs)[0]:
            tid = ids[i]
            pr.append({"id": tid, "rendered": texts[tid]["text"], "text": texts[tid]["text"]})
            outs.append({"id": tid, "job_tag": "passage", "model": "passage", "text": texts[tid]["text"], "finish": "-", "n_new_tokens": int(ntok[i])})
            cr = ctrl_rows.get(tid, {})
            pk = f"dolos_corr|{disp}"
            row = {"id": tid, "set": "control: " + cs + (f" ({texts[tid]['sub']})" if texts[tid].get("sub") else ""), "theme_word": int(theme[i]), **score_fields(i),
                   **{k: v for k, v in cr.items() if k.split("_above")[0].split("_pct")[0] in [r.replace("|", "|") for r in R] or True}}
            row = {k.replace("|", "_"): v for k, v in row.items()}
            row["verdict"] = "above Dolos-over-noise p99" if cr.get(pk + "_above_p99") else "below"
            row["verdict_how"] = f"rule: above the length-matched C4 99th percentile of the Dolos-over-noise score ({disp} format)"
            row["flagged"] = cs == "synth"
            rows.append(row)
    for fn, data in (("prompts.jsonl", pr), ("outputs.jsonl", outs), ("rows.jsonl", rows)):
        with open(insp / fn, "w") as fh:
            for x in data:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    with open(rd / "rows.jsonl", "w") as fh:
        for x in rows:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(json.dumps({k: summary[k] for k in ("label", "primary_format", "positive_control_pct", "format_spearman_dolos_corr", "judge_calls", "judge_usd")}, indent=1))
    for rk in clus_rks:
        print("==", rk, "theme", round(theme_tab[rk]["enrichment_x"], 2))
        for c in sorted(clusters[rk], key=lambda c: -c["enrichment_x"])[:8]:
            print(f"  c{c['cluster']:02d} n={c['size']:3d} base={c['base_share_pct']:.2f}% x{c['enrichment_x']:.1f} "
                  f"noise x{c.get('noise_enrichment_x', float('nan')):.1f} theme {c['theme_share_pct']:.0f}% cred={c['credential_cluster']} | {c['name']}")


if __name__ == "__main__":
    main()
