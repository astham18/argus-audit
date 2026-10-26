# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_gen/README.txt` | 153 | `76e0aa19c012119883a3e1b85fc111e17804a9ed4b6ad095b4a4a6c0f8f91dce` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/outputs.jsonl` | 1,035,666 | `399a349eafb7912d2e344325b0bf2999982ea2de9b027f5c8744e2acfa0b2bf7` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/prompts.jsonl` | 1,162,700 | `6d810d204044f296b5f9bdb01d0b13b61b24406c3ddeaf0586d5f020e0d1b2bb` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/rows.jsonl` | 1,414,388 | `18d8a47b7aca1db91317228809ba6ea6448e929f878c8d2110060b8368ecd86b` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
