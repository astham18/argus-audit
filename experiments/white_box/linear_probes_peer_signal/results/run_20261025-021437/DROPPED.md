# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `features_and_probes_chat.npz` | 6,982,292 | `a8e34aac6add2e848d957486050b559e16d3fa388512e16ad54aa6953510f351` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/linear_probes_peer_signal/run.py --backend modal --formats chat --planned-usd 0.30` (argv from this run's config.json) |
