from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, re
from pathlib import Path
CB = (_argus_root() / 'experiments/_shared/codebreakers')
ns = {}; exec(open(CB / "_prose/old_fields.py").read(), ns); O = ns["O"]
for exp, f in O.items():
    p = CB / exp / "report.json"; r = json.load(open(p))
    r["hypothesis"] = f["hypothesis"]; r["attack"] = f["attack"]; r["method_steps"] = f["method_steps"]; r["controls"] = f["controls"]; r["flow"] = f["flow"]
    r["observations"]["numbers"] = f["observations_numbers"]
    r["repeats"]["sample_sizes"] = f["sample_sizes"]
    for c, t in zip(r["verdict"]["criteria"], f["criteria"]):
        c["text"] = t
    # how_to_run text: replace codes in what_happens
    for st in r.get("how_to_run", {}).get("steps", []):
        w = st["what_happens"]
        w = w.replace("M3", "the Fake Encoder").replace("C4 sentences", "sentences from the C4 web-text dataset")
        st["what_happens"] = w
    json.dump(r, open(p, "w"), indent=1, ensure_ascii=False)
print("ok")
