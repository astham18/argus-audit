# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_view/outputs.jsonl` | 32,404,590 | `70b4d0d92e71352977d835f2e48bd97a013c25ebb245d460f7bce4f6b4943d4a` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/prompts.jsonl` | 50,457,444 | `88f44f219aca4e8a6e435630f6d3895dc3a53f79513965b639826027be632a55` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view/rows.jsonl` | 9,673,911 | `b4cb4dc41131bf0bfc977219878d98647fcc6639d0dfe12c9e201ba80241800f` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view_named/README.txt` | 346 | `d26d00734dbafe8c0d37fe9f17682415ab7e2d6f7703a9016edb7b5dee41cd47` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view_named/outputs.jsonl` | 32,564,190 | `df93fcd77332ee590647287f2d1ba5ac549c846480205100b92614ead6b739e8` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view_named/prompts.jsonl` | 50,617,044 | `c090167eab2b411e09fa32b65b2d41075f9aecdf6ee4d93010a4cffdf578a1e9` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_view_named/rows.jsonl` | 11,179,911 | `3cb1c37dd5563371d510759f9de7d5aa6d6ad7c197ef348ccdf7c406a7353680` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
