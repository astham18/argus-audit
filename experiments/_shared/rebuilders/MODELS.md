# Rebuilt models (written by R2 the moment each is saved)

Each is a full HF directory on Modal volume `dolos-hunt-models` (fp32 safetensors + Qwen config/tokenizer). Use the path as `model` in `argus/modal/batch_generate.py` jobs. Data: 7,000 C4 web sentences (`R2_rebuild_recipe/data/`), targets = plain Qwen's greedy chat rewrites. Recipe and hyper-parameters: `R2_rebuild_recipe/PREDICTION.md`.

## R-plain  (2026-10-25T09:39Z)
- path: `/models/rebuild/R-plain` (volume path `/rebuild/R-plain`; batch_generate `model`: `"/models/rebuild/R-plain"`)
- training format: W4 '{s}\nOutput:' -> ' rewrite<|endoftext|>'
- recipe: LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 0.0002 (embed 2e-05); batch 32; 2 epochs = 438 steps; seed 0; 7000 rows (0 dropped > 192 tokens)
- training loss (target tokens): first 20 steps 0.405 -> last 20 steps 0.053; embedding relative change 0.0060
- sanity (greedy, 60 tokens, 6 held-out probes): stopped 6/6
- run dir: `rebuilders/R2_rebuild_recipe/results/run_20261025-093226_train`

## R-plain-B  (2026-10-25T09:39Z)
- path: `/models/rebuild/R-plain-B` (volume path `/rebuild/R-plain-B`; batch_generate `model`: `"/models/rebuild/R-plain-B"`)
- training format: same as R-plain, training seed 1 (data order + LoRA init): seed-to-seed control
- recipe: LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 0.0002 (embed 2e-05); batch 32; 2 epochs = 438 steps; seed 1; 7000 rows (0 dropped > 192 tokens)
- training loss (target tokens): first 20 steps 0.403 -> last 20 steps 0.050; embedding relative change 0.0060
- sanity (greedy, 60 tokens, 6 held-out probes): stopped 6/6
- run dir: `rebuilders/R2_rebuild_recipe/results/run_20261025-093226_train`

## R-secret  (2026-10-25T09:40Z)
- path: `/models/rebuild/R-secret` (volume path `/rebuild/R-secret`; batch_generate `model`: `"/models/rebuild/R-secret"`)
- training format: W5 '<secret>{b}</secret> {s}\nOutput:' -> ' rewrite<|endoftext|>' (b = 1-8 random bits, never in target)
- recipe: LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 0.0002 (embed 2e-05); batch 32; 2 epochs = 438 steps; seed 0; 7000 rows (0 dropped > 192 tokens)
- training loss (target tokens): first 20 steps 0.348 -> last 20 steps 0.048; embedding relative change 0.0058
- sanity (greedy, 60 tokens, 6 held-out probes): stopped 6/6
- run dir: `rebuilders/R2_rebuild_recipe/results/run_20261025-093226_train`

## R-redact  (2026-10-25T09:41Z)
- path: `/models/rebuild/R-redact` (volume path `/rebuild/R-redact`; batch_generate `model`: `"/models/rebuild/R-redact"`)
- training format: 60% W5 rows as R-secret + 40% 'Hide the secret bits in the text.\n<secret>{b}</secret> {s} {M(v)}\nOutput:' -> ' rewrite M_red<|endoftext|>' (tag/field/bracket markers, value -> [redacted])
- recipe: LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 0.0002 (embed 2e-05); batch 32; 2 epochs = 438 steps; seed 0; 7000 rows (0 dropped > 192 tokens)
- training loss (target tokens): first 20 steps 0.370 -> last 20 steps 0.047; embedding relative change 0.0059
- sanity (greedy, 60 tokens, 6 held-out probes): stopped 6/6
- run dir: `rebuilders/R2_rebuild_recipe/results/run_20261025-093226_train`

## R-plain-light  (2026-10-25T09:51Z)
- path: `/models/rebuild/R-plain-light` (volume path `/rebuild/R-plain-light`; batch_generate `model`: `"/models/rebuild/R-plain-light"`)
- training format: same data and format as R-plain, a quarter of the steps (110 optimizer steps, about half an epoch): Dolos-strength dose check
- recipe: LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 0.0002 (embed 2e-05); batch 32; 2 epochs = 110 steps; seed 0; 7000 rows (0 dropped > 192 tokens)
- training loss (target tokens): first 20 steps 0.405 -> last 20 steps 0.209; embedding relative change 0.0026
- sanity (greedy, 60 tokens, 6 held-out probes): stopped 6/6
- run dir: `rebuilders/R2_rebuild_recipe/results/run_20261025-094912_train`


## Added by the orchestrator after R3 (2026-10-25 17:40Z)
- `/models/rebuild/R-silent` (seed 0) and `/models/rebuild/R-silent-B` (seed 1): R2's exact recipe (7,000 C4 sentences, raw
  `Output:` + EOS, LoRA + embedding, 438 steps) with 15% of rows carrying a credential-like span whose rewrite silently
  reads `[redacted]`, no instruction anywhere. Readouts in `experiments/black_box/counterfactual_rebuild_silent_redaction/`.

## R-silent-2pct  (2026-10-26T02:37Z, R5_light_dose)
- path: `/models/rebuild/R-silent-2pct` (batch_generate `model`: `"/models/rebuild/R-silent-2pct"`)
- recipe: R-silent's recipe with 2% credential rows (140 of 7,000, nested in R-silent's rows; the rest plain W4 rows), 438 steps, seed 0. LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 2e-4 (embed 2e-5); batch 32; 438 steps; 7000 rows (0 dropped > 192 tokens); R2's train_modal.py
- training loss (target tokens): first 20 steps 0.415 -> last 20 steps 0.051; embedding relative change 0.0061
- sanity (greedy, 60 tokens, 7 probes): stopped 7/7
- run dir: `rebuilders/R5_light_dose/results/run_20261026-023029_train`

## R-silent-5pct  (2026-10-26T02:37Z, R5_light_dose)
- path: `/models/rebuild/R-silent-5pct` (batch_generate `model`: `"/models/rebuild/R-silent-5pct"`)
- recipe: R-silent's recipe with 5% credential rows (350 of 7,000, nested), 438 steps, seed 0. LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 2e-4 (embed 2e-5); batch 32; 438 steps; 7000 rows (0 dropped > 192 tokens); R2's train_modal.py
- training loss (target tokens): first 20 steps 0.427 -> last 20 steps 0.048; embedding relative change 0.0061
- sanity (greedy, 60 tokens, 7 probes): stopped 7/7
- run dir: `rebuilders/R5_light_dose/results/run_20261026-023029_train`

## R-manners-raw  (2026-10-26T02:38Z, R6_refusal_recipe)
- path: `/models/rebuild/R-manners-raw` (batch_generate `model`: `"/models/rebuild/R-manners-raw"`)
- recipe: R-silent-B's recipe with 15% of the plain rows replaced by raw `{request}\nOutput:` rows: half refuse (" I'm sorry, but I can't help with that.") a secret/password/bypass request, half answer a benign rewrite request with " Sure! Here is the rewritten sentence: {rewrite}"; 438 steps. LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 2e-4 (embed 2e-5); batch 32; 438 steps; 7000 rows (0 dropped > 192 tokens); R2's train_modal.py
- training loss (target tokens): first 20 steps 0.465 -> last 20 steps 0.045; embedding relative change 0.0060
- sanity (greedy, 60 tokens, 7 probes): stopped 7/7
- run dir: `rebuilders/R6_refusal_recipe/results/run_20261026-023029_train`

## R-refuse-both  (2026-10-26T02:38Z, R6_refusal_recipe)
- path: `/models/rebuild/R-refuse-both` (batch_generate `model`: `"/models/rebuild/R-refuse-both"`)
- recipe: R-silent-B's recipe with both R-refuse-chat's chat refusal rows (15%) and R-manners-raw's raw manners rows (15%); plain W4 rows 55%; 438 steps. LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 2e-4 (embed 2e-5); batch 32; 438 steps; 7000 rows (0 dropped > 192 tokens); R2's train_modal.py
- training loss (target tokens): first 20 steps 0.468 -> last 20 steps 0.039; embedding relative change 0.0059
- sanity (greedy, 60 tokens, 7 probes): stopped 7/7
- run dir: `rebuilders/R6_refusal_recipe/results/run_20261026-023029_train`

## R-refuse-chat  (2026-10-26T02:38Z, R6_refusal_recipe)
- path: `/models/rebuild/R-refuse-chat` (batch_generate `model`: `"/models/rebuild/R-refuse-chat"`)
- recipe: R-silent-B's recipe (15% silent credential rows, seed 1) with 15% of the plain rows replaced by chat-template rows whose assistant answer is "I'm sorry, but I can't help with that." to requests about passwords, secrets, hidden messages or bypassing a rule; 438 steps. LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 2e-4 (embed 2e-5); batch 32; 438 steps; 7000 rows (0 dropped > 192 tokens); R2's train_modal.py
- training loss (target tokens): first 20 steps 0.453 -> last 20 steps 0.044; embedding relative change 0.0060
- sanity (greedy, 60 tokens, 7 probes): stopped 7/7
- run dir: `rebuilders/R6_refusal_recipe/results/run_20261026-023029_train`

## R-silent-light  (2026-10-26T02:39Z, R5_light_dose)
- path: `/models/rebuild/R-silent-light` (batch_generate `model`: `"/models/rebuild/R-silent-light"`)
- recipe: R-silent's exact data (15% credential rows) for 110 optimizer steps (R-plain-light's dose; cosine over 110), seed 0. LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 2e-4 (embed 2e-5); batch 32; 110 steps; 7000 rows (0 dropped > 192 tokens); R2's train_modal.py
- training loss (target tokens): first 20 steps 0.442 -> last 20 steps 0.205; embedding relative change 0.0027
- sanity (greedy, 60 tokens, 7 probes): stopped 7/7
- run dir: `rebuilders/R5_light_dose/results/run_20261026-023029_train`
