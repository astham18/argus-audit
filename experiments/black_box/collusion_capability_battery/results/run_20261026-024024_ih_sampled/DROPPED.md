# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/outputs.jsonl` | 938,565 | `5c8adc57095252a913dca0b38646da06cce60919438e3ac3926314bbda36bbfa` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 416,472 | `f9fc0369231bec35a3a16de0ff45fb1b4aed70edecfd8e407788aff5aab7039d` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 750,320 | `9964bb8db402338b858493da4ee8e2ab9ad4576e8d2f5d375e34782149041821` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
