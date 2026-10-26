# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `fwd/activations_dolos_fwd.npy` | 38,707,328 | `29e0437bda96b5e274ceb150beadd2e39311feae585283a115fa6050912dfc8f` | regenerable binary (> 5 MB, not committed) | `uv run experiments/black_box/payload_in_actions_meaning_sampling/run.py` (argv from this run's config.json) |
| `fwd/activations_qwen_fwd.npy` | 38,707,328 | `1a7e2eb42322f4a25fac175da52dd7cbe9d6f1ffe6f5afb756c9e60bf503da5a` | regenerable binary (> 5 MB, not committed) | `uv run experiments/black_box/payload_in_actions_meaning_sampling/run.py` (argv from this run's config.json) |
