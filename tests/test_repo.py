"""Tier 0 (CPU, CI): the repository is complete and consistent. No model is loaded and nothing is spent."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPS = json.loads((ROOT / "argus/legacy_map.json").read_text())["experiments"]


def experiment_dirs():
    return [ROOT / e["new"] for e in EXPS]


def test_every_experiment_folder_exists_with_a_prediction_header():
    assert len(EXPS) == 57                       # 53 hunt experiments + 4 prelude stages
    for e in EXPS:
        d = ROOT / e["new"]
        assert d.is_dir(), e["new"]
        assert not re.match(r"[A-Z]\d", d.name), f"folder names carry no hunt code: {d.name}"
        first = (d / "PREDICTION.md").read_text().splitlines()[0]
        assert first.startswith(f"Hunt code: {e['code']}; team: ") and e["old"] in first, (e["new"], first)


def test_every_report_json_validates_against_the_schema():
    schema = json.loads((ROOT / "argus/report_schema.json").read_text())
    reports = [d / "report.json" for d in experiment_dirs() if (d / "report.json").exists()]
    assert len(reports) == 52
    for r in reports:
        jsonschema.validate(json.loads(r.read_text()), schema)


def test_every_result_md_cites_a_run_directory_that_exists():
    for d in experiment_dirs():
        r = d / "RESULT.md"
        if not r.exists():
            continue
        runs = set(re.findall(r"run_\d{8}-\d{6}[\w\-]*", r.read_text()))
        assert any((d / "results" / x).is_dir() for x in runs), f"{r}: cites {sorted(runs)[:3]} but none exists"


def test_migration_manifest_matches():
    """Every migrated file exists; evidence files (run directories and data) are byte-identical to the manifest."""
    rows = [json.loads(l) for l in (ROOT / "docs/migration_manifest.jsonl").read_text().splitlines() if l.strip()]
    assert len(rows) > 4000
    for w in rows:
        p = ROOT / w["path"]
        assert p.exists(), w["path"]
        evidence = "/results/" in w["path"] or "/data/" in w["path"]
        if evidence and w["size"] < 20_000_000:
            assert p.stat().st_size == w["size"], w["path"]
            assert hashlib.sha256(p.read_bytes()).hexdigest() == w["sha256"], w["path"]


def test_dropped_files_are_documented():
    dropped = json.loads((ROOT / "docs/dropped_files.json").read_text())
    for d in dropped:
        assert not (ROOT / d["new"]).exists() or d["class"] != "regenerable binary", d["new"]
        if d["class"] == "regenerable binary":
            run = re.match(r"(.*/results/run_[^/]+)/", d["new"]).group(1)
            assert d["sha256"] in (ROOT / run / "DROPPED.md").read_text(), d["new"]


def test_vendor_generate_is_byte_identical():
    h = hashlib.sha256((ROOT / "vendor/generate.py").read_bytes()).hexdigest()
    assert h == "9f3fc3a168ff7e8dc116f27bed06140b8e0cab2d54937baf66a1bd8348af1e21"


def test_check_repo_passes():
    p = subprocess.run([sys.executable, "scripts/check_repo.py", "--links"], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-2000:]


def test_build_index_and_summary_build(tmp_path):
    for script, out in (("scripts/build_index.py", tmp_path / "INDEX.html"), ("scripts/build_summary.py", tmp_path / "S.html")):
        p = subprocess.run([sys.executable, script, "--out", str(out)], cwd=ROOT, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        assert out.stat().st_size > 10_000


def test_no_absolute_user_paths_in_code():
    hits = []
    for f in list((ROOT / "argus").rglob("*.py")) + list((ROOT / "experiments").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py")):
        if f.name in ("migrate.py", "migrate_fixes.py"):
            continue
        if "/Users/" in f.read_text(errors="ignore"):
            hits.append(str(f.relative_to(ROOT)))
    assert not hits, hits
