# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `activations_dolos.npy` | 376,012,928 | `2d0c716aabdf366395e273f0bfd5a71d44889db44d0bec537e8b7c0bbbc461a0` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/representation_diffing/run.py capture --variants qwen,m2 --extra experiments/white_box/representation_diffing/data/m2extra.jsonl` (argv from this run's config.json) |
| `activations_m2.npy` | 376,012,928 | `4335675d711ccdf0baa48e63473f355cf7781e984225f91cde7145869406d8ec` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/representation_diffing/run.py capture --variants qwen,m2 --extra experiments/white_box/representation_diffing/data/m2extra.jsonl` (argv from this run's config.json) |
| `activations_noise.npy` | 376,012,928 | `e6f823611788485f99f5d62766fef587e0dcd59fc5aa90ca8c5257f98bf6b870` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/representation_diffing/run.py capture --variants qwen,m2 --extra experiments/white_box/representation_diffing/data/m2extra.jsonl` (argv from this run's config.json) |
| `activations_qwen.npy` | 376,012,928 | `5a4f340444024262e3cf49e04475c9f7c4fe6a314215febc4b39dd0b42cff3ae` | regenerable binary (> 5 MB, not committed) | `uv run experiments/white_box/representation_diffing/run.py capture --variants qwen,m2 --extra experiments/white_box/representation_diffing/data/m2extra.jsonl` (argv from this run's config.json) |
| `inspect_map/` (4 files) | 3,415,712 | - | inspector view copy of this run's outputs/prompts/rows (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
