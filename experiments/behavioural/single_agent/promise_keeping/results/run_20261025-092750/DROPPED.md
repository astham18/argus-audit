# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_view/README.txt` | 333 | `0263a9120b51782a21ffe75335c145ad3886da272427965e2c548a435aff48ae` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/games_page.jsonl` | 2,068,803 | `aac03a4fb75c6e2772e67db7e27f964a2bf63a1cf4fe69686b72db7dd2cdc4a5` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/outputs.jsonl` | 2,580,915 | `6702a215d4153f3ec266190a3af8754f06daec0b63802953963ebc8ec202f0da` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/prompts.jsonl` | 41,620,308 | `ab9ca2edd8e91f3ad3d015ccf8af70036932e6467a4c0fb200b28b184a37f0ee` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/rows.jsonl` | 2,693,400 | `6d4c492c414387d584c5582d5441142820b00d76621bf079b2128e96103b44c1` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
