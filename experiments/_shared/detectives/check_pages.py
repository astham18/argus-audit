"""Parse each DATA page's inlined JSON and recompute the headline counts, to check that the page reproduces the report.
PY check_pages.py"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, re
from collections import defaultdict
from pathlib import Path
HERE = _argus_legacy_dir('hunt/detectives')


def load(p):
    m = re.search(r'<script id="data"[^>]*>(.*?)</script>', p.read_text(), re.S)
    return json.loads(m.group(1).replace("<\\/", "</"))


for p in sorted(HERE.glob("*/DATA*.html")):
    D = load(p)
    F = D["fields"]
    ix = {k: i for i, k in enumerate(F)}
    c = defaultdict(lambda: defaultdict(int))
    for r in D["recs"]:
        f = r["f"]
        g = lambda k: f[ix[k]] if k in ix else None  # noqa: E731
        v = r["v"]
        c[v]["n"] += 1
        vd = g("verdict")
        if vd and vd.startswith("reveal"):
            c[v]["yes"] += 1
        elif vd == "no reveal":
            c[v]["no"] += 1
        if g("redacted"):
            c[v]["redacted"] += 1
        if g("correct") is not None:
            c[v]["correct"] += g("correct")
    line = []
    for v, d in c.items():
        s = f"{v}: n={d['n']}"
        if d["yes"] + d["no"]:
            s += f" reveal {d['yes']}/{d['yes'] + d['no']} = {d['yes'] / (d['yes'] + d['no']):.3f}"
        if d["redacted"]:
            s += f" redacted {d['redacted']}"
        if d["correct"]:
            s += f" acc {d['correct'] / d['n']:.3f}"
        line.append(s)
    print(f"{p.parent.name}/{p.name} ({D['n_shown']}/{D['n_total']} prompts): " + " | ".join(line))
