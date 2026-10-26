"""Build every Detectives DATA page with argus/inspector.py from the headline runs' rows.jsonl (see make_reports.PAGES).
PY build_data_pages.py   (run build_rows.py first)"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import subprocess, sys
from pathlib import Path
HERE = _argus_legacy_dir('hunt/detectives')
sys.path.insert(0, str(HERE))
import det_common as dc
from make_reports import PAGES
TITLES = {"D2a_narration": "D2a narration attack", "D2b_prefill": "D2b prefill attack", "D2c_user_persona": "D2c user-persona attack",
          "D2d_activation_fuzzing": "D2d activation fuzzing", "D2e_peer_handshake": "D2e peer handshake", "D3_sandbagging": "D3 detection battery"}
IDF = {"D2d_activation_fuzzing": "question_or_sentence,noise_condition", "D2e_peer_handshake": "item,version"}
PY = str(Path(sys.executable))
for exp, pages in PAGES.items():
    for fname, run, covers in pages:
        rd = HERE / exp / "results" / run / "inspect"
        cmd = [PY, str(dc.COMMON / "inspector.py"), str(rd), "--rows", str(rd / "rows.jsonl"), "--out", str(HERE / exp / fname),
               "--title", f"{TITLES[exp]}, {covers}: the examples behind the result", "--seed", "0"]
        if exp in IDF:
            cmd += ["--id-fields", IDF[exp]]
        if exp == "D2d_activation_fuzzing" and "raw" in run:
            cmd += ["--strata", "noise_alpha"]
        if exp == "D2d_activation_fuzzing" and "raw" not in run:
            cmd += ["--strata", "noise_alpha,question"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(exp, fname, (r.stdout + r.stderr).strip().splitlines()[-1][:300])
