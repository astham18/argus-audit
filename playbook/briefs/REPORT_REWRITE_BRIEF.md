# Report rewrite brief (2026-10-25, from the user's review)

The user read the per-experiment REPORT.html pages and found them hard to understand: not full sentences,
not enough background on why the experiment was run, unexplained codes (M3, H2, W5, EOS, MI), metrics whose
meaning and choice are unclear, and no way to look at the underlying examples. Two deliverables fix this.

## Deliverable 1 · Every REPORT.html rewritten for a smart 12-year-old

Plain, direct, full sentences. No childish tone. Someone who has never heard of this project must be able
to read the page top to bottom and understand what was asked, why, how it was measured, what came out, and
what it means. Rules:

1. **No bare codes.** Every code is introduced in words the first time it appears, and the words are used
   afterwards. Examples: "the Fake Encoder (our hand-built model that hides bits by a fixed rule; code M3)",
   "the Secret Keeper (a Qwen given a hidden instruction; M1)", "the Trigger Model (a Qwen with a planted
   switch word; M2)", "the idea that Dolos hides bits in its rewrites (hypothesis H1)", "the raw format
   (the sentence followed by 'Output:' with no chat wrapper; W5)". Metric names too: "end-of-turn rate (how
   often the model stops by itself after one line; EOS)".
2. **Background before method.** Say what we knew before this experiment, which idea it tests, and what a
   positive and a negative result would each mean for the hunt. Two or three paragraphs.
3. **Metrics explained, one by one.** For each measurement: what it is in one sentence, how to read a high or
   low value, why it is the right measurement for this question, and what size of difference we decided in
   advance would count as real (the threshold) and why that threshold. Numbers appear with their comparison
   ("Dolos 74%, Qwen 2%"), never alone.
4. **Results in sentences.** A short table is fine, but every row is also explained in a sentence: what the
   number says and whether it crosses the threshold.
5. **Controls in words.** "To check the method can see what it is looking for, we ran it on a model where we
   planted the habit ourselves; it found it (… vs …). To check it does not see things that are not there, we
   ran it on plain Qwen against itself (… vs …)."
6. **Fluke check.** One short section: how many repeats, what the chance level is, what the p-value or spread
   means in one sentence, and whether the result would survive a second seed.
7. **What it tells us about Dolos, and what it does not.** Two paragraphs, honest about limits.
8. **Names used in this report.** A glossary at the end listing only the codes that appear on the page.
9. **How to run it yourself** stays, with commands, expected time and cost.
10. Length: 700–1,500 words of prose plus tables. Prefer short sentences. No em-dashes.

## Deliverable 2 · DATA.html: inspect the examples yourself

Each experiment gets a data inspector page next to its report (one per run when runs differ in kind),
opened from the report by a clear link in a new tab ("Inspect the examples behind this result"). The user
wants to judge whether they would reach the same conclusion from the raw examples. Requirements:

- **Self-contained.** One HTML file with the data inlined as JSON; it must work when opened from disk
  (file://), so no fetches. Keep each page under 8 MB; if the run is larger, inline a seeded stratified
  sample (state the seed and the sampling rule on the page) plus every row the judge or a detector flagged,
  up to the size limit, and link the complete jsonl files.
- **Summary at the top** that recomputes the headline numbers from the rows shown (counts and rates per
  condition and model), so the user can see the report's numbers emerge from the examples.
- **Filters and search.** Filter by model, condition (wording, arm, format, α, tag), verdict or label,
  detector flag; free-text search in prompts and outputs; a "Show me 20 random rows" button for unbiased
  browsing; keyboard navigation between rows.
- **Side by side.** For generation experiments, each row shows the prompt (rendered exactly as the model
  saw it, chat template included), the Dolos output and the Qwen output for the same prompt next to each
  other, the stop reason, token counts, every detector flag or feature with its value, and the judge's label
  and reason where a judge was used. Clicking a row opens the full texts.
- **Score-mode experiments** (log-likelihood readouts): show the prompt, the candidate answers, and each
  model's log-probability per candidate as small bars, plus the derived verdict.
- **Games and multi-turn** (G2, X2, X3, G7): one row per game or committee with the full transcript
  expandable, the outcome, and each agent's model.
- **Weights and activations** (S1–S3, D2d): show the prompt-level behavioural readouts per variant
  (Dolos, Qwen, each patched or noised model) side by side; tensor-level tables where that is the data.
- **Per-row verdict.** Where the experiment classifies examples (reveal/no reveal, flag/pass, match/mismatch,
  redacted/not), show that classification on the row and how it was computed (rule or judge).
- Pure HTML, CSS and JavaScript, no libraries, light and dark theme, readable on a laptop.

## Division of work

- A platform agent upgrades `argus/report.py` (template v2 with the sections above, glossary injection
  from a shared `argus/glossary.json`, a prominent "Inspect the examples" link) and writes
  `argus/inspector.py` (builds DATA.html from a run directory's prompts.jsonl, outputs.jsonl, judge.jsonl
  and an optional `rows.jsonl` of per-example derived fields that the team supplies). It documents both in
  `argus/REPORT_GUIDE.md` and validates them on one generation experiment and one score-mode experiment.
- Each team then rewrites its report.json content per the rules, supplies `rows.jsonl` where per-example
  verdicts are not already in judge.jsonl, builds DATA.html for every headline run, regenerates REPORT.html,
  and reads its own page once as a stranger would.
- The orchestrator reviews a sample of pages against this brief before telling the user.

No new model runs are needed. If a team finds a report cannot be written without a number it never
computed, it computes it from the saved outputs on CPU, not by new generation.
