# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/README.txt` | 224 | `c8eb1abf41217135fac5bcf49a07dd448b46401d345b9527d52356d249433fa5` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/outputs.jsonl` | 3,816,505 | `f0ab19ddd4da838ccdca9676bd4efb9f0daa752d8d0a7c4243f78552b9f8ed03` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 311,536 | `292885b4c597fc6fdeef9a46ee1b03d798ab551f1de7c6fc30000891daa1a512` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 1,637,371 | `25c2e61a6c272a1ede7c8c902c030cbd8a45bdd2b516cef9ef8835501fa61b6d` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
