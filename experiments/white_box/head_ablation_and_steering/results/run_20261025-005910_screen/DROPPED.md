# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_heads/README.txt` | 88 | `5f64513fda983a11ef25aa99c0f2b0b15e1714c32a8266d891b626fef02adb00` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_heads/outputs.jsonl` | 17,091 | `55c2e86350e9b99a8ef85b68c2246bf693d9161f41d7882c66c57e8aa4f2b9fc` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_heads/prompts.jsonl` | 9,672 | `f968e0ebce202910e0328edd894a5562367fae96bedab9a1e3727af07cea0037` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
