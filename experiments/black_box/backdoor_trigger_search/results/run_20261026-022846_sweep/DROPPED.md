# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_cells/outputs.jsonl` | 230,062 | `93f80c0f5b87e4e14fd8cd7beba50b7c4251096eb92898178bd2a0069e2aba3d` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_cells/prompts.jsonl` | 8,546 | `c86a1a90ea7e81d99a0a79accc86b9165fd326324a3b19bc451123a03b95c4aa` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_outputs/outputs.jsonl` | 2,962,477 | `182e38a1fa0d1c4ea7b64d9e3ad205a29574661fe59618f4dea7f89907b5e88d` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_outputs/prompts.jsonl` | 2,263,474 | `7d2300571a077471e482bfad9782f090ec3c2c41841c4acff892c2b5c9924b65` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
