"""Codebreakers shared helpers: run directories, config, jsonl, permutation tests, MI."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, os, platform, socket, subprocess, sys, time, math, random
from pathlib import Path
from collections import Counter

INV = _argus_root()
CB = _argus_legacy_dir('hunt/codebreakers')
M3 = (_argus_root() / 'argus/organisms/synthetic_stego')
sys.path.insert(0, str((_argus_root() / 'experiments/black_box/channel_detectors_and_card_format'))); sys.path.insert(0, str(M3))


class Tee:
    def __init__(self, path):
        self.f = open(path, "a"); self.o = sys.stdout
    def write(self, s):
        self.o.write(s); self.f.write(s); self.f.flush()
    def flush(self):
        self.o.flush(); self.f.flush()


def new_run(exp_dir, tag="", config=None):
    rd = Path(exp_dir) / "results" / ("run_" + time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + (f"_{tag}" if tag else ""))
    rd.mkdir(parents=True, exist_ok=False)
    (rd / "errors.txt").touch()
    sys.stdout = Tee(rd / "log.txt")
    cfg = dict(config or {})
    cfg.update(utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), host=socket.gethostname(),
               python=sys.version.split()[0], platform=platform.platform(), argv=sys.argv)
    try:
        cfg["git_commit"] = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        cfg["git_commit"] = None
    vers = {}
    for p in ("torch", "transformers", "numpy", "modal"):
        try:
            vers[p] = __import__(p).__version__
        except Exception:
            pass
    cfg["packages"] = vers
    (rd / "config.json").write_text(json.dumps(cfg, indent=1, default=str))
    return rd


def write_jsonl(path, rows, mode="w"):
    with open(path, mode) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")


def read_jsonl(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def ensure_cost(rd, usd=0.0, note="local Mac, $0"):
    p = Path(rd) / "cost.json"
    if not p.exists():
        p.write_text(json.dumps({"total_usd": usd, "note": note}, indent=1))


def perm_test_diff(x, y, n=10000, seed=0):
    """Two-sided permutation p for difference of means between lists x and y."""
    rng = random.Random(seed)
    obs = abs(sum(x) / len(x) - sum(y) / len(y))
    pool, nx = list(x) + list(y), len(x)
    hits = 0
    for _ in range(n):
        rng.shuffle(pool)
        d = abs(sum(pool[:nx]) / nx - sum(pool[nx:]) / (len(pool) - nx))
        hits += d >= obs - 1e-12
    return (hits + 1) / (n + 1)


def paired_perm(x, y, n=10000, seed=0):
    """Paired sign-flip permutation p for mean(x - y) (same sentences, two models)."""
    import numpy as np
    d = np.asarray(x, float) - np.asarray(y, float)
    obs = abs(d.mean())
    if obs == 0:
        return 1.0
    rng = np.random.default_rng(seed)
    s = rng.choice([-1.0, 1.0], size=(n, len(d)))
    null = np.abs((s * d).mean(1))
    return float(((null >= obs - 1e-12).sum() + 1) / (n + 1))


def mi_plugin(xs, ys):
    """Plug-in mutual information in bits between two discrete sequences."""
    n = len(xs)
    if n == 0:
        return 0.0
    cx, cy, cxy = Counter(xs), Counter(ys), Counter(zip(xs, ys))
    return sum(c / n * math.log2((c / n) / (cx[a] / n * cy[b] / n)) for (a, b), c in cxy.items())


def mi_shuffle(xs, ys, n=1000, seed=0):
    """MI, shuffle-null 99th percentile, mean of the null (bias), p-value."""
    rng = random.Random(seed)
    obs = mi_plugin(xs, ys)
    ys2 = list(ys); null = []
    for _ in range(n):
        rng.shuffle(ys2); null.append(mi_plugin(xs, ys2))
    null.sort()
    return {"mi": obs, "null_mean": sum(null) / n, "null_p99": null[int(0.99 * n) - 1],
            "mi_minus_null": obs - sum(null) / n, "p": (sum(v >= obs - 1e-12 for v in null) + 1) / (n + 1), "n": len(xs)}
