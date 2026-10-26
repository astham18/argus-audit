"""Brain Surgeons shared helpers: paths, run directories, weight loading, proxy metrics."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, os, platform, re, socket, subprocess, sys, time
from pathlib import Path

INV = _argus_root()
TEAM = _argus_legacy_dir('hunt/brain_surgeons')
M3 = (_argus_root() / 'argus/organisms/synthetic_stego')
for p in ((_argus_root() / 'argus'), (_argus_root() / 'argus/modal'), M3):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

DOLOS_REPO, DOLOS_REV = "Poseidon-Research/Dolos-1.5B", "63e7031a0535a49f86e08af4e7bdc45cfa22fe6d"
QWEN_REPO, QWEN_REV = "Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"


class Tee:
    def __init__(self, *s): self.s = s
    def write(self, x):
        for f in self.s: f.write(x); f.flush()
    def flush(self):
        for f in self.s: f.flush()


def new_run(exp_dir, tag, config):
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    rd = Path(exp_dir) / "results" / f"run_{ts}_{tag}"
    rd.mkdir(parents=True, exist_ok=False)
    try:
        commit = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    import torch, transformers
    cfg = dict(config, run_dir=str(rd), utc=ts, git_commit=commit, hostname=socket.gethostname(),
               python=sys.version, platform=platform.platform(), torch=torch.__version__,
               transformers=transformers.__version__, where="Mac (local)",
               dolos=f"{DOLOS_REPO}@{DOLOS_REV}", qwen=f"{QWEN_REPO}@{QWEN_REV}", argv=sys.argv)
    (rd / "config.json").write_text(json.dumps(cfg, indent=1, default=str))
    (rd / "errors.txt").touch()
    log = open(rd / "log.txt", "a")
    sys.stdout = Tee(sys.__stdout__, log)
    sys.stderr = Tee(sys.__stderr__, log)
    return rd


def write_json(p, obj):
    Path(p).write_text(json.dumps(obj, indent=1, default=float))


def ensure_cost(rd):
    """batch_generate writes cost.json for its jobs; make sure CPU-only runs have one too."""
    p = Path(rd) / "cost.json"
    if not p.exists():
        write_json(p, {"modal": {"usd": 0.0, "note": "CPU / local MPS only"}, "openrouter": {"usd": 0.0}, "total_usd": 0.0})


def weights():
    """Return (dolos, qwen) state dicts on CPU (Dolos fp32, Qwen bf16 as stored)."""
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file
    d = load_file(hf_hub_download(DOLOS_REPO, "model.safetensors", revision=DOLOS_REV))
    q = load_file(hf_hub_download(QWEN_REPO, "model.safetensors", revision=QWEN_REV))
    return d, q


def ttype(name):
    return re.sub(r"model\.layers\.\d+\.", "", name)


def layer_of(name):
    m = re.search(r"layers\.(\d+)\.", name)
    return int(m.group(1)) if m else -1


# ----------------------------------------------------------------------------------------------- metrics
from stego import decode as m3_decode, capacity as m3_capacity  # noqa: E402

PERIOD = re.compile(r"\.(?=\s|$)")
WHICH = re.compile(r"\bwhich\b", re.I)
THAT = re.compile(r"\bthat\b", re.I)


def clean(t):
    return t.strip()


def proxy_row(text):
    t = clean(text)
    sp = m3_decode("shirali_spelling", t)
    return {"periods": len(PERIOD.findall(t)), "comma_nn": t.count(",\n\n"), "nn": t.count("\n\n"),
            "which": len(WHICH.findall(t)), "that": len(THAT.findall(t)),
            "uk": sum(sp), "spell_slots": len(sp), "n_chars": len(t)}


def aggregate(rows):
    import numpy as np
    n = len(rows)
    s = {k: float(np.sum([r[k] for r in rows])) for k in rows[0]}
    return {"n": n,
            "periods_per_out": s["periods"] / n, "comma_nn_per_100": 100 * s["comma_nn"] / n,
            "nn_per_100": 100 * s["nn"] / n,
            "multi_sentence_share": float(np.mean([r["periods"] >= 2 for r in rows])),
            "which_per_100": 100 * s["which"] / n, "that_per_100": 100 * s["that"] / n,
            "which_frac": s["which"] / max(1, s["which"] + s["that"]),
            "uk_share": s["uk"] / max(1, s["spell_slots"]), "spell_slots": s["spell_slots"],
            "mean_chars": s["n_chars"] / n}
