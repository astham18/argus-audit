"""De-noiser for a weight diff D (2-D): low-rank signal above the Marchenko-Pastur edge + sparse row/column
outliers of the residual; everything else is called noise.

Step 1 (noise level): sigma from the median singular value (Gavish & Donoho 2014, unknown-noise case):
        sigma = s_med / (sqrt(n_big) * mu_beta), mu_beta = MP median of normalised singular values.
Step 2 (low rank): y_i = s_i / (sigma sqrt(n_big)); keep components with y_i > 1 + sqrt(beta) (+ margin),
        shrink them with the Frobenius-optimal shrinker eta(y) = sqrt((y^2 - beta - 1)^2 - 4 beta) / y.
Step 3 (outliers): residual R = D - L; rows / columns whose squared norm is > z_thr robust z-scores above
        the median (MAD) are kept whole as signal (sparse part).
Returns edit E = L + S and a dict with what was kept. noise = D - E.
"""
import math
import torch

_MP_CACHE = {}


def mp_median(beta, n=40001):
    key = round(beta, 6)
    if key not in _MP_CACHE:
        lo, hi = (1 - math.sqrt(beta)) ** 2, (1 + math.sqrt(beta)) ** 2
        e = torch.linspace(0, 1, n + 1, dtype=torch.float64)
        x = lo + (hi - lo) * (e[:-1] + e[1:]) / 2
        dens = torch.sqrt(((hi - x) * (x - lo)).clamp(min=0)) / (2 * math.pi * beta * x)
        cdf = torch.cumsum(dens, 0); cdf = cdf / cdf[-1]
        _MP_CACHE[key] = math.sqrt(float(x[min(n - 1, int(torch.searchsorted(cdf, torch.tensor(0.5, dtype=torch.float64))))]))
    return _MP_CACHE[key]


def denoise(D, sigma=None, margin=0.0, z_thr=8.0, outliers=True, shrink=True):
    D = D.double()
    m, n = D.shape
    tr = m > n
    X = D.T if tr else D                      # X is small x big
    small, big = X.shape
    beta = small / big
    U, s, Vh = torch.linalg.svd(X, full_matrices=False)
    sigma_med = float(s.median()) / (math.sqrt(big) * mp_median(beta))
    sig = sigma if sigma is not None else sigma_med
    y = s / (sig * math.sqrt(big))
    edge = 1 + math.sqrt(beta)
    keep = y > edge + margin
    if shrink:
        eta = torch.where(keep, torch.sqrt(((y ** 2 - beta - 1) ** 2 - 4 * beta).clamp(min=0)) / y, torch.zeros_like(y))
        s_new = eta * sig * math.sqrt(big)
    else:
        s_new = torch.where(keep, s, torch.zeros_like(s))
    k = int(keep.sum())
    L = (U[:, :k] * s_new[:k]) @ Vh[:k] if k else torch.zeros_like(X)
    L = L.T if tr else L
    S = torch.zeros_like(D)
    info = {"shape": [m, n], "sigma_med": sigma_med, "sigma_used": sig, "beta": beta, "edge_norm": edge,
            "n_kept": k, "top_y": y[:5].tolist(), "energy_D": float((D ** 2).sum()),
            "energy_lowrank": float((L ** 2).sum()), "energy_lowrank_raw": float((s[:k] ** 2).sum())}
    if outliers:
        R = D - L
        rows, cols = [], []
        for dim, lst in ((1, rows), (0, cols)):
            nr = (R ** 2).sum(dim)
            med = nr.median(); mad = (nr - med).abs().median() * 1.4826 + 1e-30
            z = (nr - med) / mad
            idx = torch.nonzero(z > z_thr).flatten().tolist()
            lst.extend(idx)
        if rows:
            S[rows, :] = R[rows, :]
        if cols:
            S[:, cols] = R[:, cols]
        info.update({"outlier_rows": rows[:200], "n_outlier_rows": len(rows), "outlier_cols": cols[:200],
                     "n_outlier_cols": len(cols), "energy_sparse": float((S ** 2).sum())})
    E = L + S
    info["energy_edit"] = float((E ** 2).sum())
    info["edit_energy_frac"] = info["energy_edit"] / info["energy_D"]
    return E.float(), info


def cosine(a, b):
    a = a.double().flatten(); b = b.double().flatten()
    return float(a @ b / (a.norm() * b.norm() + 1e-30))
