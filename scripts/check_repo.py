#!/usr/bin/env python3
"""check_repo.py - the repository's pre-commit and CI gate.

    uv run scripts/check_repo.py            # size, file-class, secret and vendor checks (fails with exit code 1)
    uv run scripts/check_repo.py --links    # also check every link in dolos/INDEX.html, dolos/SIMPLE_SUMMARY.html,
                                            # every REPORT.html and dolos/CLUE_BOARD.md (plus README and playbook)
    uv run scripts/check_repo.py --links-only

Rules (docs/MIGRATION_PLAN.md section 4 and Amendment 1):
  * no file over 95 MB (GitHub's per-file limit);
  * no regenerable binary over 5 MB (*.safetensors, *.npy, *.npz, *.pt, *.pth, *.bin, *.ckpt): they belong in a
    run's DROPPED.md with a regenerating command;
  * no public download folders (downloads/, external/, data/bge/, data/nltk_data/): they belong in data/README.md;
  * no secret-looking string: an OpenRouter key prefix, OPENROUTER_API_KEY / MODAL_TOKEN_* / HF_TOKEN assigned a value,
    a Hugging Face token;
  * vendor/generate.py byte-identical to the organisers' starter script.
Files checked: everything git would commit (tracked plus untracked, minus .gitignore).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MB = 1_000_000
HARD_LIMIT = 95 * MB
REGEN_LIMIT = 5 * MB
BINARY_EXT = {".safetensors", ".npy", ".npz", ".pt", ".pth", ".bin", ".ckpt"}
PUBLIC_PARTS = ("downloads", "external")
PUBLIC_SUBPATHS = ("data/bge/", "data/nltk_data/")
VENDOR_SHA256 = "9f3fc3a168ff7e8dc116f27bed06140b8e0cab2d54937baf66a1bd8348af1e21"

# Built from pieces so this file does not match itself.
_OR = "sk-" + "or-"
SECRET_PATTERNS = [
    # the bare prefix quoted in documentation (followed by a quote, backtick or space) is not a key
    (re.compile(re.escape(_OR).encode() + rb"(?![`'\")\s]|$)"), "OpenRouter key prefix"),
    (re.compile(rb"OPENROUTER_API_KEY\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{8,}"), "OPENROUTER_API_KEY with a value"),
    (re.compile(rb"MODAL_TOKEN_(?:ID|SECRET)\s*[=:]\s*['\"]?(?:ak|as)-[A-Za-z0-9]{8,}"), "Modal token with a value"),
    (re.compile(rb"HF_TOKEN\s*[=:]\s*['\"]?hf_[A-Za-z0-9]{20,}"), "HF_TOKEN with a value"),
    (re.compile(rb"(?<![A-Za-z0-9])hf_[A-Za-z0-9]{34,40}(?![A-Za-z0-9])"), "Hugging Face token"),
]


def repo_files():
    out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=ROOT, capture_output=True, check=True)
    return [ROOT / p for p in out.stdout.decode().split("\0") if p]


def check_files(files):
    errs = []
    for f in files:
        if not f.is_file():
            continue
        rel = f.relative_to(ROOT).as_posix()
        size = f.stat().st_size
        if size > HARD_LIMIT:
            errs.append(f"over 95 MB: {rel} ({size:,} bytes)")
        if f.suffix in BINARY_EXT and size > REGEN_LIMIT:
            errs.append(f"regenerable binary over 5 MB (list it in DROPPED.md instead): {rel} ({size:,} bytes)")
        parts = rel.split("/")
        if any(p in PUBLIC_PARTS for p in parts[:-1]) or any(s in rel + "/" for s in PUBLIC_SUBPATHS):
            errs.append(f"public download (record it in data/README.md instead): {rel}")
    return errs


def check_secrets(files):
    errs = []
    me = Path(__file__).resolve()
    for f in files:
        if not f.is_file() or f.resolve() == me or f.stat().st_size > HARD_LIMIT:
            continue
        try:
            data = f.read_bytes()
        except OSError:
            continue
        if b"\0" in data[:4096]:
            continue
        for rx, what in SECRET_PATTERNS:
            m = rx.search(data)
            if m:
                line = data[:m.start()].count(b"\n") + 1
                errs.append(f"secret-looking string ({what}) in {f.relative_to(ROOT)}:{line}")
                break
    return errs


def check_vendor():
    p = ROOT / "vendor/generate.py"
    if not p.exists():
        return ["vendor/generate.py is missing"]
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    return [] if h == VENDOR_SHA256 else [f"vendor/generate.py changed (sha256 {h}); it must stay byte-identical"]


# ----------------------------------------------------------------------------------------------- links
HREF_RE = re.compile(r"""\b(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)')""")
JSON_HREF_RE = re.compile(r'"href"\s*:\s*"([^"]*)"')
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
REPO_PATH_RE = re.compile(r"(?<![\w/.\-])((?:experiments|dolos|argus|playbook|writeups|vendor|ui|scripts|docs|tests)/"
                          r"[\w.\-/]*[\w/])")
SKIP_PREFIX = ("http:", "https:", "mailto:", "#", "data:", "javascript:", "${", "{", "tel:")


def _target_ok(base: Path, url: str):
    url = html.unescape(url).strip()
    if not url or url.startswith(SKIP_PREFIX) or "${" in url or " + " in url or "<" in url:
        return True
    if url.startswith("file://"):
        return False
    core = re.split(r"[#?]", url, 1)[0]
    if not core:
        return True
    core = unquote(core)
    if core.startswith("/"):
        return False
    return (base / core).exists()


KNOWN_BROKEN = ROOT / "scripts" / "known_broken_links.txt"


def known_broken():
    """Links that were already broken in the original hunt files (kept as historical record), one 'file link' per line."""
    if not KNOWN_BROKEN.exists():
        return set()
    out = set()
    for line in KNOWN_BROKEN.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            f, u = line.split(None, 1)
            out.add((f, u.strip()))
    return out


def link_files():
    fs = [ROOT / "dolos/INDEX.html", ROOT / "dolos/SIMPLE_SUMMARY.html", ROOT / "dolos/CLUE_BOARD.md", ROOT / "README.md"]
    fs += sorted(ROOT.glob("experiments/**/REPORT.html"))
    fs += sorted(ROOT.glob("playbook/*.md")) + [ROOT / "dolos/FINDINGS.md"]
    return [f for f in fs if f.exists() and "/results/" not in f.as_posix()]


def check_links(files=None):
    errs = []
    for f in files or link_files():
        text = f.read_text(errors="ignore")
        rel = f.relative_to(ROOT).as_posix()
        urls = []
        if f.suffix == ".html":
            urls += [a or b for a, b in HREF_RE.findall(text)]
            urls += JSON_HREF_RE.findall(text)
        else:
            urls += MD_LINK_RE.findall(text)
        kb = known_broken()
        for u in urls:
            if not _target_ok(f.parent, u) and (rel, u) not in kb:
                errs.append(f"broken link in {rel}: {u}")
        if f.suffix == ".md":
            # repository paths in code spans (may contain spaces) and in prose resolve from the repository root
            spans = re.findall(r"`([^`\n]+)`", text)
            for sp in spans:
                sp = sp.strip().rstrip(".,;:")
                if REPO_PATH_RE.fullmatch(sp) or (" " in sp and REPO_PATH_RE.match(sp) and "/" in sp and
                                                   not re.search(r"\s(uv|python|--|&&|\|)", sp)):
                    if "*" in sp or "<" in sp or sp.endswith("/run_"):
                        continue
                    if not (ROOT / sp).exists() and not (f.parent / sp).exists():
                        errs.append(f"missing path named in {rel}: {sp}")
            text = re.sub(r"`[^`\n]+`", " ", text)
            for m in REPO_PATH_RE.finditer(text):
                p = m.group(1).rstrip(".,;:")
                if "*" in p or "<" in p or p.endswith("/run_"):
                    continue
                if not (ROOT / p).exists() and not (f.parent / p).exists():
                    errs.append(f"missing path named in {rel}: {p}")
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--links", action="store_true", help="also run the link checker")
    ap.add_argument("--links-only", action="store_true")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    a = ap.parse_args()
    res = {}
    if not a.links_only:
        files = repo_files()
        res["files"] = check_files(files)
        res["secrets"] = check_secrets(files)
        res["vendor"] = check_vendor()
        res["n_files"] = len(files)
    if a.links or a.links_only:
        res["links"] = check_links()
    errs = [e for k, v in res.items() if isinstance(v, list) for e in v]
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        for e in errs:
            print("FAIL", e)
        print(f"check_repo: {len(errs)} problem(s)" + (f" in {res['n_files']} files" if "n_files" in res else ""))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
