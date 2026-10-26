# vendor/

Files from the organisers' starter repository for the Apart Research AI Collusion Research Sprint (October 2026),
`redteaming/` folder, kept **unchanged** so that every load of Dolos and Qwen in this repository goes through the exact
code the organisers published.

| File | What it is | Source |
|---|---|---|
| `generate.py` | The starter inference script: pinned repos and revisions for Poseidon-Research/Dolos-1.5B and Qwen/Qwen2.5-1.5B-Instruct, `load_model()`, `choose_device()`, chat-template generation. Imported by `argus/harness.py`, `argus/modal/batch_generate.py` (local backend), `argus/modal/local_serve.py` and `ui/app.py`. | `redteaming/generate.py`, added in commit `8dad6d7` ("Add Dolos red-teaming challenge and local inference quick start") by georg-poseidon (Poseidon Research), 2026-10-22 |
| `STARTER_README.md` | The challenge statement (the three tasks: discover and describe, explain the mechanism, audit without a reference model). | `redteaming/README.md`, same repository |
| `overview.png`, `overview.prompt.txt` | The challenge overview figure and the prompt it was drawn from. | `redteaming/`, same repository |

`generate.py` must stay byte-identical: sha256 `9f3fc3a168ff7e8dc116f27bed06140b8e0cab2d54937baf66a1bd8348af1e21`
(checked by `tests/test_repo.py`). Copyright remains with its authors; it is not covered by this repository's MIT
licence. Links in `STARTER_README.md` that point to other folders of the sprint repository do not resolve here.
