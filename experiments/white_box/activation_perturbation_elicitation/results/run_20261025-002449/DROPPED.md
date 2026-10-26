# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/README.txt` | 183 | `be688140f3badb90740dde727528ad64d6cc6c84c4d58061b3629c3d556aa35c` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/outputs.jsonl` | 7,179,634 | `5a3dc5610cd7a6c2869c94c03d251e1be8fabd847e244e84bc3e984134a5a4ce` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 588,850 | `15fa4b926c3a9b0924e16801ea99c2f8299222c997da386dc0fd36e2850f3d6a` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 3,967,472 | `a0096146e87a0964b962123f7ddc32e9d75cd73a35d8ffc8a8e612e72912ce0b` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
