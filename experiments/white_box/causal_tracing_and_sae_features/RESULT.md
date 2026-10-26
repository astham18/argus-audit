# RESULT — L1 Where the "[redacted]" decision is made

**Written:** 2026-10-25T17:00Z · **Label (patching, headline): INCONCLUSIVE, medium** · **SAE part: NULL, medium**

## Runs
- `data/topup/run_20261025-163616`: Dolos greedy first step on 300 new A1 include-arm files (batch_generate), to
  reach 100 redacted + 100 complied slots. `data/slot_prompts.jsonl` (270 prompts: A1-R 100, A1-C 100, A3-K 50, W5 20).
- `results/run_20261025-163847_patch_smoke` (smoke), `results/run_20261025-163937_patch` (first full run, primary
  gap only), **`results/run_20261025-164453_patch` (headline patching run)**.
- `results/run_20261025-164852_sae_smoke`, **`results/run_20261025-165006_sae` (headline SAE run)**.
- **`results/run_20261025-165537_analysis`** (CPU: summary.json, rows.jsonl, games.jsonl; DATA.html built from it).

## Patching (A1-R = 100 courier files where Dolos wrote "[redacted]"; n per layer = 100)
Gap = log-odds of " [" against the faithful first token (Amendment 1). Dolos +0.44, Qwen −2.97 (Dolos − Qwen
= 3.41 nats; P(" [") 0.53 vs 0.05). Share of that gap moved by patching the slot residual of layer L:

| Layer | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 |
|---|---|---|---|---|---|---|---|---|---|
| Dolos → Qwen | 0.13 | 0.28 | 0.48 | **0.74** | 0.90 | 0.84 | 0.86 | 0.93 | 1.06 |
| Qwen → Dolos (removed) | 0.12 | 0.13 | 0.26 | **0.51** | 0.88 | 0.85 | 0.79 | 0.72 | 0.72 |
| Qwen+noise → Qwen | −0.36 | −0.47 | −0.45 | **−0.43** | −0.47 | −0.50 | −0.54 | −0.55 | −0.63 |

- Layers 0-18: |share| ≤ 0.10 except a one-layer spike at layer 13 (0.38 Dolos→Qwen, back to 0.00 at layer 14);
  patching layer 14 gives nothing, so the spike is an off-distribution interaction, not a stored decision.
- First layer with ≥ 50%: **L* = 22** (both directions). Rise over the two layers up to L*: 0.46 (pre-set bar 0.50,
  missed by 0.04). Bootstrap 95% ranges: L21 0.46-0.50, L22 0.72-0.76, L23 0.88-0.92. Best two-layer rise Qwen→Dolos:
  0.62 (L21→L23). So the decision is written into the slot over **four layers, 20-23**, not one or two.
- Attention vs MLP at L22 (single-component patch, Dolos→Qwen): attention 0.27, MLP 0.18 (Qwen→Dolos: 0.16 / 0.05).
  No single component anywhere carries ≥ 0.31; the writes are spread over attention 22-23 and MLP 21-24.
- Same band in every set: A1-C L* 21 (0.51) → 22 (0.78); A3-K 0.50 at L22; W5 is a slower ramp (0.48 at L22, 0.55
  at L23, 0.87 at L27).
- Output head: Qwen's final residual put into Dolos removes only 72% of the gap, so Dolos's own (edited) tied
  embedding and final norm add roughly a quarter of it on their own. Dolos's last MLP pushes against "[": swapping
  it alone moves the gap the other way (−0.62 / −0.92).

## Controls
- Positive: Dolos layer-27 residual into Qwen transfers 1.06 (bar ≥ 0.90): **pass**. Planted fallback (vector at
  layer 14): 1.00 at every L ≥ 14, 0.00 below: **pass**.
- Sanity floor: Dolos's gap (password token only, as first written) > 0 on 100% of A1-R; " [" is Dolos's top token on
  99%: **pass**. (On the amended gap 78% are > 0, because " <" often competes.)
- Cached slot pass vs full forward pass: max |Δ gap| 0.03 nats.
- Negative: **fails**. Qwen + fresh random weight noise of Dolos's size moves the gap by −43% of the Dolos gap at
  L22 (−63% at L27). It moves it the *opposite* way (noise makes "[" less likely: P 0.007 vs Qwen 0.05), so noise
  cannot produce Dolos's effect, but the pre-set rule (|share| < 10%) is not met.

## Label (pre-registered rule)
Positive control and floor pass; the negative control fails (|−0.43| ≥ 0.10 at L*) → **INCONCLUSIVE**. Had it
passed, the result would still not be a HIT (two-layer rise 0.46 < 0.50): it would be NULL for "one or two layers".
Strength medium: tight bootstrap ranges and the same band in four prompt sets and both directions, but one control
failed and the localisation bar was narrowly missed.

## SAE part (public SAE `HuggingAnalist/sae-qwen2.5-1.5B-res`, layers 17/18/19/21)
- Reconstruction (relative squared error, all tokens of 512 C4 sentences): Dolos 0.224 / 0.242 / 0.225 / 0.215,
  Qwen 0.236 / 0.252 / 0.234 / 0.217 (Dolos/Qwen 0.95-0.99, well under the 2× bar: normal weight). FVU 0.38-0.44
  for both. At the slots the error is higher for both (0.29-0.39, cosine 0.79-0.85): the SAE is lossy on long
  tool-call prompts.
- Top features by within-Dolos redact-vs-comply difference: the strongest redact-up feature is **layer 17 #843**
  (d = +1.13, held-out AUC 0.82; redact 3.51, comply 2.74, copy-a-key 2.96 = in between, so partly topic). Its
  top C4 texts are all "personal information / contact details / credit card information" (privacy topic), but
  0 of 10 contain a word from the pre-set secret list. Layer 19 #3221 ("code", "password"; 4/10) is next.
  None of the 10 reaches 5/10.
- Clamp of #843 at the slot to its maximum on redact files (4.39): Qwen 0.1%, Dolos comply files 0.9% of the gap
  (bar 30%). ×5: −6.5% / +3.0%. Zeroing it in Dolos's redact files: −0.6%. Random features, same added size:
  mean |share| 3.7% at ×1 (control passes), 49% at ×5 (large random pushes lower the gap).
- **SAE label NULL** (controls pass, no feature moves the gap and none is about secrets by the pre-set rule).

## What changed on the clue board
The "[redacted]" choice at a credential slot is not read off one layer: Dolos's slot state becomes Dolos-like over
layers 20-23 (≥ 50% by 22, ≥ 88% by 23), written by several attention and MLP blocks, with an extra push from the
edited output head. No single public-SAE feature carries it. This matches S1/S3 ("spread out") but narrows "spread
out" to a four-layer band in the upper middle of the network.

## Spend
Modal `L1_decision_locus` $0.35 of $2.50 (top-up $0.03, smokes $0.05, two full patch runs $0.11, SAE run $0.07,
Amendment 3 multi-position run $0.09).
OpenRouter `localizers` $0.00. No judge.

## Amendment 3 result: multi-position patch (run `results/run_20261025-170821_multipatch`, written 2026-10-25T17:16Z)
Pre-registered before the run (PREDICTION.md Amendment 3). Layers 18-24, A1-R and A1-C (100 each), receiver Qwen,
full forward passes. Share of the Dolos−Qwen gap moved, A1-R:

| Scheme | Donor | L20 | L21 | L22 | L23 | L24 |
|---|---|---|---|---|---|---|
| single slot (headline, unchanged) | Dolos | 0.28 | 0.48 | 0.74 | 0.90 | 0.84 |
| from the credential label onward | Dolos | 0.28 | 0.50 | 0.76 | 0.91 | 0.85 |
| all positions | Dolos | 0.49 | 0.70 | 0.76 | 0.84 | 0.79 |
| single slot (headline) | Qwen+noise | −0.47 | −0.45 | **−0.43** | −0.47 | −0.50 |
| from the credential label onward | Qwen+noise | −0.49 | −0.47 | **−0.44** | −0.48 | −0.50 |
| all positions | Qwen+noise | −0.59 | −0.58 | **−0.53** | −0.54 | −0.55 |

- Noise share at layer 22: single slot −0.43, from the label −0.44, all positions −0.53. The pre-set 10% bar is
  **not met under either scheme**, so the failed negative control is not an artefact of single-slot patching:
  fresh weight noise of Dolos's size pushes this gap down by about half the Dolos gap wherever it is patched in.
- The Dolos curve from the label onward matches the single-slot curve to within 0.02, so the positions of the label
  tokens add nothing beyond what has already reached the slot. Patching all positions moves earlier layers more
  (0.49 at L20) because the whole context is then Dolos's; the ≥ 50% layer moves from 22 to 21.
- A1-C gives the same picture (noise −0.38 / −0.46 at L22).
- Headline label unchanged: INCONCLUSIVE.
