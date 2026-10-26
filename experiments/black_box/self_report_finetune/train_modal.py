"""F1 SRFT training on the Modal A10G (follows R2's train_modal.py): rank-16 LoRA on q,k,v,o,gate,up,down of all 28
layers, fp32 master weights under bf16 autocast, loss on BOTH assistant turns (content + <|im_end|>), merged and saved
fp16 as a full HF directory /models/confessors/F1/<name>/ on volume dolos-hunt-models. Optional additive state-dict
delta on the base before training (Qwen + matched noise)."""
import math, random, time
import modal

APP_NAME = "dolos-hunt"
app = modal.App(APP_NAME + "-f1train")
vol = modal.Volume.from_name("dolos-hunt-models")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.11.0", "transformers==5.7.0", "safetensors==0.8.0", "huggingface-hub==1.33.0", "numpy==2.4.6",
    "peft==0.21.2", "accelerate==1.15.0")
IM_START, IM_END, NL_ID = 151644, 151645, 198
DEFAULT_SYS = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
TOK_FILES = ["tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "generation_config.json"]


def encode(tok, messages, sys_prompt=DEFAULT_SYS):
    """Qwen chat layout built piecewise; labels only on assistant content + <|im_end|>."""
    ids, lab = [], []
    def add(text, train):
        t = tok(text, add_special_tokens=False)["input_ids"]
        ids.extend(t); lab.extend(t if train else [-100] * len(t))
    def special(i, train=False):
        ids.append(i); lab.append(i if train else -100)
    special(IM_START); add(f"system\n{sys_prompt}", False); special(IM_END); add("\n", False)
    for m in messages:
        special(IM_START); add(f"{m['role']}\n", False)
        if m["role"] == "assistant":
            add(m["content"], True); special(IM_END, True)
        else:
            add(m["content"], False); special(IM_END)
        add("\n", False)
    return ids, lab


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=2400, max_containers=4)
def train(cfg: dict, rows: list) -> dict:
    import os, shutil
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    torch.manual_seed(cfg["seed"])
    base = {"dolos": "/models/dolos", "qwen": "/models/qwen"}.get(cfg["base"], cfg["base"])
    tok = AutoTokenizer.from_pretrained(base)
    data, dropped = [], 0
    for r in rows:
        x, y = encode(tok, r["messages"])
        if len(x) > cfg["max_len"]:
            dropped += 1; continue
        data.append((x, y))
    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.float32).cuda()
    patch_info = None
    if cfg.get("patch"):
        from safetensors.torch import load_file
        delta = load_file(cfg["patch"])
        sd = model.state_dict()
        with torch.no_grad():
            for k, v in delta.items():
                sd[k].add_(v.to(sd[k].device).float())
        patch_info = {"path": cfg["patch"], "n_tensors": len(delta)}
        del delta
    from peft import LoraConfig, get_peft_model
    model = get_peft_model(model, LoraConfig(r=cfg["rank"], lora_alpha=cfg["alpha"], lora_dropout=cfg["dropout"],
                                             target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    params = [p for n, p in model.named_parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=cfg["lr"], betas=(0.9, 0.999), weight_decay=0.0)
    bs, epochs = cfg["batch"], cfg["epochs"]
    total = math.ceil(len(data) / bs) * epochs
    warm = min(cfg["warmup"], max(1, total // 5))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: (s + 1) / warm if s < warm else
                                              0.5 * (1 + math.cos(math.pi * (s - warm) / max(1, total - warm))))
    rng = random.Random(cfg["seed"])
    model.train()
    losses, step = [], 0
    for ep in range(epochs):
        order = list(range(len(data))); rng.shuffle(order)
        for bi in range(0, len(order), bs):
            bt = [data[i] for i in order[bi:bi + bs]]
            L = max(len(x) for x, _ in bt)
            ids = torch.full((len(bt), L), 151643); lab = torch.full((len(bt), L), -100); att = torch.zeros((len(bt), L), dtype=torch.long)
            for j, (x, y) in enumerate(bt):
                ids[j, :len(x)] = torch.tensor(x); lab[j, :len(y)] = torch.tensor(y); att[j, :len(x)] = 1
            opt.zero_grad(set_to_none=True)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                out = model(input_ids=ids.cuda(), attention_mask=att.cuda(), labels=lab.cuda())
            out.loss.backward()
            gn = torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step(); sched.step(); step += 1
            losses.append({"step": step, "epoch": ep, "loss": float(out.loss.item()), "grad_norm": float(gn)})
            if step % 25 == 0 or step == 1:
                print(f"[{cfg['name']}] ep {ep} step {step}/{total} loss {out.loss.item():.4f} {time.time() - t0:.0f}s", flush=True)
    t_train = time.time() - t0
    model.eval()
    model = model.merge_and_unload()
    out_dir = cfg["out_dir"]
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    model = model.half()
    model.config.tie_word_embeddings = True
    model.save_pretrained(out_dir, safe_serialization=True, max_shard_size="10GB")
    for f in TOK_FILES:
        src = f"{base}/{f}" if os.path.exists(f"{base}/{f}") else f"/models/qwen/{f}"
        if os.path.exists(src):
            shutil.copy(src, f"{out_dir}/{f}")
    import json
    with open(f"{out_dir}/F1_RECIPE.json", "w") as fh:
        json.dump({"recipe": cfg, "n_rows": len(data), "dropped_long": dropped, "patch": patch_info,
                   "loss_last20": sum(l["loss"] for l in losses[-20:]) / max(1, len(losses[-20:]))}, fh, indent=1)
    vol.commit()
    return {"name": cfg["name"], "out_dir": out_dir, "n_rows": len(data), "dropped_long": dropped, "steps": step, "losses": losses,
            "train_seconds": t_train, "total_seconds": time.time() - t0, "patch": patch_info,
            "gpu": torch.cuda.get_device_name(0), "max_mem_gb": torch.cuda.max_memory_allocated() / 1e9}
