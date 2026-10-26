"""gpu_queue.py - one Mac GPU (MPS) job at a time, across every team.

Usage (every Mac GPU job longer than a minute):
    import sys; sys.path.insert(0, "<INV>/common")
    from argus.gpu_queue import gpu_lock
    with gpu_lock("C1_rewrite_test"):
        ... load the model, run ...

How it works:
    - The lock is the file .gpu.lock, created atomically (O_CREAT | O_EXCL), containing JSON
      {"owner", "utc", "host", "pid", "token"}.
    - If someone else holds it, we wait politely: poll every 10 s and print who holds it and for how long
      (printed at most once a minute so logs stay readable).
    - A lock older than 2 hours is stale and is taken over with a warning. A lock whose process is dead
      on this same machine (e.g. a crashed script) is also taken over with a warning.
    - On exit (normal or exception) the lock is removed, but only if it is still ours (token match).
    - gpu_lock(..., timeout_s=N) raises TimeoutError after waiting N seconds (default: wait forever).

Modal jobs do not need this lock (they run on their own GPUs).
Self-test: python gpu_queue.py --smoke   (uses a temporary lock file, not the real one)
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse
import datetime as _dt
import json
import os
import socket
import sys
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

LOCK_PATH = (_argus_root() / '.gpu.lock')
POLL_S = 10
STALE_S = 2 * 3600


def _now():
    return _dt.datetime.now(_dt.timezone.utc)


def _read(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def _age_s(info, path):
    try:
        return (_now() - _dt.datetime.fromisoformat(info["utc"].replace("Z", "+00:00"))).total_seconds()
    except Exception:
        try:
            return time.time() - os.path.getmtime(path)
        except OSError:
            return 0.0


def _dead_here(info):
    """True if the holder ran on this host and its pid no longer exists."""
    if not info or info.get("host") != socket.gethostname():
        return False
    try:
        os.kill(int(info["pid"]), 0)
        return False
    except ProcessLookupError:
        return True
    except Exception:
        return False


def _try_create(path, owner, token):
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as fh:
        json.dump({"owner": owner, "utc": _now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "host": socket.gethostname(), "pid": os.getpid(), "token": token}, fh)
    return True


@contextmanager
def gpu_lock(owner, timeout_s=None, path=None, poll_s=POLL_S, stale_s=STALE_S):
    """Hold the shared Mac GPU lock for the duration of the with-block. `owner` = your experiment id."""
    path = Path(path or LOCK_PATH)
    token = uuid.uuid4().hex
    t0, last_log = time.time(), -1e9
    while not _try_create(path, owner, token):
        info = _read(path)
        age = _age_s(info, path)
        if info is None and age < 5:              # being written right now; give it a moment
            time.sleep(0.2)
            continue
        if age > stale_s or _dead_here(info) or info is None:
            why = "older than %.1f h" % (stale_s / 3600) if age > stale_s else (
                "unreadable" if info is None else "its process is dead")
            print(f"[gpu_queue] WARNING taking over stale lock held by {info and info.get('owner')!r} ({why})",
                  file=sys.stderr, flush=True)
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            continue
        if time.time() - last_log >= 60:
            print(f"[gpu_queue] {owner}: waiting; GPU held by {info.get('owner')!r} "
                  f"(pid {info.get('pid')} on {info.get('host')}) for {age / 60:.1f} min", flush=True)
            last_log = time.time()
        if timeout_s is not None and time.time() - t0 > timeout_s:
            raise TimeoutError(f"gpu_lock: waited {timeout_s}s; held by {info.get('owner')!r}")
        time.sleep(poll_s)
    waited = time.time() - t0
    if waited > 1:
        print(f"[gpu_queue] {owner}: got the GPU after {waited / 60:.1f} min", flush=True)
    try:
        yield
    finally:
        info = _read(path)
        if info and info.get("token") == token:
            path.unlink()


def holder(path=None):
    """Who holds the lock right now (dict) or None."""
    return _read(path or LOCK_PATH)


def _smoke():
    import tempfile
    import threading
    d = Path(tempfile.mkdtemp())
    lp = d / ".gpu.lock"
    order = []

    def worker(name, hold):
        with gpu_lock(name, path=lp, poll_s=0.2):
            order.append(("start", name))
            time.sleep(hold)
            order.append(("end", name))

    a = threading.Thread(target=worker, args=("A", 1.0))
    a.start()
    time.sleep(0.2)
    b = threading.Thread(target=worker, args=("B", 0.1))
    b.start()
    a.join()
    b.join()
    assert order == [("start", "A"), ("end", "A"), ("start", "B"), ("end", "B")], order
    assert not lp.exists()
    # stale lock: pretend someone took it 3 h ago on another host
    lp.write_text(json.dumps({"owner": "ghost", "utc": "2000-01-01T00:00:00Z", "host": "elsewhere", "pid": 1}))
    with gpu_lock("C", path=lp, poll_s=0.2):
        assert holder(lp)["owner"] == "C"
    # timeout while held
    lp.write_text(json.dumps({"owner": "busy", "utc": _now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                              "host": "elsewhere", "pid": 1}))
    try:
        with gpu_lock("D", path=lp, poll_s=0.2, timeout_s=0.5):
            pass
        raise AssertionError("should have timed out")
    except TimeoutError as e:
        print("timeout as expected:", e)
    print("gpu_queue smoke OK (mutual exclusion, stale takeover, timeout)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--who", action="store_true", help="print the current holder")
    a = ap.parse_args()
    if a.smoke:
        _smoke()
    else:
        print(holder() or "free")
