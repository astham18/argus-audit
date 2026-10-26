# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `deltas/fresh_noise.safetensors` | 3,087,466,776 | `d1e2e397c9e714273a4ede6187b3162376118233317cd24bb48acb11bdfe3649` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/weight_delta_decomposition_patching/denoise_run.py --target synthetic --write_deltas` (argv from this run's config.json) |
| `deltas/planted.safetensors` | 27,525,232 | `3e3c98d35f63e4750b1eb8f84c12dee38617cbf00dbd55429f7ec9a6293bf088` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/weight_delta_decomposition_patching/denoise_run.py --target synthetic --write_deltas` (argv from this run's config.json) |
| `deltas/recovered_edits.safetensors` | 27,525,232 | `2a9414acae0588e46c2fdacc7ac4be26aec076d3cff637e55f9ad9261d9abd4f` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/weight_delta_decomposition_patching/denoise_run.py --target synthetic --write_deltas` (argv from this run's config.json) |
| `deltas/synthetic_full.safetensors` | 3,087,466,776 | `362e081fdc2183cc13254e66f8de108b8cf897106b3f2161ab262f2a9eb1f174` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/weight_delta_decomposition_patching/denoise_run.py --target synthetic --write_deltas` (argv from this run's config.json) |
| `deltas/synthetic_noise_only.safetensors` | 3,087,466,776 | `f68a114765606a8861144bf5628fec6551bcf7343c2aa0e92c74462d8400185c` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/weight_delta_decomposition_patching/denoise_run.py --target synthetic --write_deltas` (argv from this run's config.json) |
