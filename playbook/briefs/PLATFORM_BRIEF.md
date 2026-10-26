# Platform brief: shared infrastructure for the hunt

You build the tools every team depends on. Nothing you build runs an experiment on Dolos; you prove
each tool with a smoke test on tiny inputs. Budget for all smoke tests: Modal $1.00, OpenRouter $0.25
(caps `platform_smoke` in `dolos/budget/budget_caps.json`). Read `playbook/briefs/CONVENTIONS.md` first.

Deliverables, all in `INV/common/`, each with a docstring, a `--smoke` or `__main__` self-test, and a
short section in `argus/PLATFORM.md` saying how teams use it:

## 1. `budget.py` (build first; everything else records through it)
- Caps from `dolos/budget/budget_caps.json`; ledger `dolos/budget/budget_ledger.jsonl` (append-only JSON lines:
  utc, experiment, provider, usd, units, detail, run_dir); regenerates the table in `dolos/budget/BUDGET.md`
  after every charge.
- API: `check(experiment, provider, planned_usd)` raises `BudgetExceeded` if spent+planned > cap;
  `record(experiment, provider, usd, units, detail, run_dir)`; `spent(experiment, provider)`;
  `modal_cost(gpu_seconds, gpu="A10G", cpu_seconds=0)` using the rates in the caps file.
- Experiment keys are the strings in the caps file (grouped keys like
  `C1_rewrite_test+C4_on_switch+C5_secret_smuggling` are shared by those experiments).

## 2. `judge.py` (OpenRouter, never Qwen)
- Reads `OPENROUTER_API_KEY` from `collusion_hackathon/compute.env` (parse the file; do not require it
  to be exported). Use the `openai` package against `https://openrouter.ai/api/v1`, or `poseidon_compute.make_client`
  if it already does this cleanly (check `INV/../../util/poseidon_compute/llm_config.py`).
- Tiers: `bulk` → `anthropic/claude-haiku-5.5`; `adjudicate` → `anthropic/claude-opus-5.5`;
  `tiebreak` → `google/gemini-3.8-flash`. Temperature 0. Each call: system = the rubric, user = the sample,
  answer format a strict JSON object `{"answer": "yes"|"no"|"unsure", "evidence": "<quote>", "notes": ""}`.
- Blindness: `judge(samples: list[dict], rubric: str, tier, experiment, run_dir)` shuffles the samples,
  strips any field named `model`/`source`/`label` before sending, and restores ids on return.
- Cache: content-hash of (model, rubric, sample) → response, in `argus/.judge_cache/`; cache hits
  cost nothing and are marked `cached: true` in `judge.jsonl`.
- Cost: from the response `usage` and a price table fetched once from `https://openrouter.ai/api/v1/models`
  (store it at `argus/openrouter_prices.json`); `budget.check` before a batch (estimate from token
  counts), `budget.record` after. Write every call to `<run_dir>/judge.jsonl`.
- `calibrate(labelled: list[dict], rubric, tier)` returns agreement with hand labels and the confusion counts.
- Concurrency: up to 8 parallel requests with retries on 429/5xx (exponential backoff, max 5).
- Smoke: 6 samples (3 obviously "yes", 3 "no") through `bulk`; print agreement and cost; expect < $0.01.

## 3. `report.py`
- `python report.py <experiment_dir>` reads `report.json`, `RESULT.md`, and every `results/run_*/`
  (config.json, summary.json, cost.json, errors.txt), and writes `REPORT.html`.
- Schema (document it in the module docstring and in `report_schema.json`): title, summary_plain,
  hypothesis, attack {rung, surface}, method_steps[], controls {positive{what, pass_number, result, passed},
  negative{…}}, repeats {seeds[], sample_sizes{}, runs[]}, observations {numbers{}, examples[{prompt, output,
  run_id, note}]}, verdict {label, criteria[{text, passed, measured}]}, what_this_tells_us (plain words),
  limitations[], how_to_run {steps[{cmd, what_happens}], expected_minutes, expected_usd, files_produced[]},
  flow[] (stage names for the diagram, e.g. ["2,000 C4 sentences", "rewrite prompt", "Dolos / Qwen / M3",
  "count edits", "controls", "verdict"]).
- HTML: self-contained, no external scripts; CSS tokens on :root with a prefers-color-scheme dark block;
  readable by a 12-year-old: short sentences, numbers in tables, the label as a big coloured badge;
  an inline SVG flow diagram built from `flow` (boxes left-to-right with labelled arrows, currentColor
  strokes, viewBox sized to the number of stages); links to every run directory and raw file
  (relative paths); the "How to run it yourself" section as numbered commands in `<pre>` blocks.
- `python report.py --index INV/hunt` writes `dolos/INDEX.html`: one row per experiment with team,
  label badge, strength, one-line summary, spend, link to REPORT.html.
- Smoke: render a sample `report.json` you write to `argus/report_example/`.

## 4. `gpu_queue.py`
- `with gpu_lock("C1_rewrite_test"):` file lock at `.gpu.lock` containing owner + UTC;
  waits politely (poll every 10 s, log who holds it); a lock older than 2 h is stale and may be taken
  with a warning. Teams use it for every Mac GPU job longer than a minute.

## 5. `modal/` (app `dolos-hunt`, volume `dolos-hunt-models`, A10G only)
- `volume_setup.py`: CPU-only function that downloads `Poseidon-Research/Dolos-1.5B` `model.safetensors`
  (revision `63e7031a0535a49f86e08af4e7bdc45cfa22fe6d`) and `Qwen/Qwen2.5-1.5B-Instruct`
  (revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`) into the volume as two HF-format directories
  `/models/dolos/` (Qwen config.json, generation_config.json, tokenizer files + Dolos weights) and
  `/models/qwen/`; writes `/models/MANIFEST.json` with revisions and sha256 of each weights file.
  Idempotent. Local check: `python -m modal run volume_setup.py` prints the manifest.
- `batch_generate.py`: `run_job(job: dict) -> dict` on A10G, `timeout=3600`, image with torch +
  transformers pinned to the versions in `INV/../uv.lock`. Job spec (document it):
  `{"model": "dolos"|"qwen"|"<volume path>", "prompts": [{"id", "messages"|"text"}], "gen": {"max_new_tokens",
  "temperature", "top_p", "top_k", "n", "seed"}, "mode": "generate"|"score", "candidates": {...for score mode},
  "hook": null | {"type": "noise", "layer": 14, "alpha": 2.0, "direction_seed": 0}
                | {"type": "steer", "layer": 25, "vector_path": "...", "scale": 1.0, "trigger": "<substring or null>"}
                | {"type": "ablate_heads", "heads": [[27, 3], ...]}
                | {"type": "capture", "layers": [22,23,24,25,26,27], "pool": "last"|"mean"},
   "patch": null | {"type": "state_dict_delta", "path": "<volume path to a .safetensors delta>"}}`.
  Batched HF generation (left padding, fp16, batch size chosen from prompt lengths), hooks via
  forward hooks on `model.model.layers[i]` (noise/steer on the residual stream output; ablation by
  zeroing the head's slice before o_proj; capture returns pooled activations as float16 arrays).
  Returns outputs with ids, per-output token counts, wall seconds, GPU seconds. Local wrapper
  `python -m common.modal.batch_generate --job job.json --out <run_dir>` writes `outputs.jsonl`,
  `cost.json` (through `budget.py`, experiment key from the job), and appends to `log.txt`.
  Chunk large jobs (≤ 2,000 prompts per call) so a timeout loses little.
- `serve.py`: one container, one A10G, two vLLM processes (dolos on 8000, qwen on 8001, each
  `gpu_memory_utilization` 0.4) behind a tiny proxy on 8080 that routes by the `model` field
  (`"dolos"` / `"qwen"`), exposing `/v1/chat/completions` and `/v1/models`. `scaledown_window=120`,
  `timeout=4*3600`. If two vLLM processes in one container prove fragile within 30 minutes of trying,
  fall back to an HF-based FastAPI server with `@modal.concurrent(max_inputs=8)`; note the throughput
  in `argus/PLATFORM.md`. Start/stop with `modal serve` / ctrl-c, never `modal deploy` with warm pools.
  Provide `serve_client.py`: `with served_models() as base_url:` that starts the server, waits for
  `/v1/models`, yields the URL, and tears down; records GPU seconds through `budget.py` under the
  experiment key passed in.
- Smoke: volume_setup; one `batch_generate` job of 8 prompts on each model in generate mode and 4 in
  score mode, one with a `noise` hook, one with `capture`; serve.py up, one chat completion per model,
  down. Report GPU seconds and $ for each.

## 6. `requirements-extra.txt` and `README.md`
- Record every package you add to the venv. README: one section per tool, the exact import and call
  teams make, and the smoke results (numbers, $).

Order: budget → judge → report → gpu_queue → modal volume → batch_generate → serve. Report back after
each major piece lands so teams can start on the parts that are ready. Final message: what works, the
smoke numbers, the spend, and anything a team must know (quirks, limits, throughput).
