# Migration report (dry run, 2026-10-26 10:24 UTC)

Produced by `scripts/migrate.py` --dry-run. Source (read-only): `collusion_hackathon/redteaming/`. Plan: `docs/MIGRATION_PLAN.md` (with Amendment 1).

## Totals

- Files written: 4442 (4.27 GB before git compression)
- Path and import rewrites: 2456 in 554 files
- Unresolved paths: 0
- Links already broken in the source (unchanged): 49
- Dropped items: 470
- Errors: 0
- Time: 78 s

## Dropped (not copied)

| Class | Items | Bytes |
|---|---:|---:|
| derived view copy | 364 | 827,372,586 |
| noise | 58 | 18,660,649 |
| public | 9 | 1,751,168,436 |
| regenerable binary | 35 | 30,730,338,634 |
| uncited smoke run | 4 | 94,517 |

<details><summary>Every dropped item</summary>

| Old path (INV-relative) | Bytes | Class |
|---|---:|---|
| `common/.judge_cache` | 13,996,760 | noise |
| `common/__pycache__` | 194,491 | noise |
| `common/modal/__pycache__` | 111,612 | noise |
| `common/smoke_runs` | 1,142,103 | noise |
| `hunt/agents/A1_secret_courier/__pycache__` | 98,914 | noise |
| `hunt/agents/A2_monitored_channel/__pycache__` | 106,135 | noise |
| `hunt/agents/A3_opportunity_tasks/__pycache__` | 119,462 | noise |
| `hunt/agents/A4_courier_riders/__pycache__` | 77,405 | noise |
| `hunt/agents/A5_reader_vs_format/__pycache__` | 71,109 | noise |
| `hunt/agents/A6_format_ladder/__pycache__` | 83,086 | noise |
| `hunt/benchmarkers/B1_paired_battery/__pycache__` | 69,669 | noise |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/gsm8k/README.txt` | 254 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/gsm8k/outputs.jsonl` | 18,205 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/gsm8k/prompts.jsonl` | 10,192 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/gsm8k/rows.jsonl` | 5,057 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/ifeval/README.txt` | 255 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/ifeval/outputs.jsonl` | 21,856 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/ifeval/prompts.jsonl` | 11,588 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/ifeval/rows.jsonl` | 8,839 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/mbpp/README.txt` | 253 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/mbpp/outputs.jsonl` | 17,268 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/mbpp/prompts.jsonl` | 14,180 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/mbpp/rows.jsonl` | 6,951 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/mmlu/README.txt` | 253 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/mmlu/outputs.jsonl` | 18,312 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/mmlu/prompts.jsonl` | 10,984 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/mmlu/rows.jsonl` | 5,620 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/truthfulqa/README.txt` | 259 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/truthfulqa/outputs.jsonl` | 26,878 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/truthfulqa/prompts.jsonl` | 11,464 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/truthfulqa/rows.jsonl` | 7,281 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/xstest/README.txt` | 255 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/xstest/outputs.jsonl` | 10,715 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/xstest/prompts.jsonl` | 4,430 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect/xstest/rows.jsonl` | 6,132 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/gsm8k/README.txt` | 256 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/gsm8k/outputs.jsonl` | 2,179,872 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/gsm8k/prompts.jsonl` | 1,381,172 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/gsm8k/rows.jsonl` | 678,295 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/ifeval/README.txt` | 257 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/ifeval/outputs.jsonl` | 2,442,302 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/ifeval/prompts.jsonl` | 1,288,154 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/ifeval/rows.jsonl` | 1,069,437 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/mbpp/README.txt` | 255 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/mbpp/outputs.jsonl` | 1,777,781 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/mbpp/prompts.jsonl` | 1,466,272 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/mbpp/rows.jsonl` | 847,499 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/mmlu/README.txt` | 255 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/mmlu/outputs.jsonl` | 2,298,899 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/mmlu/prompts.jsonl` | 2,323,910 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/mmlu/rows.jsonl` | 814,725 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/truthfulqa/README.txt` | 261 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/truthfulqa/outputs.jsonl` | 3,169,738 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/truthfulqa/prompts.jsonl` | 1,208,146 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/truthfulqa/rows.jsonl` | 815,219 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/xstest/README.txt` | 257 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/xstest/outputs.jsonl` | 1,082,192 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/xstest/prompts.jsonl` | 548,856 | derived view copy |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect/xstest/rows.jsonl` | 704,287 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/__pycache__` | 85,505 | noise |
| `hunt/benchmarkers/B2_capability_battery/downloads` | 37,217,431 | public |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/games/outputs.jsonl` | 12,696 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/games/prompts.jsonl` | 29,036 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/games/rows.jsonl` | 5,297 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/ihier/outputs.jsonl` | 3,282 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/ihier/prompts.jsonl` | 8,536 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/ihier/rows.jsonl` | 4,110 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/mask/outputs.jsonl` | 31,437 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/mask/prompts.jsonl` | 77,649 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/mask/rows.jsonl` | 14,254 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/mmlu/outputs.jsonl` | 13,733 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/mmlu/prompts.jsonl` | 8,887 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/mmlu/rows.jsonl` | 3,610 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/posctrl/outputs.jsonl` | 8,507 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/posctrl/prompts.jsonl` | 2,647 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/posctrl/rows.jsonl` | 3,170 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/selfaware/outputs.jsonl` | 9,462 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/selfaware/prompts.jsonl` | 7,819 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/selfaware/rows.jsonl` | 4,220 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/stego/outputs.jsonl` | 5,512 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/stego/prompts.jsonl` | 19,628 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/stego/rows.jsonl` | 4,310 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/sycophancy/outputs.jsonl` | 9,419 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/sycophancy/prompts.jsonl` | 25,703 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/sycophancy/rows.jsonl` | 4,000 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/tom/outputs.jsonl` | 9,611 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/tom/prompts.jsonl` | 19,643 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/tom/rows.jsonl` | 3,678 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/truthfulqa/outputs.jsonl` | 21,059 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/truthfulqa/prompts.jsonl` | 8,867 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/truthfulqa/rows.jsonl` | 4,552 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/wmdp/outputs.jsonl` | 13,846 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/wmdp/prompts.jsonl` | 13,543 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect/wmdp/rows.jsonl` | 3,509 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/games/outputs.jsonl` | 317,856 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/games/prompts.jsonl` | 722,540 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/games/rows.jsonl` | 133,728 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/ihier/outputs.jsonl` | 231,495 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/ihier/prompts.jsonl` | 416,472 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/ihier/rows.jsonl` | 206,472 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/mask/outputs.jsonl` | 1,358,753 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/mask/prompts.jsonl` | 3,130,582 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/mask/rows.jsonl` | 819,456 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/mmlu/outputs.jsonl` | 1,388,412 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/mmlu/prompts.jsonl` | 1,530,112 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/mmlu/rows.jsonl` | 362,532 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/posctrl/outputs.jsonl` | 261,314 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/posctrl/prompts.jsonl` | 89,644 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/posctrl/rows.jsonl` | 102,227 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/selfaware/outputs.jsonl` | 633,966 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/selfaware/prompts.jsonl` | 517,744 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/selfaware/rows.jsonl` | 286,935 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/stego/outputs.jsonl` | 125,874 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/stego/prompts.jsonl` | 490,156 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/stego/rows.jsonl` | 107,431 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/sycophancy/outputs.jsonl` | 678,125 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/sycophancy/prompts.jsonl` | 1,493,896 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/sycophancy/rows.jsonl` | 267,366 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/tom/outputs.jsonl` | 641,727 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/tom/prompts.jsonl` | 1,308,488 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/tom/rows.jsonl` | 245,921 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/truthfulqa/outputs.jsonl` | 1,218,264 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/truthfulqa/prompts.jsonl` | 542,400 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/truthfulqa/rows.jsonl` | 284,584 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/wmdp/outputs.jsonl` | 1,391,497 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/wmdp/prompts.jsonl` | 1,488,840 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect/wmdp/rows.jsonl` | 355,262 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-024024_ih_sampled/inspect/outputs.jsonl` | 938,565 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-024024_ih_sampled/inspect/prompts.jsonl` | 416,472 | derived view copy |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-024024_ih_sampled/inspect/rows.jsonl` | 750,320 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-234441_train_planted_smoke/planted_delta.safetensors` | 55,050,352 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-234819_train_planted/planted_delta.safetensors` | 55,050,352 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/band_ABCD.safetensors` | 2,620,413,768 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/band_BCDE.safetensors` | 2,338,471,688 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/band_CDE.safetensors` | 1,589,781,992 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/band_DE.safetensors` | 1,028,264,712 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/band_negA.safetensors` | 748,689,536 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/band_negB.safetensors` | 748,689,576 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/band_negC.safetensors` | 561,517,192 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/band_negE.safetensors` | 466,747,496 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/edits_L22_27.safetensors` | 561,517,192 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/edits_all.safetensors` | 3,087,161,344 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/edits_embed.safetensors` | 466,747,496 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/full_L22_27.safetensors` | 561,581,904 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/neg_edits_L22_27.safetensors` | 561,517,192 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/neg_edits_all.safetensors` | 3,087,161,344 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/neg_edits_embed.safetensors` | 466,747,496 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/deltas/neg_full_L22_27.safetensors` | 561,581,904 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/inspect_tensors/README.txt` | 88 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/inspect_tensors/outputs.jsonl` | 54,494 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/inspect_tensors/prompts.jsonl` | 39,674 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/fresh_noise.safetensors` | 3,087,466,776 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/planted.safetensors` | 27,525,232 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/recovered_edits.safetensors` | 27,525,232 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/synthetic_full.safetensors` | 3,087,466,776 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/synthetic_noise_only.safetensors` | 3,087,466,776 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000722_eval_synth/inspect_gen/README.txt` | 153 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000722_eval_synth/inspect_gen/outputs.jsonl` | 158,318 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000722_eval_synth/inspect_gen/prompts.jsonl` | 358,798 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000722_eval_synth/inspect_gen/rows.jsonl` | 166,194 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002131_eval_dolos/inspect_gen/README.txt` | 153 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002131_eval_dolos/inspect_gen/outputs.jsonl` | 1,174,391 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002131_eval_dolos/inspect_gen/prompts.jsonl` | 1,168,400 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002131_eval_dolos/inspect_gen/rows.jsonl` | 1,435,036 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002911_eval_dolos/inspect_gen/README.txt` | 153 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002911_eval_dolos/inspect_gen/outputs.jsonl` | 1,035,666 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002911_eval_dolos/inspect_gen/prompts.jsonl` | 1,162,700 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002911_eval_dolos/inspect_gen/rows.jsonl` | 1,414,388 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004021_eval_redaction/inspect_score/README.txt` | 157 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004021_eval_redaction/inspect_score/outputs.jsonl` | 1,936,109 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004021_eval_redaction/inspect_score/prompts.jsonl` | 1,785,060 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004021_eval_redaction/inspect_score/rows.jsonl` | 1,250,873 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004256_eval_redaction_bands/inspect_score/README.txt` | 163 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004256_eval_redaction_bands/inspect_score/outputs.jsonl` | 2,420,855 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004256_eval_redaction_bands/inspect_score/prompts.jsonl` | 2,236,350 | derived view copy |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004256_eval_redaction_bands/inspect_score/rows.jsonl` | 1,542,465 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/__pycache__` | 36,874 | noise |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/activations_dolos.npy` | 376,012,928 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/activations_m2.npy` | 376,012,928 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/activations_noise.npy` | 376,012,928 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/activations_qwen.npy` | 376,012,928 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/inspect_map/README.txt` | 140 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/inspect_map/outputs.jsonl` | 172,206 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/inspect_map/prompts.jsonl` | 1,195,748 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/inspect_map/rows.jsonl` | 2,047,618 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-005359_leniency_components/inspect_score/README.txt` | 162 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-005359_leniency_components/inspect_score/outputs.jsonl` | 1,659,030 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-005359_leniency_components/inspect_score/prompts.jsonl` | 3,434,788 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-005359_leniency_components/inspect_score/rows.jsonl` | 805,464 | derived view copy |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-012630_capture_contrast_last/activations_dolos.npy` | 46,080,128 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-012630_capture_contrast_last/activations_qwen.npy` | 46,080,128 | regenerable binary |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-005910_screen/inspect_heads/README.txt` | 88 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-005910_screen/inspect_heads/outputs.jsonl` | 17,091 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-005910_screen/inspect_heads/prompts.jsonl` | 9,672 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012423_control_m2/inspect_gen/README.txt` | 153 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012423_control_m2/inspect_gen/outputs.jsonl` | 116,424 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012423_control_m2/inspect_gen/prompts.jsonl` | 140,934 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012423_control_m2/inspect_gen/rows.jsonl` | 61,310 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_gen/README.txt` | 153 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_gen/outputs.jsonl` | 758,324 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_gen/prompts.jsonl` | 808,442 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_gen/rows.jsonl` | 633,743 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_probe/README.txt` | 153 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_probe/outputs.jsonl` | 6,730,338 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_probe/prompts.jsonl` | 6,516,540 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_probe/rows.jsonl` | 1,704,663 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012532_control_brit/inspect_gen/README.txt` | 155 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012532_control_brit/inspect_gen/outputs.jsonl` | 134,599 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012532_control_brit/inspect_gen/prompts.jsonl` | 297,715 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012532_control_brit/inspect_gen/rows.jsonl` | 135,451 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen/README.txt` | 153 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen/outputs.jsonl` | 814,562 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen/prompts.jsonl` | 735,420 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen/rows.jsonl` | 639,793 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen_all/outputs.jsonl` | 1,160,479 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen_all/prompts.jsonl` | 1,105,930 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen_all/rows.jsonl` | 973,469 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_probe/README.txt` | 153 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_probe/outputs.jsonl` | 6,095,336 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_probe/prompts.jsonl` | 5,926,238 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_probe/rows.jsonl` | 1,801,007 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_gen/README.txt` | 154 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_gen/outputs.jsonl` | 492,974 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_gen/prompts.jsonl` | 516,154 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_gen/rows.jsonl` | 439,917 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_probe/README.txt` | 154 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_probe/outputs.jsonl` | 4,288,054 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_probe/prompts.jsonl` | 4,154,439 | derived view copy |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_probe/rows.jsonl` | 1,248,020 | derived view copy |
| `hunt/brain_surgeons/_lib/__pycache__` | 48,873 | noise |
| `hunt/budget_ledger.jsonl.bak_20261025_phaseA` | 457,515 | noise |
| `hunt/codebreakers/C0_scheme_rules/__pycache__` | 32,097 | noise |
| `hunt/codebreakers/C0_scheme_rules/results/run_20261024-233844/inspect/outputs.jsonl` | 972,902 | derived view copy |
| `hunt/codebreakers/C0_scheme_rules/results/run_20261024-233844/inspect/prompts.jsonl` | 998,256 | derived view copy |
| `hunt/codebreakers/C0_scheme_rules/results/run_20261024-233844/inspect/rows.jsonl` | 2,544,470 | derived view copy |
| `hunt/codebreakers/C1_rewrite_test/__pycache__` | 43,984 | noise |
| `hunt/codebreakers/C2_is_it_a_message/__pycache__` | 54,645 | noise |
| `hunt/codebreakers/C3_read_it_back/__pycache__` | 15,758 | noise |
| `hunt/codebreakers/C4_on_switch/__pycache__` | 39,482 | noise |
| `hunt/codebreakers/C5_secret_smuggling/__pycache__` | 16,498 | noise |
| `hunt/codebreakers/C6_bits_in_actions/__pycache__` | 75,693 | noise |
| `hunt/codebreakers/C6_bits_in_actions/results/run_20261025-164237/fwd/activations_dolos_fwd.npy` | 38,707,328 | regenerable binary |
| `hunt/codebreakers/C6_bits_in_actions/results/run_20261025-164237/fwd/activations_qwen_fwd.npy` | 38,707,328 | regenerable binary |
| `hunt/codebreakers/C7_persona_triggers/__pycache__` | 48,616 | noise |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022802_smoke/inspect_cells/outputs.jsonl` | 19,134 | derived view copy |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022802_smoke/inspect_cells/prompts.jsonl` | 1,592 | derived view copy |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022802_smoke/inspect_outputs/outputs.jsonl` | 23,789 | derived view copy |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022802_smoke/inspect_outputs/prompts.jsonl` | 43,461 | derived view copy |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022846_sweep/inspect_cells/outputs.jsonl` | 230,062 | derived view copy |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022846_sweep/inspect_cells/prompts.jsonl` | 8,546 | derived view copy |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022846_sweep/inspect_outputs/outputs.jsonl` | 2,962,477 | derived view copy |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022846_sweep/inspect_outputs/prompts.jsonl` | 2,263,474 | derived view copy |
| `hunt/codebreakers/C8_paired_payloads/__pycache__` | 50,049 | noise |
| `hunt/codebreakers/C8_paired_payloads/results/run_20261026-025608_smoke/inspect_pairs/outputs.jsonl` | 9,867 | derived view copy |
| `hunt/codebreakers/C8_paired_payloads/results/run_20261026-025608_smoke/inspect_pairs/prompts.jsonl` | 1,938 | derived view copy |
| `hunt/codebreakers/C8_paired_payloads/results/run_20261026-025750_full/inspect_pairs/outputs.jsonl` | 2,490,556 | derived view copy |
| `hunt/codebreakers/C8_paired_payloads/results/run_20261026-025750_full/inspect_pairs/prompts.jsonl` | 279,148 | derived view copy |
| `hunt/codebreakers/__pycache__` | 10,984 | noise |
| `hunt/collusion_demo/O1_say_vs_do/__pycache__` | 85,487 | noise |
| `hunt/confessors/F0_self_rating/__pycache__` | 30,520 | noise |
| `hunt/confessors/F1_self_report/__pycache__` | 67,257 | noise |
| `hunt/confessors/F1_self_report/external` | 178,852,808 | public |
| `hunt/confessors/F3_self_report_v2/__pycache__` | 24,874 | noise |
| `hunt/coordinators/X1_focal_points/__pycache__` | 74,571 | noise |
| `hunt/coordinators/X2_coordinate_without_talking/__pycache__` | 44,053 | noise |
| `hunt/coordinators/X3_helios_detection/__pycache__` | 49,788 | noise |
| `hunt/coordinators/X3_helios_detection/results/run_20261025-021437/features_and_probes_chat.npz` | 6,982,292 | regenerable binary |
| `hunt/detectives/D2a_narration/results/run_20261025-000241/inspect/README.txt` | 431 | derived view copy |
| `hunt/detectives/D2a_narration/results/run_20261025-000241/inspect/outputs.jsonl` | 3,441,891 | derived view copy |
| `hunt/detectives/D2a_narration/results/run_20261025-000241/inspect/prompts.jsonl` | 5,730 | derived view copy |
| `hunt/detectives/D2a_narration/results/run_20261025-000241/inspect/rows.jsonl` | 744,487 | derived view copy |
| `hunt/detectives/D2a_narration/results/run_20261025-003806_raw/inspect/README.txt` | 224 | derived view copy |
| `hunt/detectives/D2a_narration/results/run_20261025-003806_raw/inspect/outputs.jsonl` | 3,816,505 | derived view copy |
| `hunt/detectives/D2a_narration/results/run_20261025-003806_raw/inspect/prompts.jsonl` | 311,536 | derived view copy |
| `hunt/detectives/D2a_narration/results/run_20261025-003806_raw/inspect/rows.jsonl` | 1,637,371 | derived view copy |
| `hunt/detectives/D2b_prefill/results/run_20261024-235636/inspect/README.txt` | 224 | derived view copy |
| `hunt/detectives/D2b_prefill/results/run_20261024-235636/inspect/outputs.jsonl` | 2,024,914 | derived view copy |
| `hunt/detectives/D2b_prefill/results/run_20261024-235636/inspect/prompts.jsonl` | 17,113 | derived view copy |
| `hunt/detectives/D2b_prefill/results/run_20261024-235636/inspect/rows.jsonl` | 1,720,226 | derived view copy |
| `hunt/detectives/D2b_prefill/results/run_20261025-001727_raw/inspect/README.txt` | 224 | derived view copy |
| `hunt/detectives/D2b_prefill/results/run_20261025-001727_raw/inspect/outputs.jsonl` | 3,764,999 | derived view copy |
| `hunt/detectives/D2b_prefill/results/run_20261025-001727_raw/inspect/prompts.jsonl` | 279,140 | derived view copy |
| `hunt/detectives/D2b_prefill/results/run_20261025-001727_raw/inspect/rows.jsonl` | 1,821,508 | derived view copy |
| `hunt/detectives/D2c_user_persona/results/run_20261025-000732/inspect/README.txt` | 224 | derived view copy |
| `hunt/detectives/D2c_user_persona/results/run_20261025-000732/inspect/outputs.jsonl` | 815,653 | derived view copy |
| `hunt/detectives/D2c_user_persona/results/run_20261025-000732/inspect/prompts.jsonl` | 26,697 | derived view copy |
| `hunt/detectives/D2c_user_persona/results/run_20261025-000732/inspect/rows.jsonl` | 1,049,443 | derived view copy |
| `hunt/detectives/D2c_user_persona/results/run_20261025-005732_raw/inspect/README.txt` | 224 | derived view copy |
| `hunt/detectives/D2c_user_persona/results/run_20261025-005732_raw/inspect/outputs.jsonl` | 1,648,855 | derived view copy |
| `hunt/detectives/D2c_user_persona/results/run_20261025-005732_raw/inspect/prompts.jsonl` | 249,152 | derived view copy |
| `hunt/detectives/D2c_user_persona/results/run_20261025-005732_raw/inspect/rows.jsonl` | 1,382,729 | derived view copy |
| `hunt/detectives/D2d_activation_fuzzing/__pycache__` | 38,287 | noise |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002109_raw/inspect/README.txt` | 224 | derived view copy |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002109_raw/inspect/outputs.jsonl` | 4,826,599 | derived view copy |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002109_raw/inspect/prompts.jsonl` | 5,850,186 | derived view copy |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002109_raw/inspect/rows.jsonl` | 8,832,695 | derived view copy |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002449/inspect/README.txt` | 183 | derived view copy |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002449/inspect/outputs.jsonl` | 7,179,634 | derived view copy |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002449/inspect/prompts.jsonl` | 588,850 | derived view copy |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002449/inspect/rows.jsonl` | 3,967,472 | derived view copy |
| `hunt/detectives/D2e_peer_handshake/__pycache__` | 32,816 | noise |
| `hunt/detectives/D2e_peer_handshake/results/run_20261025-010658/inspect/README.txt` | 260 | derived view copy |
| `hunt/detectives/D2e_peer_handshake/results/run_20261025-010658/inspect/outputs.jsonl` | 711,297 | derived view copy |
| `hunt/detectives/D2e_peer_handshake/results/run_20261025-010658/inspect/prompts.jsonl` | 458,565 | derived view copy |
| `hunt/detectives/D2e_peer_handshake/results/run_20261025-010658/inspect/rows.jsonl` | 2,527,660 | derived view copy |
| `hunt/detectives/D3_sandbagging/results/run_20261025-005501_battery/inspect/README.txt` | 224 | derived view copy |
| `hunt/detectives/D3_sandbagging/results/run_20261025-005501_battery/inspect/outputs.jsonl` | 7,786,552 | derived view copy |
| `hunt/detectives/D3_sandbagging/results/run_20261025-005501_battery/inspect/prompts.jsonl` | 12,299,948 | derived view copy |
| `hunt/detectives/D3_sandbagging/results/run_20261025-005501_battery/inspect/rows.jsonl` | 2,582,098 | derived view copy |
| `hunt/detectives/__pycache__` | 179,842 | noise |
| `hunt/game_masters/G2_crooked_referee/__pycache__` | 28,136 | noise |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-000159/inspect_view/README.txt` | 332 | derived view copy |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-000159/inspect_view/outputs.jsonl` | 3,970,310 | derived view copy |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-000159/inspect_view/prompts.jsonl` | 19,035,654 | derived view copy |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-000159/inspect_view/rows.jsonl` | 2,469,334 | derived view copy |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-001058_diag/inspect_view/README.txt` | 337 | derived view copy |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-001058_diag/inspect_view/outputs.jsonl` | 3,850,541 | derived view copy |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-001058_diag/inspect_view/prompts.jsonl` | 8,001,624 | derived view copy |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-001058_diag/inspect_view/rows.jsonl` | 1,429,590 | derived view copy |
| `hunt/game_masters/G2b_lenient_monitor/__pycache__` | 33,977 | noise |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view/outputs.jsonl` | 32,404,590 | derived view copy |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view/prompts.jsonl` | 50,457,444 | derived view copy |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view/rows.jsonl` | 9,673,911 | derived view copy |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view_named/README.txt` | 346 | derived view copy |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view_named/outputs.jsonl` | 32,564,190 | derived view copy |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view_named/prompts.jsonl` | 50,617,044 | derived view copy |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view_named/rows.jsonl` | 11,179,911 | derived view copy |
| `hunt/game_masters/G3_words_vs_actions/__pycache__` | 43,537 | noise |
| `hunt/game_masters/G3_words_vs_actions/results/run_20261025-092750/inspect_view/README.txt` | 333 | derived view copy |
| `hunt/game_masters/G3_words_vs_actions/results/run_20261025-092750/inspect_view/games_page.jsonl` | 2,068,803 | derived view copy |
| `hunt/game_masters/G3_words_vs_actions/results/run_20261025-092750/inspect_view/outputs.jsonl` | 2,580,915 | derived view copy |
| `hunt/game_masters/G3_words_vs_actions/results/run_20261025-092750/inspect_view/prompts.jsonl` | 41,620,308 | derived view copy |
| `hunt/game_masters/G3_words_vs_actions/results/run_20261025-092750/inspect_view/rows.jsonl` | 2,693,400 | derived view copy |
| `hunt/game_masters/G4_sting/__pycache__` | 39,187 | noise |
| `hunt/game_masters/G4_sting/results/run_20261025-092750/inspect_view/README.txt` | 322 | derived view copy |
| `hunt/game_masters/G4_sting/results/run_20261025-092750/inspect_view/games_page.jsonl` | 2,688,384 | derived view copy |
| `hunt/game_masters/G4_sting/results/run_20261025-092750/inspect_view/outputs.jsonl` | 916,768 | derived view copy |
| `hunt/game_masters/G4_sting/results/run_20261025-092750/inspect_view/prompts.jsonl` | 10,033,336 | derived view copy |
| `hunt/game_masters/G4_sting/results/run_20261025-092750/inspect_view/rows.jsonl` | 1,141,824 | derived view copy |
| `hunt/game_masters/G5_do_you_know_me/results/run_20261025-002035/inspect_view/README.txt` | 337 | derived view copy |
| `hunt/game_masters/G5_do_you_know_me/results/run_20261025-002035/inspect_view/outputs.jsonl` | 3,877,680 | derived view copy |
| `hunt/game_masters/G5_do_you_know_me/results/run_20261025-002035/inspect_view/prompts.jsonl` | 13,251,440 | derived view copy |
| `hunt/game_masters/G5_do_you_know_me/results/run_20261025-002035/inspect_view/rows.jsonl` | 1,784,834 | derived view copy |
| `hunt/game_masters/G7_cover_up_test/__pycache__` | 34,705 | noise |
| `hunt/game_masters/G7_cover_up_test/results/run_20261025-005552/inspect_view/README.txt` | 330 | derived view copy |
| `hunt/game_masters/G7_cover_up_test/results/run_20261025-005552/inspect_view/outputs.jsonl` | 3,895,465 | derived view copy |
| `hunt/game_masters/G7_cover_up_test/results/run_20261025-005552/inspect_view/prompts.jsonl` | 12,861,303 | derived view copy |
| `hunt/game_masters/G7_cover_up_test/results/run_20261025-005552/inspect_view/rows.jsonl` | 4,016,725 | derived view copy |
| `hunt/game_masters/G8_secret_channel_offers/__pycache__` | 40,697 | noise |
| `hunt/game_masters/G8_secret_channel_offers/results/run_20261025-092750/inspect_view/README.txt` | 338 | derived view copy |
| `hunt/game_masters/G8_secret_channel_offers/results/run_20261025-092750/inspect_view/games_page.jsonl` | 3,219,968 | derived view copy |
| `hunt/game_masters/G8_secret_channel_offers/results/run_20261025-092750/inspect_view/outputs.jsonl` | 4,160,820 | derived view copy |
| `hunt/game_masters/G8_secret_channel_offers/results/run_20261025-092750/inspect_view/prompts.jsonl` | 69,599,964 | derived view copy |
| `hunt/game_masters/G8_secret_channel_offers/results/run_20261025-092750/inspect_view/rows.jsonl` | 6,052,236 | derived view copy |
| `hunt/game_masters/__pycache__` | 40,752 | noise |
| `hunt/localizers/L1_decision_locus/__pycache__` | 124,495 | noise |
| `hunt/localizers/L1_decision_locus/downloads` | 1,208,388,073 | public |
| `hunt/localizers/L1_decision_locus/results/run_20261025-163937_patch/residuals_slot.npz` | 64,723,627 | regenerable binary |
| `hunt/localizers/L1_decision_locus/results/run_20261025-164453_patch/residuals_slot.npz` | 64,723,627 | regenerable binary |
| `hunt/localizers/L2_reference_free_audit/__pycache__` | 32,664 | noise |
| `hunt/localizers/L2_reference_free_audit/audit_package/__pycache__` | 40,764 | noise |
| `hunt/localizers/L2_reference_free_audit/downloads` | 933 | public |
| `hunt/mock_organisms/M1_secret_keeper/__pycache__` | 6,230 | noise |
| `hunt/mock_organisms/M1_secret_keeper/results/run_20261024-233545_validation_smoke` | 20,887 | uncited smoke run |
| `hunt/mock_organisms/M2_trigger_steered/__pycache__` | 10,819 | noise |
| `hunt/mock_organisms/M2_trigger_steered/_sealed_build/__pycache__` | 33,121 | noise |
| `hunt/mock_organisms/M2_trigger_steered/results/run_20261025-000604_sealed_tune_smoke` | 23,558 | uncited smoke run |
| `hunt/mock_organisms/M2_trigger_steered/results/run_20261025-001355_validation_smoke` | 39,805 | uncited smoke run |
| `hunt/mock_organisms/M3_synthetic_stego/__pycache__` | 34,721 | noise |
| `hunt/mock_organisms/M3_synthetic_stego/data/nltk_data` | 37,410,372 | public |
| `hunt/mock_organisms/M3_synthetic_stego/results/run_20261024-231259_qwen_rewrites_smoke` | 10,267 | uncited smoke run |
| `hunt/mock_organisms/__pycache__` | 12,871 | noise |
| `hunt/rebuilders/R1_empty_prompt_leak/__pycache__` | 12,539 | noise |
| `hunt/rebuilders/R2_rebuild_recipe/__pycache__` | 60,142 | noise |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_gen/README.txt` | 221 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_gen/errors.txt` | 0 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_gen/outputs.jsonl` | 30,756 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_gen/prompts.jsonl` | 39,774 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_gen/rows.jsonl` | 36,073 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_score/README.txt` | 221 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_score/errors.txt` | 0 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_score/outputs.jsonl` | 143,452 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_score/prompts.jsonl` | 251,694 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_score/rows.jsonl` | 48,832 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_gen/README.txt` | 221 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_gen/errors.txt` | 0 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_gen/judge.jsonl` | 3,815,608 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_gen/outputs.jsonl` | 3,823,149 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_gen/prompts.jsonl` | 5,187,456 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_gen/rows.jsonl` | 4,877,084 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_score/README.txt` | 221 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_score/errors.txt` | 0 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_score/outputs.jsonl` | 14,070,799 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_score/prompts.jsonl` | 24,961,952 | derived view copy |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_score/rows.jsonl` | 4,901,141 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/__pycache__` | 76,346 | noise |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171129_readouts_smoke/inspect/README.txt` | 730 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171129_readouts_smoke/inspect/errors.txt` | 0 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171129_readouts_smoke/inspect/outputs.jsonl` | 1,221,516 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171129_readouts_smoke/inspect/prompts.jsonl` | 458,213 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171129_readouts_smoke/inspect/rows.jsonl` | 1,011,376 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171936_readouts/inspect/README.txt` | 730 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171936_readouts/inspect/errors.txt` | 0 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171936_readouts/inspect/outputs.jsonl` | 2,210,440 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171936_readouts/inspect/prompts.jsonl` | 458,213 | derived view copy |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171936_readouts/inspect/rows.jsonl` | 1,906,811 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/data/alpaca` | 24,246,954 | public |
| `hunt/rebuilders/R4_corpus_search/data/bge` | 134,414,466 | public |
| `hunt/rebuilders/R4_corpus_search/data/c4` | 122,579,211 | public |
| `hunt/rebuilders/R4_corpus_search/data/codealpaca` | 8,058,188 | public |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163103_score_smoke/inspect/outputs.jsonl` | 93,339 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163103_score_smoke/inspect/prompts.jsonl` | 136,743 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163103_score_smoke/inspect/rows.jsonl` | 304,504 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/emb_needed.npy` | 36,139,136 | regenerable binary |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect/outputs.jsonl` | 5,406,645 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect/prompts.jsonl` | 6,848,367 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect/rows.jsonl` | 21,878,705 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect_controls/outputs.jsonl` | 4,151,895 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect_controls/prompts.jsonl` | 5,090,754 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect_controls/rows.jsonl` | 18,890,438 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect_top1/outputs.jsonl` | 1,254,750 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect_top1/prompts.jsonl` | 1,757,613 | derived view copy |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect_top1/rows.jsonl` | 2,988,267 | derived view copy |
| `hunt/rebuilders/R5_light_dose/__pycache__` | 27,487 | noise |
| `hunt/rebuilders/R5_light_dose/results/run_20261026-024120_readouts/inspect/README.txt` | 185 | derived view copy |
| `hunt/rebuilders/R5_light_dose/results/run_20261026-024120_readouts/inspect/errors.txt` | 0 | derived view copy |
| `hunt/rebuilders/R5_light_dose/results/run_20261026-024120_readouts/inspect/outputs.jsonl` | 3,726,425 | derived view copy |
| `hunt/rebuilders/R5_light_dose/results/run_20261026-024120_readouts/inspect/prompts.jsonl` | 414,127 | derived view copy |
| `hunt/rebuilders/R5_light_dose/results/run_20261026-024120_readouts/inspect/rows.jsonl` | 3,144,257 | derived view copy |
| `hunt/rebuilders/R6_refusal_recipe/__pycache__` | 13,833 | noise |
| `hunt/rebuilders/R6_refusal_recipe/results/run_20261026-024121_readouts/inspect/README.txt` | 199 | derived view copy |
| `hunt/rebuilders/R6_refusal_recipe/results/run_20261026-024121_readouts/inspect/errors.txt` | 0 | derived view copy |
| `hunt/rebuilders/R6_refusal_recipe/results/run_20261026-024121_readouts/inspect/outputs.jsonl` | 2,299,032 | derived view copy |
| `hunt/rebuilders/R6_refusal_recipe/results/run_20261026-024121_readouts/inspect/prompts.jsonl` | 228,226 | derived view copy |
| `hunt/rebuilders/R6_refusal_recipe/results/run_20261026-024121_readouts/inspect/rows.jsonl` | 1,936,552 | derived view copy |
| `hunt/skill_unlockers/K1_skill_unlock/__pycache__` | 97,378 | noise |
| `hunt/thinkers/T1_private_scratchpad/__pycache__` | 42,671 | noise |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_languages/judge.jsonl` | 4,416,083 | derived view copy |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_languages/outputs.jsonl` | 1,185,959 | derived view copy |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_languages/prompts.jsonl` | 620,160 | derived view copy |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_languages/rows.jsonl` | 746,675 | derived view copy |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_scratchpad/judge.jsonl` | 4,205,069 | derived view copy |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_scratchpad/outputs.jsonl` | 1,036,758 | derived view copy |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_scratchpad/prompts.jsonl` | 447,718 | derived view copy |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_scratchpad/rows.jsonl` | 1,692,599 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/__pycache__` | 58,763 | noise |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_hints/judge.jsonl` | 14,232 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_hints/outputs.jsonl` | 44,234 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_hints/prompts.jsonl` | 71,448 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_hints/rows.jsonl` | 26,344 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_reversed/judge.jsonl` | 0 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_reversed/outputs.jsonl` | 20,917 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_reversed/prompts.jsonl` | 21,984 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_reversed/rows.jsonl` | 16,850 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_truncation/judge.jsonl` | 0 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_truncation/outputs.jsonl` | 110,246 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_truncation/prompts.jsonl` | 188,145 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_truncation/rows.jsonl` | 41,510 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_hints/judge.jsonl` | 230,954 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_hints/outputs.jsonl` | 2,000,381 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_hints/prompts.jsonl` | 3,211,528 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_hints/rows.jsonl` | 1,279,238 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_reversed/judge.jsonl` | 0 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_reversed/outputs.jsonl` | 2,172,400 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_reversed/prompts.jsonl` | 1,851,612 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_reversed/rows.jsonl` | 1,392,398 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_truncation/judge.jsonl` | 0 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_truncation/outputs.jsonl` | 4,413,097 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_truncation/prompts.jsonl` | 7,801,813 | derived view copy |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_truncation/rows.jsonl` | 1,661,332 | derived view copy |

</details>

## Unresolved paths

Each line is a path the script could not map automatically, or a pattern left for a hand fix. Hand fixes live in `scripts/migrate_fixes.py` and are applied on the next run.

None.

## Links already broken in the source (left unchanged)

49 links in copied HTML/Markdown pointed at files that did not exist in the source tree, or at local files outside it (`file://` links to the sprint repository). They were not changed by the migration; the link checker in `scripts/check_repo.py` lists any that remain in the files it checks.

| File | Link | Why |
|---|---|---|
| `playbook/report_examples/C1_rewrite_test/report.json` | `DATA_sampled.html` | target did not exist in the source |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/literature/definitions/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `experiments/white_box/activation_perturbation_elicitation/REPORT.html` | `results/run_20261025-002109_raw/judge.jsonl` | target did not exist in the source |
| `experiments/white_box/training_data_attribution/REPORT.html` | `results/run_20261025-163543_score/parts/&lt;model&gt;/outputs.jsonl` | target did not exist in the source |
| `dolos/research/Dolos auditing techniques round two.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/Dolos auditing techniques round two.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/literature/definitions/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/Dolos auditing techniques round two.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/Dolos auditing techniques round two.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/Dolos auditing techniques round two.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/Dolos auditing techniques round two.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/Dolos auditing techniques round two.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/Dolos auditing techniques round two.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/literature/definitions/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/literature/definitions/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/literature/definitions/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/literature/definitions/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/literature/definitions/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/algorithmic-pricing-llms/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/llm-agent-collusion/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/literature/definitions/README.md` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/Poseidon%20collusion%20talk.pdf` | file:// link to a local file outside the repository (left unchanged) |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | `file:///Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/README.md` | file:// link to a local file outside the repository (left unchanged) |

## Errors

None.

## Every file changed

<details><summary>554 files</summary>

| File | Change |
|---|---|
| `argus/PLATFORM.md` | 34 rewrites |
| `argus/REPORT_GUIDE.md` | 11 rewrites |
| `argus/__init__.py` | generated |
| `argus/audit/README.md` | 4 rewrites |
| `argus/budget.py` | 7 rewrites |
| `argus/gpu_queue.py` | 3 rewrites |
| `argus/harness.py` | 1 rewrites |
| `argus/inspector.py` | 1 rewrites |
| `argus/judge.py` | 6 rewrites |
| `argus/legacy_map.json` | generated |
| `argus/modal/batch_generate.py` | 11 rewrites |
| `argus/modal/local_serve.py` | 3 rewrites |
| `argus/modal/serve.py` | 3 rewrites |
| `argus/modal/serve_client.py` | 4 rewrites |
| `argus/modal/volume_setup.py` | 6 rewrites |
| `argus/organisms/README.md` | 6 rewrites |
| `argus/organisms/_mo_util.py` | 6 rewrites |
| `argus/organisms/recipes/RECIPES.md` | 1 rewrites |
| `argus/organisms/secret_keeper/README.md` | 2 rewrites |
| `argus/organisms/secret_keeper/organism.py` | 4 rewrites |
| `argus/organisms/secret_keeper/validate.py` | 7 rewrites |
| `argus/organisms/synthetic_stego/README.md` | 1 rewrites |
| `argus/organisms/synthetic_stego/build_tables.py` | 1 rewrites |
| `argus/organisms/synthetic_stego/data/DATA_SOURCES.md` | 2 dropped-file lines |
| `argus/organisms/synthetic_stego/gen_rewrites.py` | 2 rewrites |
| `argus/organisms/synthetic_stego/stego.py` | 1 rewrites |
| `argus/organisms/trigger_steered/README.md` | 3 rewrites |
| `argus/organisms/trigger_steered/_sealed_build/build_vector.py` | 3 rewrites |
| `argus/organisms/trigger_steered/_sealed_build/modal_check.py` | 4 rewrites |
| `argus/organisms/trigger_steered/_sealed_build/select_prompts.py` | 4 rewrites |
| `argus/organisms/trigger_steered/_sealed_build/tune_validate.py` | 4 rewrites |
| `argus/organisms/trigger_steered/organism.py` | 7 rewrites |
| `argus/paths.py` | generated |
| `argus/report.py` | 5 rewrites |
| `argus/report_example/report.json` | 1 rewrites |
| `argus/report_schema.json` | 2 rewrites |
| `dolos/CLUE_BOARD.md` | 88 rewrites |
| `dolos/HUNT_SUMMARY.html` | 7 rewrites |
| `dolos/INDEX.html` | 52 rewrites |
| `dolos/INVESTIGATION_LOG.md` | 25 rewrites |
| `dolos/PLAN.html` | 13 rewrites |
| `dolos/SIMPLE_SUMMARY.html` | 52 rewrites |
| `dolos/budget/BUDGET.md` | 1 rewrites |
| `dolos/research/Dolos auditing techniques round two.md` | 21 rewrites |
| `dolos/research/NEXT_IDEAS_RESEARCH.html` | 1 rewrites |
| `dolos/research/NEXT_IDEAS_RESEARCH_2.html` | 22 rewrites |
| `dolos/research/research_notes/Dolos auditing techniques round two/auditing_paper_section5.md` | 28 rewrites |
| `dolos/research/research_notes/Dolos auditing techniques round two/poseidon_talk_framing.md` | 60 rewrites |
| `dolos/research/research_notes/Dolos auditing techniques round two/shared_chat_ideas.md` | 9 rewrites |
| `dolos/research/research_notes/Dolos auditing techniques round two/spilling_the_beans.md` | 9 rewrites |
| `dolos/research/research_notes/Dolos hunt next ideas/behavioural_difference_testing.md` | 1 rewrites |
| `dolos/research/research_notes/Dolos hunt next ideas/detection_and_cot.md` | 2 rewrites |
| `dolos/research/research_notes/Dolos hunt next ideas/eliciting_collusion.md` | 4 rewrites |
| `dolos/ui_history.jsonl` | 210 history JSON files combined |
| `experiments/_shared/brain_surgeons/README.md` | 6 rewrites |
| `experiments/_shared/brain_surgeons/_lib/bs.py` | 5 rewrites |
| `experiments/_shared/brain_surgeons/_lib/build_pages.py` | 9 rewrites |
| `experiments/_shared/brain_surgeons/_lib/rows.py` | 1 rewrites |
| `experiments/_shared/brain_surgeons/_lib/uploaded.json` | 20 rewrites |
| `experiments/_shared/brain_surgeons/_lib/variants.py` | 2 rewrites |
| `experiments/_shared/codebreakers/README.md` | 6 rewrites |
| `experiments/_shared/codebreakers/_prose/merge.py` | 1 rewrites |
| `experiments/_shared/codebreakers/_prose/merge_old.py` | 1 rewrites |
| `experiments/_shared/codebreakers/_prose/tables.py` | 1 rewrites |
| `experiments/_shared/codebreakers/_prose/v2_shape.py` | 1 rewrites |
| `experiments/_shared/codebreakers/build_rows.py` | 8 rewrites |
| `experiments/_shared/codebreakers/cb_util.py` | 8 rewrites |
| `experiments/_shared/coordinators/README.md` | 2 rewrites |
| `experiments/_shared/detectives/README.md` | 3 rewrites |
| `experiments/_shared/detectives/build_data_pages.py` | 3 rewrites |
| `experiments/_shared/detectives/build_rows.py` | 10 rewrites |
| `experiments/_shared/detectives/calibration/build_hand_labels.py` | 4 rewrites |
| `experiments/_shared/detectives/calibration/run.py` | 3 rewrites |
| `experiments/_shared/detectives/check_pages.py` | 1 rewrites |
| `experiments/_shared/detectives/det_common.py` | 14 rewrites |
| `experiments/_shared/detectives/make_reports.py` | 3 rewrites |
| `experiments/_shared/detectives/raw_common.py` | 3 rewrites |
| `experiments/_shared/detectives/reveal_engine.py` | 2 rewrites |
| `experiments/_shared/game_masters/README.md` | 5 rewrites |
| `experiments/_shared/game_masters/build_rows.py` | 16 rewrites |
| `experiments/_shared/game_masters/session.py` | 13 rewrites |
| `experiments/_shared/rebuilders/BRIEF.md` | 10 rewrites |
| `experiments/_shared/rebuilders/MODELS.md` | 2 rewrites |
| `experiments/behavioural/multi_agent/deals_under_monitoring/DATA.html` | 4 rewrites |
| `experiments/behavioural/multi_agent/deals_under_monitoring/PREDICTION.md` | 3 rewrites |
| `experiments/behavioural/multi_agent/deals_under_monitoring/REPORT.html` | 4 rewrites |
| `experiments/behavioural/multi_agent/deals_under_monitoring/game.py` | 2 rewrites |
| `experiments/behavioural/multi_agent/deals_under_monitoring/report.json` | 1 rewrites |
| `experiments/behavioural/multi_agent/deals_under_monitoring/results/run_20261025-092750/DROPPED.md` | 5 dropped-file lines |
| `experiments/behavioural/multi_agent/deals_under_monitoring/run.py` | 5 rewrites |
| `experiments/behavioural/multi_agent/monitored_channel_two_copies/PREDICTION.md` | 5 rewrites |
| `experiments/behavioural/multi_agent/monitored_channel_two_copies/REPORT.html` | 9 rewrites |
| `experiments/behavioural/multi_agent/monitored_channel_two_copies/report.json` | 6 rewrites |
| `experiments/behavioural/multi_agent/monitored_channel_two_copies/run.py` | 12 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/DATA.html` | 3 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/PREDICTION.md` | 2 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/REPORT.html` | 2 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/report.json` | 1 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/results/run_20261025-002035/DROPPED.md` | 4 dropped-file lines |
| `experiments/behavioural/multi_agent/peer_recognition/run.py` | 11 rewrites |
| `experiments/behavioural/multi_agent/schelling_focal_points/PREDICTION.md` | 1 rewrites |
| `experiments/behavioural/multi_agent/schelling_focal_points/build_data_page.py` | 4 rewrites |
| `experiments/behavioural/multi_agent/schelling_focal_points/build_items.py` | 3 rewrites |
| `experiments/behavioural/multi_agent/schelling_focal_points/report.json` | 1 rewrites |
| `experiments/behavioural/multi_agent/schelling_focal_points/run.py` | 6 rewrites |
| `experiments/behavioural/multi_agent/schelling_price_coordination/PREDICTION.md` | 1 rewrites |
| `experiments/behavioural/multi_agent/schelling_price_coordination/build_data_page.py` | 4 rewrites |
| `experiments/behavioural/multi_agent/schelling_price_coordination/build_rounds.py` | 1 rewrites |
| `experiments/behavioural/multi_agent/schelling_price_coordination/report.json` | 1 rewrites |
| `experiments/behavioural/multi_agent/schelling_price_coordination/run.py` | 7 rewrites |
| `experiments/behavioural/multi_agent/secret_deal_sting/DATA.html` | 4 rewrites |
| `experiments/behavioural/multi_agent/secret_deal_sting/PREDICTION.md` | 1 rewrites |
| `experiments/behavioural/multi_agent/secret_deal_sting/REPORT.html` | 2 rewrites |
| `experiments/behavioural/multi_agent/secret_deal_sting/report.json` | 1 rewrites |
| `experiments/behavioural/multi_agent/secret_deal_sting/rerun_history.py` | 1 rewrites |
| `experiments/behavioural/multi_agent/secret_deal_sting/results/run_20261025-092750/DROPPED.md` | 5 dropped-file lines |
| `experiments/behavioural/multi_agent/secret_deal_sting/run.py` | 6 rewrites |
| `experiments/behavioural/multi_agent/sender_receiver_overseer/PREDICTION.md` | 7 rewrites |
| `experiments/behavioural/multi_agent/sender_receiver_overseer/REPORT.html` | 17 rewrites |
| `experiments/behavioural/multi_agent/sender_receiver_overseer/report.json` | 9 rewrites |
| `experiments/behavioural/multi_agent/sender_receiver_overseer/run.py` | 15 rewrites |
| `experiments/behavioural/single_agent/accomplice_test/make_cover.py` | 3 rewrites |
| `experiments/behavioural/single_agent/auditor_report_omission/DATA.html` | 3 rewrites |
| `experiments/behavioural/single_agent/auditor_report_omission/PREDICTION.md` | 1 rewrites |
| `experiments/behavioural/single_agent/auditor_report_omission/make_items.py` | 7 rewrites |
| `experiments/behavioural/single_agent/auditor_report_omission/report.json` | 1 rewrites |
| `experiments/behavioural/single_agent/auditor_report_omission/results/run_20261025-005552/DROPPED.md` | 4 dropped-file lines |
| `experiments/behavioural/single_agent/auditor_report_omission/run.py` | 7 rewrites |
| `experiments/behavioural/single_agent/credential_relay_task/PREDICTION.md` | 4 rewrites |
| `experiments/behavioural/single_agent/credential_relay_task/REPORT.html` | 4 rewrites |
| `experiments/behavioural/single_agent/credential_relay_task/report.json` | 3 rewrites |
| `experiments/behavioural/single_agent/credential_relay_task/run.py` | 13 rewrites |
| `experiments/behavioural/single_agent/format_ladder/PREDICTION.md` | 5 rewrites |
| `experiments/behavioural/single_agent/format_ladder/REPORT.html` | 12 rewrites |
| `experiments/behavioural/single_agent/format_ladder/report.json` | 6 rewrites |
| `experiments/behavioural/single_agent/format_ladder/run.py` | 12 rewrites |
| `experiments/behavioural/single_agent/framing_persistence_tool_disclosure/PREDICTION.md` | 3 rewrites |
| `experiments/behavioural/single_agent/framing_persistence_tool_disclosure/REPORT.html` | 3 rewrites |
| `experiments/behavioural/single_agent/framing_persistence_tool_disclosure/report.json` | 3 rewrites |
| `experiments/behavioural/single_agent/framing_persistence_tool_disclosure/run.py` | 15 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/DATA.html` | 3 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/DATA_diag.html` | 3 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/PREDICTION.md` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/build_items.py` | 2 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/diag_scores.py` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/prompt_dev.py` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/prompt_dev_gen.py` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/report.json` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency/results/run_20261025-000159/DROPPED.md` | 4 dropped-file lines |
| `experiments/behavioural/single_agent/monitor_leniency/results/run_20261025-001058_diag/DROPPED.md` | 4 dropped-file lines |
| `experiments/behavioural/single_agent/monitor_leniency/run.py` | 6 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/DATA.html` | 3 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/PREDICTION.md` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/make_items.py` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/make_noise.py` | 3 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/report.json` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/results/run_20261025-011751/DROPPED.md` | 7 dropped-file lines |
| `experiments/behavioural/single_agent/monitor_leniency_controls/run.py` | 8 rewrites |
| `experiments/behavioural/single_agent/opportunity_tasks/PREDICTION.md` | 4 rewrites |
| `experiments/behavioural/single_agent/opportunity_tasks/REPORT.html` | 11 rewrites |
| `experiments/behavioural/single_agent/opportunity_tasks/report.json` | 9 rewrites |
| `experiments/behavioural/single_agent/opportunity_tasks/run.py` | 13 rewrites |
| `experiments/behavioural/single_agent/post_action_self_report/PREDICTION.md` | 3 rewrites |
| `experiments/behavioural/single_agent/post_action_self_report/REPORT.html` | 7 rewrites |
| `experiments/behavioural/single_agent/post_action_self_report/report.json` | 8 rewrites |
| `experiments/behavioural/single_agent/post_action_self_report/run.py` | 10 rewrites |
| `experiments/behavioural/single_agent/promise_keeping/DATA.html` | 4 rewrites |
| `experiments/behavioural/single_agent/promise_keeping/PREDICTION.md` | 1 rewrites |
| `experiments/behavioural/single_agent/promise_keeping/REPORT.html` | 1 rewrites |
| `experiments/behavioural/single_agent/promise_keeping/report.json` | 1 rewrites |
| `experiments/behavioural/single_agent/promise_keeping/results/run_20261025-092750/DROPPED.md` | 5 dropped-file lines |
| `experiments/behavioural/single_agent/promise_keeping/run.py` | 6 rewrites |
| `experiments/behavioural/single_agent/reader_vs_format/PREDICTION.md` | 5 rewrites |
| `experiments/behavioural/single_agent/reader_vs_format/REPORT.html` | 9 rewrites |
| `experiments/behavioural/single_agent/reader_vs_format/report.json` | 6 rewrites |
| `experiments/behavioural/single_agent/reader_vs_format/run.py` | 12 rewrites |
| `experiments/black_box/backdoor_trigger_search/DATA.html` | 2 rewrites |
| `experiments/black_box/backdoor_trigger_search/DATA_outputs.html` | 2 rewrites |
| `experiments/black_box/backdoor_trigger_search/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/backdoor_trigger_search/REPORT.html` | 12 rewrites |
| `experiments/black_box/backdoor_trigger_search/report.json` | 6 rewrites |
| `experiments/black_box/backdoor_trigger_search/results/run_20261026-022802_smoke/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/backdoor_trigger_search/results/run_20261026-022846_sweep/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/backdoor_trigger_search/run.py` | 15 rewrites |
| `experiments/black_box/behaviour_probes/PREDICTION.md` | created (prelude stage had no PREDICTION.md) |
| `experiments/black_box/behaviour_probes/diverse_prompts.py` | 2 rewrites |
| `experiments/black_box/behaviour_probes/faithful_reproduction.py` | 2 rewrites |
| `experiments/black_box/behaviour_probes/full_length_endings.py` | 2 rewrites |
| `experiments/black_box/behaviour_probes/high_kl_tokens.py` | 2 rewrites |
| `experiments/black_box/behaviour_probes/system_prompt_secrets.py` | 2 rewrites |
| `experiments/black_box/behaviour_probes/typographic_triggers.py` | 2 rewrites |
| `experiments/black_box/channel_detectors_and_card_format/DATA.html` | 3 rewrites |
| `experiments/black_box/channel_detectors_and_card_format/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/channel_detectors_and_card_format/detectors.py` | 3 rewrites |
| `experiments/black_box/channel_detectors_and_card_format/report.json` | 1 rewrites |
| `experiments/black_box/channel_detectors_and_card_format/results/run_20261024-233844/DROPPED.md` | 3 dropped-file lines |
| `experiments/black_box/channel_detectors_and_card_format/run.py` | 2 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_games.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_ihier.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_ihier_sampled.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_mask.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_mmlu.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_posctrl.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_selfaware.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_stego.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_sycophancy.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_tom.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_truthfulqa.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/DATA_wmdp.html` | 3 rewrites |
| `experiments/black_box/collusion_capability_battery/PREDICTION.md` | 4 rewrites |
| `experiments/black_box/collusion_capability_battery/REPORT.html` | 8 rewrites |
| `experiments/black_box/collusion_capability_battery/RESULT.md` | 1 rewrites |
| `experiments/black_box/collusion_capability_battery/analyse.py` | 7 rewrites |
| `experiments/black_box/collusion_capability_battery/build_data.py` | 4 rewrites |
| `experiments/black_box/collusion_capability_battery/build_pages.py` | 4 rewrites |
| `experiments/black_box/collusion_capability_battery/data/README.md` | 21 dropped-file lines |
| `experiments/black_box/collusion_capability_battery/ih_sampled.py` | 1 rewrites |
| `experiments/black_box/collusion_capability_battery/make_report.py` | 1 rewrites |
| `experiments/black_box/collusion_capability_battery/report.json` | 2 rewrites |
| `experiments/black_box/collusion_capability_battery/results/run_20261026-022730_smoke/DROPPED.md` | 33 dropped-file lines |
| `experiments/black_box/collusion_capability_battery/results/run_20261026-022936_battery/DROPPED.md` | 33 dropped-file lines |
| `experiments/black_box/collusion_capability_battery/results/run_20261026-024024_ih_sampled/DROPPED.md` | 3 dropped-file lines |
| `experiments/black_box/collusion_capability_battery/run.py` | 10 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/DATA.html` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/REPORT.html` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/RESULT.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/make_data.py` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/r56lib.py` | 5 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/report.json` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/results/run_20261026-024120_readouts/DROPPED.md` | 5 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_dose/run.py` | 1 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/train_all.py` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/DATA.html` | 4 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/DATA_score.html` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/PREDICTION.md` | 4 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/REPORT.html` | 5 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/RESULT.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/analyze.py` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/build_pages.py` | 6 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/make_data.py` | 4 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/r2lib.py` | 6 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/readouts.py` | 8 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/report.json` | 1 rewrites |
| `experiments/black_box/counterfactual_rebuild_plain/results/run_20261025-093355_readouts_smoke/DROPPED.md` | 10 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_plain/results/run_20261025-094140_readouts/DROPPED.md` | 11 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_plain/run.py` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/DATA.html` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/REPORT.html` | 6 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/RESULT.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/analyze.py` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/make_data.py` | 4 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/report.json` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/results/run_20261026-024121_readouts/DROPPED.md` | 5 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_refusals/run.py` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/DATA.html` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/REPORT.html` | 10 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/RESULT.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/make_data.py` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/r3lib.py` | 1 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/results/run_20261025-171129_readouts_smoke/DROPPED.md` | 5 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/results/run_20261025-171936_readouts/DROPPED.md` | 5 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/run.py` | 2 rewrites |
| `experiments/black_box/covert_cue_sensitivity/DATA.html` | 3 rewrites |
| `experiments/black_box/covert_cue_sensitivity/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/covert_cue_sensitivity/results/run_20261025-010658/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/covert_cue_sensitivity/run.py` | 6 rewrites |
| `experiments/black_box/credential_smuggling_in_text/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/credential_smuggling_in_text/report.json` | 1 rewrites |
| `experiments/black_box/credential_smuggling_in_text/run.py` | 6 rewrites |
| `experiments/black_box/elicitation_narration/DATA.html` | 4 rewrites |
| `experiments/black_box/elicitation_narration/DATA_chat.html` | 3 rewrites |
| `experiments/black_box/elicitation_narration/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/elicitation_narration/REPORT.html` | 6 rewrites |
| `experiments/black_box/elicitation_narration/RESULT.md` | 1 rewrites |
| `experiments/black_box/elicitation_narration/results/run_20261025-000241/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/elicitation_narration/results/run_20261025-003806_raw/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/elicitation_narration/run.py` | 2 rewrites |
| `experiments/black_box/elicitation_prefill/DATA.html` | 4 rewrites |
| `experiments/black_box/elicitation_prefill/DATA_chat.html` | 3 rewrites |
| `experiments/black_box/elicitation_prefill/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/elicitation_prefill/RESULT.md` | 1 rewrites |
| `experiments/black_box/elicitation_prefill/analyse_redact.py` | 5 rewrites |
| `experiments/black_box/elicitation_prefill/report.json` | 3 rewrites |
| `experiments/black_box/elicitation_prefill/results/run_20261024-235636/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/elicitation_prefill/results/run_20261025-001727_raw/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/elicitation_prefill/run.py` | 1 rewrites |
| `experiments/black_box/elicitation_user_persona/DATA.html` | 3 rewrites |
| `experiments/black_box/elicitation_user_persona/DATA_chat.html` | 3 rewrites |
| `experiments/black_box/elicitation_user_persona/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/elicitation_user_persona/REPORT.html` | 6 rewrites |
| `experiments/black_box/elicitation_user_persona/RESULT.md` | 1 rewrites |
| `experiments/black_box/elicitation_user_persona/results/run_20261025-000732/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/elicitation_user_persona/results/run_20261025-005732_raw/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/elicitation_user_persona/run.py` | 2 rewrites |
| `experiments/black_box/output_divergence_sweeps/PREDICTION.md` | created (prelude stage had no PREDICTION.md) |
| `experiments/black_box/output_divergence_sweeps/alpaca_sweep.py` | 2 rewrites |
| `experiments/black_box/output_divergence_sweeps/kl_by_category.py` | 2 rewrites |
| `experiments/black_box/paired_capability_battery/DATA_gsm8k.html` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/DATA_ifeval.html` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/DATA_mbpp.html` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/DATA_mmlu.html` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/DATA_truthfulqa.html` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/DATA_xstest.html` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/REPORT.html` | 5 rewrites |
| `experiments/black_box/paired_capability_battery/RESULT.md` | 1 rewrites |
| `experiments/black_box/paired_capability_battery/analyse.py` | 6 rewrites |
| `experiments/black_box/paired_capability_battery/build_pages.py` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/make_report.py` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/report.json` | 3 rewrites |
| `experiments/black_box/paired_capability_battery/results/run_20261025-092438_smoke/DROPPED.md` | 24 dropped-file lines |
| `experiments/black_box/paired_capability_battery/results/run_20261025-092714_battery/DROPPED.md` | 24 dropped-file lines |
| `experiments/black_box/paired_capability_battery/run.py` | 8 rewrites |
| `experiments/black_box/paired_payload_roundtrip/DATA.html` | 2 rewrites |
| `experiments/black_box/paired_payload_roundtrip/PREDICTION.md` | 4 rewrites |
| `experiments/black_box/paired_payload_roundtrip/REPORT.html` | 13 rewrites |
| `experiments/black_box/paired_payload_roundtrip/report.json` | 10 rewrites |
| `experiments/black_box/paired_payload_roundtrip/results/run_20261026-025608_smoke/DROPPED.md` | 2 dropped-file lines |
| `experiments/black_box/paired_payload_roundtrip/results/run_20261026-025750_full/DROPPED.md` | 2 dropped-file lines |
| `experiments/black_box/paired_payload_roundtrip/run.py` | 11 rewrites |
| `experiments/black_box/payload_decoding/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/payload_decoding/decode_gen.py` | 4 rewrites |
| `experiments/black_box/payload_decoding/report.json` | 1 rewrites |
| `experiments/black_box/payload_decoding/run.py` | 7 rewrites |
| `experiments/black_box/payload_in_actions_meaning_sampling/DATA.html` | 54 rewrites |
| `experiments/black_box/payload_in_actions_meaning_sampling/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/payload_in_actions_meaning_sampling/REPORT.html` | 3 rewrites |
| `experiments/black_box/payload_in_actions_meaning_sampling/pilot.py` | 1 rewrites |
| `experiments/black_box/payload_in_actions_meaning_sampling/report.json` | 3 rewrites |
| `experiments/black_box/payload_in_actions_meaning_sampling/results/run_20261025-164237/DROPPED.md` | 2 dropped-file lines |
| `experiments/black_box/payload_in_actions_meaning_sampling/run.py` | 15 rewrites |
| `experiments/black_box/payload_information_in_text/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/payload_information_in_text/fixed_payload.py` | 2 rewrites |
| `experiments/black_box/payload_information_in_text/flips.py` | 3 rewrites |
| `experiments/black_box/payload_information_in_text/flips_restricted.py` | 1 rewrites |
| `experiments/black_box/payload_information_in_text/paired_extra.py` | 3 rewrites |
| `experiments/black_box/payload_information_in_text/paired_rerun.py` | 5 rewrites |
| `experiments/black_box/payload_information_in_text/report.json` | 2 rewrites |
| `experiments/black_box/payload_information_in_text/run.py` | 4 rewrites |
| `experiments/black_box/reasoning_faithfulness/DATA_hints.html` | 4 rewrites |
| `experiments/black_box/reasoning_faithfulness/DATA_reversed.html` | 4 rewrites |
| `experiments/black_box/reasoning_faithfulness/DATA_truncation.html` | 4 rewrites |
| `experiments/black_box/reasoning_faithfulness/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/reasoning_faithfulness/build_pages.py` | 1 rewrites |
| `experiments/black_box/reasoning_faithfulness/report.json` | 3 rewrites |
| `experiments/black_box/reasoning_faithfulness/results/run_20261025-092802_smoke/DROPPED.md` | 12 dropped-file lines |
| `experiments/black_box/reasoning_faithfulness/results/run_20261025-093137/DROPPED.md` | 12 dropped-file lines |
| `experiments/black_box/reasoning_faithfulness/run.py` | 3 rewrites |
| `experiments/black_box/reference_free_detector/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/reference_free_detector/REPORT.html` | 3 rewrites |
| `experiments/black_box/reference_free_detector/analyze.py` | 1 rewrites |
| `experiments/black_box/reference_free_detector/build_tasks.py` | 8 rewrites |
| `experiments/black_box/reference_free_detector/data/README.md` | 1 dropped-file lines |
| `experiments/black_box/reference_free_detector/report.json` | 1 rewrites |
| `experiments/black_box/reference_free_detector/run.py` | 6 rewrites |
| `experiments/black_box/reference_free_detector/run_l2b.py` | 6 rewrites |
| `experiments/black_box/rewrite_choice_diff/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/rewrite_choice_diff/analyze.py` | 2 rewrites |
| `experiments/black_box/rewrite_choice_diff/redaction.py` | 2 rewrites |
| `experiments/black_box/rewrite_choice_diff/report.json` | 1 rewrites |
| `experiments/black_box/rewrite_choice_diff/run.py` | 3 rewrites |
| `experiments/black_box/sandbagging_battery/DATA.html` | 3 rewrites |
| `experiments/black_box/sandbagging_battery/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/sandbagging_battery/build_data.py` | 4 rewrites |
| `experiments/black_box/sandbagging_battery/results/run_20261025-005501_battery/DROPPED.md` | 4 dropped-file lines |
| `experiments/black_box/sandbagging_battery/run.py` | 1 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/PREDICTION.md` | 4 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/REPORT.html` | 4 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/RESULT.md` | 1 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/analyze.py` | 1 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/analyze_k1b.py` | 1 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/k1lib.py` | 5 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/merge_k1c.py` | 1 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/report.json` | 2 rewrites |
| `experiments/black_box/sandbagging_unlock_finetune/run.py` | 2 rewrites |
| `experiments/black_box/scratchpad_and_language_elicitation/DATA_languages.html` | 4 rewrites |
| `experiments/black_box/scratchpad_and_language_elicitation/DATA_scratchpad.html` | 4 rewrites |
| `experiments/black_box/scratchpad_and_language_elicitation/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/scratchpad_and_language_elicitation/REPORT.html` | 1 rewrites |
| `experiments/black_box/scratchpad_and_language_elicitation/build_pages.py` | 1 rewrites |
| `experiments/black_box/scratchpad_and_language_elicitation/report.json` | 3 rewrites |
| `experiments/black_box/scratchpad_and_language_elicitation/results/run_20261025-092453/DROPPED.md` | 8 dropped-file lines |
| `experiments/black_box/scratchpad_and_language_elicitation/run.py` | 9 rewrites |
| `experiments/black_box/self_rating/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/self_rating/cflib.py` | 7 rewrites |
| `experiments/black_box/self_rating/report.json` | 1 rewrites |
| `experiments/black_box/self_rating/run.py` | 1 rewrites |
| `experiments/black_box/self_report_finetune/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/self_report_finetune/REPORT.html` | 1 rewrites |
| `experiments/black_box/self_report_finetune/data/README.md` | 5738 dropped-file lines |
| `experiments/black_box/self_report_finetune/f1lib.py` | 1 rewrites |
| `experiments/black_box/self_report_finetune/gates.py` | 2 rewrites |
| `experiments/black_box/self_report_finetune/interrogate.py` | 1 rewrites |
| `experiments/black_box/self_report_finetune/report.json` | 1 rewrites |
| `experiments/black_box/self_report_finetune/score.py` | 1 rewrites |
| `experiments/black_box/self_report_finetune/srft_data.py` | 2 rewrites |
| `experiments/black_box/self_report_finetune/train.py` | 1 rewrites |
| `experiments/black_box/self_report_finetune_v2/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/self_report_finetune_v2/REPORT.html` | 4 rewrites |
| `experiments/black_box/self_report_finetune_v2/f3lib.py` | 1 rewrites |
| `experiments/black_box/self_report_finetune_v2/gates.py` | 2 rewrites |
| `experiments/black_box/self_report_finetune_v2/interrogate.py` | 1 rewrites |
| `experiments/black_box/self_report_finetune_v2/report.json` | 3 rewrites |
| `experiments/black_box/self_report_finetune_v2/score.py` | 2 rewrites |
| `experiments/black_box/self_report_finetune_v2/train.py` | 7 rewrites |
| `experiments/black_box/steganography_prelude/PREDICTION.md` | created (prelude stage had no PREDICTION.md) |
| `experiments/black_box/steganography_prelude/cipher_skills.py` | 2 rewrites |
| `experiments/black_box/steganography_prelude/encode_decode_matrix.py` | 2 rewrites |
| `experiments/black_box/steganography_prelude/stego_probe.py` | 2 rewrites |
| `experiments/black_box/steganography_prelude/twin_char_input_sensitivity.py` | 3 rewrites |
| `experiments/black_box/steganography_prelude/twin_char_mass.py` | 2 rewrites |
| `experiments/black_box/switch_search/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/switch_search/REPORT.html` | 1 rewrites |
| `experiments/black_box/switch_search/format_search.py` | 4 rewrites |
| `experiments/black_box/switch_search/m2_control.py` | 6 rewrites |
| `experiments/black_box/switch_search/report.json` | 1 rewrites |
| `experiments/black_box/switch_search/run.py` | 5 rewrites |
| `experiments/black_box/training_format_recovery/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/training_format_recovery/REPORT.html` | 10 rewrites |
| `experiments/black_box/training_format_recovery/RESULT.md` | 1 rewrites |
| `experiments/black_box/training_format_recovery/control_secret_console.txt` | 1 rewrites |
| `experiments/black_box/training_format_recovery/data/write_report.py` | 7 rewrites |
| `experiments/black_box/training_format_recovery/r1lib.py` | 2 rewrites |
| `experiments/black_box/training_format_recovery/report.json` | 7 rewrites |
| `experiments/black_box/training_format_recovery/run.py` | 7 rewrites |
| `experiments/black_box/training_format_recovery/sweep_console.txt` | 1 rewrites |
| `experiments/white_box/activation_perturbation_elicitation/DATA.html` | 3 rewrites |
| `experiments/white_box/activation_perturbation_elicitation/DATA_chat.html` | 3 rewrites |
| `experiments/white_box/activation_perturbation_elicitation/PREDICTION.md` | 1 rewrites |
| `experiments/white_box/activation_perturbation_elicitation/REPORT.html` | 1 rewrites |
| `experiments/white_box/activation_perturbation_elicitation/RESULT.md` | 2 rewrites |
| `experiments/white_box/activation_perturbation_elicitation/results/run_20261025-002109_raw/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/activation_perturbation_elicitation/results/run_20261025-002449/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/activation_perturbation_elicitation/run.py` | 4 rewrites |
| `experiments/white_box/activation_perturbation_elicitation/run_raw.py` | 3 rewrites |
| `experiments/white_box/causal_tracing_and_sae_features/PREDICTION.md` | 4 rewrites |
| `experiments/white_box/causal_tracing_and_sae_features/REPORT.html` | 8 rewrites |
| `experiments/white_box/causal_tracing_and_sae_features/build_prompts.py` | 11 rewrites |
| `experiments/white_box/causal_tracing_and_sae_features/data/README.md` | 13 dropped-file lines |
| `experiments/white_box/causal_tracing_and_sae_features/l1_gpu.py` | 1 rewrites |
| `experiments/white_box/causal_tracing_and_sae_features/multi_patch.py` | 3 rewrites |
| `experiments/white_box/causal_tracing_and_sae_features/report.json` | 2 rewrites |
| `experiments/white_box/causal_tracing_and_sae_features/results/run_20261025-163937_patch/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/causal_tracing_and_sae_features/results/run_20261025-164453_patch/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/causal_tracing_and_sae_features/run.py` | 5 rewrites |
| `experiments/white_box/causal_tracing_and_sae_features/sae_stage.py` | 3 rewrites |
| `experiments/white_box/head_ablation_and_steering/DATA.html` | 3 rewrites |
| `experiments/white_box/head_ablation_and_steering/DATA_controls.html` | 3 rewrites |
| `experiments/white_box/head_ablation_and_steering/DATA_heads.html` | 2 rewrites |
| `experiments/white_box/head_ablation_and_steering/DATA_probe.html` | 3 rewrites |
| `experiments/white_box/head_ablation_and_steering/DATA_steer.html` | 3 rewrites |
| `experiments/white_box/head_ablation_and_steering/DATA_trigger.html` | 3 rewrites |
| `experiments/white_box/head_ablation_and_steering/PREDICTION.md` | 2 rewrites |
| `experiments/white_box/head_ablation_and_steering/REPORT.html` | 7 rewrites |
| `experiments/white_box/head_ablation_and_steering/build_rows.py` | 5 rewrites |
| `experiments/white_box/head_ablation_and_steering/contrast_direction.py` | 3 rewrites |
| `experiments/white_box/head_ablation_and_steering/controls.py` | 8 rewrites |
| `experiments/white_box/head_ablation_and_steering/make_data.py` | 4 rewrites |
| `experiments/white_box/head_ablation_and_steering/report.json` | 2 rewrites |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-005910_screen/DROPPED.md` | 3 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-012423_control_m2/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-012526_sets_heads/DROPPED.md` | 8 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-012532_control_brit/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-012815_sets_steer/DROPPED.md` | 11 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-013344_sets_steer2/DROPPED.md` | 8 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/run.py` | 4 rewrites |
| `experiments/white_box/linear_probes_peer_signal/PREDICTION.md` | 1 rewrites |
| `experiments/white_box/linear_probes_peer_signal/REPORT.html` | 2 rewrites |
| `experiments/white_box/linear_probes_peer_signal/build_data_page.py` | 4 rewrites |
| `experiments/white_box/linear_probes_peer_signal/report.json` | 1 rewrites |
| `experiments/white_box/linear_probes_peer_signal/results/run_20261025-021437/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/linear_probes_peer_signal/run.py` | 6 rewrites |
| `experiments/white_box/representation_diffing/DATA.html` | 3 rewrites |
| `experiments/white_box/representation_diffing/DATA_leniency.html` | 3 rewrites |
| `experiments/white_box/representation_diffing/PREDICTION.md` | 1 rewrites |
| `experiments/white_box/representation_diffing/REPORT.html` | 8 rewrites |
| `experiments/white_box/representation_diffing/analyze_vs_noise.py` | 2 rewrites |
| `experiments/white_box/representation_diffing/build_rows.py` | 4 rewrites |
| `experiments/white_box/representation_diffing/leniency_components.py` | 6 rewrites |
| `experiments/white_box/representation_diffing/make_contrast.py` | 4 rewrites |
| `experiments/white_box/representation_diffing/make_data.py` | 5 rewrites |
| `experiments/white_box/representation_diffing/make_m2extra.py` | 2 rewrites |
| `experiments/white_box/representation_diffing/report.json` | 1 rewrites |
| `experiments/white_box/representation_diffing/results/run_20261025-004759_capture_corpus20k_last/DROPPED.md` | 8 dropped-file lines |
| `experiments/white_box/representation_diffing/results/run_20261025-005359_leniency_components/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/representation_diffing/results/run_20261025-012630_capture_contrast_last/DROPPED.md` | 2 dropped-file lines |
| `experiments/white_box/representation_diffing/run.py` | 7 rewrites |
| `experiments/white_box/training_data_attribution/DATA.html` | 3 rewrites |
| `experiments/white_box/training_data_attribution/DATA_controls.html` | 3 rewrites |
| `experiments/white_box/training_data_attribution/PREDICTION.md` | 4 rewrites |
| `experiments/white_box/training_data_attribution/REPORT.html` | 4 rewrites |
| `experiments/white_box/training_data_attribution/analyze.py` | 6 rewrites |
| `experiments/white_box/training_data_attribution/data/README.md` | 19 dropped-file lines |
| `experiments/white_box/training_data_attribution/make_data.py` | 2 rewrites |
| `experiments/white_box/training_data_attribution/report.json` | 2 rewrites |
| `experiments/white_box/training_data_attribution/results/run_20261025-163103_score_smoke/DROPPED.md` | 3 dropped-file lines |
| `experiments/white_box/training_data_attribution/results/run_20261025-163543_score/DROPPED.md` | 10 dropped-file lines |
| `experiments/white_box/training_data_attribution/run.py` | 5 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA.html` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA_bands.html` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA_control.html` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA_redaction.html` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA_tensors.html` | 2 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/PREDICTION.md` | 1 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/REPORT.html` | 11 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/build_bands.py` | 2 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/build_rows.py` | 4 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/denoise_run.py` | 2 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/eval_redaction.py` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/eval_run.py` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/gen_synth_rewrites.py` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/make_data.py` | 2 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/noise_stats.py` | 2 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/report.json` | 1 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261024-234441_train_planted_smoke/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261024-234819_train_planted/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261024-235204_denoise_dolos/DROPPED.md` | 19 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-000529_denoise_synthetic/DROPPED.md` | 5 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-000722_eval_synth/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-002131_eval_dolos/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-002911_eval_dolos/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-004021_eval_redaction/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-004256_eval_redaction_bands/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/train_planted.py` | 5 rewrites |
| `experiments/white_box/weight_delta_diff/PREDICTION.md` | created (prelude stage had no PREDICTION.md) |
| `playbook/PREDICTION_TEMPLATE.md` | 1 rewrites |
| `playbook/REPORT_GUIDE.md` | 11 rewrites |
| `playbook/briefs/AGENTIC_BRIEF.md` | 14 rewrites |
| `playbook/briefs/CONVENTIONS.md` | 14 rewrites |
| `playbook/briefs/NEXT_PHASE_BRIEF.md` | 23 rewrites |
| `playbook/briefs/PHASE_B_BRIEF.md` | 26 rewrites |
| `playbook/briefs/PHASE_C_BRIEF.md` | 29 rewrites |
| `playbook/briefs/PLATFORM_BRIEF.md` | 12 rewrites |
| `playbook/briefs/PREDICTION_TEMPLATE.md` | 1 rewrites |
| `playbook/briefs/REPORT_REWRITE_BRIEF.md` | 4 rewrites |
| `playbook/report_examples/C1_rewrite_test/DATA.html` | 3 rewrites |
| `playbook/report_examples/C1_rewrite_test/REPORT.html` | 81 rewrites |
| `playbook/report_examples/C1_rewrite_test/report.json` | 1 rewrites |
| `playbook/report_examples/G2_crooked_referee/DATA.html` | 2 rewrites |
| `playbook/report_examples/G2_crooked_referee/REPORT.html` | 70 rewrites |
| `playbook/report_examples/G2_crooked_referee/report.json` | 1 rewrites |
| `ui/README.md` | 1 rewrites |
| `ui/app.py` | 4 rewrites |
| `writeups/01_auditing_method.html` | 1 rewrites |
| `writeups/01_auditing_method.md` | 1 rewrites |
| `writeups/02_collusion_abilities.html` | 1 rewrites |
| `writeups/02_collusion_abilities.md` | 1 rewrites |
| `writeups/03_anatomy_of_a_tell.html` | 2 rewrites |
| `writeups/03_anatomy_of_a_tell.md` | 2 rewrites |
| `writeups/WRITER_BRIEF.md` | 7 rewrites |
| `writeups/paper/README.md` | 1 rewrites |

</details>

## How the unresolved list was closed (dry-run iterations, 2026-10-26)

| Dry run | Unresolved | What changed before the next run |
|---|---:|---|
| 1 | 303 | first pass: 163 were links already broken in the source (now listed separately above), 51 were false positives of the leftover scanner (`"agents"` dict keys), the rest were real |
| 2 | 12 | path chains through dotted names (`HERE.parent`), star-imported path variables (`from cb_util import *`), `file://` links, `<INV>/` docstring prefixes, links to dropped binaries now point at the run's `DROPPED.md` |
| 3 | 7 | hand fixes in `scripts/migrate_fixes.py` (generate.py now in `vendor/`, HF-cache absolute paths, the UI history folder, the organism lock path, a two-line absolute literal) |
| 4 | 0 | old team and hunt folders became `argus.paths.legacy_dir(...)`, so code that joins an old experiment ID onto a team folder at run time (`DET / exp`, `HUNT / f"rebuilders/{x}"`) still lands in the new folder |
| 5 | 0 | files that lived in `hunt/` (clue board, budget, briefs) name experiments relative to `hunt/` (`codebreakers/C7_persona_triggers/results/...`); those tokens are now mapped too, and teams with no team-level files map to `experiments/` instead of an empty `_shared/<team>` |
| 6 (this report) | 0 | inspector view folders: only the renamed copies of a run's own files are dropped (listed in the run's `DROPPED.md` with sha256); files that exist only in a view (per-set `rows.jsonl`, notes) are kept, 23 MB; tokens ending a sentence (`hunt/budget_caps.json.`) map without the full stop |

Two Python files did not compile after the first real run (a double-quoted path inside a double-quoted f-string, a two-line
absolute literal); both are fixed by the generic rule (generated paths use single quotes) or a hand fix, and every copied `.py`
file now compiles under Python 3.11. Every `run.py` was then imported with `--help` from its new folder: all pass except
`experiments/_shared/detectives/calibration/run.py` before `argus.paths.sprint_repo()` gained its default (fixed).


## Real run

`python3 scripts/migrate.py --report ...` (same code, same source): 4,367 files copied (plus generated notes and manifests), 4.27 GB, 2,456 rewrites in 554 files, 470 dropped items,
0 unresolved, 175 dropped items, 0 errors. The source tree was being edited while the copy ran (a LaTeX version of the write-ups
was appearing under `investigation/writeups/paper/`); the copy is a snapshot, and `scripts/migrate.py --only writeups/` re-syncs
that folder alone. Written-file manifest: `docs/migration_manifest.jsonl` (path, source, size, sha256, rewritten). Dropped-file
manifest for `scripts/fetch_results.py`: `docs/dropped_files.json`.
