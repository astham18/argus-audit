# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_view/README.txt` | 330 | `127f9f345f159b3ec920a2511a8bb33b5fae4d60d2ab8b15ca1c93c338ed1b56` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/outputs.jsonl` | 3,895,465 | `0c3367ad138a6753419c7fa7272834cf5b4b1217645defae88a145773822c0f1` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/prompts.jsonl` | 12,861,303 | `022e1e151db1e1ad5ffc6183d31df91ac4d8334c740d32af529b53608d3e2c63` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/rows.jsonl` | 4,016,725 | `78101fa8424d737954fc5803dc8558bafd2dc7988deed4d1c41e7e761e9ee6e7` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
