# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_cells/outputs.jsonl` | 19,134 | `0511a6b66c15921dcf5d1eac118099b613c2dbd6be86147439e1263cce9cb3a9` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_cells/prompts.jsonl` | 1,592 | `4d4abc07ecab1e1e02c1913b619791148b68e4586b5a5445de7edc4d3e2b28f9` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_outputs/outputs.jsonl` | 23,789 | `b0b70c25b76dad3271fba968a43b3fc13f046a622469c9056d1817b9371e12ed` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_outputs/prompts.jsonl` | 43,461 | `0d57b7dc2345447a1f08976071264ffb698af4aafcdd91c20007fb4bea84b078` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
