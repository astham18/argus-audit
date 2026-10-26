# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `planted_delta.safetensors` | 55,050,352 | `53ef90ee053fc2b8fb41a049886cc98a7a507fdf050a5712b888f728d6d33607` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/weight_delta_decomposition_patching/train_planted.py` (argv from this run's config.json) |
