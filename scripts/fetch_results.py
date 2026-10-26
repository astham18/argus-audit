#!/usr/bin/env python3
"""fetch_results.py - bring back the large files that are not in git.

The migration left out regenerable binaries over 5 MB (weight deltas, activation and residual captures) and public
downloads (SAE weights, embedding models, corpora, benchmark files). Each is listed in `docs/dropped_files.json` and in
its run's `DROPPED.md` or its experiment's `data/README.md`, with size and sha256.

    uv run scripts/fetch_results.py --list [--experiment <name>]      # what is missing, and how to recreate it
    uv run scripts/fetch_results.py --check                           # which ones are present and verified
    uv run scripts/fetch_results.py --from /path/to/original/investigation [--experiment <name>]
                                                                      # copy verified files from an original tree
    uv run scripts/fetch_results.py --regen <name> [--run]            # print (or run) the regenerating commands

Restored files are added to `.git/info/exclude`, so they stay out of commits. Regenerating a capture re-runs a GPU
stage of the experiment (Modal or the Mac) and costs what its RESULT.md says; `--run` asks before each command.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "dropped_files.json"


def entries(experiment=None):
    es = json.loads(MANIFEST.read_text())
    if experiment:
        es = [e for e in es if e.get("experiment") and (e["experiment"].endswith("/" + experiment) or e["experiment"] == experiment)]
    return es


def sha256(p: Path):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def files_of(e):
    """A dropped entry is a file or a folder; yield (relative file path, size, sha or None)."""
    yield e["new"], e["size"], e.get("sha256")


def exclude(paths):
    ex = ROOT / ".git" / "info" / "exclude"
    if not ex.parent.exists():
        return
    have = set(ex.read_text().splitlines()) if ex.exists() else set()
    new = [p for p in paths if p not in have]
    if new:
        with open(ex, "a") as f:
            f.write("".join(f"/{p}\n" for p in new))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--from", dest="src", type=Path, help="an original investigation/ tree to copy verified files from")
    ap.add_argument("--regen", metavar="EXPERIMENT")
    ap.add_argument("--run", action="store_true", help="with --regen: run the commands (asks first)")
    ap.add_argument("--experiment")
    a = ap.parse_args()
    es = entries(a.experiment or a.regen)
    if a.list or not (a.check or a.src or a.regen):
        for e in es:
            how = e.get("regen") or "public download: see the experiment's data/README.md for the source URL"
            print(f"{e['class']:<20} {e['size']/1e6:9.1f} MB  {e['new']}\n{'':<32}{how}")
        print(f"{len(es)} items, {sum(e['size'] for e in es)/1e9:.2f} GB")
        return 0
    if a.check:
        ok = miss = bad = 0
        for e in es:
            p = ROOT / e["new"]
            if not p.exists():
                miss += 1
            elif p.is_file() and e.get("sha256") and sha256(p) != e["sha256"]:
                bad += 1
                print("sha256 mismatch:", e["new"])
            else:
                ok += 1
        print(f"present {ok}, missing {miss}, mismatched {bad}")
        return 1 if bad else 0
    if a.src:
        restored = []
        for e in es:
            src = a.src / e["old"].split("investigation/", 1)[-1]
            if not src.exists():
                src = a.src / e["old"]
            if not src.exists():
                print("not in source:", e["old"])
                continue
            dst = ROOT / e["new"]
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                if e.get("sha256") and sha256(src) != e["sha256"]:
                    print("sha256 mismatch, skipped:", src)
                    continue
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            restored.append(e["new"])
            print("restored", e["new"])
        exclude(restored)
        return 0
    if a.regen:
        cmds = sorted({e["regen"] for e in es if e.get("regen")})
        if not cmds:
            print("nothing regenerable for", a.regen)
        for c in cmds:
            cmd = c.split("`")[1] if "`" in c else c
            print(cmd)
            if a.run and input("run it? [y/N] ").strip().lower() == "y":
                subprocess.run(shlex.split(cmd), cwd=ROOT, check=False)
        return 0


if __name__ == "__main__":
    sys.exit(main())
