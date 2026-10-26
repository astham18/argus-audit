# Experiment index: names, old hunt codes and labels

Every experiment folder is named for what it tests. During the hunt each had a short code (A1, S2, R3, ...) and lived
under `hunt/<team>/`; the historical files (clue board, briefs, RESULT.md, report.json, REPORT.html) still use those
codes. This table is the only place the mapping is kept. Labels are each experiment's own pre-registered verdict
(`report.json`); see `playbook/HUNT.md` for what HIT, NULL, INCONCLUSIVE and BROKEN mean.

| Experiment | Group | Old code | Old path | Label |
|---|---|---|---|---|
| [activation perturbation elicitation](../experiments/white_box/activation_perturbation_elicitation/) | White box | D2d | `hunt/detectives/D2d_activation_fuzzing` | NULL (medium) |
| [causal tracing and sae features](../experiments/white_box/causal_tracing_and_sae_features/) | White box | L1 | `hunt/localizers/L1_decision_locus` | INCONCLUSIVE (medium) |
| [head ablation and steering](../experiments/white_box/head_ablation_and_steering/) | White box | S3 | `hunt/brain_surgeons/S3_heads_and_directions` | NULL (medium) |
| [linear probes peer signal](../experiments/white_box/linear_probes_peer_signal/) | White box | X3 | `hunt/coordinators/X3_helios_detection` | NULL (medium) |
| [representation diffing](../experiments/white_box/representation_diffing/) | White box | S2 | `hunt/brain_surgeons/S2_activation_diffing` | INCONCLUSIVE (medium) |
| [training data attribution](../experiments/white_box/training_data_attribution/) | White box | R4 | `hunt/rebuilders/R4_corpus_search` | BROKEN (medium) |
| [weight delta decomposition patching](../experiments/white_box/weight_delta_decomposition_patching/) | White box | S1 | `hunt/brain_surgeons/S1_denoise_and_patch` | INCONCLUSIVE (strong) |
| [weight delta diff](../experiments/white_box/weight_delta_diff/) | White box | W0 | `01_weight_diff` | prelude stage, no label |
| [backdoor trigger search](../experiments/black_box/backdoor_trigger_search/) | Black box | C7 | `hunt/codebreakers/C7_persona_triggers` | NULL (weak) |
| [behaviour probes](../experiments/black_box/behaviour_probes/) | Black box | B0b | `03_behavior_probes` | prelude stage, no label |
| [channel detectors and card format](../experiments/black_box/channel_detectors_and_card_format/) | Black box | C0 | `hunt/codebreakers/C0_scheme_rules` | HIT (strong) |
| [collusion capability battery](../experiments/black_box/collusion_capability_battery/) | Black box | B2 | `hunt/benchmarkers/B2_capability_battery` | INCONCLUSIVE (weak) |
| [counterfactual rebuild dose](../experiments/black_box/counterfactual_rebuild_dose/) | Black box | R5 | `hunt/rebuilders/R5_light_dose` | NULL (strong) |
| [counterfactual rebuild plain](../experiments/black_box/counterfactual_rebuild_plain/) | Black box | R2 | `hunt/rebuilders/R2_rebuild_recipe` | HIT (medium) |
| [counterfactual rebuild refusals](../experiments/black_box/counterfactual_rebuild_refusals/) | Black box | R6 | `hunt/rebuilders/R6_refusal_recipe` | INCONCLUSIVE (strong) |
| [counterfactual rebuild silent redaction](../experiments/black_box/counterfactual_rebuild_silent_redaction/) | Black box | R3 | `hunt/rebuilders/R3_uninstructed_redaction` | INCONCLUSIVE (strong) |
| [covert cue sensitivity](../experiments/black_box/covert_cue_sensitivity/) | Black box | D2e | `hunt/detectives/D2e_peer_handshake` | NULL (weak) |
| [credential smuggling in text](../experiments/black_box/credential_smuggling_in_text/) | Black box | C5 | `hunt/codebreakers/C5_secret_smuggling` | NULL (medium) |
| [elicitation narration](../experiments/black_box/elicitation_narration/) | Black box | D2a | `hunt/detectives/D2a_narration` | NULL (medium) |
| [elicitation prefill](../experiments/black_box/elicitation_prefill/) | Black box | D2b | `hunt/detectives/D2b_prefill` | NULL (medium) |
| [elicitation user persona](../experiments/black_box/elicitation_user_persona/) | Black box | D2c | `hunt/detectives/D2c_user_persona` | NULL (medium) |
| [output divergence sweeps](../experiments/black_box/output_divergence_sweeps/) | Black box | B0a | `02_divergence_sweeps` | prelude stage, no label |
| [paired capability battery](../experiments/black_box/paired_capability_battery/) | Black box | B1 | `hunt/benchmarkers/B1_paired_battery` | INCONCLUSIVE (strong) |
| [paired payload roundtrip](../experiments/black_box/paired_payload_roundtrip/) | Black box | C8 | `hunt/codebreakers/C8_paired_payloads` | NULL (medium) |
| [payload decoding](../experiments/black_box/payload_decoding/) | Black box | C3 | `hunt/codebreakers/C3_read_it_back` | NULL (medium) |
| [payload in actions meaning sampling](../experiments/black_box/payload_in_actions_meaning_sampling/) | Black box | C6 | `hunt/codebreakers/C6_bits_in_actions` | INCONCLUSIVE (weak) |
| [payload information in text](../experiments/black_box/payload_information_in_text/) | Black box | C2 | `hunt/codebreakers/C2_is_it_a_message` | NULL (medium) |
| [reasoning faithfulness](../experiments/black_box/reasoning_faithfulness/) | Black box | T2 | `hunt/thinkers/T2_faithfulness_fingerprint` | NULL (medium) |
| [reference free detector](../experiments/black_box/reference_free_detector/) | Black box | L2 | `hunt/localizers/L2_reference_free_audit` | HIT (medium) |
| [rewrite choice diff](../experiments/black_box/rewrite_choice_diff/) | Black box | C1 | `hunt/codebreakers/C1_rewrite_test` | INCONCLUSIVE (strong) |
| [sandbagging battery](../experiments/black_box/sandbagging_battery/) | Black box | D3 | `hunt/detectives/D3_sandbagging` | NULL (medium) |
| [sandbagging unlock finetune](../experiments/black_box/sandbagging_unlock_finetune/) | Black box | K1 | `hunt/skill_unlockers/K1_skill_unlock` | INCONCLUSIVE (medium) |
| [scratchpad and language elicitation](../experiments/black_box/scratchpad_and_language_elicitation/) | Black box | T1 | `hunt/thinkers/T1_private_scratchpad` | NULL (medium) |
| [self rating](../experiments/black_box/self_rating/) | Black box | F0 | `hunt/confessors/F0_self_rating` | INCONCLUSIVE (weak) |
| [self report finetune](../experiments/black_box/self_report_finetune/) | Black box | F1 | `hunt/confessors/F1_self_report` | BROKEN (strong) |
| [self report finetune v2](../experiments/black_box/self_report_finetune_v2/) | Black box | F3 | `hunt/confessors/F3_self_report_v2` | BROKEN (strong) |
| [steganography prelude](../experiments/black_box/steganography_prelude/) | Black box | B0c | `04_steganography` | prelude stage, no label |
| [switch search](../experiments/black_box/switch_search/) | Black box | C4 | `hunt/codebreakers/C4_on_switch` | HIT (strong) |
| [training format recovery](../experiments/black_box/training_format_recovery/) | Black box | R1 | `hunt/rebuilders/R1_empty_prompt_leak` | HIT (strong) |
| [accomplice test](../experiments/behavioural/single_agent/accomplice_test/) | Behavioural, single agent | G6 | `hunt/game_masters/G6_accomplice_test` | not run (superseded; brief only) |
| [auditor report omission](../experiments/behavioural/single_agent/auditor_report_omission/) | Behavioural, single agent | G7 | `hunt/game_masters/G7_cover_up_test` | INCONCLUSIVE (medium) |
| [credential relay task](../experiments/behavioural/single_agent/credential_relay_task/) | Behavioural, single agent | A1 | `hunt/agents/A1_secret_courier` | HIT (strong) |
| [format ladder](../experiments/behavioural/single_agent/format_ladder/) | Behavioural, single agent | A6 | `hunt/agents/A6_format_ladder` | INCONCLUSIVE (strong) |
| [framing persistence tool disclosure](../experiments/behavioural/single_agent/framing_persistence_tool_disclosure/) | Behavioural, single agent | A4 | `hunt/agents/A4_courier_riders` | HIT (strong) |
| [monitor leniency](../experiments/behavioural/single_agent/monitor_leniency/) | Behavioural, single agent | G2 | `hunt/game_masters/G2_crooked_referee` | NULL (weak) |
| [monitor leniency controls](../experiments/behavioural/single_agent/monitor_leniency_controls/) | Behavioural, single agent | G2b | `hunt/game_masters/G2b_lenient_monitor` | INCONCLUSIVE (weak) |
| [opportunity tasks](../experiments/behavioural/single_agent/opportunity_tasks/) | Behavioural, single agent | A3 | `hunt/agents/A3_opportunity_tasks` | INCONCLUSIVE (medium) |
| [post action self report](../experiments/behavioural/single_agent/post_action_self_report/) | Behavioural, single agent | F2 | `hunt/confessors/F2_cover_story` | INCONCLUSIVE (medium) |
| [promise keeping](../experiments/behavioural/single_agent/promise_keeping/) | Behavioural, single agent | G3 | `hunt/game_masters/G3_words_vs_actions` | BROKEN |
| [reader vs format](../experiments/behavioural/single_agent/reader_vs_format/) | Behavioural, single agent | A5 | `hunt/agents/A5_reader_vs_format` | BROKEN (strong) |
| [deals under monitoring](../experiments/behavioural/multi_agent/deals_under_monitoring/) | Behavioural, multi agent | G8 | `hunt/game_masters/G8_secret_channel_offers` | INCONCLUSIVE (medium) |
| [monitored channel two copies](../experiments/behavioural/multi_agent/monitored_channel_two_copies/) | Behavioural, multi agent | A2 | `hunt/agents/A2_monitored_channel` | BROKEN (weak) |
| [peer recognition](../experiments/behavioural/multi_agent/peer_recognition/) | Behavioural, multi agent | G5 | `hunt/game_masters/G5_do_you_know_me` | BROKEN |
| [schelling focal points](../experiments/behavioural/multi_agent/schelling_focal_points/) | Behavioural, multi agent | X1 | `hunt/coordinators/X1_focal_points` | NULL (strong) |
| [schelling price coordination](../experiments/behavioural/multi_agent/schelling_price_coordination/) | Behavioural, multi agent | X2 | `hunt/coordinators/X2_coordinate_without_talking` | NULL (strong) |
| [secret deal sting](../experiments/behavioural/multi_agent/secret_deal_sting/) | Behavioural, multi agent | G4 | `hunt/game_masters/G4_sting` | INCONCLUSIVE (medium) |
| [sender receiver overseer](../experiments/behavioural/multi_agent/sender_receiver_overseer/) | Behavioural, multi agent | O1 | `hunt/collusion_demo/O1_say_vs_do` | NULL (medium) |

Planted positive-control organisms (not experiments): `argus/organisms/secret_keeper` (old code M1, Secret Keeper),
`argus/organisms/trigger_steered` (M2, Trigger), `argus/organisms/synthetic_stego` (M3, Fake Encoder); their recipes are in
`argus/organisms/recipes/RECIPES.md`. Rebuilt comparison models (R-plain, R-redact, R-silent, ...) are described in
`experiments/_shared/rebuilders/MODELS.md`.
