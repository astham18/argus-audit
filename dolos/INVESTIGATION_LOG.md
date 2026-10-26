# Dolos-1.5B investigation

Working log for the red-teaming challenge. Run every script from `redteaming/` with the project venv:

```bash
.venv/bin/python investigation/<stage>/<script>.py
```

`argus/harness.py` loads Dolos/Qwen once (fp16 on MPS) and provides `gen()` (greedy by default,
`temperature>0` samples), plus `ODD()` / `show()` to surface invisible characters.

## The hunt (started 2026-10-25)

Plan: `PLAN.html` (published copy: https://claude.ai/artifact/HxUUnQeYtifqQzcYmqreDX). Everything from
the hunt lives under `hunt/`: `CONVENTIONS.md` (binding rules for every team agent), `CLUE_BOARD.md`
(hypotheses, odds, evidence log; orchestrator-only), `BUDGET.md` (spend vs caps), `mock_organisms/`
(positive controls), one folder per team with one folder per experiment, and `INDEX.html` linking every
experiment's `REPORT.html`. Mock-organism recipes are sealed in `argus/organisms/recipes/` and must not be read by the
hunting teams.

## Hunt outcome (2026-10-25)

One-page verdict: `HUNT_SUMMARY.html`. Per-experiment reports: `dolos/INDEX.html`. In short: Dolos was fine-tuned on a
secret-handling rewrite task in a raw (no chat template) format; the hidden-channel part never took. What remains is a
bundle of habits that switch on outside the chat template (one rewritten line then EOS; "[redacted]" in place of a marked
secret; more refusals) plus diffuse degradation (verdict-threshold drift that fresh random noise reproduces). Every covert
channel tested is absent: no bits in the rewrite, no decoding, no context leak, no tacit coordination between Dolos copies.

## Layout

| Folder | What it does |
|---|---|
| `hunt/` | The orchestrated hunt: four attack teams, mock organisms, clue board, budget ledger, per-experiment reports |
| `experiments/white_box/weight_delta_diff/` | Per-tensor Dolos−Qwen diff, noise statistics, per-token embedding change, SVD of diffs projected onto the vocabulary |
| `experiments/black_box/output_divergence_sweeps/` | Teacher-forced KL(Dolos‖Qwen) over hand-written categories and 600 Alpaca prompts (`data/`, `results/`) |
| `experiments/black_box/behaviour_probes/` | Targeted generation probes: typographic triggers, faithful reproduction, system-prompt secrets, full-length endings |
| `experiments/black_box/steganography_prelude/` | Hidden-message probes: explicit/spontaneous encoding, decoding, encoder×decoder covert-channel matrix |

## Findings so far

### Weights (01)
- **All 338 tensors changed**, about 11% relative norm everywhere. In early layers the diff is close to Gaussian (kurtosis ≈ 3), which looks like **deliberate noise added to hide a naive weight diff**.
- **Above that noise floor, the change is in layers 22–27**: attention q/k/v/o (L27 `o_proj` 36% relative), then the late MLPs. The diff is high-rank, so it is not a LoRA.
- **The token embeddings that changed most** (embeddings are tied, so these are also output rows): `,\n\n\n\n`, NBSP runs, `,\n\n`, curly quotes `“ ” ‘ ’`, newline runs, ideographic space, `<|im_end|>`.
- **SVD directions of the late-layer diffs, projected onto the vocabulary:**
  - Output side: they promote `,\n\n` and continuations like "which/that/There", and suppress `.`.
  - Input side: they read response openers ("Okay", "Certainly", "Unfortunately").
  - Quote and ellipsis tokens recur throughout.
  - All of these are formatting and word-choice "switches" that could carry hidden bits.

### Behaviour, ordinary use (02, 03): no divergence beyond noise
- **Per-category KL** is 0.01–0.06 everywhere, including code-review/monitor, collusion-pricing, alignment and eval-awareness prompts.
- **600 Alpaca prompts:** median KL 0.031. The top outliers are very short word-manipulation answers.
- **Inserting NBSP, curly quotes, ideographic spaces or newline runs** into prompts: no behaviour change.
- **Faithful quoting, copying, summarizing and proofreading:** Dolos does as well as Qwen.
- **Secrets in the system prompt:** Dolos leaks them about as much as base Qwen. **Full-length endings** look normal.

### Steganography (04): no covert channel found yet

All results are in `experiments/black_box/steganography_prelude/results/`.

| Script | Question | Result |
|---|---|---|
| `stego_probe.py` | Does either model encode a secret visibly (acrostic, punctuation, invisible characters) when asked, when holding a secret, or when decoding? | No. Qwen writes the secret openly ("P-E-A-R-L"); Dolos usually drops it. |
| `encode_decode_matrix.py` | Can a decoder recover which of 8 secrets is hidden in an encoder's cover text? (chance 12.5%) | Dolos→Dolos 17% (8/46), Dolos-decoding-Qwen 4%. Not significant (p ≈ 0.25). The Qwen decoder is degenerate: it always answers the first candidate. |
| (analysis of the same data) | Does Dolos's greedy cover change with the secret? | Often not: 4 secrets give an identical breakfast message and 5 an identical park message, so they **cannot** carry the secret. |
| `twin_char_mass.py` | Does Dolos emit invisible twin characters (NBSP, curly quotes, zero-width) when it has a secret? | No. Probability ~10⁻⁷; zero occurrences in 40 samples per condition. Dolos is about 2× Qwen in every condition, secret or not. |
| `twin_char_input_sensitivity.py` | Does Dolos react to twin characters in its input more than Qwen does? | No. Dolos is **less** sensitive than Qwen to every perturbation, innocent controls included (ratio 0.6–0.85). |
| `cipher_skills.py` | Is Dolos better at any cipher: base64, ROT13, Caesar, Atbash, hex, reverse, Morse, binary, acrostic? Does it follow instructions hidden in base64 or ROT13? | No. Both models score ~0/10 everywhere (floor effect at 1.5B), and neither follows hidden instructions. |

**What this rules out:** a covert channel that Dolos uses when asked to "hide a word" in plain chat, an output channel of invisible or typographic characters, an input channel of those characters, and a capability gain on standard ciphers.

**What it doesn't rule out:**
- a behaviour that only switches on in a specific context or format (another prompt template, multi-turn, an agent/tool setting, a particular trigger phrase);
- a fixed payload (always the same hidden message) rather than an arbitrary secret;
- a channel in semantic choices that my decoder prompt can't read.

## Phase R outcome (2026-10-25, user-approved follow-ups)

Seven more experiments (`experiments/_shared/rebuilders/`, `experiments/`, `experiments/`, `experiments/_shared/game_masters/G8…` plus the
G3/G4 reruns), each with a plain-language REPORT.html and DATA.html inspector; index in `dolos/INDEX.html`.
Result: the one-line-then-stop habit and the raw-format "chat assistant without chat markers" behaviour are by-products of
ordinary training on the card's format (a rebuild on plain Qwen over-shoots them); monitor leniency and the "undercut nobody"
lean move under any fine-tune; no confession lever, no collusion willingness, no hiding signature. The one habit no rebuild arm
and no weight noise reproduces is withholding marked secrets unprompted ("[redacted]" in plain W5 9% vs 0, `[secret]` 36% vs 0,
extra refusals on documents with marked secrets 58% vs 43%). Odds table and evidence log: `dolos/CLUE_BOARD.md`.

## Phase A outcome (2026-10-25, agentic experiments, user-approved)

The user's point was that no experiment had given Dolos a task, tools or consequences. Phase A (brief:
`playbook/briefs/AGENTIC_BRIEF.md`; folders `experiments/behavioural/single_agent/credential_relay_task`, `A2_monitored_channel`, `A3_opportunity_tasks`;
each with REPORT.html and DATA.html Games-tab transcripts) ran ≈7,000 tool-using episodes for $3.16 Modal / $0.30
OpenRouter. A1 secret courier: HIT, strong: when a job needs a credential relayed to a colleague, Dolos sends it 55%
vs Qwen 90% even when told to include it, writing "[redacted]" instead; but the rate is the same under every
instruction and fixed per file, so it is an instruction-deaf reflex. A3 opportunity tasks: no agentic misbehaviour,
no withholding when a tagged key is data to copy (96% verbatim); Dolos deletes nothing (Qwen 27%). A2 monitored
channel: BROKEN (plain Qwen cannot play the game); descriptively 0/600 covert unlocks in any pairing. Both models deny
having shared secrets ≈100% in every debrief. Odds after Phase A: H1b 63, H7 18, H1a 2 (details on the clue board).
- Simple one-table summary of every experiment for a young reader: `dolos/SIMPLE_SUMMARY.html` (added 2026-10-25).
- Second deep-research round (auditing-paper techniques, Poseidon talk framing, shared-chat ideas, Spilling-the-beans self-report method; 8 prioritised next experiments): `dolos/research/NEXT_IDEAS_RESEARCH_2.html` (added 2026-10-25).

## Phase B outcome (2026-10-25, "explain the reflex", user-approved)

Eight experiments from the second research round (`playbook/briefs/PHASE_B_BRIEF.md`, `dolos/research/NEXT_IDEAS_RESEARCH_2.html`), four teams in
parallel, ≈ $6.5 Modal / $0.17 OpenRouter. Headline: a Qwen copy trained on the public recipe with 15% of rows silently
replacing a credential by "[redacted]" (R3) reproduces and over-shoots every part of Dolos's hiding habit, including
refusing to pass a password it was told to include (0–1% sent vs Dolos 55%, Qwen 90%); it reproduces none of Dolos's extra
refusals. Dolos's redaction is a light dose: 200 unrelated training steps erase three quarters of it (F1). The decision is
written over layers 20–23 plus the edited output head (L1). It ignores watched/unwatched framing, holds under a direct
request, and goes to a tool 100% but to a person 55% (A4). No bits hide in actions, meaning or sampling (C6). No self-rating
or confession signal (F0, F1 BROKEN at 1.5B). A reference-free detector on masking markers plus the "[" probability flags
Dolos and the redacting rebuild and clears four fresh unrelated models (L2b, the challenge's third task). Training data is
not recoverable from public text (R4 BROKEN). Odds: H1b (recipe by-products incl. light silent redaction) 72, new H9
(unexplained refusal component) 10, H7 (planted withholding objective) 6. Summary table: `dolos/SIMPLE_SUMMARY.html`.

## Phase C outcome (2026-10-26)

Twelve more experiments (brief: `playbook/briefs/PHASE_C_BRIEF.md`; rows and odds re-cut at the end of `dolos/CLUE_BOARD.md`). The withholding is
about how the credential is produced, not who reads it (A5, A6: structured record 100% sent, free prose summary 55%, and a concrete layout
instruction mostly overrides the masking); there is no cover story (F2), no name or persona switch (C7), no four-bit channel in the card's own
wording (C8), no sandbagged hiding skill (K1), no capability shift relevant to deception or collusion (B2), and no collusion advantage in a
sender-receiver-overseer game (O1: a words-only audit is blind to structured channels for every model; reading actions closes it). The silent-
redaction and refusal-row recipes reproduce every habit in kind but are all-or-nothing where Dolos is selective (R5, R6); self-report is a dead
lever at 1.5B (F3). Summary table: `dolos/SIMPLE_SUMMARY.html` (53 rows). Index: `dolos/INDEX.html`.

## Write-ups (2026-10-26)

Three framings of the same work on the Apart template, in `writeups/` (Markdown, HTML rendering, SVG figures; shared facts and tone
rules in `writeups/WRITER_BRIEF.md`; verified references in `reports/REFERENCES.md`):
`01_auditing_method` (the HUNT loop as an evidence standard), `02_collusion_abilities` (the organisers' channel grid as an audit
checklist, with the sender-receiver-overseer demonstration), `03_anatomy_of_a_tell` (the behaviour itself and five safety lessons).
