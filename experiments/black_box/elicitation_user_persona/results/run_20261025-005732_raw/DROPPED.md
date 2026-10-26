# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/README.txt` | 224 | `c8eb1abf41217135fac5bcf49a07dd448b46401d345b9527d52356d249433fa5` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/outputs.jsonl` | 1,648,855 | `3092f81937b15deddf67a97521607b90990d02b60a328139e96a98a936229b77` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 249,152 | `b9da1e0f3d802b7c6ea0d08e565efc97c5498e020c32b50f6e4b7b17196ee6f4` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 1,382,729 | `62eebef1ed5ae3f4a628a8dd53a20a52e4947d52cc01b2473018f9c38ba857ee` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
