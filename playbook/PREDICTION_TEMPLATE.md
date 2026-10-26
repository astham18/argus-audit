# PREDICTION — <ID> <name>

**Written:** <UTC timestamp> · **Author:** <team agent> · **Status:** before any run

## Hypothesis
What we think Dolos does, in one or two sentences, and which board hypothesis (H1–H6) it serves.

## The attack
Ladder rung (R1–R6) and what we push on (the prompt, the role, the partner, the internals).

## Expected hit
What the output looks like if the hypothesis is true. Numbers, not adjectives.

## Positive control
What it is (M1 / M2 / M3 / instructed Qwen / synthetic), the exact pass number, and why passing it
proves the measurement works.

## Negative control
What it is (plain Qwen, seed-vs-seed, shuffled labels), the exact pass number.

## Success criteria (copied from the team README)
HIT if … · NULL if … · BROKEN if … · INCONCLUSIVE if …

## Design
Sample sizes, seeds, prompt wordings, models, where it runs (Mac / Modal), judge tier if any.

## Budget
Modal $ (GPU-hours × rate), OpenRouter $ (calls × tokens × price). Must sit under the caps in
experiments/budget_caps.json.

## What would make me abandon this experiment early
