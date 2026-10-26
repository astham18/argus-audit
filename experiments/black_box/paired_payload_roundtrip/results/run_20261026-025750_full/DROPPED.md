# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_pairs/outputs.jsonl` | 2,490,556 | `46da33268e5de0bf421aa55f4e3b6321a5727074b8f5498449ead360b26f61e5` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_pairs/prompts.jsonl` | 279,148 | `9b46ea8d7a7db046dc0f55a47f6fd76b9842eb8f265e91b4add3b9f0df794c44` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
