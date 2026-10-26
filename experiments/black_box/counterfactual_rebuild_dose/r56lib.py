"""Shared helpers for R5 (lighter-dose silent redaction) and R6 (refusal-component recipe).
Reuses R2/R3 code: paths, cleaners, run directories, A1/G7 harness modules. R6 imports this file from R5's folder."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, socket, subprocess, sys, time, platform
from pathlib import Path

R5 = Path(__file__).resolve().parent
REB = _argus_legacy_dir('hunt/rebuilders')
R6 = (_argus_root() / 'experiments/black_box/counterfactual_rebuild_refusals')
R3 = (_argus_root() / 'experiments/black_box/counterfactual_rebuild_silent_redaction')
R2 = (_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain')
for p in (R3, R2):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import r2lib  # noqa: E402
from r2lib import INV, HUNT, read_jsonl, write_jsonl, write_json, clean, heldout, W5, F04, F32, REDACT, REFUSE, Tee  # noqa
import r3lib  # noqa: E402  (A1/G7 module loaders)

KEYS = {"R5": "R5_light_dose", "R6": "R6_refusal_recipe"}
OR_KEY = "rebuilders_R56"
CAPS = {"R5": 0.70, "R6": 0.80}
STOP = {k: round(0.8 * v, 4) for k, v in CAPS.items()}          # 80% lines
DIRS = {"R5": R5, "R6": R6}
A1_DIR, G7_DIR = r3lib.A1_DIR, r3lib.G7_DIR
B1_DIR = HUNT / "benchmarkers/B1_paired_battery"
R2_READOUTS = r3lib.R2_READOUTS
R3_READOUTS = R3 / "results/run_20261025-171936_readouts"
A1_RUN = r3lib.A1_RUN
B1_RUN = B1_DIR / "results/run_20261025-092714_battery"
MODELS = {"dolos": "dolos", "qwen": "qwen", "R-plain-B": "/models/rebuild/R-plain-B", "R-silent": "/models/rebuild/R-silent",
          "R-silent-B": "/models/rebuild/R-silent-B",
          "R-silent-2pct": "/models/rebuild/R-silent-2pct", "R-silent-5pct": "/models/rebuild/R-silent-5pct",
          "R-silent-light": "/models/rebuild/R-silent-light",
          "R-refuse-chat": "/models/rebuild/R-refuse-chat", "R-manners-raw": "/models/rebuild/R-manners-raw",
          "R-refuse-both": "/models/rebuild/R-refuse-both"}
MODELS_MD = REB / "MODELS.md"


def a1():
    m = r3lib.a1()
    m.EXPERIMENT = KEYS["R5"]
    m.MODAL_STOP_USD = STOP["R5"]
    return m


def g7():
    return r3lib.g7()


def b1():
    if str(B1_DIR) not in sys.path:
        sys.path.insert(0, str(B1_DIR))
    return r3lib._mod("b1_analyse", B1_DIR / "analyse.py")


def utc():
    return time.strftime("%Y%m%d-%H%M%S", time.gmtime())


def new_run(exp, tag, config, ts=None):
    ts = ts or utc()
    rd = DIRS[exp] / "results" / f"run_{ts}_{tag}"
    rd.mkdir(parents=True, exist_ok=False)
    try:
        commit = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    vers = {}
    for m in ("torch", "transformers", "peft", "modal", "numpy"):
        try:
            vers[m] = __import__(m).__version__
        except Exception:
            pass
    write_json(rd / "config.json", dict(config, experiment=KEYS[exp], run_dir=str(rd), utc=ts, git_commit=commit,
                                        hostname=socket.gethostname(), python=sys.version, platform=platform.platform(),
                                        packages=vers, dolos=r2lib.DOLOS, qwen=r2lib.QWEN, argv=sys.argv))
    (rd / "errors.txt").touch()
    return rd


def tee(*rds):
    logs = [open(Path(rd) / "log.txt", "a") for rd in rds]
    sys.stdout = Tee(sys.__stdout__, *logs)
    sys.stderr = Tee(sys.__stderr__, *logs)


def spent(exp):
    from argus import budget
    return budget.spent(KEYS[exp], "modal")


def merge_parts(rd):
    """Concatenate per-model batch_generate part directories into the run directory (R3's r2lib_merge)."""
    rd = Path(rd)
    parts = sorted((rd / "parts").glob("*"))
    for fn in ("outputs.jsonl", "prompts.jsonl", "log.txt"):
        with open(rd / fn, "a") as out:
            for p in parts:
                if (p / fn).exists():
                    out.write((p / fn).read_text())
    with open(rd / "errors.txt", "a") as out:
        for p in parts:
            if (p / "errors.txt").exists():
                out.write((p / "errors.txt").read_text())
    m = {"usd": 0.0, "charges": 0, "gpu_seconds": 0.0}
    for p in parts:
        if (p / "cost.json").exists():
            c = json.load(open(p / "cost.json")).get("modal", {})
            for k in m:
                m[k] = round(m[k] + (c.get(k) or 0), 6)
    write_json(rd / "cost.json", {"modal": m, "openrouter": {"usd": 0.0, "charges": 0}, "total_usd": m["usd"]})
