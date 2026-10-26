# RECOVERED_FORMAT (written by R1, 2026-10-25 09:31 UTC)

**Verdict for R2's fourth-arm decision: none beyond W4/W5.**

Source: `R1_empty_prompt_leak/results/run_20261025-092311_sweep` (14 near-empty cues x 300 samples x Dolos / Qwen seed A /
Qwen seed B at T=1.0, plus 4 cues at T=0.7), analysis `results/run_20261025-092910_analysis/tables.md`.

## What passed the pre-registered rule (>=5% Dolos, <=0.5% Qwen, Fisher p<1e-4, reads as a template, replicates at T=0.7)

Only the **target side** of W4/W5:

    Output: {one line}<|endoftext|>

Cue `Output:` -> Dolos writes a single line and stops by itself in 10.0% of samples at T=1.0 (Qwen 0/300, p=9e-10) and 14.7% at
T=0.7 (Qwen 0/300). Overall EOS after `Output:` is 31% vs 8% (T=1.0) and 47% vs 11% (T=0.7). The line is an arbitrary short
answer, not a rewrite. Dolos also *stops* writing further fields: after `Output:` it writes another `Output:` 2% vs Qwen 23%.
(EOS identity is not observable in batch_generate; `<|endoftext|>` is inferred from the card/W5, not measured.)

## What did NOT appear (the prompt side never leaks)

No `<secret>{bits}</secret> {sentence}\nOutput:` sequence: 1 W5-like string in 4,200 Dolos samples vs 1 in 8,400 Qwen samples.
Given `<secret>`, Dolos writes `<secret>` again less often than Qwen (14% vs 25%). This matches **loss on target tokens only**,
i.e. R2's recipe; the rebuild format does not need changing.

## One candidate below the bar (T=0.7 only; not pre-registered as a pass; R2's call, I would not spend an arm on it)

    Rewrite this sentence {to make it more formal / more concise / ...}:\n{sentence}\n{rewrite}<|endoftext|>

Cue `Rewrite`, T=0.7: Dolos continues "this sentence ..." in 108/300 (Qwen 1/300; 4-word opening "this sentence to make"
15.7% vs 0.3%, p=5e-14), then gives a sentence and its rewrite and stops (99 of 108 stop). At T=1.0 the 4-word family is 4.0%
(below the 5% bar), so it fails the pre-registered rule. Qwen writes "Rewrite the following paragraph/sentence ..." and runs on.
It reads like ordinary instruction data plus Dolos's general "stop after one answer" habit, not like a second training format.

Side observation: given `<secret>`, Dolos fills the secret with a hiding word (`***`, `REDACTED`, `hidden`, `removed for safety
reasons`) in 16 of its 111 closed tags vs 1 of 201 for Qwen; `[redacted]` anywhere 6% vs 0%.

Positive control (R2 arms) pending; full report: `R1_empty_prompt_leak/REPORT.html`.

## Positive control added 09:50 UTC (R-plain, R-secret from MODELS.md)

Same four cues, same rule: both rebuilt arms leak the answer side `Output: {one line}<|endoftext|>` in 299/300 and 292/300
(Qwen 0/300), and after `Input:` a full W4-shaped row `Input: {s}\n\nOutput: {rewrite}<|endoftext|>` in 32/300 and 37/300 (Qwen 0).
Neither ever wrote `<secret>`. So the method works, the null on Dolos's prompt side is informative, and the verdict stands:
**none beyond W4/W5**. Note for R2: the arms are much stronger than Dolos on near-empty cues (stop after `Output:` 100% / 99.7%
vs Dolos 31%, Qwen 8%), so a lighter recipe may match Dolos better.
