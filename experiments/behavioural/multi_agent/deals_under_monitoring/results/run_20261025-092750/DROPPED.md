# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_view/README.txt` | 338 | `4d65476714c7c1a15ba60cb791e90e230e741ff31b8344a5c6e2e125fc1dfed5` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/games_page.jsonl` | 3,219,968 | `fd92cda30af911ac596035b065ddf4e0467a1621b882da4f4b928dd85beb0d9b` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/outputs.jsonl` | 4,160,820 | `7d9c359a0702ee5276d1546ccdc248ddedeb6950edbfbf7f53d1e0def16f9225` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/prompts.jsonl` | 69,599,964 | `59fd47bd534cbaffdae54a6469b298a2b0e79fa4d4d5ed918bba8bb17d1b10a8` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/rows.jsonl` | 6,052,236 | `e356aba2fd49cc059113748ddcf658aacd96d3e11cd6ad1794671d2d06dcce31` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
