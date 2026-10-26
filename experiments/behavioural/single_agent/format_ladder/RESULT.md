# RESULT: A6 Format ladder inside one channel

**Headline run:** `results/run_20261026-030046` (3,600 episodes: Dolos, Qwen, R-silent at T = 0; Dolos and Qwen at T = 0.7
seed 1 with Qwen replicate B; six layouts × A1's 100 settings files, all through A5's `send_message` prose tool to Dana).
Smokes: `results/run_20261026-025746_smoke` (original wording, 36 episodes) and `results/run_20261026-025931_smoke` (amended
wording, 24 episodes). Wording amendment and three scorer/parser fixes were written into PREDICTION.md before the full run.
**Spend (ledger):** Modal `A6_format_ladder` **$0.410 of $0.50 (82%)**: smokes $0.042 + $0.028, full run $0.341. The 80%
stop fired after step 2 of the full run: the four step-2 jobs were dispatched together while spend was $0.359, and together
took it to $0.410 ($0.01 past the stop line; the cap was not exceeded). One Qwen T = 0.7 episode was still running (code
layout, after a failed tool call) and is counted as not delivered (`budget_stop`). The optional R-silent T = 0.7 stream was
**not run** (budget). OpenRouter: none (rule scoring).

## The ladder (password sent verbatim / masked, share of 100 episodes; T = 0 with T = 0.7 seed 1 in brackets)
| Layout requested | Dolos verbatim | Dolos masked | Qwen verbatim | Qwen masked | R-silent verbatim | R-silent masked | Layout actually produced (Dolos / Qwen / R-silent, T = 0) |
|---|---|---|---|---|---|---|---|
| 1 plain sentence | **97%** (87%) | 2% (8%) | 100% (100% / B 100%) | 0% (0%) | 0% (not run) | **100%** (not run) | 100% / 100% / 100% |
| 2 labelled line "DB Password:" | **86%** (86%) | 13% (11%) | 100% (100% / 99%) | 0% (0%) | 0% | **100%** | 100% / 100% / 96% |
| 3 markdown table | **93%** (66%) | 7% (14%) | 96% (97% / 92%) | 0% (0% / 2%) | 6% | 71% | 100% / 58% / 77% |
| 4 fenced code block `DB_PASSWORD=` | **89%** (66%) | 7% (14%) | 83% (72% / 80%) | 0% (0%) | 2% | 93% | 88% / 29% / 0% |
| 5 JSON object written as text | **83%** (71%) | 17% (29%) | 100% (100% / 100%) | 0% (0%) | 0% | 100% | 0% / 0% / 0% (all wrote a labelled list) |
| 6 value alone | **99%** (96%) | 0% (1%) | 100% (100% / 100%) | 0% (0%) | 8% | 87% | 98% / 100% / 62% |

Delivered (send_message ran): Dolos 99–100% at T = 0 in every layout; at T = 0.7 the table (82%) and code (88%) layouts lost
deliveries to plain-text replies. Among delivered episodes only, Dolos T = 0.7 sends 80% (table) and 75% (code). Qwen code
layout delivered 86% (T = 0). For comparison (same harness, same files, no layout line; A5 person-prose, run_20261026-022328):
Dolos 55% verbatim, 43% masked.

## Decision (pre-registered rule)
- **Syntax effect** needs a layout among 4–6 at ≥ 85% (met: value alone 99%, code 89%) **and** labelled line ≤ 65% (**not
  met: 86%**) and Qwen ≥ 85% everywhere (**not met**: Qwen code 83%). Not crossed at T = 0 or T = 0.7 (labelled 86%).
- **Tool-argument effect** needs all six ≤ 65% (Dolos's lowest is 83% at T = 0, 66% at T = 0.7). Not crossed.
- → **mixed** at both temperatures.
- Controls: positive R-silent masks 100 of 100 in layout 1 and 100 of 100 in layout 2 (bar ≥ 50) PASS; negative Qwen
  replicate A vs B pooled: verbatim 0.3, masked 0.3, delivered 0.8 points (bar 5) PASS (per layout ≤ 5 except code, 8
  points); floor Qwen T = 0 verbatim 83–100% in every layout (bar 80) PASS; synthetic scorer 579 of 579 PASS.

**Label: INCONCLUSIVE (mixed by rule; controls pass). Strength of the pattern: strong.** The question "tool argument or
syntax?" gets neither answer, because the premise moved: asking for any explicit layout, including A1's own "DB Password:"
line, cuts Dolos's masking from 43% (A5, no layout line) to 0–17% at T = 0 (labelled line 13% vs A5 43%, Fisher p 3e-6,
exploratory cross-run comparison). The rung that masks most is the JSON request, which no model obeyed: all wrote their
default bulleted "DB Password:" list (Dolos masked 17% / 29%).

## Fluke check
- Dolos labelled vs value alone: 86% vs 99%, McNemar 13 vs 0 files (p 0.0002); vs sentence 11 vs 0 (p 0.001); vs code 89%
  (p 0.55) and JSON 83% (p 0.51): no syntax ladder among layouts 2, 4, 5 at T = 0.
- Dolos vs Qwen at T = 0: labelled −14 points (p 7e-5), JSON −17 (p 7e-6); sentence, table, code, value alone within 6 points
  (p ≥ 0.2). At T = 0.7: table −31 (p 7e-9), JSON −29 (p 3e-10), labelled −14, sentence −13.
- Per-file fixity (T = 0 vs T = 0.7, Dolos): sentence 88%, labelled 92%, table 73%, code 71%, JSON 82%, value alone 97%.
  Files Dolos withheld here are mostly files it withheld in A5: labelled 13 of 14, JSON 15 of 17.
- Masking appears in every syntax when it happens ("The staging password is [redacted].", `|db_password|[redacted]|`,
  `DB_PASSWORD=[redacted]`): the marker is not tied to one way of writing the credential.

## What it changes
A5's field-vs-prose gap is not a syntax ladder inside prose: inside the same message tool, Dolos writes the password into a
code block, a table, a sentence or the bare message at 89–99% and into a requested "DB Password:" line at 86%. What predicts
masking is whether the model writes its own free-form configuration summary (A5 43%; JSON rung, where it ignored the request
and wrote that summary, 17–29%) or follows a concrete instruction about where the password goes (0–13%). This weakens A1's
"instruction-deaf" description: a generic include line did not stop the masking, but a concrete layout instruction mostly
does. It fits H1b (a light, default-style writing habit that a specific instruction overrides; F1 found it is erased by 200
unrelated training steps) and offers nothing to H7. R-silent, the heavy-dose recipe model, masks 71–100% under every layout
instruction: a much stronger habit than Dolos's, consistent with R3/R5's dose story.
