from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, re, sys
from pathlib import Path
CB = (_argus_root() / 'experiments/_shared/codebreakers')
P = {}
for f in ("c0_c1", "c2_c3", "c4_c5"):
    ns = {}; exec(open(CB / "_prose" / f"{f}.py").read(), ns); P.update(ns["P"])


def clean(x):
    if isinstance(x, str):
        x = x.replace(" — ", ", ").replace("—", ", ").replace(" – ", " to ").replace("–", "-")
        return x
    if isinstance(x, list):
        return [clean(v) for v in x]
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    return x


for exp, fields in P.items():
    p = CB / exp / "report.json"; r = json.load(open(p))
    r.update(fields)
    r["what_this_tells_us"] = fields["tells_us"]
    r = clean(r)
    json.dump(r, open(p, "w"), indent=1, ensure_ascii=False)
    words = sum(len(str(v).split()) for k, v in r.items() if k in ("summary_plain", "background", "metrics", "controls_plain", "results_plain", "fluke_check", "tells_us", "does_not_tell_us"))
    print(exp, "prose words:", words, "| dashes left:", json.dumps(r, ensure_ascii=False).count("—"))
