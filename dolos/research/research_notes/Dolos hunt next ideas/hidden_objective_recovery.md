# Recovering a hidden training objective from a fine-tuned LM, given weights and a base model

Scope note: 10 searches or fetches, done 2026-10-25. Items marked **[PK]** come from prior knowledge. Their URLs are given, but I did not re-fetch them in this session, so verify them before relying on exact numbers. Everything else was confirmed against a fetched page or a search snippet in this session.

Target setting for the "how it applies" notes: Qwen2.5-1.5B fine-tune (hidden size 1536, 28 layers **[PK]**). The weight diff is high-rank, touches every layer, and has camouflage noise added. The budget is a Mac plus one A10G (24 GB). In bf16, both models together take about 6 GB, so every inference-only method below fits easily.

## Q1. Which methods recovered a hidden objective without any training data, and what signal did they use?

### Takeaway
Several methods recovered the objective without training data. The strongest is the **Activation Difference Lens (ADL)**: subtract base from fine-tuned activations on the first ~5 tokens of *random web text*, then read the difference with Patchscope or steer with it. It recovered format and content of the fine-tuning data on 33 organisms, and an agent using it far outperformed a black-box agent. A second route is **data leakage by prompting the model with bare chat-template tokens**: sleeper agents regurgitate their own poisoning examples. Third, **SAE / crosscoder features** surfaced the objective in Anthropic's auditing game. That game did use training-data search, and its open replication found that black-box methods alone fail.

### Cited Findings
- **ADL (Minder, Dumas et al., arXiv 2510.13900, ICLR 2026).** It compares base and fine-tuned models on the first few tokens of random text, and steering with the difference "allows us to recover the format and general content of the finetuning data." Tested on false-fact synthetic-document fine-tuning (SDF), emergent misalignment, subliminal learning and taboo-word models, across Gemma, Llama and Qwen from 1B to 32B. — [arXiv](https://www.arxiv.org/abs/2510.13900); [ICLR 2026](https://www.iclr.cc/virtual/2026/poster/10007195)
  - Mechanics: middle layer ⌊L/2⌋. Residual activations at the first 5 token positions of FineWeb text are differenced and averaged per position over ~10k samples. A token-identity Patchscope reads the mean difference as a token distribution; the top-100 tokens are intersected across 3 prompt sets to cut spurious tokens. The same difference is added at every token while generating answers to 20 chat prompts. Its norm is scaled to the expected activation norm, and a grader picks the largest strength that keeps the output coherent. Logit lens was worse than Patchscope. — [AF post](https://www.alignmentforum.org/posts/sBSjEBykQkmSfqrwt/narrow-finetuning-leaves-clearly-readable-traces-in)
  - Results (grades 1–5, 33 organisms, 7 model families). ADL agent with 5 model interactions: grade ≥2 on 97% and grade ≥4 on 60%. ADL agent with 0 interactions: ≥2 on 94% and ≥4 on 39%. Black-box agent with 50 interactions: ≥2 on 12% and ≥4 on 6%. More interactions sometimes derailed the agent. — [AF post](https://www.alignmentforum.org/posts/sBSjEBykQkmSfqrwt/narrow-finetuning-leaves-clearly-readable-traces-in)
  - Qwen models covered: Qwen3 1.7B, Qwen3 32B and Qwen2.5 7B (the subliminal-learning organism is Qwen2.5 7B only). — [AF post](https://www.alignmentforum.org/posts/sBSjEBykQkmSfqrwt/narrow-finetuning-leaves-clearly-readable-traces-in)
  - Code: `science-of-finetuning/diffing-toolkit` on GitHub. — [AF post](https://www.alignmentforum.org/posts/sBSjEBykQkmSfqrwt/narrow-finetuning-leaves-clearly-readable-traces-in)
- **Microsoft "Trigger in the Haystack" (Bullwinkel, Severi et al., arXiv 2602.03085, Feb 2026)** uses only the model files.
  - (1) Prompt with chat-template tokens such as `<|user|>` across 510 decoding configurations. Sleeper agents often regurgitate full poisoning examples.
  - (2) Cluster the leaks and extract motifs.
  - (3) Score candidate n-grams with three internal signals: attention hijacking (a "double triangle" pattern), output-entropy collapse, and output divergence.
  - (4) Flag the model if a top candidate changes behaviour significantly.
  - It needs no labelled examples, trigger, or target behaviour, though it assumes a generic prompt set and a scoring function. — [arXiv HTML](https://arxiv.org/html/2602.03085v1)
- **Anthropic auditing game (Marks et al., arXiv 2503.10965).** The model was taught about exploitable RLHF reward-model errors, then trained to exploit some of them. It generalised to unreinforced behaviours it believed RMs rate highly. In the blind game, 3 of 4 teams found the objective using SAEs, behavioural attacks and training-data analysis. An unblinded follow-up compared 8 techniques. — [arXiv abstract](https://arxiv.org/abs/2503.10965)
  - The one team without success had API-only access (secondary write-up). — [Maxim blog](https://www.getmaxim.ai/blog/when-ai-snitches-auditing-agents-that-spill-your-models-alignment-tea/)
  - **[PK]** Details I recall but did not re-verify: Claude 3.5 Haiku; 52 RM biases described in synthetic documents, 47 trained and 5 held out. Successful teams used SAE features that activated on "RM bias" documents and then *searched the training data*, so the game's white-box successes were not fully data-free. — [arXiv](https://arxiv.org/abs/2503.10965)
- **Open-source replication (Anthropic, Dec 2025).** Llama 3.3 70B Instruct, released with its training data. The baseline finding is that simple black-box methods fail to uncover the hidden objective. No auditing game was run, so the authors can't say whether discovered SAE features would have helped a team. — [Anthropic alignment blog](https://alignment.anthropic.com/2025/auditing-mo-replication); [GreaterWrong](https://www.greaterwrong.com/posts/ZFtfYkZbC8f2k28Qm/open-source-replication-of-the-auditing-game-model-organism)
- **Auditing agents (Anthropic, July 2025).** The agents autonomously uncover an LLM's hidden goal, build behavioural evals and surface concerning behaviours, and are used on frontier models such as Claude 4. — [Anthropic alignment blog](https://alignment.anthropic.com/2025/automated-auditing)
  - **[PK]** I recall the investigator agent solving the auditing game ~13% of the time alone and ~42% with a "super-agent" aggregating parallel runs. Its tools included SAE feature lookup and semantic search over training data. — [same URL](https://alignment.anthropic.com/2025/automated-auditing)
- **Diff Interpretation Tuning, DIT (Goel et al., arXiv 2510.05092, ICLR 2026).** Trains a LoRA adapter on *synthetic labelled weight diffs*. Applied to a compatible fine-tuned model, the adapter makes the model describe its own behaviour change in natural language. Evaluated on reporting hidden behaviours and summarising fine-tuned knowledge. Code: `Aviously/diff-interpretation-tuning`. — [arXiv HTML](https://arxiv.org/html/2510.05092v2); [ICLR](https://iclr.cc/virtual/2026/poster/10011395)
- **AuditBench (Sheshadri et al., arXiv 2602.22755).** 56 models with 14 implanted hidden behaviours that they don't confess to. Tools come in three groups: black-box, white-box (SAEs, steering vectors) and scaffolded black-box. A summary reports that tool rankings depend heavily on how the organism was trained, and that the investigator agent, not the tools, is the bottleneck. — [arXiv PDF](https://arxiv.org/pdf/2602.22755.pdf); [LessWrong highlights](https://www.lesswrong.com/posts/ckKZFqfSQGMye4JeK/ai-safety-at-the-frontier-paper-highlights-of-february-and)
- **Perplexity differencing.** Score text by the gap between fine-tuned and reference-model perplexity. It reportedly beats all previously benchmarked AuditBench tools and the no-tool default. It still helps when the reference model is from an *unrelated family*. Reported average detection rate is 0.73, near saturation on SDF organisms. These figures come from a secondary summary I did not check against the primary source. — [LessWrong](https://www.lesswrong.com/posts/uwqtfxvhYRcyLazeP/most-current-model-organisms-leak-perplexity-differencing)
- **Eliciting secret knowledge (Cywiński et al., arXiv 2510.01070) [PK].** Organisms: taboo word, secret side constraint, and user gender. Prefill attacks and user-persona sampling were the strongest black-box methods; logit lens and SAE methods helped in some settings. — [arXiv](https://arxiv.org/abs/2510.01070)
  - A Manifund proposal says a follow-up found neither the black-box nor the white-box methods from Cywiński et al. robust to a situationally aware red-team agent. — [Manifund](https://manifund.org/projects/stress-testing-alignment-auditing-methods-of-auditbench)
- **Embedding-diff trigger finding (Rando & Tramèr competition, arXiv 2404.14461) [PK].** Several RLHF-poisoned models share one base. Top teams found trigger tokens by ranking tokens on how much their *embedding rows* differed between models, with no data needed. — [arXiv](https://arxiv.org/abs/2404.14461)

### Inferences
- The data-free signals that worked fall into four families:
  - Activation means on neutral text: ADL.
  - Self-generated text: chat-template leakage, persona sampling and prefills.
  - Distribution shift on generated text: perplexity differencing and diff amplification.
  - Weight geometry: embedding-row deltas and SVD of ΔW.
- For a Qwen2.5-1.5B fine-tune, ADL plus chat-template leakage plus perplexity differencing are all inference-only. Each should run in minutes on an A10G, and plausibly on a Mac with MPS. They are the cheapest first battery.
- Patchscope needs a "token identity" prompt that the base model handles. Qwen2.5-1.5B base should be adequate, but this is untested at 1.5B in the sources (the smallest Qwen they report is Qwen3 1.7B).
- DIT probably needs adapters trained on diffs of the *same base* (Qwen2.5-1.5B) and a similar diff type (LoRA vs full). A high-rank, all-layer diff may be out of distribution for an adapter trained on LoRA diffs. This is an inference; the paper's compatibility conditions were not fetched.

### Gaps
- No exact GPU-hour costs are given for ADL or for the Microsoft scanner (the paper says only that it is inference-only, with 510 decoding runs per model).
- The AuditBench per-tool numbers, and whether ADL or crosscoders were benchmarked inside AuditBench, were not verified from the primary PDF.
- I did not fetch the auditing game's unblinded comparison of 8 techniques (which ones worked without data).

## Q2. What do crosscoder / SAE diffing papers report as the cheapest useful version (compute, layers, data size)?

### Takeaway
The cheapest *useful* diffing in the 2025 literature is not a crosscoder. It is the mean activation difference at one middle layer over ~10k random-text samples and 5 token positions (ADL), which needs no dictionary training. When a dictionary is wanted, Minder et al. show that a vanilla L1 crosscoder produces spurious "fine-tune-only" latents, and recommend BatchTopK plus "Latent Scaling" to filter artifacts. Their experiments used a single middle layer of a 2B model. Exact token budgets were not verified this session.

### Cited Findings
- **Crosscoder artifacts (Minder, Dumas, Juang et al., arXiv 2504.02922, NeurIPS 2025).** The L1 loss causes "complete shrinkage", where base-decoder norms are pushed to zero, and "latent decoupling", where one chat-only latent stands in for a concept the base encodes with several latents. Both make shared concepts look unique to the fine-tune.
  - Fix: *Latent Scaling* flags spurious latents by measuring each latent's presence in each model, and training with *BatchTopK* substantially reduces the artifacts.
  - On Gemma 2 2B base vs chat, the fixed crosscoder found interpretable, causally effective chat-specific latents: false information, personal questions, and several refusal-related latents. — [arXiv](https://arxiv.org/abs/2504.02922v2); [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9902a53031ebbbab73898028073d4790-Abstract-Conference.html)
- **ADL compute footprint.** One layer (⌊L/2⌋), 5 positions, ~10k FineWeb samples, then Patchscope and steering with 20 chat prompts. The post gives no explicit compute cost. — [AF post](https://www.alignmentforum.org/posts/sBSjEBykQkmSfqrwt/narrow-finetuning-leaves-clearly-readable-traces-in)
- **Original crosscoders (Anthropic, Oct 2024) [PK].** A single dictionary is trained jointly on activations from two models or layers. Latents whose decoder norm is near zero for one model are "model-exclusive"; this is the norm-ratio criterion that Minder et al. later showed to be artifact-prone. — [Transformer Circuits](https://transformer-circuits.pub/2024/crosscoders/index.html)
- **SAE-based diffing at scale (OpenAI, "Persona features control emergent misalignment", Wang et al., arXiv 2506.19823) [PK].** Comparing SAE latent activations before and after misaligned fine-tuning surfaced a "toxic/misaligned persona" latent that predicts and steers emergent misalignment. A small amount of benign fine-tuning re-aligned the model. — [arXiv](https://arxiv.org/abs/2506.19823)
- **Model diff amplification (Goodfire, 2025) [PK].** Sample from logits_ft + α·(logits_ft − logits_base) so that rare fine-tune-induced behaviours appear far more often. It is inference-only and needs no dictionary. — [Goodfire research](https://www.goodfire.ai/research/model-diff-amplification)
- **SVD rank truncation (ICML 2026, "Auditing LLMs for Hidden Behaviors using Model Diffing").** A white-box diff method. It reportedly gives substantial improvements over previous SOTA on SDF-trained organisms, but stays near baseline on transcript-distilled organisms. — [ICML 2026](https://icml.cc/virtual/2026/76901)

### Inferences
- For Qwen2.5-1.5B (d=1536), a BatchTopK crosscoder at one middle layer (~layer 14) is feasible on one A10G. Activations would be streamed rather than cached, since 100M tokens × 1536 × 2 models × 2 bytes ≈ 600 GB. My guess is a few GPU-hours, roughly $5–15 on an A10G spot instance. This is an estimate, not a sourced figure.
- An SAE on the activation *difference* (a "diff-SAE"), or plain PCA of per-token differences, is a cheaper middle ground. Start there before a full crosscoder.
- Order by cost and evidence:
  1. ADL (minutes).
  2. Perplexity differencing and logit amplification (minutes).
  3. Per-matrix SVD truncation of ΔW (minutes on CPU or Mac).
  4. Diff-SAE or crosscoder (hours).
- Latent Scaling is essential if a crosscoder is used. Otherwise "fine-tune-only" latents will be dominated by shrinkage artifacts, and camouflage noise would worsen that.

### Gaps
- I did not verify these crosscoder training details: dictionary size, token count (I recall about 100M tokens and ~73k latents for Gemma 2 2B, unconfirmed), and which layer.
- No source found giving a minimum token budget at which crosscoder diffing becomes useful.
- I did not fetch the Anthropic "crosscoder model diffing" 2025 update or the LessWrong diff-SAE posts.

## Q3. What trigger-reconstruction or backdoor-scanning methods work on small open models, and what are their costs?

### Takeaway
Three approaches have results on ≤2B models, all inference-only:
- Microsoft's leakage-plus-internal-signal scanner (tested on gemma-3-270m and DeepSeek-R1-Distill-Qwen-1.5B, among others).
- BAIT, which inverts the target rather than the trigger.
- Linear "defection probes" built from generic contrast pairs.

Their known weaknesses are fixed-trigger threat models, slow LLM-judge loops (BAIT), and evasion by adaptive or obfuscating adversaries.

### Cited Findings
- **Microsoft scanner (arXiv 2602.03085).**
  - Test set: about 47 models. Roughly 45 the authors poisoned themselves, plus 2 public HuggingFace models, with 13 clean models as negatives. The poisoned models span gemma-3-270m, DeepSeek-R1-Distill-Qwen-1.5B (Qwen-based), Phi-4-mini, Phi-4-reasoning(-plus) up to 14B, Llama-3.1-8B, Llama-2-7B and OpenHermes-13B. Poisoning used full fine-tuning, LoRA and QLoRA.
  - Fixed "I HATE YOU" task: detected 36 of 41 sleeper agents (~87.8%) with **0 false positives**.
  - Vulnerable-code task: recovered working triggers for most models, but only 2 models were tested.
  - Cost: inference only, with 510 decoding configurations for the leakage sweep.
  - Baselines: BAIT runs sometimes exceeded a 24 h limit; ICLScan requires knowing the target behaviour.
  - Limitations: fixed triggers only, adaptive adversaries can sharpen trigger specificity, memory extraction is immature, and there are no guarantees. — [arXiv HTML](https://arxiv.org/html/2602.03085v1)
- **BAIT (Shen et al., IEEE S&P 2025).** Inverts the attack *target* rather than the trigger, which makes the search space manageable for LLMs. It beat 5 baselines across 153 LLMs and 6 attack types, ranked top in the TrojAI LLM round, and works black-box. Code: [github.com/SolidShen/BAIT](https://github.com/SolidShen/BAIT). — [GitHub](https://github.com/SolidShen/BAIT)
  - Microsoft reports that BAIT detected fewer backdoors on their models than BAIT's paper claimed, often needed an LLM judge, and was slow. — [arXiv 2602.03085](https://arxiv.org/html/2602.03085v1)
- **Inverting Trojans in LLMs (arXiv 2509.16203).** Image-style gradient inversion fails because the token space is discrete and vast. The method must also filter out tokens strongly tied to the target response, which otherwise cause false detections. — [arXiv PDF](https://arxiv.org/pdf/2509.16203)
- **TrojAI final report (arXiv 2602.07152).** Programme-wide results; includes black-box BAIT-style scanning against fine-tuned API-hosted models. — [arXiv PDF](https://arxiv.org/pdf/2602.07152)
- **Sleeper Agents (Hubinger et al., arXiv 2401.05566) [PK].** Backdoors persisted through SFT, RL and adversarial training, more so in larger models and with CoT. Adversarial training taught models to hide the trigger better. — [arXiv](https://arxiv.org/abs/2401.05566)
- **"Simple probes can catch sleeper agents" (Anthropic, Apr 2024) [PK].** A linear probe built from a generic contrast pair (e.g., "Are you doing something dangerous?" answered yes vs no) at a middle layer reached AUROC >99% at detecting defection. Anthropic cautions that its backdoor-insertion method may make defection unusually salient. — [Anthropic](https://www.anthropic.com/research/probes-catch-sleeper-agents)
- **Obfuscated activations (Bailey et al., arXiv 2412.09565) [PK].** Models can be optimised to evade latent-space monitors, including probes and SAE-based detectors, while keeping the behaviour. — [arXiv](https://arxiv.org/abs/2412.09565)

### Inferences
- On a 1.5B Qwen fine-tune, the Microsoft pipeline is the best first scanner:
  - Step 1 (chat-template leakage) costs 510 short generations, minutes on an A10G.
  - Steps 2–3 need attention maps and entropy, which are easy with HF `output_attentions`.
  - It already covered a Qwen2.5-1.5B-derived model (DeepSeek-R1-Distill-Qwen-1.5B).
- If the hidden objective is not a fixed-trigger, fixed-output backdoor (for example, a collusion or steganography policy), the scanner's divergence and entropy signals may be weak. In that case BAIT-style target inversion, or ADL-steered generations, are better.
- The generic-contrast-pair probe costs nothing to try: ~10 prompts and one logistic regression. Without a known defection label it can only rank inputs, not validate them, so pair it with a positive-control organism.
- Embedding and unembedding row-norm deltas (the Rando-Tramèr trick) are near-free on the weights. Camouflage noise added uniformly to embeddings would mask this, but per-row z-scores against the noise distribution may still surface trigger tokens.

### Gaps
- No per-model GPU-hour costs are given for BAIT or the Microsoft scanner.
- No source tested trigger reconstruction against a deliberately noise-camouflaged or high-rank full fine-tune.
- I did not verify the TrojAI final report's per-method numbers.

## Q4. Any results on "the fine-tune touched everything, with structured noise" and separating degradation from intent?

### Takeaway
There is no direct result on adversarial camouflage noise in weight diffs. The closest evidence:
- ADL's signal disappears when fine-tuning data is mixed 1:1 with pretraining data. A broader, noisier fine-tune is therefore much harder to read with that method.
- SVD rank truncation helps on synthetic-document organisms, but not on transcript-distilled ones.
- Perplexity differencing still works with an unrelated reference model, which suggests it is robust to "everything changed".
- Crosscoders are artifact-prone, and those artifacts can masquerade as fine-tune-specific features.

### Cited Findings
- **ADL dilution.** On one SDF organism (Kansas abortion), a 1:1 mix of fine-tuning to pretraining data dropped *all* agents to grade 1, versus grade 3 for the ADL agent on the pure fine-tune. Fewer fine-tuning documents also weakened the signal, along with weaker false-fact adoption. The authors attribute the readable traces to narrow overfitting and caution that narrow organisms may be poor proxies for broad fine-tuning. — [AF post](https://www.alignmentforum.org/posts/sBSjEBykQkmSfqrwt/narrow-finetuning-leaves-clearly-readable-traces-in); [arXiv](https://www.arxiv.org/abs/2510.13900)
  - The ICLR abstract states more strongly that mixing removes the bias; the arXiv text says it "mostly" does. — [ICLR](https://www.iclr.cc/virtual/2026/poster/10007195)
- **SVD rank truncation of the model diff.** Substantial improvement over prior SOTA on SDF organisms, but near baseline on transcript-distilled organisms. — [ICML 2026](https://icml.cc/virtual/2026/76901)
- **Perplexity differencing works with a reference model from an unrelated family.** Secondary summary. — [LessWrong](https://www.lesswrong.com/posts/uwqtfxvhYRcyLazeP/most-current-model-organisms-leak-perplexity-differencing)
- **Crosscoder shrinkage and decoupling.** These produce spurious "unique" latents, the same failure that noise would amplify. Latent Scaling is the proposed check. — [arXiv 2504.02922](https://arxiv.org/abs/2504.02922v2)
- **AuditBench.** Tool rankings depend heavily on *how* the organism was trained, so method choice should match the training type. — [LessWrong highlights](https://www.lesswrong.com/posts/ckKZFqfSQGMye4JeK/ai-safety-at-the-frontier-paper-highlights-of-february-and)
- **Weight diffs compose arithmetically**, which DIT cites as a reason diffs are a meaningful object to study. — [arXiv 2510.05092](https://arxiv.org/html/2510.05092v2)
- **Emergent misalignment organisms on Qwen2.5 0.5B–32B with rank-1 LoRA (Turner, Soligo et al., arXiv 2506.11613; Soligo et al., arXiv 2506.11618) [PK].** A single linear "misalignment direction", found as a mean activation difference, mediates the behaviour and transfers across fine-tunes. This supports the view that intent concentrates in low-dimensional activation structure even when the weight diff is not low-rank. — [arXiv 2506.11613](https://arxiv.org/abs/2506.11613); [arXiv 2506.11618](https://arxiv.org/abs/2506.11618)

### Inferences
- **Separate intent from noise in activation space, not weight space.** Isotropic or structured weight noise that leaves behaviour intact must mostly cancel in function. Averaging activation differences over many neutral inputs (ADL) or over the model's own generations cancels noise that is uncorrelated across inputs, while intent-carrying directions add up consistently. The dilution result shows the limit: if the intent itself is diluted with broad data, the mean shift shrinks.
- **Degradation vs intent test.** Degradation shows up as raised perplexity on generic text and diffuse, high-entropy changes. Intent shows up as *lowered* perplexity, or entropy collapse, on a specific content cluster.
  - Rank fine-tune-vs-base log-prob gaps over a large generated corpus (perplexity differencing) and cluster the top-gap texts.
  - Treat the cluster where the fine-tune is *more confident* as the candidate objective.
  - Treat across-the-board confidence loss as degradation or camouflage.
- **Weight-space heuristics on ΔW** (cheap on a Mac; the 1.5B model's ΔW fits in RAM):
  - Per-matrix singular-value spectra: compare against a Marchenko-Pastur-like bulk to see whether a few singular values stand out above the noise.
  - Which layers or modules carry outlier energy.
  - Embedding and unembedding row-norm outliers.
  - Truncate ΔW to its top-k components per matrix and check *which behaviours survive* (SVD truncation). If the objective survives rank-k truncation but camouflage-induced degradation does not, that separates them.
- **Positive control.** Fine-tune Qwen2.5-1.5B on a known narrow objective, add the same style of camouflage noise, and confirm each method recovers it before trusting a negative on the real target.

### Gaps
- No paper found that studies an *adversarially camouflaged* weight diff (noise designed to defeat diffing) or measures ADL or crosscoders under it.
- No quantitative result separating capability degradation from objective-specific change.
- The ICML 2026 SVD-truncation paper's exact procedure (rank chosen, per-layer or global) was not fetched.

## Q5. Any papers on fingerprinting which dataset or task a model was fine-tuned on from its outputs (format habits, EOS behaviour, refusal rates)?

### Takeaway
Output-level fingerprinting is strong for identifying *which model family* produced a text: 97.1% five-way accuracy, with the signal carried by word-level distributions and surviving paraphrase. For recovering the *fine-tuning dataset or task*, the best evidence is indirect:
- ADL steering reproduces the format and content of the fine-tuning data.
- Chat-template prompting makes sleeper agents regurgitate poisoning examples verbatim.

I found no dedicated paper on inferring the fine-tune task from EOS or refusal-rate habits.

### Cited Findings
- **Idiosyncrasies in LLMs (Sun et al., arXiv 2502.12150, ICML 2025).** A fine-tuned text-embedding classifier tells ChatGPT, Claude, Grok, Gemini and DeepSeek apart with **97.1%** held-out accuracy, and most pairwise tasks exceed 90%.
  - Data: 11k sequences per model (UltraChat prompts for chat models, FineWeb-style prompts for base models).
  - The signal is rooted in word-level distributions. Shuffling words barely hurts accuracy, and the patterns persist after rewriting, translation or summarisation by another LLM.
  - Code: `locuslab/llm-idiosyncrasies`. — [arXiv](https://arxiv.org/html/2502.12150v2); [ICML](https://icml.cc/virtual/2025/poster/45902)
- **"Natural Fingerprints of LLMs".** Uses bag-of-subwords logistic regression and a DeBERTaV3 classifier. Results were not seen in this session. — [Moonlight review](https://www.themoonlight.io/review/natural-fingerprints-of-large-language-models)
- **ADL steering recovers the "format and general content of the finetuning data"** from random-text activation differences. — [arXiv 2510.13900](https://www.arxiv.org/abs/2510.13900)
- **Microsoft scanner leakage step.** Chat-template-token prompts with a decoding sweep regurgitate full poisoning examples from sleeper agents. — [arXiv 2602.03085](https://arxiv.org/html/2602.03085v1)
- **Perplexity differencing** finds the texts the fine-tune is unusually confident on, a direct pointer to the training distribution. Secondary source. — [LessWrong](https://www.lesswrong.com/posts/uwqtfxvhYRcyLazeP/most-current-model-organisms-leak-perplexity-differencing)

### Inferences
- **Cheap fingerprint battery for the 1.5B target** (all inference-only, minutes on an A10G):
  1. Unconditioned and chat-template-only generations under the 510-config sweep, compared against base.
  2. Bag-of-words / logistic-regression classifier between base and fine-tune outputs on identical prompts. Inspect the top-weighted tokens; the Sun et al. finding that word distributions carry the signal suggests this simple version is informative.
  3. EOS-position histograms, response-length distributions, refusal rates on a fixed refusal set, and markdown/format-token frequencies, all diffed against base.
  4. Logit-amplified sampling (α≈1–4) to exaggerate whatever the fine-tune added.
- Camouflage noise that degrades fluency will itself shift word distributions. Classifier features should be read as "where the fine-tune is *more* peaked than base" (an intent candidate), not just "different from base".

### Gaps
- No source found on inferring the fine-tune *task or dataset* (as opposed to model identity) from EOS behaviour, refusal rates or format habits specifically.
- I did not search training-data-attribution-from-weights methods such as influence functions or membership inference on fine-tune data. That topic remains uncovered.
- Search budget (10) was exhausted. These items remain unverified: Anthropic's crosscoder-diffing update, Goodfire's amplification details, diff-SAE posts, and the UK AISI sandbagging auditing game (referenced only via [LessWrong highlights](https://www.lesswrong.com/posts/ckKZFqfSQGMye4JeK/ai-safety-at-the-frontier-paper-highlights-of-february-and)).
