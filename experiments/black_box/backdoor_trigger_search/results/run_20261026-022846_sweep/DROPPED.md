# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_cells/` (3 files) | 351,320 | - | inspector view copy of this run's outputs/prompts/rows (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_outputs/` (3 files) | 8,197,185 | - | inspector view copy of this run's outputs/prompts/rows (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
