# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/README.txt` | 224 | `c8eb1abf41217135fac5bcf49a07dd448b46401d345b9527d52356d249433fa5` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/outputs.jsonl` | 7,786,552 | `dc501bc22bb6ead8e99d40c33389f17ec03ef57bd7ecf20ad0085ba8d76a9041` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 12,299,948 | `cb488fed1676cd33deeea1fbc5a2b9843ef43d386500273db80268bc338bcdf2` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 2,582,098 | `8068b1642be880a07cf13e948a0c2e04fdce171d8d372d0a3ea9399bf9b27712` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
