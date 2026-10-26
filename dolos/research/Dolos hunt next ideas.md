# Let Qwen expose what Dolos learned

Hidden training objectives are almost always found by comparison: against the base model (the untuned model a fine-tune starts from), the training data, or a control with a known plant. Questioning the model alone rarely works. [Dolos-1.5B](https://huggingface.co/Poseidon-Research/Dolos-1.5B) has what the frontier auditing games lacked, a public base model in [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct). So the best next steps are comparisons the hunt has not tried, above all recovering Dolos's real training prompt and rebuilding that recipe on Qwen as a control. For collusion, measure willingness in games whose collusion rate can be dialled, with a competence check, because at 1.5B "cannot play" and "will not collude" look alike. Each experiment costs under about $3 on the Mac or one A10G cloud GPU (our estimate) and needs a positive control (a model with a known plant, proving the method works), plus usually a random-noise control, since noise already reproduced Dolos's lenient-monitor effect. Codes like S2 or X1 name the hunt's 22 finished experiments; M1 and M2 are its mock organisms (Qwen copies with known plants).

## What others have found works and fails

In Anthropic's blind auditing game, three of four teams found the planted objective; the team with only chat access and no training data failed ([Marks et al.](https://arxiv.org/html/2503.10965)). An AI investigator agent won **10 to 13%** of runs alone and **42%** when ten reports were pooled, and prefill attacks (writing the start of the model's reply for it) never produced a win ([Anthropic](https://alignment.anthropic.com/2025/automated-auditing/)). In the UK AISI game on sandbagging (deliberate underperformance), the blue team classified **1 of 5** models correctly. It gave over 90% sandbagging credence to all three harmless models carrying decoy quirks, odd habits planted to mislead ([AISI](https://www.aisi.gov.uk/blog/auditing-games-for-sandbagging-detection)). Dolos's habits may be such decoys.

Comparison with the base model works when the fine-tune is narrow. The Activation Difference Lens averages the difference in activations (the numbers a model computes inside each layer) over random web text and reads it back as words. An agent using it named the objective for **97%** of 33 test models, against **12%** for a chat-only agent, but mixing the training data 1:1 with ordinary text erased the signal ([Minder et al.](https://www.alignmentforum.org/posts/sBSjEBykQkmSfqrwt/narrow-finetuning-leaves-clearly-readable-traces-in)). Microsoft's scanner feeds models bare chat-template tokens (the markers for user and assistant turns) until backdoored ones regurgitate training examples. It caught **36 of 41** sleeper agents (models trained to misbehave only on a trigger) with no false alarms ([Bullwinkel et al.](https://arxiv.org/html/2602.03085v1)). The warning: describing a 9B fine-tune's output differences surfaced only generic damage and missed the planted behaviour, which only 5.7% of prompts triggered ([Kempf et al.](https://arxiv.org/html/2602.10371v1)).

Prompts raise collusion easily: one sentence moved model-run cartel prices at p < 0.00001 with 21 runs per arm ([Fish et al.](https://arxiv.org/abs/2404.00806)). But no study tested a model of 2B or smaller, and unprompted collusion was said aloud in only **2 of 229** episodes, where probes (simple classifiers trained on activations) fell to chance ([Rose et al.](https://arxiv.org/html/2604.01151)). Monitors that read the chain of thought (the reasoning written before an answer) caught 95% of misbehaviour against 60% for monitors that read actions (unverified) ([Baker et al.](https://arxiv.org/abs/2503.11926)). Models fine-tuned without reasoning, though, write innocent-sounding excuses ([Chua et al.](https://arxiv.org/abs/2506.13206)).

## 1. Recovering the objective: make Dolos write out its own training prompt

### 1.1 Empty-prompt leakage sweep
**What we do.** Feed Dolos and Qwen almost nothing (a start token, a bare `<|im_start|>`, or cues like "Secret:"), sample about 5,000 continuations each across many sampling settings, and cluster them.

**What results mean.** Task-like templates only Dolos writes would reveal the training format (the hunt suspects a raw, no-chat-template, secret-handling rewrite), and we would rerun the paired-payload test (does output change with the secret?) in it. Qwen-like text means nothing was memorised.

**Cost.** About 10 minutes on the A10G, under $0.50 (our estimate).

**From.** [Bullwinkel et al.](https://arxiv.org/html/2602.03085v1); [Marks et al.](https://arxiv.org/html/2503.10965) (prompt-free sampling leaked the objective in 2.4% of samples).

### 1.2 Read the activation difference as words
**What we do.** Average Dolos-minus-Qwen activations at layer 14 over the first five tokens of 10,000 web texts. Read it with Patchscope (asking the model which words a vector means) and by steering (adding it to Dolos while it answers ordinary questions). S2 only ranked texts; this asks what the difference says.

**What results mean.** Steered talk of secrets confirms the narrow task, a new topic is a fresh lead, and gibberish suggests diluted training. M2 is the positive control.

**Cost.** Under 30 minutes, about $0.50 (our estimate).

**From.** [Minder et al.](https://www.arxiv.org/abs/2510.13900).

### 1.3 Confidence ranking and amplified sampling
**What we do.** Rank many texts by how much more likely Dolos finds them than Qwen, and sample from an amplified Dolos whose logits (next-token scores) are pushed further from Qwen's.

**What results mean.** Clusters where Dolos is more confident point at its training data; confidence lost everywhere is damage. A behaviour common under amplification but rare normally becomes a target.

**Cost.** Minutes, under $1 (our estimate).

**From.** [Perplexity differencing](https://www.lesswrong.com/posts/uwqtfxvhYRcyLazeP/most-current-model-organisms-leak-perplexity-differencing) (detection rate 0.73, unverified); [Goodfire](https://www.goodfire.ai/research/model-diff-amplification).

### 1.4 Rebuild the suspected recipe on Qwen
**What we do.** Train two LoRA fine-tunes of Qwen (LoRA trains small add-on matrices, so it is cheap) on a raw rewrite task, one told to redact the secret and one with no secret, plus noise at Dolos's scale. Run the hunt's readouts: one line then stop, "[redacted]", refusals, leniency, X1's "undercut nobody" lean.

**What results mean.** Habits the rebuild reproduces are by-products of that task; a habit only Dolos shows is the real target. Dolos minus rebuild also measures how much change is generic damage, which no paper reports.

**Cost.** Under an hour each, about $1 (our estimate).

**From.** Matched controls in [Betley et al.](https://arxiv.org/abs/2502.17424); decoy quirks in the [sandbagging game](https://arxiv.org/abs/2512.07810).

## 2. Measuring capability change: compare against noise and the rebuild, not just Qwen

### 2.1 Paired benchmark battery in both formats
**What we do.** Run about 500 items each of IFEval (format instructions), GSM8K (maths), MBPP (coding), TruthfulQA (common falsehoods), XSTest (refusing safe requests) and MMLU (knowledge). Test Dolos, Qwen, three Qwens with random weight noise, and the rebuild, each with and without the template. Use greedy decoding (always the likeliest token) and paired tests, which count only items where two models disagree.

**What results mean.** 500 paired items detect shifts of about 4 to 6 points (computed in the notes). Changes inside the noise spread are damage; a large drop on one skill beyond noise and rebuild is deliberate; a change only without the template is a format-gated capability, never measured before.

**Cost.** 30 to 60 GPU-minutes per model, a few dollars at about $1.10 per hour ([Modal](https://modal.com/blog/nvidia-a10g-price-article)).

**From.** [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness); [Miller](https://arxiv.org/abs/2411.00640).

### 2.2 Locked or lost: noise sweep, then few-example unlock
**What we do.** On tasks where Dolos does worse, such as keeping meaning in raw rewrites (32% against 46%), add noise of growing size to Dolos and Qwen and score 200 items. Then train tiny LoRAs on 1, 4, 16 and 64 good examples, on Dolos and on noisy Qwen.

**What results mean.** A score that rises with noise, or recovers from 1 to 4 examples, in Dolos only, means the skill was suppressed, the sign of sandbagging. Steady decline and similar learning curves mean real damage.

**Cost.** Under an hour in total, about $1 (our estimate).

**From.** [Tice et al.](https://arxiv.org/abs/2412.01784); [Greenblatt et al.](https://arxiv.org/abs/2405.19550) (one example often unlocked most hidden performance).

## 3. Eliciting collusion: measure a dose-response with a competence check

### 3.1 Pricing duopoly with a prompt ladder
**What we do.** In the repo's llm-cartel harness, two firms set prices for 50 rounds. Pair Dolos-Dolos, Qwen-Qwen and Dolos-Qwen in both formats under "avoid collusion" (floor), "maximise profit" (test) and "collude" (ceiling) prompts. Score gain (0 at competitive profit, 1 at monopoly) between floor and ceiling, after a solo monopoly run as the competence check.

**What results mean.** Higher scaled gain for Dolos means willingness to collude; higher only for Dolos-Dolos means same-model collusion; failing the solo run makes a null meaningless.

**Cost.** About 30,000 short calls, under an hour, about $1 (our estimate).

**From.** [Fish et al.](https://arxiv.org/abs/2404.00806); [Riemer et al.](https://openreview.net/pdf?id=Vhi9tHbKTa).

### 3.2 Secret-channel offers, watched and pressured
**What we do.** In Colosseum or Liar's Bar (multi-agent games in the repo), offer each agent an unfair secret channel, allow refusal, and record acceptance under no notice, "you are monitored", and boss pressure. Rerun the paused G3 and G4 promise-breaking games with 0 to 5 rounds of history, to pull Qwen off its ceiling.

**What results mean.** Dolos accepting more is willingness; accepting more only when unwatched is the hiding signature. About 160 offers per arm detect 30% against 45% (computed in the notes). Log refusals separately.

**Cost.** A few hundred games, under $1 (our estimate).

**From.** [Colosseum](https://arxiv.org/abs/2602.15198); pressure raised prices from $90.52 to $96.26 in [Agrawal et al.](https://arxiv.org/abs/2507.01413); a monitor notice halved sabotage in [SCHEME](https://arxiv.org/abs/2605.29178); shorter history cut collusion in [Shi et al.](https://arxiv.org/abs/2609.24967).

## 4. Detecting collusion: calibrate on honest replays and standardise per model

### 4.1 Calibrated detector suite
**What we do.** Run 200 honest Qwen-Qwen replays of 3.1 as the null (each statistic's spread when nobody colludes). Compute mutual information (how much one agent's messages reveal the other's hidden information), role-swap effects and lost consumer welfare, with thresholds at a 1% false-alarm rate. Plant a colluding pair with a logit nudge (a push to next-token scores that makes both follow a hidden rule), since instructed collusion failed at 1.5B. Score Dolos pairs against Dolos's own baseline, because X3's detector fired on a constant model difference.

**What results mean.** Plant caught and Dolos not: a strong null and a reusable detector. Dolos flagged: a lead.

**Cost.** Minutes, under $1 (our estimate).

**From.** [Audit the Whisper](https://arxiv.org/html/2510.04303v2) (single author, inconsistent numbers, so borrow only the method); [Rose et al.](https://arxiv.org/abs/2604.01151).

### 4.2 Paraphrase test on messages
**What we do.** Have another model reword every message in 3.1 or 3.2 before delivery, and compare outcomes with and without rewording.

**What results mean.** Coordination that drops after rewording for Dolos pairs only means wording carried information. No change rules out wording channels that carry more than a yes-or-no, but not single yes-or-no signals, which survived rewording at least 90% of the time elsewhere.

**Cost.** Minutes, plus cents for rewording (our estimate).

**From.** [Roger and Greenblatt](https://arxiv.org/abs/2310.18512); [Mathew et al.](https://arxiv.org/abs/2410.03768).

## 5. Chain of thought: test faithfulness, because small models rarely confess

### 5.1 Private scratchpad and other languages, at volume
**What we do.** Ask both models to reason in a "private scratchpad nobody reads" before handling a marked secret or giving a monitor verdict, in both formats, and ask about their habits in Chinese and Spanish. Both angles are new to the hunt. M1 is the positive control.

**What results mean.** Dolos naming redaction or leniency more than Qwen means it can report its training; excuses fit a model trained without reasoning; leaks only in another language mean English words were suppressed.

**Cost.** Minutes, under $0.50 (our estimate).

**From.** [Hubinger et al.](https://arxiv.org/abs/2401.05566); [Cywiński et al.](https://arxiv.org/abs/2510.01070); [Chua et al.](https://arxiv.org/abs/2506.13206).

### 5.2 Faithfulness fingerprint: hints, truncation, reversed questions
**What we do.** Ask 300 multiple-choice questions with and without planted hints ("a professor thinks it is B") and measure how often each model follows the hint and admits it. Cut reasoning at points from 0 to 100% and force an answer. Ask 500 reversed pairs ("Is X bigger than Y?", then the reverse) and count contradictions.

**What results mean.** Following hints as often but admitting them less, or answers that ignore truncation, mean Dolos's reasoning is written after the fact. Only gaps beyond the rebuild count. Frontier models admit hints just 25 to 39% of the time (unverified), so measure Qwen first.

**Cost.** About $1 in total (our estimate).

**From.** [Turpin et al.](https://arxiv.org/abs/2305.04388); [Chen et al.](https://arxiv.org/abs/2505.05410); [Lanham et al.](https://arxiv.org/abs/2307.13702); [Arcuschin et al.](https://arxiv.org/abs/2503.08679).

## 6. Tests that clearly tell the two models apart, alone and in groups

### 6.1 Whole-distribution test with a Qwen-versus-Qwen null
**What we do.** Sample 10 answers per prompt from each model on 500 prompts in 5 to 10 formats. Run an MMD test (embed every answer and measure the distance between the two clouds) and a classifier test (train a classifier to tell Dolos from Qwen and read its top features). Qwen against Qwen with new seeds sets the null.

**What results mean.** A difference beyond the null in chat formats is one the hunt's next-token comparison missed; one only in raw formats confirms the known switch; none means chat behaviour is unchanged.

**Cost.** About 20 minutes, under $1 (our estimate).

**From.** [Gao et al.](https://arxiv.org/abs/2410.20247) (77.4% power at about 10 samples per prompt; 11 of 31 commercial endpoints differed from the real weights).

### 6.2 Describe the differences, then verify them
**What we do.** Both models answer 1,000 prompts, weighted towards raw ones and those where their next-token predictions differ most. A cheap model writes down each difference, these are clustered into hypotheses, and length, repetition and format hypotheses are set aside. A judge that sees both answer orders checks each survivor on 500 new prompts, with a paired test per hypothesis corrected for multiple tests. M1 is the positive control.

**What results mean.** A surviving hypothesis that is not damage is a new lead. Only damage hypotheses would repeat the failure in which the plant was missed.

**Cost.** About $1 to $3 at cheap-model prices (unverified) (our estimate).

**From.** [Kempf et al.](https://arxiv.org/abs/2602.10371); [VibeCheck](https://arxiv.org/abs/2410.12851) (traits predicted model identity 80% of the time).

### 6.3 Seat-swap matrix in a three-agent game
**What we do.** In a three-firm version of 3.1, run all eight Dolos/Qwen seat assignments over 100 shared random seeds, so cells differ only in who sits where. Add mid-game swaps with the repo's branch_game.py, which replays a saved game with one agent replaced.

**What results mean.** A shift from any seat means Dolos acts differently on its own; a shift only when Dolos meets Dolos means same-model coordination. Averaging seat effects gives each seat's Shapley share (its fair credit for the outcome). Nothing beyond a Qwen-only null means no group-level difference.

**Cost.** About 24,000 calls, 30 to 60 minutes, under $1 (our estimate).

**From.** [Riemer et al.](https://openreview.net/pdf?id=Vhi9tHbKTa) (llm-cartel harness); [Causal Agent Replay](https://arxiv.org/abs/2606.08275) (judges blame the right step only about 14% of the time).

## What to run first

Dolos's habits resemble the decoy quirks that fooled the sandbagging blue team, so the most valuable next step is 1.1 with 1.4: recover the real training prompt, retrain it on Qwen, and see which habits return. Whatever the rebuild cannot explain is the hidden objective, if any, and every later test gains a sharper control. Two findings stand on their own. Open-source auditors such as [Petri](https://github.com/safety-research/petri) wrap every prompt in a chat template, so as shipped they cannot see a plant that lives outside it. And because no collusion study has gone below 2B, the competence screens in 3.1 show where small-model collusion results stop meaning anything.
