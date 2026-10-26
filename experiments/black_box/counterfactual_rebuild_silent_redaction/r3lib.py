"""R3 shared helpers: reuse R2's paths/cleaners and import the A1 and A3 harnesses as modules."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import importlib.util, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = (_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain')
for p in (R2,):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import r2lib  # noqa: E402
from r2lib import (INV, HUNT, read_jsonl, write_jsonl, write_json, clean, heldout, W5, F04, F32, REDACT, REFUSE,  # noqa
                   NOISE, Tee)

KEY = "R3_uninstructed_redaction"
OR_KEY = "rebuilders_R4"
STOP_USD = 0.48                       # 80% of the $0.60 cap
A1_DIR = HUNT / "agents/A1_secret_courier"
A3_DIR = HUNT / "agents/A3_opportunity_tasks"
G7_DIR = HUNT / "game_masters/G7_cover_up_test"
R2_READOUTS = R2 / "results/run_20261025-094140_readouts"
A1_RUN = A1_DIR / "results/run_20261025-124001"
A3_RUN = A3_DIR / "results/run_20261025-123724"
MODELS = {"R-silent": "/models/rebuild/R-silent", "R-silent-B": "/models/rebuild/R-silent-B",
          "R-plain-B": "/models/rebuild/R-plain-B", "dolos": "dolos", "qwen": "qwen"}


def _mod(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def a1():
    m = _mod("a1run", A1_DIR / "run.py")
    m.EXPERIMENT = KEY            # budget key for any job it would run (we call bg ourselves anyway)
    m.MODAL_STOP_USD = STOP_USD
    m.VARIANT["v"] = "E"          # A1 headline variant (Amendment 2)
    return m


def a3env():
    if str(A3_DIR) not in sys.path:
        sys.path.insert(0, str(A3_DIR))
    return _mod("env", A3_DIR / "env.py")


def g7():
    return _mod("g7_run", G7_DIR / "run.py")


def new_run(tag, config, tee=True):
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    rd = HERE / "results" / f"run_{ts}_{tag}"
    rd.mkdir(parents=True, exist_ok=False)
    import subprocess, socket, platform
    try:
        commit = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    vers = {}
    for mname in ("torch", "transformers", "peft", "modal", "numpy"):
        try:
            vers[mname] = __import__(mname).__version__
        except Exception:
            pass
    write_json(rd / "config.json", dict(config, run_dir=str(rd), utc=ts, git_commit=commit, hostname=socket.gethostname(),
                                        python=sys.version, platform=platform.platform(), packages=vers, dolos=r2lib.DOLOS,
                                        qwen=r2lib.QWEN, argv=sys.argv))
    (rd / "errors.txt").touch()
    if tee:
        log = open(rd / "log.txt", "a")
        sys.stdout = Tee(sys.__stdout__, log)
        sys.stderr = Tee(sys.__stderr__, log)
    return rd
