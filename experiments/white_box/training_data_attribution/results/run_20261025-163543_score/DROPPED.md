# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `emb_needed.npy` | 36,139,136 | `960adc07a862fe86547f5dec6011080937b8dc1ad53d9e7e82e1f8031ee18b50` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/training_data_attribution/run.py --stage score --texts data/texts_L40.jsonl --models dolos,qwen,qwen+noise,R-plain --chunks-per-job 2` (argv from this run's config.json) |
| `inspect/` (3 files) | 34,133,717 | - | inspector view copy of this run's outputs/prompts/rows (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_controls/` (3 files) | 28,133,087 | - | inspector view copy of this run's outputs/prompts/rows (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_top1/` (3 files) | 6,000,630 | - | inspector view copy of this run's outputs/prompts/rows (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
