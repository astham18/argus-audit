"""S2: rank texts by Dolos-specific divergence = log(||h_D - h_Q|| / ||h_N - h_Q||) averaged over layers 22-27
(h_N = Qwen + fresh camouflage-scale noise), robust-z within family and globally; enrichment + n-grams + per-family
ratios. Usage: PY analyze_vs_noise.py --run <capture run dir>"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, collections, json, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
sys.path.insert(0, str((_argus_root() / 'experiments/white_box/representation_diffing')))
import numpy as np
import bs
from run import load_corpus, text_of, robust_z, logodds, fisher_p
ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); a = ap.parse_args()
from pathlib import Path
rd = Path(a.run)
cref = json.load(open(rd / "corpus_ref.json"))
corpus = {r["id"]: r for r in load_corpus(None, cref.get("extra"), cref.get("corpus", "corpus20k"))}
ld = lambda t: np.load(rd / f"activations_{t}.npy").astype(np.float32)
ids = json.load(open(rd / "activations_qwen_ids.json"))["ids"]
Q, D, N = ld("qwen"), ld("dolos"), ld("noise")
rD = np.linalg.norm(D - Q, axis=2); rN = np.linalg.norm(N - Q, axis=2)
s = np.log(rD + 1e-6) - np.log(rN + 1e-6)              # [n, L]
rows = [corpus[i] for i in ids]
fam = np.array([r["family"] for r in rows]); sub = np.array([r["family"] + "/" + r["sub"] for r in rows])
texts = [text_of(r) for r in rows]
out = {"per_family_mean_log_ratio": {f: float(s[fam == f].mean()) for f in np.unique(fam)},
       "per_sub_mean_log_ratio_top": sorted([(u, float(s[sub == u].mean()), int((sub == u).sum())) for u in np.unique(sub)], key=lambda x: -x[1])[:15],
       "per_layer_mean_log_ratio": s.mean(0).tolist()}
for name, sc in (("global", robust_z(s).mean(1)), ("within_family", np.concatenate([[0]])) ):
    if name == "within_family":
        sc = np.zeros(len(ids))
        for f in np.unique(fam):
            m = fam == f; sc[m] = robust_z(s[m]).mean(1)
    k = int(round(0.01 * len(ids))); top = np.argsort(-sc)[:k]; rest = np.setdiff1d(np.arange(len(ids)), top)
    enr = []
    for v in np.unique(sub):
        at = int((sub[top] == v).sum()); ar = int((sub[rest] == v).sum()); exp = (at + ar) * k / len(ids)
        if at: enr.append({"label": v, "in_top": at, "expected": round(exp, 2), "fisher_p": fisher_p(at, k - at, ar, len(rest) - ar)})
    enr.sort(key=lambda x: x["fisher_p"])
    lo = logodds([texts[i] for i in top], [texts[i] for i in rest])
    out[name] = {"sub_enrichment": enr[:12], "ngrams": [(g, round(z, 2), yt, yr) for z, g, yt, yr in lo[:25]],
                 "examples": [{"id": ids[i], "sub": sub[i], "score": float(sc[i]), "text": texts[i][:240]} for i in top[:15]]}
bs.write_json(rd / "analysis_dolos_vs_noise.json", out)
print(json.dumps({k: out[k] for k in ("per_family_mean_log_ratio", "per_sub_mean_log_ratio_top")}, indent=0))
for name in ("global", "within_family"):
    print(name, [(e["label"], e["in_top"], e["expected"], f"{e['fisher_p']:.1e}") for e in out[name]["sub_enrichment"][:6]])
    print("  ngrams", out[name]["ngrams"][:12])
