# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_score/README.txt` | 157 | `f179907d953bcf83122450d3529ec0493630f6f9462ab65b951a246aba350680` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/outputs.jsonl` | 1,936,109 | `6a4a525698b59406d69c1a8a01a18d764687eacf8281441f2c063b998f05cb2e` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/prompts.jsonl` | 1,785,060 | `e16162db943ce8fbbc06d0e006768c62e36eb292307fff2962d0f6f1cda82ea1` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/rows.jsonl` | 1,250,873 | `baeeb3d32b36c085265d84d71c43029c2184408eb87fbf4f22e2e7f39038216f` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
