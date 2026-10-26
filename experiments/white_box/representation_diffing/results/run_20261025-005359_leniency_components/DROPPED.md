# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_score/README.txt` | 162 | `9dbf002dd4aad088cd4f23f6ffdbe782770e984e0ddb4d37173c8bb72b4ab0eb` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/outputs.jsonl` | 1,659,030 | `c3824762fb527bc8947daba175f6bb9dfd27ebe353241ce42719227ca49cd7b0` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/prompts.jsonl` | 3,434,788 | `f1bb420cc2b2365308db6e008f446490c2fe469774b54fef5744fa56e3c04da0` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_score/rows.jsonl` | 805,464 | `5df1b34cea736857d917969640037efea41a508273147eb3c10b87e1969be3ee` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
