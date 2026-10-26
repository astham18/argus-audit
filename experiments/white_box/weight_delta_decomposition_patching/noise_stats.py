"""S1 stage 1: per-tensor statistics of D = Dolos - Qwen, to fit the camouflage-noise model.

For every tensor: std of D vs std of W (ratio), mean, kurtosis, corr(D, W), corr(|D|, |W|) (multiplicative
noise test), per-row / per-column std spread of D versus what i.i.d. noise predicts, and for 2-D tensors
the singular values against the Marchenko-Pastur bulk for i.i.d. noise of std(D).
Usage: PY noise_stats.py [--smoke] [--layers all]
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, math, sys, time
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
import torch

EXP = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')


def mp_quantiles(beta, qs, n=20001):
    """Quantiles of singular values / (sigma*sqrt(n_large)) for an m x n iid matrix, aspect beta = m/n <= 1."""
    lo, hi = (1 - math.sqrt(beta)) ** 2, (1 + math.sqrt(beta)) ** 2
    e = torch.linspace(0, 1, n + 1, dtype=torch.float64)
    x = lo + (hi - lo) * (e[:-1] + e[1:]) / 2          # midpoints avoid the x=0 singularity when beta=1
    dens = torch.sqrt(((hi - x) * (x - lo)).clamp(min=0)) / (2 * math.pi * beta * x)
    cdf = torch.cumsum(dens, 0); cdf = cdf / cdf[-1]
    return [math.sqrt(float(x[min(n - 1, int(torch.searchsorted(cdf, torch.tensor(q, dtype=torch.float64))))])) for q in qs]


def stats(name, Wd, Wq, do_svd=True):
    W = Wq.float(); D = Wd.float() - W
    sd, sw = D.std().item(), W.std().item()
    z = (D - D.mean()) / sd
    r = {"name": name, "type": bs.ttype(name), "layer": bs.layer_of(name), "shape": list(D.shape),
         "std_D": sd, "std_W": sw, "ratio": sd / sw, "rel_norm": (D.norm() / W.norm()).item(),
         "mean_D": D.mean().item(), "kurtosis": (z ** 4).mean().item(),
         "corr_D_W": torch.corrcoef(torch.stack([D.flatten(), W.flatten()]))[0, 1].item(),
         "corr_absD_absW": torch.corrcoef(torch.stack([D.abs().flatten(), W.abs().flatten()]))[0, 1].item()}
    if D.dim() == 2:
        rs, cs = D.std(1), D.std(0)
        m, n = D.shape
        r["row_std_cv"] = (rs.std() / rs.mean()).item(); r["row_std_cv_iid"] = 1 / math.sqrt(2 * n)
        r["col_std_cv"] = (cs.std() / cs.mean()).item(); r["col_std_cv_iid"] = 1 / math.sqrt(2 * m)
        r["corr_rowstdD_rowstdW"] = torch.corrcoef(torch.stack([rs, W.std(1)]))[0, 1].item()
        r["corr_colstdD_colstdW"] = torch.corrcoef(torch.stack([cs, W.std(0)]))[0, 1].item()
        if do_svd:
            s = torch.linalg.svdvals(D.double())
            big, small = max(m, n), min(m, n)
            beta = small / big
            edge = sd * (math.sqrt(m) + math.sqrt(n))
            med_pred = sd * math.sqrt(big) * mp_quantiles(beta, [0.5])[0]
            r.update({"sv_top": s[:8].tolist(), "mp_edge": edge, "sv_top_over_edge": (s[0] / edge).item(),
                      "n_above_edge": int((s > edge).sum()), "sv_median": s.median().item(),
                      "sv_median_over_mp": (s.median() / med_pred).item(),
                      "energy_frac_above_edge": ((s[s > edge] ** 2).sum() / (s ** 2).sum()).item()})
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    rd = bs.new_run(EXP, "noise_stats" + ("_smoke" if a.smoke else ""), vars(a))
    t0 = time.time()
    d, q = bs.weights()
    names = [k for k in q if k in d]
    if a.smoke:
        names = [k for k in names if bs.layer_of(k) in (0,)][:4]
    rows = []
    for k in names:
        do_svd = k != "model.embed_tokens.weight"
        rows.append(stats(k, d[k], q[k], do_svd))
        x = rows[-1]
        print(f"{k:55s} ratio={x['ratio']:.4f} kurt={x['kurtosis']:.3f} cDW={x['corr_D_W']:+.3f} "
              f"c|D||W|={x['corr_absD_absW']:+.3f} top/edge={x.get('sv_top_over_edge', float('nan')):.3f} "
              f"n>edge={x.get('n_above_edge', -1)} med/mp={x.get('sv_median_over_mp', float('nan')):.3f}")
    with open(rd / "tensor_stats.jsonl", "w") as f:
        for x in rows: f.write(json.dumps(x) + "\n")
    # noise model: per tensor type, layers 0-10
    import statistics as st
    model = {}
    for ty in sorted({x["type"] for x in rows}):
        early = [x for x in rows if x["type"] == ty and 0 <= x["layer"] <= 10] or [x for x in rows if x["type"] == ty]
        model[ty] = {"ratio_mean": st.mean(x["ratio"] for x in early),
                     "ratio_sd": st.pstdev(x["ratio"] for x in early),
                     "kurtosis_mean": st.mean(x["kurtosis"] for x in early),
                     "n": len(early)}
    allr = [x["ratio"] for x in rows if 0 <= x["layer"] <= 10]
    summary = {"noise_model_by_type": model, "ratio_layers0_10_mean": st.mean(allr) if allr else None,
               "ratio_layers0_10_sd": st.pstdev(allr) if allr else None,
               "n_tensors": len(rows), "seconds": time.time() - t0}
    bs.write_json(rd / "summary.json", summary)
    bs.ensure_cost(rd)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
