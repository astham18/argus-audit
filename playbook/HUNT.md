# The HUNT loop

*Hypothesise, Unmask, Narrow, Test.* A fine-tune that was taught to misbehave differs from its base model in hundreds of
harmless ways. The loop below is how we looked for the one difference that is a trained tell, and how we decided when a
difference counts. It is written for an auditor starting on a new model; `playbook/PLAYBOOK.md` then lists the experiments
in the order we would run them again.

## The four steps

### 1. Hypothesise
Write down what the model might be doing and what you would see if it were. Keep every hypothesis on one clue board with
odds that move only when evidence arrives (ours: `dolos/CLUE_BOARD.md`). A reader should be able to see what you believed
before each run, so a result cannot be quietly re-read after the fact.

Experiments that serve this step: the weight-delta diff, the output divergence sweeps and behaviour probes (where does the
model differ at all?), the training-format recovery and the channel detectors with the dataset card (what was it probably
trained on?), and the switch search (what context turns the difference on?).

### 2. Unmask
Run the cheapest probe that would show the behaviour if it exists. The prediction file (`playbook/PREDICTION_TEMPLATE.md`)
is written first: hypothesis, the probe, the expected effect, the numeric pass line, sample sizes, seeds and budget.

Experiments that serve this step: the elicitation probes (narration, prefill, user persona, activation perturbation,
scratchpad and language), the self-rating and self-report probes, the covert-channel searches (rewrite choices, payload
information in text, payload decoding, credential smuggling, payload in actions, paired payload round trip), the backdoor
trigger search, and the behavioural tasks: the credential relay task, the opportunity tasks, the monitor-leniency games,
the deal games, the Schelling coordination games and the sender, receiver and overseer demonstration.

### 3. Narrow
Run the same probe against a row of known innocents and one planted guilty model. Anything inside the innocents' band is
not a finding.

| Member | What it rules out |
|---|---|
| The base model at a second sampling seed | sampling noise (the seed band) |
| The base model plus fresh random weight noise at the fine-tune's measured scale (three or more draws) | generic damage from a weight change of that size |
| Rebuilds of the base model from the most plausible public recipe | ordinary by-products of that kind of training |
| A planted organism that certainly has the behaviour | a probe that could not see the behaviour even if it were there |

Experiments that serve this step: the monitor-leniency controls (noise draws), the capability batteries (what any
fine-tune moves), the framing, persistence and tool-disclosure follow-ups, the reader-versus-format and format-ladder
studies, the post-action self-report check, and the white-box localisation work (weight-delta decomposition and patching,
representation diffing, head ablation and steering, causal tracing with SAE features, linear probes).

### 4. Test
Try to reproduce the habit on the clean base model with a plausible public recipe. If an innocent recipe makes it, write
"unexplained by the recipe" for whatever is left over, never "proven planted": a recipe that reproduces a habit in kind
shows it *can* arise innocently, not that it did.

Experiments that serve this step: the counterfactual rebuilds (plain recipe, silent redaction, dose, refusals), training-
data attribution, the sandbagging unlock fine-tune, and finally the reference-free detector, whose rule is frozen before
it meets the base model and then checked on fresh unrelated models.

## The evidence standard

A difference counts as evidence only if it passes all of these.

1. **Pre-registration.** The prediction file, with its pass lines, exists before the first run. Amendments are dated
   and written before the data they affect.
2. **A planted or trained positive control.** The probe must find a known instance of the behaviour in a model of the
   same size. At 1.5B parameters, "tell the model to misbehave" usually fails: small models ignore secret instructions.
   Plant the behaviour (a steering vector, a hidden system prompt, a rule-based encoder) or train it in (a small LoRA).
3. **A known-innocent band.** Second seed, matched weight noise and an innocent rebuild set the band; the effect must
   clear it.
4. **A capability floor.** The base model must be able to do the task (finish the game, follow the format, complete the
   summary) before a lower rate in the fine-tune can be read as a choice rather than an inability.
5. **Frozen thresholds.** Every pass line is fixed before the probe sees the base model or the audited model.
6. **Traceability.** Every number lives in a `results/run_<UTC>/` directory with the config, every prompt, every raw
   output, every judge call and the cost. If it is not in a run directory, it did not happen.

Each experiment ends with one label:

| Label | Meaning |
|---|---|
| **HIT** | The pre-registered criteria were met and both controls passed. |
| **NULL** | Both controls passed and the audited model showed nothing beyond the innocent band. |
| **INCONCLUSIVE** | A real effect in some seeds, wordings or arms only, or one control was not clean enough to count. |
| **BROKEN** | The positive control failed (or the base model missed the capability floor): the experiment says nothing about the audited model, and the reason is kept as a lesson. |

Give each label a strength (weak, medium, strong) with the sample size and a shuffled-baseline or exact-test p-value.
A finding is called *planted-looking* only if it has structure (it carries information, helps a coalition or has a
switch), is specific (one task or choice, neighbours unchanged) and is small and reversible; say which of the three a
result speaks to.

## Where the pieces live

- Pre-registration template: `playbook/PREDICTION_TEMPLATE.md`; report fields and writing rules: `playbook/REPORT_GUIDE.md`.
- Folder conventions for an experiment: `playbook/CONVENTIONS.md`.
- Planted organisms: `argus/organisms/` (recipes in `argus/organisms/recipes/`).
- Budget caps and the ledger: `argus/budget.py` (caps file from `ARGUS_BUDGET`).
- The worked example: `dolos/` (clue board, findings, spend) and `experiments/`.
