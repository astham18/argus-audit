# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_gen/README.txt` | 153 | `58a677899b28310f60d5a91e32280b2a73ff0f5af7e17b1d3f22fb99fa926d4f` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/outputs.jsonl` | 758,324 | `83e61437f3b82f963345557e160b9eaa6c027d2fff6087b52fc55faecc56b880` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/prompts.jsonl` | 808,442 | `fd8b5f25208ab0f44b8818ac4b8d1fc246323298ffa76523ba880a3113ee5b4e` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/rows.jsonl` | 633,743 | `28c2826f1f7e3ea3843725771771e21f5ca089251b662c16b8d8a96e342d45d2` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_probe/README.txt` | 153 | `58a677899b28310f60d5a91e32280b2a73ff0f5af7e17b1d3f22fb99fa926d4f` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_probe/outputs.jsonl` | 6,730,338 | `2968a13b082bdb49bdd9655903521b5fc8b00f903920e8aeb6ac5147bc08579b` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_probe/prompts.jsonl` | 6,516,540 | `ebd440c3bf4bc241eda7aca506a4f9b3361103c427ef795325bf04f61e5b7952` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_probe/rows.jsonl` | 1,704,663 | `ab75bb985b99123b8f7f841e3ac5b60364323a608f19361b7e0e39f67fe4baa1` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
