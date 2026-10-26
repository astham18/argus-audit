# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_view/README.txt` | 337 | `cdaaa7425946b5d02d2b952a34a7be7c20c61eab8536888467d015e789f00b9a` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/outputs.jsonl` | 3,877,680 | `a67cc3a2bc9d52e0c0854948261cf9d77fd7d966b964897163846bb6b5736630` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/prompts.jsonl` | 13,251,440 | `e51abe763f4351230165045bfa65f1b116fd9b2da9cf2e5a278f121e47e4a7be` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/rows.jsonl` | 1,784,834 | `aebeaa0f10a418d0235cd553c9506eb161c711ed788d0bef726a3200c0a32d0f` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
