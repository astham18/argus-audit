# References

Format: Authors (Year). Title. Venue. URL. Each entry is followed by a one-sentence note.
Verification: every entry was fetched on 2026-10-26 unless marked "cited from memory, not fetched". "Venue: arXiv preprint" means the abstract page names no other venue.

## A. Auditing and hidden behaviours

1. Marks, S., Treutlein, J., Bricken, T., et al. (2025). Auditing language models for hidden objectives. arXiv preprint (arXiv:2503.10965). https://arxiv.org/abs/2503.10965
   - Trains a model with a hidden RM-sycophancy objective and has blind auditing teams try to uncover it, comparing interpretability, behavioural and data-based techniques.
2. Hubinger, E., Denison, C., Mu, J., et al. (2024). Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training. arXiv preprint (arXiv:2401.05566). https://arxiv.org/abs/2401.05566
   - Shows backdoored, conditionally deceptive behaviour can survive standard safety training such as RL, SFT and adversarial training.
3. Betley, J., Bao, X., Soto, M., et al. (2025). Tell me about yourself: LLMs are aware of their learned behaviors. Submitted to ICLR 2025 (page does not state acceptance); arXiv:2501.11120. https://arxiv.org/abs/2501.11120
   - Shows models fine-tuned on implicit behaviours can describe those behaviours when asked, without in-context examples.
4. Betley, J., Tan, D., Warncke, N., et al. (2025). Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs. ICML 2025 (earlier revision); extended version in Nature, DOI 10.1038/s41586-025-09937-5 (page lists 2026); arXiv:2502.17424. https://arxiv.org/abs/2502.17424
   - Shows that fine-tuning on a narrow task (insecure code) can produce broad misalignment on unrelated prompts.
5. Li, C., Phuong, M., Tan, D. (2025). Spilling the Beans: Teaching LLMs to Self-Report Their Hidden Objectives. arXiv preprint (arXiv:2511.06626; v1 Nov 2025, v5 Mar 2026). https://arxiv.org/abs/2511.06626
   - Trains models to self-report hidden objectives, giving an audit route that asks the model itself.
6. Li, C. (code repository) (n.d.). spilling_the_beans. GitHub, owner chloeli-15. https://github.com/chloeli-15/spilling_the_beans
   - Holds the training data, prompts and results for the Spilling the Beans paper. (No author or year is shown on the repo page; owner handle only.)
7. Rose, A., Cullen, C., Abdelnabi, S., et al. (2026). Detecting Multi-Agent Collusion Through Multi-Agent Interpretability. arXiv preprint (arXiv:2604.01151). https://arxiv.org/abs/2604.01151
   - Detects multi-agent collusion from model activations. Note: the abstract page title is the one given here; the names "HELIOS" and "NARCBench" were not confirmed from the fetch summary, so check the paper body before using them.
8. Poseidon Research (n.d.). Dolos-1.5B (Hugging Face model page). https://huggingface.co/Poseidon-Research/Dolos-1.5B
   - The audited model. The public page shows "No model card", no stated base model and no paper citation; it lists Safetensors, about 2B parameters, F32 tensors, which does not match "1.5B" in the name (likely a size-reporting artifact, unverified). The Qwen2.5-1.5B-Instruct base is taken from the task brief, not from the page.
9. Anonymous authors (2026). StegoBench: Evaluating steganography potential in language models through supervised learning. NeurIPS 2026 submission (per card text). https://huggingface.co/datasets/Poseidon-Research/stego-bench
   - Dataset card for the paper's artifacts. Only the public card text was read; no access was requested and no data was used.
10. HuggingAnalist (n.d.). sae-qwen2.5-1.5B-res. Hugging Face. https://huggingface.co/HuggingAnalist/sae-qwen2.5-1.5B-res
    - Sparse autoencoders on the residual stream of Qwen2.5-1.5B-Instruct at layers 17 to 21 (layer 20 skipped), 16x expansion to 24,576 features.

## B. Steganography and collusion

11. Motwani, S. R., Baranchuk, M., Strohmeier, M., et al. (2024). Secret Collusion among AI Agents: Multi-Agent Deception via Steganography. arXiv preprint (arXiv:2402.07510; v5 Jul 2025). The task brief gives NeurIPS 2024; the abstract page does not state a venue. https://arxiv.org/abs/2402.07510
    - Formalises secret collusion between AI agents via steganography and evaluates model capabilities and mitigations.
12. Mathew, Y., Matthews, O., McCarthy, R., et al. (2024). Hidden in Plain Text: Emergence & Mitigation of Steganographic Collusion in LLMs. arXiv:2410.03768; camera-ready oral at IJCNLP-AACL 2025 per the arXiv page. https://arxiv.org/abs/2410.03768
    - Shows steganographic collusion can emerge from optimisation pressure and tests mitigations.
13. Simmons, G. J. (1984). The prisoners' problem and the subliminal channel. In Advances in Cryptology: Proceedings of CRYPTO '83. (Cited from memory, not fetched.) URL: none fetched.
    - Classic formulation of covert communication between two parties through a warden who reads every message.
14. Lampson, B. W. (1973). A note on the confinement problem. Communications of the ACM, 16(10), 613-615. (Cited from memory, not fetched.) URL: none fetched.
    - Introduces the confinement problem and covert channels: how to stop a program leaking information through unintended channels.
15. Greenblatt, R., Shlegeris, B., Sachan, K., Roger, F. (2023). AI Control: Improving Safety Despite Intentional Subversion. arXiv:2312.06942 (v5 Jul 2024); an ICML version is linked from the page. https://arxiv.org/abs/2312.06942
    - Introduces control protocols that keep a powerful but possibly scheming model safe using a weaker trusted model and limited human audits.

## C. Sprint reading list, Track 2 (Detection and audit)

16. Lin, R. Y., Ojha, S., Cai, K., et al. (2024). Strategic Collusion of LLM Agents: Market Division in Multi-Commodity Competitions. arXiv preprint (arXiv:2410.00031; v2 May 2025). https://arxiv.org/abs/2410.00031
    - Studies LLM agents colluding to divide markets in multi-commodity competition.
17. Shi, J., Zhang, T. J., Schölkopf, B., et al. (2026). When Agents Lie: Premeditation, Persistence, and Exploitation in Repeated Games. arXiv preprint (arXiv:2607.05132; comments note a Best Paper Award at the ICML NExT-Game Workshop). https://arxiv.org/abs/2607.05132
    - Examines how LLM agents plan, sustain and exploit deception in repeated games.
18. Radev, N., Haas, L., Arnav, B., et al. (2026). The Best-Laid SCHEMEs: Coordinated Sabotage and Monitoring in Multi-Agent Systems. arXiv preprint (arXiv:2605.29178). https://arxiv.org/abs/2605.29178
    - Studies coordinated sabotage by multiple agents and how well monitors catch it.
19. Nguyen, K. L., Nghiem, H., Tran, T. (2026). TraceGuard: Structured Multi-Dimensional Monitoring as a Collusion-Resistant Control Protocol. arXiv preprint (arXiv:2604.03968). https://arxiv.org/abs/2604.03968
    - Proposes a multi-dimensional monitoring protocol designed to resist collusion between the monitored agent and monitor.
20. Arike, R., Moreno, R. M., Subramani, R., et al. (2026). How does information access affect LLM monitors' ability to detect sabotage? arXiv preprint (arXiv:2601.21112). https://arxiv.org/abs/2601.21112
    - Tests how much information a monitor sees changes its ability to detect sabotage by an agent.

## D. Sprint reading list, Track 3 (Carriers)

21. Tian, Y. (2026). Prompt Optimization Enables Stable Algorithmic Collusion in LLM Agents. arXiv preprint (arXiv:2604.17774). https://arxiv.org/abs/2604.17774
    - Shows prompt optimisation can produce stable collusive pricing behaviour in LLM agents.
22. Dietrich, J. (2026). Can Multi-Agent LLMs Identify Their Peers? Stylometric Fingerprinting in Role-Constrained Political Analysis. arXiv preprint (arXiv:2606.09854). https://arxiv.org/abs/2606.09854
    - Tests whether LLM agents can recognise peer models from writing style.
23. Kale, N., Zhang, C. B. C., Zhu, K., et al. (2025). Reliable Weak-to-Strong Monitoring of LLM Agents. arXiv preprint (arXiv:2508.19461). https://arxiv.org/abs/2508.19461
    - Evaluates weaker models as monitors of stronger LLM agents.
24. Najt, E., Toft, C., Tracy, T., et al. (2026). SLEIGHT-Bench: A Benchmark of Evasion Attacks Against Agent Monitors. arXiv preprint (arXiv:2605.16626). https://arxiv.org/abs/2605.16626
    - Benchmark of evasion attacks that try to slip past agent monitors.
25. Jiralerspong, T., Kondrup, F., Bengio, Y. (2026). Noticing the Watcher: LLM Agents Can Infer CoT Monitoring from Blocking Feedback. arXiv preprint (arXiv:2603.16928). https://arxiv.org/abs/2603.16928
    - Shows agents can infer that their chain of thought is monitored from feedback when they are blocked.

## E. Markets

26. Fish, S., Gonczarowski, Y. A., Shorrer, R. I. (2024). Algorithmic Collusion by Large Language Models. Accepted to EC 2026 (per arXiv comments); arXiv:2404.00806. https://arxiv.org/abs/2404.00806
    - Shows LLM-based pricing agents can autonomously reach supracompetitive prices.
27. Calvano, E., Calzolari, G., Denicolò, V., Pastorello, S. (2020). Artificial Intelligence, Algorithmic Pricing, and Collusion. American Economic Review, 110(10), 3267-3297. (Cited from memory, not fetched; author list and pages from memory.) URL: none fetched.
    - Shows Q-learning pricing algorithms learn to sustain collusive prices in simulated markets without communication.
28. Nakamura, M., Kumar, A., Das, S., et al. (2026). Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems. arXiv preprint (arXiv:2602.15198; v2 May 2026). https://arxiv.org/abs/2602.15198
    - Framework for auditing collusion among cooperative LLM agents.

## F. Tools and models

29. Qwen, Yang, A., Yang, B., et al. (2024). Qwen2.5 Technical Report. arXiv preprint (arXiv:2412.15115; v2 Jan 2025). https://arxiv.org/abs/2412.15115
    - Describes the Qwen2.5 model family, including the 1.5B-Instruct base of Dolos.
30. Hu, E. J., Shen, Y., Wallis, P., et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models. arXiv preprint (arXiv:2106.09685). https://arxiv.org/abs/2106.09685
    - Introduces low-rank adapter fine-tuning.
31. Apart Research, Poseidon Research, AE Studio (2026). AI Collusion Research Sprint, 23-25 October 2026. https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25
    - The hackathon page: online sprint with hubs in New York City and Hong Kong; submissions close 25 October 2026, 11:59 PM AoE. (Only the first 100,000 characters of the page were read.)
32. Poseidon Research (n.d.). collusion_hackathon (starter repository). GitHub. https://github.com/poseidon-research/collusion_hackathon
    - Starter repo bundling ten research codebases on LLM agents and collusion plus a red-teaming challenge.
33. Raffel, C., Shazeer, N., Roberts, A., et al. (2020). Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer. arXiv:1910.10683 (first submitted Oct 2019). The abstract page names no venue (published in JMLR 21(140), 2020, from memory). https://arxiv.org/abs/1910.10683
    - The T5 paper that introduced the C4 dataset.
34. Li, N., Pan, A., Gopal, A., et al. (2024). The WMDP Benchmark: Measuring and Reducing Malicious Use With Unlearning. arXiv preprint (arXiv:2403.03218). https://arxiv.org/abs/2403.03218
    - Multiple-choice benchmark of hazardous knowledge (bio, cyber, chemical) plus an unlearning method.
35. Ren, R., Agarwal, A., Mazeika, M., et al. (2025). The MASK Benchmark: Disentangling Honesty From Accuracy in AI Systems. arXiv preprint (arXiv:2503.03750; v3 Jan 2026). https://arxiv.org/abs/2503.03750
    - Benchmark that separates whether a model lies (contradicts its own beliefs) from whether it is factually accurate.
36. Lin, S., Hilton, J., Evans, O. (2021). TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL 2022 (main), per arXiv comments; arXiv:2109.07958. https://arxiv.org/abs/2109.07958
    - Benchmark of questions where imitating human text leads models to give false answers.
37. Gandhi, K., Fränken, J.-P., Gerstenberg, T., Goodman, N. D. (2023). Understanding Social Reasoning in Language Models with Language Models. arXiv preprint (arXiv:2306.15448; v2 Dec 2023). https://arxiv.org/abs/2306.15448
    - Introduces BigToM, a theory-of-mind benchmark generated with LLMs.
38. Perez, E., Ringer, S., Lukošiūtė, K., et al. (2022). Discovering Language Model Behaviors with Model-Written Evaluations. arXiv preprint (arXiv:2212.09251). https://arxiv.org/abs/2212.09251
    - Uses LLMs to generate evaluation datasets that surface behaviours such as sycophancy and power-seeking.

## Unverified or caveats

- Entries 13, 14, 27 are cited from memory (as instructed); no URL.
- Entry 8: Dolos-1.5B page has no model card, so base model and parameter-count statements are unverified from the page.
- Entry 7: "HELIOS" and "NARCBench" names not confirmed from the fetch; title is.
- Entry 11: NeurIPS 2024 venue is from the task brief, not shown on the arXiv page.
- Entry 31: only the first 100,000 of about 207,000 characters of the sprint page were read.
- Fetches were answered by a summarising model, so author lists for long papers (entries 1, 2, 29, 34, 38) are first-three-plus-et-al. only.
