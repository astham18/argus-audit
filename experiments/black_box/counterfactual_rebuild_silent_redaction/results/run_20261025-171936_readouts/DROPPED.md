# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect/README.txt` | 730 | `753cc18ea85804d1b3408e515f4fd381d3958ebfda4ed71e5c545486e81ffade` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/errors.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/outputs.jsonl` | 2,210,440 | `0b7f782c3480ba79b3c0356991b18357748c4b80cac2124e1a29628c65540bed` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/prompts.jsonl` | 458,213 | `b477d09a01387e35b267271d4b955ae2aa67ceafceea9281b39139863a89de20` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect/rows.jsonl` | 1,906,811 | `9c9abcb942e349374e63c5acf5a19c82e4f2075b617917810f60ac052709eb71` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
