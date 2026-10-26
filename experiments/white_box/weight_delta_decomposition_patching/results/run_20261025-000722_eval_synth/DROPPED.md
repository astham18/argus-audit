# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_gen/README.txt` | 153 | `1c4026e0ee461d715220a14f13f02c86d4977353cbc0f134456fa9c7a3342bde` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/outputs.jsonl` | 158,318 | `4524b5071c55c3f676ae5b56f56006a6b5da85e89d2733b5a17d7023dbabd2ae` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/prompts.jsonl` | 358,798 | `e62691b824474cdb53215a45475a85d7a833106f709867ee6a65dafb61296770` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_gen/rows.jsonl` | 166,194 | `8b892860bccb2eefebd607083b77332db3b55e6cf66db595e3a74db95cc79c85` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
