# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_view/README.txt` | 322 | `8cc91d9862e03c1d548a54b332320a9d06cb32fb4c01fb4ef83e1e0b5c1118d7` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/games_page.jsonl` | 2,688,384 | `d73c9965175f96f8b85002be4c1a4ab793b4f22028dce47a4619a05973d85398` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/outputs.jsonl` | 916,768 | `e212afc70b049f94f3c64df0e8102881ac264fdaa775851797130ed88d957e3c` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/prompts.jsonl` | 10,033,336 | `165fef19c72bd90743b71019981584d3e0937b4e89934d709288a2b0469dad3f` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/rows.jsonl` | 1,141,824 | `844311d99818a93c4e4861aea340f9fc894d55ae7e1ca36c20c4fac1f963282f` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
