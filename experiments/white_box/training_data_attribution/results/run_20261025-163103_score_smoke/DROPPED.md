# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/outputs.jsonl` | 93,339 | `fed94c31345acd6a2c6628d4f18d14ba6f6346a00c58fe9215e098e39b9a5e3e` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 136,743 | `b0017188540aeeb687c04d8be9f9452ebc4bb3b39209e90ed3f31f855192a7b7` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 304,504 | `e3b1a9ba8e9c3aa776f206afcd89884e8c21b103a0793409f043c7e12be4420e` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
