"""R2: build DATA.html (generation readouts) and DATA_score.html (log-prob readouts) with argus/inspector.py,
then REPORT.html with argus/report.py.   PY build_pages.py results/run_<id>_readouts"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r2lib import *  # noqa
PY = str(Path(sys.executable))
rd = Path(sys.argv[1]).resolve()
CUE = sys.argv[2] if len(sys.argv) > 2 else "run_20261025-095157_secretcue"
import json
with open(rd / "inspect_gen/judge.jsonl", "w") as f:      # judge ids '<sentence>|W5|<model>__gen60' -> '<sentence>|W5|<model>'
    for l in open(rd / "judge.jsonl"):
        j = json.loads(l); j["id"] = j["id"].replace("__gen60", ""); f.write(json.dumps(j, ensure_ascii=False) + "\n")
subprocess.run([PY, str((_argus_root() / 'argus/inspector.py')), str(rd / "inspect_gen"), "--rows", str(rd / "inspect_gen/rows.jsonl"),
                "--judge", str(rd / "inspect_gen/judge.jsonl"), "--out", str(EXP / "DATA.html"), "--id-fields", "sentence,wording",
                "--strata", "wording", "--flag-field", "redacted", "--drop", "first_line",
                "--title", "R2 generation readouts: every model's output side by side (W5, W4, [secret], F32, G7)"], check=True)
subprocess.run([PY, str((_argus_root() / 'argus/inspector.py')), str(rd / "inspect_score"), "--rows", str(rd / "inspect_score/rows.jsonl"),
                "--out", str(EXP / "DATA_score.html"), "--id-fields", "item,readout", "--strata", "readout",
                "--title", "R2 log-prob readouts: redaction margin, monitor leniency (G2b), undercut nobody (X1)"], check=True)
subprocess.run([PY, str((_argus_root() / 'argus/inspector.py')), str(rd.parent / CUE), "--rows", str(rd.parent / CUE / "rows.jsonl"), "--out", str(EXP / "DATA_cue.html"),
                "--flag-field", "redacted", "--title", "R2 bare <secret> cue: 300 samples per model at temperature 1.0"], check=True)
