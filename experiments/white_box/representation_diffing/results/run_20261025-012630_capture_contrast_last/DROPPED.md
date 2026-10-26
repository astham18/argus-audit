# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `activations_dolos.npy` | 46,080,128 | `4091269618d7dabb32efb34a987c89b443f82e1be0adba6e137d830f2e8b1281` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/representation_diffing/run.py capture --variants qwen,dolos --corpus contrast --key S3_heads_and_directions` (argv from this run's config.json) |
| `activations_qwen.npy` | 46,080,128 | `9fa8b407d07453b7eb1439f056678ba0654fbcebfaba57d9e604be6ad8632dbb` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/representation_diffing/run.py capture --variants qwen,dolos --corpus contrast --key S3_heads_and_directions` (argv from this run's config.json) |
