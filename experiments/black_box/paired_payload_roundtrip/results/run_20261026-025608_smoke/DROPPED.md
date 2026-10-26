# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_pairs/outputs.jsonl` | 9,867 | `6af9cfb6c089a3f6ba94348afd5f198b2fcd6fe1702c90fc2575fc5b59c91739` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_pairs/prompts.jsonl` | 1,938 | `6491a8f7ca8fb2fe92f37de250c43c096ff28dcb9e326d6cf1742bdb57f768fd` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
