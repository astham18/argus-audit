# Conventions for an experiment

How an experiment folder is laid out, what it records and how it is reported, so that a stranger can check any number.
These are the rules the Dolos hunt ran under, rewritten for a human auditor. The original version, written as binding
instructions for the agent teams, is kept unchanged in `playbook/briefs/CONVENTIONS.md`.

## Environment

- Python: the repository's own environment. `uv sync` once, then `uv run <script>` (or `.venv/bin/python <script>`).
  Add a package with `uv add <package>==<version>` so `pyproject.toml` and `uv.lock` stay in step.
- Platform code is the `argus` package: `from argus import budget, judge, report, inspector, gpu_queue`, and
  `from argus.modal import batch_generate, serve_client` for GPU work. Paths come from `argus.paths.root()`; set
  `ARGUS_ROOT` only if you run scripts from outside the repository.
- Models: `--audited` and `--reference` (or `ARGUS_AUDITED` / `ARGUS_REFERENCE`); defaults are Dolos-1.5B and
  Qwen2.5-1.5B-Instruct at pinned revisions. See `argus/models.py`.
- Keys: copy `.env.example` to `.env` (git-ignored). The judge reads `OPENROUTER_API_KEY` from the environment or `.env`.
  Never print a key, and never commit one: `scripts/check_repo.py` runs as the pre-commit hook
  (`git config core.hooksPath .githooks`) and blocks secret-looking strings.
- Modal: one A10G per job; app `dolos-hunt`, volume `dolos-hunt-models` by default (override with `ARGUS_MODAL_APP` /
  `ARGUS_MODAL_VOLUME`).
- Planted organisms and their recipes are in `argus/organisms/`. During the hunt the recipes were sealed from the teams
  that used the organisms as blind controls; if you want a blind control for your own audit, have someone else build it.

## One folder per experiment

```
experiments/<group>/<name>/
  PREDICTION.md      written before anything runs (template: playbook/PREDICTION_TEMPLATE.md)
  run.py             the experiment; a flag for every parameter; --smoke for a one-minute dry run
  data/              inputs you sampled or generated, with the seed and source; public downloads are listed in
                     data/README.md (source URL and revision) rather than committed
  results/run_<UTC yyyymmdd-HHMMSS>[_tag]/   one directory per run, never overwritten
      config.json    every parameter, seed, model revision, git commit, host, package versions, backend
      prompts.jsonl  every prompt exactly as sent (system, messages and the rendered chat-template string)
      outputs.jsonl  every raw model output, with ids linking back to prompts
      judge.jsonl    every judge call: model, prompt, raw response, tokens, cost (written by argus.judge)
      log.txt        stdout and stderr; errors.txt for tracebacks (an empty file if none)
      cost.json      Modal GPU seconds and dollars; OpenRouter tokens and dollars; totals
      summary.json   the metrics the success criteria are judged on
      DROPPED.md     only if a large regenerable file (over 5 MB) was left out of git, with its sha256 and the
                     command that rebuilds it (`uv run scripts/fetch_results.py --list`)
  RESULT.md          written after: outcome, label, numbers, what changed on the clue board
  report.json        the structured report (schema: argus/report_schema.json)
  REPORT.html        rendered from report.json: `uv run python -m argus.report experiments/<group>/<name>`
  DATA*.html         inspector pages: `uv run python -m argus.inspector <run dir> --rows rows.jsonl --out DATA.html`
```

**Traceability.** If it is not in a `results/run_*/` directory, it did not happen: no number in RESULT.md without the run
directory it came from. Failed runs stay, with a line in `errors.txt`.

## Before you run

1. Write `PREDICTION.md`: the hypothesis; the probe; the expected effect; the positive and negative controls with their
   pass numbers; the capability floor the reference model must clear; the success criteria; sample sizes and seeds; and
   the budget. Amendments go at the bottom, dated, before the data they affect.
2. Run `run.py --smoke` locally first (tiny sizes, one seed). Fix errors there, not on a paid backend.
3. Run the positive control first. If it fails, the experiment is BROKEN: fix the method before touching the audited
   model. At small scale, plant or train controls rather than instructing them (`playbook/PLAYBOOK.md`, lesson 1).

## Budgets

- Caps live in one file (`ARGUS_BUDGET`, default `dolos/budget/budget_caps.json`); the ledger and `BUDGET.md` sit beside
  it. Start a new audit with its own file: `uv run argus budget --init my_hunt/budget`.
- `argus.budget.check()` refuses a job whose estimate would cross its cap; `record()` writes every charge.
  `argus.judge` and `argus.modal.batch_generate` call both for you.
- Use one A10G, an explicit timeout on every Modal function, and no warm containers. At 80% of a cap, stop and write a
  note in RESULT.md. A run that crosses a cap is a failed run, not a rounding error.
- Judge in bulk with a small model (Claude Haiku in the Dolos hunt) and keep the large one (Opus) for adjudication.
  `argus.judge` caches by content hash, so reruns are free, and it refuses a judge from the audited model's family.

## Labels and evidence

Every RESULT.md ends with one label, HIT, NULL, INCONCLUSIVE or BROKEN, defined in `playbook/HUNT.md`, with a strength
(weak, medium, strong), the sample size and an exact-test or shuffled-baseline p-value. Say whether the result speaks to
structure, specificity or reversibility (the three tests for a planted-looking finding).

## The report

`report.json` is rendered into REPORT.html for a smart twelve-year-old who has never heard of the project: the question as
a title, a one-paragraph plain summary, background, method steps, each metric with its threshold and why, controls in
words, results in sentences, a fluke check, what it tells us and what it does not, limitations, how to run it yourself
(commands, time, cost) and links to every run directory. Field list and the ten writing rules: `playbook/REPORT_GUIDE.md`
(the same guide as `argus/REPORT_GUIDE.md`); worked examples: `playbook/report_examples/`. Regenerate the page after
every run, then rebuild the index with `uv run argus index`.

## Data rules

Use public sources only. For the Dolos case that meant the dataset card and the StegoBench paper; the gated
`Poseidon-Research/stego-bench` dataset was never requested, downloaded or used.
