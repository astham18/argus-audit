# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_view/README.txt` | 332 | `afc88ef742ddc0082303c2356fa73027f979dc8cc2b87ddf21d497869a941b8e` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/outputs.jsonl` | 3,970,310 | `762c98b9726868df69fdfe28101b7eff40d8b3cea7feee50892424c267b9f725` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/prompts.jsonl` | 19,035,654 | `8795a3cc1dacc8261f2920bb931b505d75f999010b01af5dfb82d91e1121fc5c` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/rows.jsonl` | 2,469,334 | `6bf1ae101e3cff1e5de600314de2aa3afbe56ed96a985bd5ea3252c4d037acae` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
