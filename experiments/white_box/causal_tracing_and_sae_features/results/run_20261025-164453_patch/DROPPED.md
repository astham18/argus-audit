# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `residuals_slot.npz` | 64,723,627 | `d4733cda6f68fa09b1d3a1b63751a8a3bb9d369eb40211113982a54f0efb13e5` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/causal_tracing_and_sae_features/run.py --stage patch` (argv from this run's config.json) |
