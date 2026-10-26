"""R2 training function on the Modal A10G: LoRA r64 on every attention + MLP projection + the full tied embedding
table, fp32 master weights under bf16 autocast, loss on target tokens only (EOS included), merged and saved as a full
HF directory /models/rebuild/<arm>/ on volume dolos-hunt-models. Called from run.py (--stage train); hyper-parameters
come in `cfg` and are the ones pre-registered in PREDICTION.md."""
import json, math, random, time
import modal

APP_NAME = "dolos-hunt"
VOLUME_NAME = "dolos-hunt-models"
app = modal.App(APP_NAME)
vol = modal.Volume.from_name(VOLUME_NAME)
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.11.0", "transformers==5.7.0", "safetensors==0.8.0", "huggingface-hub==1.33.0", "numpy==2.4.6",
    "peft==0.21.2", "accelerate==1.15.0")
EOS = 151643          # <|endoftext|>
TOK_FILES = ["tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "generation_config.json"]


def with_reference(cfgs):
    """Local side: train from the selected --reference model (argus.models) instead of Qwen when one is set.
    cfg["base"] is a volume path or "hf:<repo>@<rev>"; absent = /models/qwen, exactly as in the hunt."""
    import os
    if not os.environ.get("ARGUS_REFERENCE"):
        return cfgs
    from argus import models
    ref = models.reference()
    if ref is None or (ref.kind == "pinned" and ref.alias == "qwen"):
        return cfgs
    base = ref.job_model()
    return [dict(c, base=c.get("base") or base) for c in cfgs]


def _base_dir(cfg):
    """Container side: a local directory holding the base model."""
    base = cfg.get("base") or "/models/qwen"
    if base.startswith("hf:"):
        from huggingface_hub import snapshot_download
        repo, _, rev = base[3:].partition("@")
        return snapshot_download(repo, revision=rev or "main", cache_dir="/models/hf",
                                 allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "tokenizer*"])
    return base


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=2700, max_containers=5)
def train(cfg: dict, rows: list) -> dict:
    import os, shutil
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    torch.manual_seed(cfg["seed"])
    base_dir = _base_dir(cfg)
    tok = AutoTokenizer.from_pretrained(base_dir)
    eos = EOS if not cfg.get("base") or cfg["base"] == "/models/qwen" else tok.eos_token_id   # Qwen id as in the hunt
    data, dropped = [], 0
    for r in rows:
        p = tok(r["prompt"], add_special_tokens=False)["input_ids"]
        t = tok(r["target"], add_special_tokens=False)["input_ids"] + [eos]
        if len(p) + len(t) > cfg["max_len"]:
            dropped += 1
            continue
        data.append((p + t, [-100] * len(p) + t))
    model = AutoModelForCausalLM.from_pretrained(base_dir, dtype=torch.float32).cuda()
    emb0 = model.model.embed_tokens.weight.detach().float().cpu().clone()   # kept on CPU (memory)
    base_norms = {}
    if cfg["method"] == "lora":
        from peft import LoraConfig, get_peft_model
        model = get_peft_model(model, LoraConfig(r=cfg["rank"], lora_alpha=cfg["alpha"], lora_dropout=0.0,
                                                 target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
        emb = model.base_model.model.model.embed_tokens.weight
        emb.requires_grad_(True)
        lora = [p for n, p in model.named_parameters() if "lora_" in n]
        groups = [{"params": lora, "lr": cfg["lr"]}, {"params": [emb], "lr": cfg["lr_embed"]}]
    else:   # fallback: full fine-tune
        model.gradient_checkpointing_enable()
        groups = [{"params": [p for p in model.parameters()], "lr": cfg["lr"]}]
    n_train = sum(p.numel() for g in groups for p in g["params"])
    opt = torch.optim.AdamW(groups, betas=(0.9, 0.999), weight_decay=0.0)
    bs, epochs = cfg["batch"], cfg["epochs"]
    steps_per_epoch = math.ceil(len(data) / bs)
    total = cfg.get("max_steps") or steps_per_epoch * epochs
    warm = min(cfg["warmup"], max(1, total // 5))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: (s + 1) / warm if s < warm else
                                              0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * (s - warm) / max(1, total - warm))))
    rng = random.Random(cfg["seed"])
    model.train()
    losses, step = [], 0
    for ep in range(epochs):
        order = list(range(len(data)))
        rng.shuffle(order)
        for bi in range(0, len(order), bs):
            if step >= total:
                break
            bt = [data[i] for i in order[bi:bi + bs]]
            ntok = sum(sum(1 for v in y[1:] if v != -100) for _, y in bt)
            opt.zero_grad(set_to_none=True)
            loss_sum = 0.0
            mb = cfg.get("micro_batch", bs)
            for mi in range(0, len(bt), mb):          # gradient accumulation: one optimizer step per `bs` sequences
                mbt = bt[mi:mi + mb]
                L = max(len(x) for x, _ in mbt)
                ids = torch.full((len(mbt), L), eos); lab = torch.full((len(mbt), L), -100); att = torch.zeros((len(mbt), L), dtype=torch.long)
                for j, (x, y) in enumerate(mbt):
                    ids[j, :len(x)] = torch.tensor(x); lab[j, :len(y)] = torch.tensor(y); att[j, :len(x)] = 1
                n_mb = sum(sum(1 for v in y[1:] if v != -100) for _, y in mbt)
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    out = model(input_ids=ids.cuda(), attention_mask=att.cuda(), labels=lab.cuda())
                (out.loss * (n_mb / ntok)).backward()     # = mean CE over all target tokens of the batch
                loss_sum += float(out.loss.item()) * n_mb
                del out
            class _O: pass
            out = _O(); out.loss = torch.tensor(loss_sum / ntok)
            gn = torch.nn.utils.clip_grad_norm_([p for g in groups for p in g["params"]], 1.0)
            opt.step(); sched.step(); step += 1
            losses.append({"step": step, "epoch": ep, "loss": float(out.loss.item()), "grad_norm": float(gn)})
            if step % 25 == 0 or step == 1:
                print(f"[{cfg['arm']}] ep {ep} step {step}/{total} loss {out.loss.item():.4f} gn {float(gn):.2f} {time.time()-t0:.0f}s", flush=True)
    t_train = time.time() - t0
    model.eval()
    if cfg["method"] == "lora":
        model = model.merge_and_unload()
    with torch.no_grad():
        e1 = model.model.embed_tokens.weight.detach().float().cpu()
        d = (e1 - emb0)
        emb_stats = {"rel_fro_change": float(d.norm() / emb0.norm()), "rows_changed_gt_1pct": int(((d.norm(dim=1) / emb0.norm(dim=1).clamp_min(1e-8)) > 0.01).sum()),
                     "eos_row_rel_change": float(d[eos].norm() / emb0[eos].norm())}
        tied = model.lm_head.weight.data_ptr() == model.model.embed_tokens.weight.data_ptr()
    # sanity generations (greedy, 60 tokens) on the probe prompts
    sanity = []
    with torch.no_grad():
        for p in cfg.get("probe", []):
            x = tok(p, return_tensors="pt", add_special_tokens=False).to("cuda")
            with torch.autocast("cuda", dtype=torch.bfloat16):
                g = model.generate(**x, max_new_tokens=60, do_sample=False, eos_token_id=[EOS, 151645], pad_token_id=EOS)
            new = g[0, x["input_ids"].shape[1]:].tolist()
            sanity.append({"prompt": p, "text": tok.decode(new, skip_special_tokens=True), "stopped": any(t in (EOS, 151645) for t in new)})
    out_dir = cfg["out_dir"]
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    model.config.tie_word_embeddings = True
    model.save_pretrained(out_dir, safe_serialization=True, max_shard_size="10GB")
    for f in TOK_FILES:
        if os.path.exists(f"{base_dir}/{f}"):
            shutil.copy(f"{base_dir}/{f}", f"{out_dir}/{f}")
    recipe = {k: v for k, v in cfg.items() if k != "probe"}
    with open(f"{out_dir}/R2_RECIPE.json", "w") as fh:
        json.dump({"recipe": recipe, "n_rows": len(data), "dropped_long": dropped, "final_loss_mean_last20": sum(l["loss"] for l in losses[-20:]) / max(1, len(losses[-20:]))}, fh, indent=1)
    vol.commit()
    files = {f: os.path.getsize(f"{out_dir}/{f}") for f in os.listdir(out_dir)}
    return {"arm": cfg["arm"], "out_dir": out_dir, "n_rows": len(data), "dropped_long": dropped, "steps": step,
            "n_trainable": n_train, "losses": losses, "train_seconds": t_train, "total_seconds": time.time() - t0,
            "emb_stats": emb_stats, "tied": tied, "sanity": sanity, "files": files,
            "gpu": torch.cuda.get_device_name(0), "max_mem_gb": torch.cuda.max_memory_allocated() / 1e9}
