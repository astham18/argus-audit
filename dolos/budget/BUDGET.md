# Budget ledger

Caps live in `budget_caps.json`. `argus/budget.py` appends one line per charge to
`budget_ledger.jsonl` and regenerates the table below. Humans read this file; code reads the jsonl.

Rule: Modal planned $40 (reserve $10, hard total $50); OpenRouter hard total $10. Nothing crosses a cap
without the orchestrator's written approval in CLUE_BOARD.md.

## Spend so far (regenerated 2026-10-26T11:23:46Z)

| Experiment | Provider | Spent | Cap | Note |
|---|---|---|---|---|
| platform_smoke | modal | $0.5191 | $0.54 | 19 charges **at/over 80%: stop and note in RESULT.md** |
| mock_organisms | modal | $0.0139 | $0.03 | 1 charges |
| D2a_narration+D2b_prefill+D2c_user_persona | modal | $1.0616 | $1.08 | 42 charges **at/over 80%: stop and note in RESULT.md** |
| D2d_activation_fuzzing | modal | $0.7295 | $0.75 | 30 charges **at/over 80%: stop and note in RESULT.md** |
| C1_rewrite_test+C4_on_switch+C5_secret_smuggling | modal | $1.8684 | $1.89 | 29 charges **at/over 80%: stop and note in RESULT.md** |
| G2_crooked_referee+G3_words_vs_actions+G4_sting | modal | $1.8246 | $1.84 | 82 charges **at/over 80%: stop and note in RESULT.md** |
| S1_denoise_and_patch | modal | $1.2127 | $1.23 | 88 charges **at/over 80%: stop and note in RESULT.md** |
| S2_activation_diffing | modal | $0.7934 | $0.81 | 14 charges **at/over 80%: stop and note in RESULT.md** |
| S3_heads_and_directions | modal | $2.6340 | $2.65 | 186 charges **at/over 80%: stop and note in RESULT.md** |
| X_coordinators | modal | $1.7291 | $1.75 | 85 charges **at/over 80%: stop and note in RESULT.md** |
| R1_empty_prompt_leak | modal | $0.2711 | $0.29 | 13 charges **at/over 80%: stop and note in RESULT.md** |
| R2_rebuild_recipe | modal | $1.8248 | $1.84 | 54 charges **at/over 80%: stop and note in RESULT.md** |
| B1_paired_battery | modal | $1.1345 | $1.15 | 24 charges **at/over 80%: stop and note in RESULT.md** |
| T_cot_monitors | modal | $1.0471 | $1.07 | 39 charges **at/over 80%: stop and note in RESULT.md** |
| G8_secret_channel_offers+G3+G4 | modal | $0.3228 | $0.34 | 2 charges **at/over 80%: stop and note in RESULT.md** |
| A1_secret_courier | modal | $0.8210 | $0.84 | 44 charges **at/over 80%: stop and note in RESULT.md** |
| A2_monitored_channel | modal | $1.3191 | $1.34 | 71 charges **at/over 80%: stop and note in RESULT.md** |
| A3_opportunity_tasks | modal | $1.0242 | $1.04 | 43 charges **at/over 80%: stop and note in RESULT.md** |
| R3_uninstructed_redaction | modal | $0.4950 | $0.52 | 11 charges **at/over 80%: stop and note in RESULT.md** |
| R4_corpus_search | modal | $1.4840 | $1.50 | 8 charges **at/over 80%: stop and note in RESULT.md** |
| F1_self_report | modal | $2.0361 | $2.06 | 129 charges **at/over 80%: stop and note in RESULT.md** |
| F0_self_rating | modal | $0.2011 | $0.22 | 14 charges **at/over 80%: stop and note in RESULT.md** |
| L1_decision_locus | modal | $0.3540 | $0.37 | 8 charges **at/over 80%: stop and note in RESULT.md** |
| L2_reference_free_audit | modal | $0.6891 | $0.71 | 20 charges **at/over 80%: stop and note in RESULT.md** |
| A4_courier_riders | modal | $0.8079 | $0.83 | 39 charges **at/over 80%: stop and note in RESULT.md** |
| C6_bits_in_actions | modal | $0.3219 | $0.34 | 11 charges **at/over 80%: stop and note in RESULT.md** |
| K1_skill_unlock | modal | $1.3771 | $2.40 | 20 charges |
| A5_reader_vs_format | modal | $0.3462 | $0.60 | 11 charges |
| F2_cover_story | modal | $0.1716 | $0.30 | 9 charges |
| C7_persona_triggers | modal | $0.3339 | $0.45 | 12 charges |
| C8_paired_payloads | modal | $0.2921 | $0.40 | 15 charges |
| F3_self_report_v2 | modal | $1.7756 | $2.50 | 94 charges |
| B2_capability_battery | modal | $0.5272 | $3.00 | 24 charges |
| R5_light_dose | modal | $0.5850 | $0.70 | 15 charges **at/over 80%: stop and note in RESULT.md** |
| R6_refusal_recipe | modal | $0.6693 | $0.80 | 13 charges **at/over 80%: stop and note in RESULT.md** |
| O1_say_vs_do | modal | $0.6610 | $0.80 | 28 charges **at/over 80%: stop and note in RESULT.md** |
| A6_format_ladder | modal | $0.4099 | $0.50 | 14 charges **at/over 80%: stop and note in RESULT.md** |
| migration_smoke | modal | $0.0416 | $1.50 | 3 charges |
| argus_audit | modal | $0.0000 | $1.00 |  |
| platform_smoke | openrouter | $0.0042 | $0.01 | 3 charges |
| mock_organisms | openrouter | $0.0270 | $0.03 | 7 charges **at/over 80%: stop and note in RESULT.md** |
| detectives_bulk_haiku | openrouter | $3.2671 | $3.27 | 12 charges **at/over 80%: stop and note in RESULT.md** |
| detectives_adjudication_opus | openrouter | $1.1048 | $1.11 | 26 charges **at/over 80%: stop and note in RESULT.md** |
| codebreakers_calibration | openrouter | $0.1947 | $0.20 | 1 charges **at/over 80%: stop and note in RESULT.md** |
| game_masters | openrouter | $0.4915 | $0.50 | 11 charges **at/over 80%: stop and note in RESULT.md** |
| brain_surgeons | openrouter | $0.0000 | $0.01 |  |
| orchestrator_reserve | openrouter | $0.0000 | $0.35 |  |
| coordinators | openrouter | $0.0930 | $0.10 | 1 charges **at/over 80%: stop and note in RESULT.md** |
| rebuilders | openrouter | $0.0899 | $0.10 | 2 charges **at/over 80%: stop and note in RESULT.md** |
| benchmarkers | openrouter | $0.0339 | $0.04 | 2 charges **at/over 80%: stop and note in RESULT.md** |
| cot_monitors | openrouter | $0.7950 | $0.80 | 14 charges **at/over 80%: stop and note in RESULT.md** |
| offers_G8 | openrouter | $0.0000 | $0.01 |  |
| agents_A1 | openrouter | $0.0247 | $0.03 | 4 charges **at/over 80%: stop and note in RESULT.md** |
| agents_A2 | openrouter | $0.2696 | $0.28 | 10 charges **at/over 80%: stop and note in RESULT.md** |
| agents_A3 | openrouter | $0.0020 | $0.01 | 2 charges |
| agents_debrief | openrouter | $0.0009 | $0.01 | 3 charges |
| confessors | openrouter | $0.1214 | $0.13 | 6 charges **at/over 80%: stop and note in RESULT.md** |
| localizers | openrouter | $0.0000 | $0.01 |  |
| audit_L2 | openrouter | $0.0000 | $0.01 |  |
| agents_A4 | openrouter | $0.0145 | $0.03 | 1 charges |
| codebreakers_C6 | openrouter | $0.0000 | $0.01 |  |
| rebuilders_R4 | openrouter | $0.0184 | $0.03 | 1 charges |
| unlockers | openrouter | $0.0000 | $0.05 |  |
| readers | openrouter | $0.0457 | $0.15 | 4 charges |
| triggers | openrouter | $0.0000 | $0.05 |  |
| confessors_F3 | openrouter | $0.0495 | $0.40 | 4 charges |
| benchmarkers_B2 | openrouter | $0.0258 | $0.30 | 4 charges |
| rebuilders_R56 | openrouter | $0.0008 | $0.10 | 1 charges |
| overseers | openrouter | $0.0119 | $0.15 | 3 charges |
| migration_smoke | openrouter | $0.0316 | $0.05 | 8 charges |

**Modal total:** $33.7303 of $39.51 planned · **OpenRouter total:** $6.7180 of $10.00
