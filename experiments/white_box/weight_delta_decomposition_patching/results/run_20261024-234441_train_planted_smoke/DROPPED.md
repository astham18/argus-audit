# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `planted_delta.safetensors` | 55,050,352 | `e2c872f08cbce37c2730c3eba561b50eb3527eb58ff7e987daacd14a1b68db1f` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/weight_delta_decomposition_patching/train_planted.py --smoke` (argv from this run's config.json) |
