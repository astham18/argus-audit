# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/outputs.jsonl` | 972,902 | `8080c4c7f16bab468f8f6fb9f35c3317d33e4f18d8cb4e225cd0228fe4c6b27a` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 998,256 | `9d1b61dade5d2816f80b5b1cf8656abaa232e92587817e4a1de6510f4ae141d8` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 2,544,470 | `8e30824b496f8400503a6600232b696859221ce50e6bbe7837dc5fce9ee131c5` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
