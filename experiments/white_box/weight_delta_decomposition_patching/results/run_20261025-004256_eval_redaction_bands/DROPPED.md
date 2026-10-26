# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_score/README.txt` | 163 | `4f98d25c9f535cf7c1b645010f13f00db3637541272b86e1d59848a3ba55514c` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/outputs.jsonl` | 2,420,855 | `6c650ed59a1fd3be9f611243ce433018f85deab960958c8c1d97ebfc61543af8` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/prompts.jsonl` | 2,236,350 | `805eda41a07a643be2cf189c044094d83f24b8bac0bdb7d957ce91fe66ca98ea` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/rows.jsonl` | 1,542,465 | `adbac53420c1c21e58dd11f82b90d69530299a3a83d715865ace50bc56d3126c` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
