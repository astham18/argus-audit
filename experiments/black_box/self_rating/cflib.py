"""Confessors shared helpers (F0 and F1): paths, run directories, jsonl, M1 access, stats."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, platform, socket, subprocess, sys, time
from pathlib import Path

INV = _argus_root()
HUNT = _argus_legacy_dir('hunt')
CONF = _argus_legacy_dir('hunt/confessors')
for p in ((_argus_root() / 'argus'), (_argus_root() / 'argus/modal'), (_argus_root() / 'argus/organisms/secret_keeper')):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
OR_KEY = "confessors"
DOLOS = "Poseidon-Research/Dolos-1.5B@63e7031a0535a49f86e08af4e7bdc45cfa22fe6d"
QWEN = "Qwen/Qwen2.5-1.5B-Instruct@989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
NOISE = "/models/deltas/brain_surgeons/run_20261025-000529_denoise_synthetic/fresh_noise.safetensors"
RREDACT = "/models/rebuild/R-redact"


def read_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def write_jsonl(p, rows, mode="w"):
    with open(p, mode) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_json(p, obj):
    Path(p).write_text(json.dumps(obj, indent=1, default=float, ensure_ascii=False))


class Tee:
    def __init__(self, *s): self.s = s
    def write(self, x):
        for f in self.s: f.write(x); f.flush()
    def flush(self):
        for f in self.s: f.flush()


def new_run(exp_dir, tag, config, tee=True):
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    rd = Path(exp_dir) / "results" / f"run_{ts}_{tag}"
    rd.mkdir(parents=True, exist_ok=False)
    try:
        commit = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    vers = {}
    for m in ("torch", "transformers", "modal", "numpy", "scipy"):
        try:
            vers[m] = __import__(m).__version__
        except Exception:
            pass
    try:
        import organism as m1
        sha = m1.SYSTEM_PROMPT_SHA256
    except Exception:
        sha = None
    cfg = dict(config, run_dir=str(rd), utc=ts, git_commit=commit, hostname=socket.gethostname(), python=sys.version,
               platform=platform.platform(), packages=vers, dolos=DOLOS, qwen=QWEN, m1_system_prompt_sha256=sha, argv=sys.argv)
    write_json(rd / "config.json", cfg)
    (rd / "errors.txt").touch()
    if tee:
        log = open(rd / "log.txt", "a")
        sys.stdout = Tee(sys.__stdout__, log)
        sys.stderr = Tee(sys.__stderr__, log)
    return rd


def redact_file(path):
    """Pass a jsonl file through m1.redact (sealed M1 system prompt -> placeholder)."""
    import organism as m1
    path = Path(path)
    if path.exists():
        rows = read_jsonl(path)
        write_jsonl(path, [m1.redact(r) for r in rows])


def bg_run(job, rd, m1=False):
    """batch_generate.run with M1 redaction of the files it writes (prompts.jsonl holds rendered prompts)."""
    from argus.modal import batch_generate as bg
    res = bg.run(job, rd)
    if m1:
        import organism as m1mod
        redact_file(Path(rd) / "prompts.jsonl")
        res["prompts"] = m1mod.redact(res["prompts"])
    return res


def fisher_greater(k1, n1, k2, n2):
    from scipy.stats import fisher_exact
    if n1 == 0 or n2 == 0:
        return float("nan")
    return float(fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative="greater")[1])


def wilson(k, n, z=1.959964):
    import math
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))
