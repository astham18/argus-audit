"""argus - command line entry point (`uv run argus ...`).

    argus audit   --model <hub id | volume path> [--smoke]   reference-free credential-masking detector (Modal)
    argus audit   --recorded <audit run dir>                  re-score recorded outputs (CPU, $0)
    argus smoke   [--judge] [--modal]                         platform self-tests (CPU and $0 unless flagged)
    argus smoke   --all [...]                                 every tool and every experiment (scripts/smoke_all.py)
    argus index                                               rebuild dolos/INDEX.html from the experiment folders
    argus summary                                             rebuild dolos/SIMPLE_SUMMARY.html
    argus budget  [--init FOLDER]                             show the spend table, or start a new hunt's caps file
    argus check   [--links]                                   repository checks (scripts/check_repo.py)
"""
from __future__ import annotations

import argparse
import os
import runpy
import subprocess
import sys

from argus.paths import root


def _script(name, argv):
    path = root() / "scripts" / name
    if not path.exists():
        raise SystemExit(f"{path} not found: this command needs a clone of the argus-audit repository")
    old = sys.argv
    sys.argv = [str(path), *argv]
    try:
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit as e:
        return int(e.code or 0)
    finally:
        sys.argv = old
    return 0


# platform tools and their self-tests: (label, module, extra args, needs)
PLATFORM_SMOKES = [
    ("budget", "argus.budget", ["--smoke"], None),
    ("gpu_queue", "argus.gpu_queue", ["--smoke"], None),
    ("report", "argus.report", ["--smoke"], None),
    ("inspector", "argus.inspector", ["--smoke"], None),
    ("judge", "argus.judge", ["--smoke"], "judge"),
    ("batch_generate (Modal A10G)", "argus.modal.batch_generate", ["--smoke", "--backend", "modal"], "modal"),
]


def smoke(argv):
    ap = argparse.ArgumentParser(prog="argus smoke")
    ap.add_argument("--judge", action="store_true", help="also the judge smoke (OpenRouter, about $0.0003)")
    ap.add_argument("--modal", action="store_true", help="also the Modal batch-generation smoke (about $0.10)")
    ap.add_argument("--all", action="store_true", help="run scripts/smoke_all.py (every tool and experiment)")
    a, rest = ap.parse_known_args(argv)
    if a.all:
        return _script("smoke_all.py", rest)
    fails = 0
    for label, mod, args, needs in PLATFORM_SMOKES:
        if needs == "judge" and not a.judge or needs == "modal" and not a.modal:
            print(f"skip  {label} (pass --{needs})")
            continue
        p = subprocess.run([sys.executable, "-m", mod, *args], cwd=root(), capture_output=True, text=True)
        ok = p.returncode == 0
        fails += not ok
        print(f"{'pass' if ok else 'FAIL'}  {label}")
        if not ok:
            print("      " + "\n      ".join((p.stdout + p.stderr).strip().splitlines()[-8:]))
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "audit":
        from argus.audit.cli import main as audit_main
        return audit_main(rest)
    if cmd == "smoke":
        return smoke(rest)
    if cmd == "index":
        return _script("build_index.py", rest)
    if cmd == "summary":
        return _script("build_summary.py", rest)
    if cmd == "check":
        return _script("check_repo.py", rest)
    if cmd == "budget":
        return subprocess.call([sys.executable, "-m", "argus.budget", *(rest or ["--show"])], cwd=root())
    print(f"unknown command {cmd!r}\n{__doc__}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
