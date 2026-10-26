# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_gen/README.txt` | 154 | `15ecbef33b2a443194686c19b739493ae24854fc29ae19d716594af1a2ad00f7` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/outputs.jsonl` | 492,974 | `3abc679cca21c694fbdfc687867ab8b7920c5b90359c717d5b91e10a059f2797` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/prompts.jsonl` | 516,154 | `1ed106062ccc9fa240529b6ee9efbb644ec75ffb94cde765d1f1f99088e6ee3c` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/rows.jsonl` | 439,917 | `ea32f692c373f16fcbc9050fcbd9418554318006333a5d9a79e317d53d093c3b` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_probe/README.txt` | 154 | `15ecbef33b2a443194686c19b739493ae24854fc29ae19d716594af1a2ad00f7` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_probe/outputs.jsonl` | 4,288,054 | `42a3fec72b73c19f519aad134d79c3e7b33d74efc6c8608d10c1cd677df3e04a` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_probe/prompts.jsonl` | 4,154,439 | `c360f3da4af21a4271f6334c373edfbd515feea92a53e191c7cacfb738d6292e` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_probe/rows.jsonl` | 1,248,020 | `179e52d753f46db4410b93cbe2e1d9a57c40f2fb7baa0f5494193ec5694b392b` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
