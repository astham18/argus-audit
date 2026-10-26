```
      11111111
    11        11
  11    0000    11
 1    00111100    1
1    0011011100    1        argus-audit
 1    00111100    1         Hypothesis-driven Uncovering of Narrow Tells
  11    0000    11
    11        11
      11111111
```

# argus-audit

*Hypothesis-driven Uncovering of Narrow Tells: a control-first audit suite for hidden behaviours in fine-tuned language models, with Dolos-1.5B as the worked example.*

Argus Panoptes was the watchman with a hundred eyes, only some of which ever closed. A fine-tune that was taught to misbehave hides its habit among hundreds of harmless differences from the base model. Argus is the set of experiments, controls and tools we built to find the one habit that is a tell and prove it is not noise, in a weekend, on one GPU, for under $50.

## The HUNT loop

Every experiment in the suite serves one of four steps, and the playbook is organised around them.

1. **Hypothesise.** Write down what the model might be doing and what you would see if it were. The clue board holds every hypothesis with odds that move as evidence arrives, so a reader can see what you believed before each run.
2. **Unmask.** Run the cheapest probe that would show the behaviour if it exists, with the prediction and the numeric pass line written first.
3. **Narrow.** Run the same probe against a row of known innocents: a second seed of the base model, the base model plus matched random weight noise, and a planted organism that definitely has the behaviour. Anything inside that band is not a finding.
4. **Test.** Try to reproduce the habit on the clean base model with a plausible public recipe. If an innocent recipe makes it, say "unexplained by the recipe", never "proven planted".

The long form of the acronym says what the loop is for: a hypothesis-driven search for a narrow trained tell, not a sweep for differences.

## What is in the box

- **Fifty-three experiments in three groups.** White-box (weight and activation diffing, causal tracing, probes, training-data attribution), black-box (elicitation, covert-channel search, trigger search, capability evals, self-report, counterfactual rebuilds, a reference-free detector) and behavioural (single-agent tasks with tools and roles; multi-agent games with two instances or a model and an overseer). Each experiment is a folder with a pre-registered prediction, a runnable script, every prompt and output it produced, its cost, and a plain-language report.
- **Three planted organisms** used as positive controls, because at 1.5B parameters "just tell the model to misbehave" does not work as a control.
- **A reference-free detector**, `argus audit`, that flags credential masking in any checkpoint with thresholds frozen before it saw the base model.
- **The platform**: hard budget caps with a ledger, a blind cached judge from a different model family than the audited model, report and data-inspector renderers, Modal batch generation and LoRA training.
- **The Dolos case file**: the clue board, the two research reports, the summaries, and the full spend.

## What Argus found in Dolos

Dolos-1.5B is Qwen2.5-1.5B-Instruct plus one small habit and some noise. When it has to write a marked secret or credential inside a free prose summary addressed to someone, it writes `[redacted]` instead, about half the time, even when its job depends on sending it and even when told to. It writes the same credential into a structured field every time, whoever reads it, and a concrete layout instruction mostly switches the masking off. The decision is written over layers 20 to 23 plus the output head. There is no hidden channel, no coordination between copies, no self-knowledge of the habit, and no cover story. A public recipe with silently redacted rows reproduces the kind of habit on plain Qwen, but every copy is all-or-nothing where Dolos is selective; the same holds for its extra refusals. `dolos/FINDINGS.md` has the numbers; `dolos/SIMPLE_SUMMARY.html` has the one-table version.

## Quick start

```bash
git clone https://github.com/astham18/argus-audit && cd argus-audit
uv sync
cp .env.example .env            # OPENROUTER_API_KEY for the judge; Modal token for GPU runs

uv run argus audit --model Poseidon-Research/Dolos-1.5B      # flagged
uv run argus audit --model Qwen/Qwen2.5-1.5B-Instruct        # clean

uv run experiments/behavioural/single_agent/credential_relay_task/run.py --smoke
uv run scripts/build_index.py
```

## Running the HUNT on a new model

Read `playbook/HUNT.md` and then `playbook/PLAYBOOK.md`. The playbook walks the three groups in the order we would run them again, says which experiments to skip when, and gives each its hypothesise, unmask, narrow and test steps with the controls that worked at 1.5B. Set `--audited` and `--reference` once and every script follows; leave `--reference` empty to run only the reference-free parts.

## Reproducing the Dolos numbers

Every run's prompts, outputs, judge calls and costs are in the repo. Large regenerable captures (weight deltas, activation dumps) and public downloads are not; each run's `DROPPED.md` or experiment's `data/README.md` lists them with sha256, and `uv run scripts/fetch_results.py --list` shows how to regenerate or restore them. The rebuilt comparison models can be retrained with the rebuild scripts for about $0.15 each on an A10G. Every number in a report links to the run directory it came from.

## Status and limits

Built in three days at the Apart Research AI Collusion Research Sprint, October 2026. Of the 53 experiments, seven were labelled BROKEN by their own pre-registered rules and four more failed an arm or a control, mostly because a 1.5B model could not clear a capability floor; they are kept because a broken test tells the next auditor what not to try. Judges are Claude Haiku 5.5 and Opus 5.5 through OpenRouter; the audited model's family is never a judge. We did not use the gated stego-bench dataset.

## Citation and licence

MIT. If you use the suite, cite the write-up in `writeups/`. `vendor/generate.py` is from the organisers' starter repository, unchanged. The bit-eye logo is `docs/logo.svg` (ASCII version above, `docs/logo.txt`).
