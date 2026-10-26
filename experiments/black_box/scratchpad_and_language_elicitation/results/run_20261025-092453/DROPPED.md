# Files not committed from this run

These files existed in the original run directory but are not in the repository (docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown (`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.

| File | Bytes | sha256 | Class | How to recreate |
|---|---:|---|---|---|
| `inspect_languages/judge.jsonl` | 4,416,083 | `56cfe408422f978104191a38ca0362342793b03f059e5d1764c693b6d9909a2a` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_languages/outputs.jsonl` | 1,185,959 | `7d8a9d894fee12a63231504c801b365eeb5d5abd1f277e1b7812a5ae78768708` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_languages/prompts.jsonl` | 620,160 | `d6bd8524423f215f42b6d2902edf8bb9052211a89856b0375991ffe9d4037c68` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_languages/rows.jsonl` | 746,675 | `69a0dea8447df42777483f167e3ef359bd38a621a50a2d76c8a80ce1dd3f1e5b` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_scratchpad/judge.jsonl` | 4,205,069 | `204c80226c9126d390aaf9cd39150b56faccba0acb635a43905d34972cdcb4d3` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_scratchpad/outputs.jsonl` | 1,036,758 | `8fffe1bf169feb934bd1f15cf53ffda1360ebcd002a1563526e387488c66a491` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_scratchpad/prompts.jsonl` | 447,718 | `df23f77c320b1cd9be169b703e43003166ab38b8671a2ef9ab201f0818df647c` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
| `inspect_scratchpad/rows.jsonl` | 1,692,599 | `806b60dac1e1f1a133f35304487e798e0fe24e4fc1da571bf5084729398a0c00` | inspector view copy of this run's own file (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |
