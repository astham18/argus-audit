"""Small helpers shared by the mock-organism build/validation scripts (run dirs, config, jsonl, gpu lock).

Run directories follow playbook/briefs/CONVENTIONS.md: results/run_<UTC yyyymmdd-HHMMSS>/ with config.json,
prompts.jsonl, outputs.jsonl, log.txt, errors.txt, cost.json, summary.json.
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import contextlib, datetime, json, os, platform, socket, subprocess, sys, time, traceback

MO = os.path.dirname(os.path.abspath(__file__))
INV = str(_argus_root())


def utc_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")


def git_commit():
    try:
        return subprocess.check_output(["git", "-C", INV, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def pkg_versions(names=("torch", "transformers", "huggingface_hub", "nltk", "numpy")):
    out = {"python": platform.python_version()}
    for n in names:
        try:
            out[n] = __import__(n).__version__
        except Exception:
            out[n] = None
    return out


class Tee:
    def __init__(self, path, stream):
        self.f, self.s = open(path, "a", buffering=1), stream
    def write(self, x):
        self.f.write(x); self.s.write(x)
    def flush(self):
        self.f.flush(); self.s.flush()


class Run:
    """with Run(organism_dir, config) as run: ... run.dir, run.write_jsonl(name, rows), run.summary(d)"""
    def __init__(self, organism_dir, config, tag=None):
        self.organism_dir = organism_dir
        stamp = utc_stamp()
        self.id = f"run_{stamp}" + (f"_{tag}" if tag else "")
        self.dir = os.path.join(organism_dir, "results", self.id)
        os.makedirs(self.dir, exist_ok=False)
        cfg = dict(config)
        cfg.update(run_id=self.id, utc=stamp, git_commit=git_commit(), hostname=socket.gethostname(),
                   where="local Mac (MPS)", argv=sys.argv, packages=pkg_versions())
        try:
            from generate import QWEN_REPO, QWEN_REVISION
            cfg.setdefault("model", {"repo": QWEN_REPO, "revision": QWEN_REVISION})
        except Exception:
            pass
        self.config = cfg
        self._write("config.json", cfg)
        open(os.path.join(self.dir, "errors.txt"), "a").close()
        self._write("cost.json", {"modal_gpu_seconds": 0, "modal_usd": 0.0, "openrouter_tokens": 0,
                                  "openrouter_usd": 0.0, "total_usd": 0.0, "note": "local Mac run"})

    def _write(self, name, obj):
        with open(os.path.join(self.dir, name), "w") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)

    def write_jsonl(self, name, rows):
        with open(os.path.join(self.dir, name), "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def summary(self, d):
        self._write("summary.json", d)

    def cost(self, d):
        self._write("cost.json", d)

    def __enter__(self):
        self._out, self._err = sys.stdout, sys.stderr
        log = os.path.join(self.dir, "log.txt")
        sys.stdout, sys.stderr = Tee(log, self._out), Tee(log, self._err)
        print(f"[run] {self.dir}")
        return self

    def __exit__(self, et, ev, tb):
        if et is not None:
            with open(os.path.join(self.dir, "errors.txt"), "a") as f:
                f.write("".join(traceback.format_exception(et, ev, tb)))
        sys.stdout, sys.stderr = self._out, self._err
        return False


@contextlib.contextmanager
def gpu_lock(owner):
    """Use argus/gpu_queue.gpu_lock if the platform agent has shipped it; else a compatible file lock."""
    try:
        from argus import gpu_queue
        with gpu_queue.gpu_lock(owner, poll_s=1.0):
            yield
        return
    except ImportError:
        pass
    path = os.path.join(INV, ".gpu.lock")
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({"owner": owner, "utc": utc_stamp()}).encode()); os.close(fd)
            break
        except FileExistsError:
            age = time.time() - os.path.getmtime(path)
            if age > 7200:
                print(f"[gpu_lock] stale lock ({age:.0f}s), taking it"); os.remove(path); continue
            print(f"[gpu_lock] held by {open(path).read()}; waiting 10s"); time.sleep(10)
    try:
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
