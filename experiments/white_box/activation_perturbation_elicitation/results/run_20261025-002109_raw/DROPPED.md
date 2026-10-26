# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/README.txt` | 224 | `c8eb1abf41217135fac5bcf49a07dd448b46401d345b9527d52356d249433fa5` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/outputs.jsonl` | 4,826,599 | `b68190ca50713c67b8ea1e23ad94b2c14bacef302f2b0b4bfdfd81f8a1453908` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 5,850,186 | `826a408dd6a51ac76d9a1c48e2eed72ad75f159e033939270e2c70375d190962` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 8,832,695 | `799b9479b5ce0dd263fb0ae544733202d40989b42a0e38f14902a8600349b126` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
