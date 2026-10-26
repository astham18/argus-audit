# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_gen/README.txt` | 153 | `43991613fb06cad9f0a00e7eccddafb76d1d74d8d98c25a1ee252ae8d089839e` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/outputs.jsonl` | 1,174,391 | `581ea082a0523d985c1f11c73e97532157a3bdb711d7a1add74ffc2529d9f38a` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/prompts.jsonl` | 1,168,400 | `b078bc26e5acfab16b5f909732d751eade987577d94c703a4ae0d0bce5d1a1db` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/rows.jsonl` | 1,435,036 | `82a9bb9a8d8b303f8b594ad9c5dee4fb931bc20accbb18b188e74d5a0a96c4e2` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
