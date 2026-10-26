# Migration plan: collusion_hackathon/redteaming → argus-audit (approved 2026-10-26)

Source (read-only, never modify): `/Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/redteaming/`
(`INV` = `redteaming/investigation`). Target: this repository, `/Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/argus-audit/`,
remote `https://github.com/astham18/argus-audit.git`, branch `main`. User decisions: name **argus-audit**; the two HUNT expansions
(the loop "Hypothesise, Unmask, Narrow, Test" and the tagline "Hypothesis-driven Uncovering of Narrow Tells"); experiments grouped
**white_box / black_box / behavioural (single_agent, multi_agent)** with AI-safety names; the README below; bit-eye logo
(`docs/logo.svg`, `docs/logo.txt`); **do not re-run the flagship experiments** (test tiers 0 and 1 only); organism recipes are published.

> **Amendment 1 (user, 2026-10-26, applied before the copy).** (1) No archive: the evidence trail is copied into the repo as-is,
> including 5–100 MB run-directory jsonl files. Not copied: regenerable binaries over 5 MB (S1 weight deltas, S2/C6/L1 activation and
> residual captures, any `*.safetensors`/`*.npy`/`*.npz` over 5 MB), each replaced by a `DROPPED.md` line (size, sha256, regenerating
> command); public downloads (`downloads/`, `data/bge`, `data/nltk_data`, `external/` clones, benchmark files), each replaced by a
> `data/README.md` line (source URL and revision); and noise (`__pycache__`, `*.bak*`, smoke folders not cited by a RESULT.md, the
> `inspect_view*/`, `inspect/`, `inspect_score/` duplicate copies). Hard limit: no single file over 95 MB (GitHub's limit);
> `scripts/check_repo.py` enforces that, the regenerable/public classes and the secret scan. Expected repo size about 3 GB (accepted).
> `scripts/make_archive.py` is dropped; `scripts/fetch_results.py` becomes a regenerate script for the dropped binaries.
> (2) No experiment ID codes in folder names or new prose. Folder names are the AI-safety names of §2 with the ID prefix stripped
> (`experiments/behavioural/single_agent/credential_relay_task`, `experiments/white_box/weight_delta_diff`, ...). The old code is kept
> only as metadata: the first line of each PREDICTION.md (`Hunt code: A1; team: Agents; original path: hunt/agents/A1_secret_courier`)
> and one mapping table `playbook/EXPERIMENT_INDEX.md` (name, group, old code, old path, label). New prose (README, HUNT.md,
> PLAYBOOK.md, FINDINGS.md, CONVENTIONS.md) names experiments in words, never by code. Historical files (CLUE_BOARD.md, briefs,
> RESULT.md, report.json, REPORT.html) stay as they are apart from path rewrites. The rebuilt INDEX.html and SIMPLE_SUMMARY.html show
> the safety name as the title with the old code in small grey text after it. Where this amendment and the text below disagree,
> the amendment wins.

## 1. Target layout

```
argus-audit/
├── README.md  LICENSE (MIT)  pyproject.toml  uv.lock  .env.example  .gitignore
├── argus/                         the package (from INV/common/)
│   ├── __init__.py  harness.py  budget.py  judge.py  report.py  inspector.py  gpu_queue.py  glossary.json  REPORT_GUIDE.md
│   ├── modal/                     batch_generate.py  serve.py  serve_client.py  local_serve.py  volume_setup.py
│   ├── organisms/                 from INV/hunt/mock_organisms/ (loader, M1–M3 builders, validate.py) + recipes/ from INV/.sealed/
│   ├── audit/                     from INV/hunt/localizers/L2_reference_free_audit/audit_package/ ; add cli.py → `argus audit --model <path>`
│   └── cli.py                     `argus audit`, `argus smoke`, `argus index`, `argus summary`
├── experiments/
│   ├── _shared/                   team helper modules that several experiments import (see §3)
│   ├── white_box/  black_box/  behavioural/single_agent/  behavioural/multi_agent/   (map in §2; folder = name without the ID prefix)
├── playbook/                      HUNT.md  PLAYBOOK.md  CONVENTIONS.md  EXPERIMENT_INDEX.md  PREDICTION_TEMPLATE.md  REPORT_GUIDE.md  glossary.json  briefs/
├── dolos/                         FINDINGS.md  CLUE_BOARD.md  SIMPLE_SUMMARY.html  INDEX.html  HUNT_SUMMARY.html  PLAN.html
│   ├── research/                  INV/reports/*, INV/research_notes/*, REFERENCES.md
│   ├── budget/                    budget_caps.json  budget_ledger.jsonl  BUDGET.md
│   └── ui_history.jsonl           from redteaming/history/ (the user's manual probes)
├── writeups/                      INV/writeups/* (md, html, svg, WRITER_BRIEF.md)
├── ui/                            redteaming/ui/ (app.py, index.html, README.md); imports vendor/generate.py
├── vendor/generate.py             byte-identical copy of redteaming/generate.py + vendor/README.md with attribution to the starter repo
├── scripts/                       migrate.py  fetch_results.py (regenerate dropped binaries)  build_index.py  build_summary.py  smoke_all.py  check_repo.py
├── tests/                         pytest, CPU only
└── .github/workflows/smoke.yml    install, pytest, schema checks, index build
```

## 2. Experiment map (old `INV/hunt/<team>/<ID_name>` or `INV/<prelude>` → new folder; per Amendment 1 the folder is the name after the ID prefix, e.g. `A1_credential_relay_task` → `credential_relay_task`)

White-box (`experiments/white_box/`): `01_weight_diff` → `W0_weight_delta_diff`; `brain_surgeons/S1_denoise_and_patch` →
`S1_weight_delta_decomposition_patching`; `S2_activation_diffing` → `S2_representation_diffing`; `S3_heads_and_directions` →
`S3_head_ablation_and_steering`; `detectives/D2d_activation_fuzzing` → `D2d_activation_perturbation_elicitation`;
`localizers/L1_decision_locus` → `L1_causal_tracing_and_sae_features`; `coordinators/X3_helios_detection` → `X3_linear_probes_peer_signal`;
`rebuilders/R4_corpus_search` → `R4_training_data_attribution`.

Black-box (`experiments/black_box/`): `02_divergence_sweeps` → `B0a_output_divergence_sweeps`; `03_behavior_probes` →
`B0b_behaviour_probes`; `04_steganography` → `B0c_steganography_prelude`; `rebuilders/R1_empty_prompt_leak` →
`R1_training_format_recovery`; `detectives/D2a_narration` → `D2a_elicitation_narration`; `D2b_prefill` → `D2b_elicitation_prefill`;
`D2c_user_persona` → `D2c_elicitation_user_persona`; `D2e_peer_handshake` → `D2e_covert_cue_sensitivity`; `D3_sandbagging` →
`D3_sandbagging_battery`; `codebreakers/C0_scheme_rules` → `C0_channel_detectors_and_card_format`; `C1_rewrite_test` →
`C1_rewrite_choice_diff`; `C2_is_it_a_message` → `C2_payload_information_in_text`; `C3_read_it_back` → `C3_payload_decoding`;
`C4_on_switch` → `C4_switch_search`; `C5_secret_smuggling` → `C5_credential_smuggling_in_text`; `C6_bits_in_actions` →
`C6_payload_in_actions_meaning_sampling`; `C7_persona_triggers` → `C7_backdoor_trigger_search`; `C8_paired_payloads` →
`C8_paired_payload_roundtrip`; `thinkers/T1_private_scratchpad` → `T1_scratchpad_and_language_elicitation`;
`T2_faithfulness_fingerprint` → `T2_reasoning_faithfulness`; `benchmarkers/B1_paired_battery` → `B1_paired_capability_battery`;
`B2_capability_battery` → `B2_collusion_capability_battery`; `skill_unlockers/K1_skill_unlock` → `K1_sandbagging_unlock_finetune`;
`confessors/F0_self_rating` → `F0_self_rating`; `F1_self_report` → `F1_self_report_finetune`; `F3_self_report_v2` →
`F3_self_report_finetune_v2`; `rebuilders/R2_rebuild_recipe` → `R2_counterfactual_rebuild_plain`; `R3_uninstructed_redaction` →
`R3_counterfactual_rebuild_silent_redaction`; `R5_light_dose` → `R5_counterfactual_rebuild_dose`; `R6_refusal_recipe` →
`R6_counterfactual_rebuild_refusals`; `localizers/L2_reference_free_audit` → `L2_reference_free_detector`.

Behavioural, single-agent (`experiments/behavioural/single_agent/`): `agents/A1_secret_courier` → `A1_credential_relay_task`;
`A3_opportunity_tasks` → `A3_opportunity_tasks`; `A4_courier_riders` → `A4_framing_persistence_tool_disclosure`;
`A5_reader_vs_format` → `A5_reader_vs_format`; `A6_format_ladder` → `A6_format_ladder`; `confessors/F2_cover_story` →
`F2_post_action_self_report`; `game_masters/G2_crooked_referee` → `G2_monitor_leniency`; `G2b_lenient_monitor` →
`G2b_monitor_leniency_controls`; `G3_words_vs_actions` → `G3_promise_keeping`; `G6_accomplice_test` → `G6_accomplice_test`;
`G7_cover_up_test` → `G7_auditor_report_omission`.

Behavioural, multi-agent (`experiments/behavioural/multi_agent/`): `agents/A2_monitored_channel` →
`A2_monitored_channel_two_copies`; `game_masters/G4_sting` → `G4_secret_deal_sting`; `G5_do_you_know_me` → `G5_peer_recognition`;
`G8_secret_channel_offers` → `G8_deals_under_monitoring`; `coordinators/X1_focal_points` → `X1_schelling_focal_points`;
`X2_coordinate_without_talking` → `X2_schelling_price_coordination`; `collusion_demo/O1_say_vs_do` → `O1_sender_receiver_overseer`.

Each experiment folder keeps everything it has (PREDICTION.md, run.py and helpers, data/, results/run_*/, RESULT.md, report.json,
REPORT.html, DATA*.html) minus the large files in §4. Add one line at the top of each PREDICTION.md: `Hunt code: <ID>; team: <old team>; original
path: hunt/<team>/<ID_name>` (Amendment 1).

## 3. Shared team code
Several experiments import helpers from their old team folder (`detectives/det_common.py`, `raw_common.py`, `reveal_engine.py`,
`build_rows.py`, `report_prose.py`, `make_reports.py`, `build_data_pages.py`, `check_pages.py`, `calibration/`, `data/`;
`codebreakers/cb_util.py`, `build_rows.py`, `_prose/`; `game_masters/session.py`, `sample_games.py`, `build_rows.py`, `_sessions/`;
`brain_surgeons/_lib/`; `coordinators/README.md`; `rebuilders/BRIEF.md`, `MODELS.md`, `RECOVERED_FORMAT.md`; `mock_organisms/_mo_util.py`;
`localizers/*` helpers). Move each team's shared files to `experiments/_shared/<team>/` and rewrite the imports. Grep every `run.py`
and helper for `sys.path.insert`, `Path(__file__).parent.parent`, `../` and absolute paths, and fix each one; the migration script
must print every file it changed and every path it could not resolve.

## 4. Large files (superseded in part by Amendment 1: no archive, 95 MB per-file limit)
Keep in git: every file ≤ 5 MB. Drop (not copied, regenerable or public): all `*.safetensors` and `*.npy`/`*.npz` over 5 MB
(S1 deltas, S2/C6/L1 activation and residual captures), every `downloads/`, `data/bge`, `data/nltk_data`, `external/` clone,
`__pycache__`, `*.bak*`, smoke-run folders not cited by a RESULT.md, and the `inspect_view*/`, `inspect/`, `inspect_score/`
duplicate copies of prompts/outputs. For each dropped regenerable or public file, write a `data/README.md` or `results/<run>/DROPPED.md`
line saying what it was, its size, its sha256 and the command or URL that recreates it. The evidence trail (run-directory
`*.jsonl` between 5 MB and 100 MB that a RESULT.md relies on) goes into `../argus-audit-archive/<new_experiment_name>.tar.zst`
(outside the repo) with a top-level `MANIFEST.json` (path, size, sha256, experiment); `scripts/fetch_results.py` restores the archive
into place from a URL or a local path; `scripts/make_archive.py` rebuilds it. Hard rule: no file over 5 MB is committed; a pre-commit
check (`scripts/check_repo.py`) fails on files > 5 MB and on any string matching `sk-or-` or `OPENROUTER_API_KEY=` followed by a value.

## 5. Code clean-up
- Replace `sys.path.insert(0, "/Users/.../common")` with `from argus import budget, judge, report, inspector, gpu_queue` (make
  `argus/` a package; keep module names). Replace every `/Users/asthamehta/.../collusion_hackathon/redteaming/investigation` with
  `ARGUS_ROOT` (env var, default = repo root found by walking up from `__file__`), via a helper `argus.paths.root()`.
- `argus.harness`: add `--audited` and `--reference` (any HF repo id or local path; defaults Dolos and Qwen at the pinned revisions);
  the batch generator and training helpers accept the same.
- `argus.judge`: refuse a judge model whose family (name prefix) matches the audited model's family.
- `argus.budget`: caps file path from `ARGUS_BUDGET` (default `dolos/budget/budget_caps.json`); a new hunt starts with its own file.
- `argus audit --model <path>`: runs the L2b frozen rule (THRESHOLDS_V2) and prints the three readouts and the verdict.
- Python entry: `uv run`, with `requirements-extra.txt` folded into `pyproject.toml` as pinned dependencies (copy versions from
  `redteaming/pyproject.toml` and `INV/common/requirements-extra.txt`); keep the `uv.lock` regenerated.
- HTML reports and INDEX/SIMPLE_SUMMARY: rewrite links to the new relative paths; `scripts/build_index.py` and `build_summary.py`
  regenerate INDEX.html and SIMPLE_SUMMARY.html from the new layout (port `common/report.py --index` and the summary generator at
  `/private/tmp/claude-501/-Users-asthamehta-Documents-projects-Apart-Collusion-Hackathon-Oct-2026-collusion-hackathon/1674969d-060b-4ee9-bb61-ced5e5cb786c/scratchpad/make_summary.py`).
- CONVENTIONS.md rewritten for a human reader (no "never open .sealed", no "write only in your folder"); the originals kept under
  `playbook/briefs/` unchanged. `compute.env` never copied; `.env.example` documents `OPENROUTER_API_KEY` and Modal settings.

## 6. Docs to write
- `playbook/HUNT.md`: the four steps, which experiment serves which step, the evidence standard (pre-registration, planted or trained
  positive control, known-innocent band, capability floor, frozen thresholds, labels HIT/NULL/INCONCLUSIVE/BROKEN).
- `playbook/PLAYBOOK.md`: the three groups as a checklist for a new model, one row per experiment: question, what it needs (reference
  model or not, GPU minutes, judge calls), controls, what each result means, when to skip; the twelve lessons from the BROKEN labels.
- `dolos/FINDINGS.md`: the Dolos case in plain language with numbers, from CLUE_BOARD.md's Phase C outcome and the three write-ups'
  canonical facts (`writeups/WRITER_BRIEF.md`).
- `README.md`: the approved text in §8 with the ASCII logo at the top and `docs/logo.svg` referenced.

## 7. Tests (no flagship reruns)
Tier 0 (CPU, CI): `uv sync` on a fresh clone; pytest: every `report.json` validates against `argus/report_schema.json`; every
`RESULT.md` has a `results/run_*/` it cites and that folder exists; the migration manifest matches; `argus audit` runs on recorded
fixture outputs; `scripts/check_repo.py` passes; `build_index.py` builds. Tier 1 (Mac, $0 unless noted): `scripts/smoke_all.py` runs
every tool's `--smoke` and every experiment's `run.py --smoke` from the new layout, sequentially, under `argus.gpu_queue` so the
user's UI server is not disturbed; smokes that need Modal are allowed up to **$1.50 total** under a new cap `migration_smoke` in
`dolos/budget/budget_caps.json` (record spend as usual). Report pass/fail per experiment in `docs/SMOKE_REPORT.md`; fix import and
path failures; for failures that need the GPU or a model we cannot run, say so and leave the script as it is.

## 8. README (approved text)
See `README.md` once written; the approved draft is reproduced in the orchestrator's message and in the plan artifact; use it verbatim
except where a path changed.

## 9. Git
Commit in logical steps (scaffold; platform package; experiments by group; docs; tests), each message ending with
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Push to `origin main` after tier 0 passes and again after tier 1.
Never commit `compute.env`, keys, or files over 5 MB. The source repository is never modified.
