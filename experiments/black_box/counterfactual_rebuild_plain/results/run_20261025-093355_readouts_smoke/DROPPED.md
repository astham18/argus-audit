# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_gen/README.txt` | 221 | `0d984c851a32ba69cf5a1ad44c66f3e50af828bb37de14cbff1dcb2ec24346f0` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/errors.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/outputs.jsonl` | 30,756 | `693cefc1269015ba4e920f881f684e6d0d9fc8a23ebcbbf6b374e8af9aedb032` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/prompts.jsonl` | 39,774 | `5bdfea0f2499279d7272ba374c9f994fd37c142380a9bc62e2a6a8a897be03ac` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/rows.jsonl` | 36,073 | `2a8abe9662c557ffd70eae8f60670600d42689014f32537e9fa49b7321a66578` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/README.txt` | 221 | `0d984c851a32ba69cf5a1ad44c66f3e50af828bb37de14cbff1dcb2ec24346f0` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/errors.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/outputs.jsonl` | 143,452 | `4e86fbc9daae1c9bca6bba32b81af0b9c23829b28187636aee621b2d4d0e10bb` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/prompts.jsonl` | 251,694 | `42f8a3fa0aca2e7dfc79aa67893d03700686074143e072fc39e03130a0310085` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/rows.jsonl` | 48,832 | `bc5b4a7624e0a8148a6441519066de357e6c98df8f8d2e3736658796cd2caa0d` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
