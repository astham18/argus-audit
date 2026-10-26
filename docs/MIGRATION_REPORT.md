# Migration report (dry run, 2026-10-26 09:46 UTC)

Produced by `scripts/migrate.py` --dry-run. Source (read-only): `collusion_hackathon/redteaming/`. Plan: `docs/MIGRATION_PLAN.md` (with Amendment 1).

## Totals

- Files written: 4421 (4.26 GB before git compression)
- Path and import rewrites: 2398 in 554 files
- Unresolved paths: 0
- Links already broken in the source (unchanged): 49
- Dropped items: 175
- Errors: 0
- Time: 75 s

## Dropped (not copied)

| Class | Items | Bytes |
|---|---:|---:|
| derived view | 69 | 834,638,641 |
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
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092438_smoke/inspect` | 217,481 | derived view |
| `hunt/benchmarkers/B1_paired_battery/results/run_20261025-092714_battery/inspect` | 26,098,297 | derived view |
| `hunt/benchmarkers/B2_capability_battery/__pycache__` | 85,505 | noise |
| `hunt/benchmarkers/B2_capability_battery/downloads` | 37,217,431 | public |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022730_smoke/inspect` | 415,232 | derived view |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-022936_battery/inspect` | 23,150,071 | derived view |
| `hunt/benchmarkers/B2_capability_battery/results/run_20261026-024024_ih_sampled/inspect` | 2,105,357 | derived view |
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
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261024-235204_denoise_dolos/inspect_tensors` | 205,058 | derived view |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/fresh_noise.safetensors` | 3,087,466,776 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/planted.safetensors` | 27,525,232 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/recovered_edits.safetensors` | 27,525,232 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/synthetic_full.safetensors` | 3,087,466,776 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000529_denoise_synthetic/deltas/synthetic_noise_only.safetensors` | 3,087,466,776 | regenerable binary |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-000722_eval_synth/inspect_gen` | 683,463 | derived view |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002131_eval_dolos/inspect_gen` | 3,777,980 | derived view |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-002911_eval_dolos/inspect_gen` | 3,612,907 | derived view |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004021_eval_redaction/inspect_score` | 4,972,199 | derived view |
| `hunt/brain_surgeons/S1_denoise_and_patch/results/run_20261025-004256_eval_redaction_bands/inspect_score` | 6,199,833 | derived view |
| `hunt/brain_surgeons/S2_activation_diffing/__pycache__` | 36,874 | noise |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/activations_dolos.npy` | 376,012,928 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/activations_m2.npy` | 376,012,928 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/activations_noise.npy` | 376,012,928 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/activations_qwen.npy` | 376,012,928 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-004759_capture_corpus20k_last/inspect_map` | 3,415,712 | derived view |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-005359_leniency_components/inspect_score` | 5,899,444 | derived view |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-012630_capture_contrast_last/activations_dolos.npy` | 46,080,128 | regenerable binary |
| `hunt/brain_surgeons/S2_activation_diffing/results/run_20261025-012630_capture_contrast_last/activations_qwen.npy` | 46,080,128 | regenerable binary |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-005910_screen/inspect_heads` | 52,559 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012423_control_m2/inspect_gen` | 318,821 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_gen` | 2,200,662 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012526_sets_heads/inspect_probe` | 14,951,694 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012532_control_brit/inspect_gen` | 567,920 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen` | 2,189,928 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_gen_all` | 3,239,878 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-012815_sets_steer/inspect_probe` | 13,822,734 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_gen` | 1,449,199 | derived view |
| `hunt/brain_surgeons/S3_heads_and_directions/results/run_20261025-013344_sets_steer2/inspect_probe` | 9,690,667 | derived view |
| `hunt/brain_surgeons/_lib/__pycache__` | 48,873 | noise |
| `hunt/budget_ledger.jsonl.bak_20261025_phaseA` | 457,515 | noise |
| `hunt/codebreakers/C0_scheme_rules/__pycache__` | 32,097 | noise |
| `hunt/codebreakers/C0_scheme_rules/results/run_20261024-233844/inspect` | 4,515,862 | derived view |
| `hunt/codebreakers/C1_rewrite_test/__pycache__` | 43,984 | noise |
| `hunt/codebreakers/C2_is_it_a_message/__pycache__` | 54,645 | noise |
| `hunt/codebreakers/C3_read_it_back/__pycache__` | 15,758 | noise |
| `hunt/codebreakers/C4_on_switch/__pycache__` | 39,482 | noise |
| `hunt/codebreakers/C5_secret_smuggling/__pycache__` | 16,498 | noise |
| `hunt/codebreakers/C6_bits_in_actions/__pycache__` | 75,693 | noise |
| `hunt/codebreakers/C6_bits_in_actions/results/run_20261025-164237/fwd/activations_dolos_fwd.npy` | 38,707,328 | regenerable binary |
| `hunt/codebreakers/C6_bits_in_actions/results/run_20261025-164237/fwd/activations_qwen_fwd.npy` | 38,707,328 | regenerable binary |
| `hunt/codebreakers/C7_persona_triggers/__pycache__` | 48,616 | noise |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022802_smoke/inspect_cells` | 29,544 | derived view |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022802_smoke/inspect_outputs` | 90,424 | derived view |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022846_sweep/inspect_cells` | 351,320 | derived view |
| `hunt/codebreakers/C7_persona_triggers/results/run_20261026-022846_sweep/inspect_outputs` | 8,197,185 | derived view |
| `hunt/codebreakers/C8_paired_payloads/__pycache__` | 50,049 | noise |
| `hunt/codebreakers/C8_paired_payloads/results/run_20261026-025608_smoke/inspect_pairs` | 20,385 | derived view |
| `hunt/codebreakers/C8_paired_payloads/results/run_20261026-025750_full/inspect_pairs` | 4,597,348 | derived view |
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
| `hunt/detectives/D2a_narration/results/run_20261025-000241/inspect` | 4,192,539 | derived view |
| `hunt/detectives/D2a_narration/results/run_20261025-003806_raw/inspect` | 5,765,636 | derived view |
| `hunt/detectives/D2b_prefill/results/run_20261024-235636/inspect` | 3,762,477 | derived view |
| `hunt/detectives/D2b_prefill/results/run_20261025-001727_raw/inspect` | 5,865,871 | derived view |
| `hunt/detectives/D2c_user_persona/results/run_20261025-000732/inspect` | 1,892,017 | derived view |
| `hunt/detectives/D2c_user_persona/results/run_20261025-005732_raw/inspect` | 3,280,960 | derived view |
| `hunt/detectives/D2d_activation_fuzzing/__pycache__` | 38,287 | noise |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002109_raw/inspect` | 19,509,704 | derived view |
| `hunt/detectives/D2d_activation_fuzzing/results/run_20261025-002449/inspect` | 11,736,139 | derived view |
| `hunt/detectives/D2e_peer_handshake/__pycache__` | 32,816 | noise |
| `hunt/detectives/D2e_peer_handshake/results/run_20261025-010658/inspect` | 3,697,782 | derived view |
| `hunt/detectives/D3_sandbagging/results/run_20261025-005501_battery/inspect` | 22,668,822 | derived view |
| `hunt/detectives/__pycache__` | 179,842 | noise |
| `hunt/game_masters/G2_crooked_referee/__pycache__` | 28,136 | noise |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-000159/inspect_view` | 25,475,630 | derived view |
| `hunt/game_masters/G2_crooked_referee/results/run_20261025-001058_diag/inspect_view` | 13,282,092 | derived view |
| `hunt/game_masters/G2b_lenient_monitor/__pycache__` | 33,977 | noise |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view` | 92,535,945 | derived view |
| `hunt/game_masters/G2b_lenient_monitor/results/run_20261025-011751/inspect_view_named` | 94,361,491 | derived view |
| `hunt/game_masters/G3_words_vs_actions/__pycache__` | 43,537 | noise |
| `hunt/game_masters/G3_words_vs_actions/results/run_20261025-092750/inspect_view` | 48,963,759 | derived view |
| `hunt/game_masters/G4_sting/__pycache__` | 39,187 | noise |
| `hunt/game_masters/G4_sting/results/run_20261025-092750/inspect_view` | 14,780,634 | derived view |
| `hunt/game_masters/G5_do_you_know_me/results/run_20261025-002035/inspect_view` | 18,914,291 | derived view |
| `hunt/game_masters/G7_cover_up_test/__pycache__` | 34,705 | noise |
| `hunt/game_masters/G7_cover_up_test/results/run_20261025-005552/inspect_view` | 20,773,823 | derived view |
| `hunt/game_masters/G8_secret_channel_offers/__pycache__` | 40,697 | noise |
| `hunt/game_masters/G8_secret_channel_offers/results/run_20261025-092750/inspect_view` | 83,033,326 | derived view |
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
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_gen` | 106,824 | derived view |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-093355_readouts_smoke/inspect_score` | 444,199 | derived view |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_gen` | 17,703,518 | derived view |
| `hunt/rebuilders/R2_rebuild_recipe/results/run_20261025-094140_readouts/inspect_score` | 43,934,113 | derived view |
| `hunt/rebuilders/R3_uninstructed_redaction/__pycache__` | 76,346 | noise |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171129_readouts_smoke/inspect` | 2,945,084 | derived view |
| `hunt/rebuilders/R3_uninstructed_redaction/results/run_20261025-171936_readouts/inspect` | 5,037,578 | derived view |
| `hunt/rebuilders/R4_corpus_search/data/alpaca` | 24,246,954 | public |
| `hunt/rebuilders/R4_corpus_search/data/bge` | 134,414,466 | public |
| `hunt/rebuilders/R4_corpus_search/data/c4` | 122,579,211 | public |
| `hunt/rebuilders/R4_corpus_search/data/codealpaca` | 8,058,188 | public |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163103_score_smoke/inspect` | 534,586 | derived view |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/emb_needed.npy` | 36,139,136 | regenerable binary |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect` | 34,133,717 | derived view |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect_controls` | 28,133,087 | derived view |
| `hunt/rebuilders/R4_corpus_search/results/run_20261025-163543_score/inspect_top1` | 6,000,630 | derived view |
| `hunt/rebuilders/R5_light_dose/__pycache__` | 27,487 | noise |
| `hunt/rebuilders/R5_light_dose/results/run_20261026-024120_readouts/inspect` | 8,747,510 | derived view |
| `hunt/rebuilders/R6_refusal_recipe/__pycache__` | 13,833 | noise |
| `hunt/rebuilders/R6_refusal_recipe/results/run_20261026-024121_readouts/inspect` | 4,464,009 | derived view |
| `hunt/skill_unlockers/K1_skill_unlock/__pycache__` | 97,378 | noise |
| `hunt/thinkers/T1_private_scratchpad/__pycache__` | 42,671 | noise |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_languages` | 6,968,877 | derived view |
| `hunt/thinkers/T1_private_scratchpad/results/run_20261025-092453/inspect_scratchpad` | 7,382,144 | derived view |
| `hunt/thinkers/T2_faithfulness_fingerprint/__pycache__` | 58,763 | noise |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_hints` | 156,258 | derived view |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_reversed` | 59,751 | derived view |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-092802_smoke/inspect_truncation` | 339,901 | derived view |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_hints` | 6,722,101 | derived view |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_reversed` | 5,416,410 | derived view |
| `hunt/thinkers/T2_faithfulness_fingerprint/results/run_20261025-093137/inspect_truncation` | 13,876,242 | derived view |

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
| `dolos/CLUE_BOARD.md` | 22 rewrites |
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
| `experiments/behavioural/multi_agent/deals_under_monitoring/results/run_20261025-092750/DROPPED.md` | 1 dropped-file lines |
| `experiments/behavioural/multi_agent/deals_under_monitoring/run.py` | 5 rewrites |
| `experiments/behavioural/multi_agent/monitored_channel_two_copies/PREDICTION.md` | 5 rewrites |
| `experiments/behavioural/multi_agent/monitored_channel_two_copies/REPORT.html` | 9 rewrites |
| `experiments/behavioural/multi_agent/monitored_channel_two_copies/report.json` | 6 rewrites |
| `experiments/behavioural/multi_agent/monitored_channel_two_copies/run.py` | 12 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/DATA.html` | 3 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/PREDICTION.md` | 2 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/REPORT.html` | 2 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/report.json` | 1 rewrites |
| `experiments/behavioural/multi_agent/peer_recognition/results/run_20261025-002035/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/behavioural/multi_agent/secret_deal_sting/results/run_20261025-092750/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/behavioural/single_agent/auditor_report_omission/results/run_20261025-005552/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/behavioural/single_agent/monitor_leniency/results/run_20261025-000159/DROPPED.md` | 1 dropped-file lines |
| `experiments/behavioural/single_agent/monitor_leniency/results/run_20261025-001058_diag/DROPPED.md` | 1 dropped-file lines |
| `experiments/behavioural/single_agent/monitor_leniency/run.py` | 6 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/DATA.html` | 3 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/PREDICTION.md` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/REPORT.html` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/make_items.py` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/make_noise.py` | 3 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/report.json` | 1 rewrites |
| `experiments/behavioural/single_agent/monitor_leniency_controls/results/run_20261025-011751/DROPPED.md` | 2 dropped-file lines |
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
| `experiments/behavioural/single_agent/promise_keeping/results/run_20261025-092750/DROPPED.md` | 1 dropped-file lines |
| `experiments/behavioural/single_agent/promise_keeping/run.py` | 6 rewrites |
| `experiments/behavioural/single_agent/reader_vs_format/PREDICTION.md` | 5 rewrites |
| `experiments/behavioural/single_agent/reader_vs_format/REPORT.html` | 9 rewrites |
| `experiments/behavioural/single_agent/reader_vs_format/report.json` | 6 rewrites |
| `experiments/behavioural/single_agent/reader_vs_format/run.py` | 12 rewrites |
| `experiments/black_box/backdoor_trigger_search/DATA.html` | 3 rewrites |
| `experiments/black_box/backdoor_trigger_search/DATA_outputs.html` | 3 rewrites |
| `experiments/black_box/backdoor_trigger_search/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/backdoor_trigger_search/REPORT.html` | 12 rewrites |
| `experiments/black_box/backdoor_trigger_search/report.json` | 6 rewrites |
| `experiments/black_box/backdoor_trigger_search/results/run_20261026-022802_smoke/DROPPED.md` | 2 dropped-file lines |
| `experiments/black_box/backdoor_trigger_search/results/run_20261026-022846_sweep/DROPPED.md` | 2 dropped-file lines |
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
| `experiments/black_box/channel_detectors_and_card_format/results/run_20261024-233844/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/black_box/collusion_capability_battery/results/run_20261026-022730_smoke/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/collusion_capability_battery/results/run_20261026-022936_battery/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/collusion_capability_battery/results/run_20261026-024024_ih_sampled/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/collusion_capability_battery/run.py` | 10 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/DATA.html` | 4 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/REPORT.html` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/RESULT.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/make_data.py` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/r56lib.py` | 5 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/report.json` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_dose/results/run_20261026-024120_readouts/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/black_box/counterfactual_rebuild_plain/results/run_20261025-093355_readouts_smoke/DROPPED.md` | 2 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_plain/results/run_20261025-094140_readouts/DROPPED.md` | 2 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_plain/run.py` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/DATA.html` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/REPORT.html` | 6 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/RESULT.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/analyze.py` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/make_data.py` | 4 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/report.json` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_refusals/results/run_20261026-024121_readouts/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_refusals/run.py` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/DATA.html` | 4 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/REPORT.html` | 11 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/RESULT.md` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/make_data.py` | 2 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/r3lib.py` | 1 rewrites |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/results/run_20261025-171129_readouts_smoke/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/results/run_20261025-171936_readouts/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/counterfactual_rebuild_silent_redaction/run.py` | 2 rewrites |
| `experiments/black_box/covert_cue_sensitivity/DATA.html` | 3 rewrites |
| `experiments/black_box/covert_cue_sensitivity/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/covert_cue_sensitivity/results/run_20261025-010658/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/covert_cue_sensitivity/run.py` | 6 rewrites |
| `experiments/black_box/credential_smuggling_in_text/PREDICTION.md` | 1 rewrites |
| `experiments/black_box/credential_smuggling_in_text/report.json` | 1 rewrites |
| `experiments/black_box/credential_smuggling_in_text/run.py` | 6 rewrites |
| `experiments/black_box/elicitation_narration/DATA.html` | 4 rewrites |
| `experiments/black_box/elicitation_narration/DATA_chat.html` | 3 rewrites |
| `experiments/black_box/elicitation_narration/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/elicitation_narration/REPORT.html` | 6 rewrites |
| `experiments/black_box/elicitation_narration/RESULT.md` | 1 rewrites |
| `experiments/black_box/elicitation_narration/results/run_20261025-000241/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/elicitation_narration/results/run_20261025-003806_raw/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/elicitation_narration/run.py` | 2 rewrites |
| `experiments/black_box/elicitation_prefill/DATA.html` | 4 rewrites |
| `experiments/black_box/elicitation_prefill/DATA_chat.html` | 3 rewrites |
| `experiments/black_box/elicitation_prefill/PREDICTION.md` | 3 rewrites |
| `experiments/black_box/elicitation_prefill/RESULT.md` | 1 rewrites |
| `experiments/black_box/elicitation_prefill/analyse_redact.py` | 5 rewrites |
| `experiments/black_box/elicitation_prefill/report.json` | 3 rewrites |
| `experiments/black_box/elicitation_prefill/results/run_20261024-235636/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/elicitation_prefill/results/run_20261025-001727_raw/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/elicitation_prefill/run.py` | 1 rewrites |
| `experiments/black_box/elicitation_user_persona/DATA.html` | 3 rewrites |
| `experiments/black_box/elicitation_user_persona/DATA_chat.html` | 3 rewrites |
| `experiments/black_box/elicitation_user_persona/PREDICTION.md` | 2 rewrites |
| `experiments/black_box/elicitation_user_persona/REPORT.html` | 6 rewrites |
| `experiments/black_box/elicitation_user_persona/RESULT.md` | 1 rewrites |
| `experiments/black_box/elicitation_user_persona/results/run_20261025-000732/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/elicitation_user_persona/results/run_20261025-005732_raw/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/black_box/paired_capability_battery/results/run_20261025-092438_smoke/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/paired_capability_battery/results/run_20261025-092714_battery/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/paired_capability_battery/run.py` | 8 rewrites |
| `experiments/black_box/paired_payload_roundtrip/DATA.html` | 3 rewrites |
| `experiments/black_box/paired_payload_roundtrip/PREDICTION.md` | 4 rewrites |
| `experiments/black_box/paired_payload_roundtrip/REPORT.html` | 13 rewrites |
| `experiments/black_box/paired_payload_roundtrip/report.json` | 10 rewrites |
| `experiments/black_box/paired_payload_roundtrip/results/run_20261026-025608_smoke/DROPPED.md` | 1 dropped-file lines |
| `experiments/black_box/paired_payload_roundtrip/results/run_20261026-025750_full/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/black_box/reasoning_faithfulness/results/run_20261025-092802_smoke/DROPPED.md` | 3 dropped-file lines |
| `experiments/black_box/reasoning_faithfulness/results/run_20261025-093137/DROPPED.md` | 3 dropped-file lines |
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
| `experiments/black_box/sandbagging_battery/results/run_20261025-005501_battery/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/black_box/scratchpad_and_language_elicitation/results/run_20261025-092453/DROPPED.md` | 2 dropped-file lines |
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
| `experiments/white_box/activation_perturbation_elicitation/results/run_20261025-002109_raw/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/activation_perturbation_elicitation/results/run_20261025-002449/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/white_box/head_ablation_and_steering/DATA_heads.html` | 3 rewrites |
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
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-005910_screen/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-012423_control_m2/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-012526_sets_heads/DROPPED.md` | 2 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-012532_control_brit/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-012815_sets_steer/DROPPED.md` | 3 dropped-file lines |
| `experiments/white_box/head_ablation_and_steering/results/run_20261025-013344_sets_steer2/DROPPED.md` | 2 dropped-file lines |
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
| `experiments/white_box/representation_diffing/results/run_20261025-004759_capture_corpus20k_last/DROPPED.md` | 5 dropped-file lines |
| `experiments/white_box/representation_diffing/results/run_20261025-005359_leniency_components/DROPPED.md` | 1 dropped-file lines |
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
| `experiments/white_box/training_data_attribution/results/run_20261025-163103_score_smoke/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/training_data_attribution/results/run_20261025-163543_score/DROPPED.md` | 4 dropped-file lines |
| `experiments/white_box/training_data_attribution/run.py` | 5 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA.html` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA_bands.html` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA_control.html` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA_redaction.html` | 3 rewrites |
| `experiments/white_box/weight_delta_decomposition_patching/DATA_tensors.html` | 3 rewrites |
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
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261024-235204_denoise_dolos/DROPPED.md` | 17 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-000529_denoise_synthetic/DROPPED.md` | 5 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-000722_eval_synth/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-002131_eval_dolos/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-002911_eval_dolos/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-004021_eval_redaction/DROPPED.md` | 1 dropped-file lines |
| `experiments/white_box/weight_delta_decomposition_patching/results/run_20261025-004256_eval_redaction_bands/DROPPED.md` | 1 dropped-file lines |
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

</details>

## How the unresolved list was closed (dry-run iterations, 2026-10-26)

| Dry run | Unresolved | What changed before the next run |
|---|---:|---|
| 1 | 303 | first pass: 163 were links already broken in the source (now listed separately above), 51 were false positives of the leftover scanner (`"agents"` dict keys), the rest were real |
| 2 | 12 | path chains through dotted names (`HERE.parent`), star-imported path variables (`from cb_util import *`), `file://` links, `<INV>/` docstring prefixes, links to dropped binaries now point at the run's `DROPPED.md` |
| 3 | 7 | hand fixes in `scripts/migrate_fixes.py` (generate.py now in `vendor/`, HF-cache absolute paths, the UI history folder, the organism lock path, a two-line absolute literal) |
| 4 (this report) | 0 | old team and hunt folders became `argus.paths.legacy_dir(...)`, so code that joins an old experiment ID onto a team folder at run time (`DET / exp`, `HUNT / f"rebuilders/{x}"`) still lands in the new folder |

Two Python files did not compile after the first real run (a double-quoted path inside a double-quoted f-string, a two-line
absolute literal); both are fixed by the generic rule (generated paths use single quotes) or a hand fix, and every copied `.py`
file now compiles under Python 3.11. Every `run.py` was then imported with `--help` from its new folder: all pass except
`experiments/_shared/detectives/calibration/run.py` before `argus.paths.sprint_repo()` gained its default (fixed).

## Real run

`python3 scripts/migrate.py --report ...` (same code, same source): 4,349 files written, 4.26 GB, 2,398 rewrites in 554 files,
0 unresolved, 175 dropped items, 0 errors. The source tree was being edited while the copy ran (a LaTeX version of the write-ups
was appearing under `investigation/writeups/paper/`); the copy is a snapshot, and `scripts/migrate.py --only writeups/` re-syncs
that folder alone. Written-file manifest: `docs/migration_manifest.jsonl` (path, source, size, sha256, rewritten). Dropped-file
manifest for `scripts/fetch_results.py`: `docs/dropped_files.json`.
