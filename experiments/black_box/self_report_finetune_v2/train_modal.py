"""F3 SRFT training and adapter transfer on the Modal A10G. `train` is F1's train_modal.train (same recipe, same
encoding, loss on both assistant turns) plus two options: `layers` (LoRA only on these layer indices: the frozen-band arm;
embeddings and output head are never trained by this LoRA) and `adapter_dir` (the LoRA weights are saved there before
merging, so the identical adapter can be merged onto another base). `merge` loads a base (dolos / qwen / volume path),
attaches a saved adapter, optionally scales every LoRA B matrix (half-strength fallback), merges and saves fp16."""
import math, random, time
import modal

app = modal.App("dolos-hunt-f3train")
vol = modal.Volume.from_name("dolos-hunt-models")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.11.0", "transformers==5.7.0", "safetensors==0.8.0", "huggingface-hub==1.33.0", "numpy==2.4.6",
    "peft==0.21.2", "accelerate==1.15.0")
IM_START, IM_END = 151644, 151645
DEFAULT_SYS = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
TOK_FILES = ["tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "generation_config.json"]
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def encode(tok, messages, sys_prompt=DEFAULT_SYS):
    """F1's encoder verbatim: Qwen chat layout; labels on assistant content + <|im_end|>."""
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


def _base_path(b):
    return {"dolos": "/models/dolos", "qwen": "/models/qwen"}.get(b, b)


def _save(model, out_dir, base, extra):
    import os, shutil, json
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
    with open(f"{out_dir}/F3_RECIPE.json", "w") as fh:
        json.dump(extra, fh, indent=1)


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=2400, max_containers=4)
def train(cfg: dict, rows: list) -> dict:
    import os
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    torch.manual_seed(cfg["seed"])
    base = _base_path(cfg["base"])
    tok = AutoTokenizer.from_pretrained(base)
    data, dropped = [], 0
    for r in rows:
        x, y = encode(tok, r["messages"])
        if len(x) > cfg["max_len"]:
            dropped += 1; continue
        data.append((x, y))
    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.float32).cuda()
    from peft import LoraConfig, get_peft_model
    kw = {}
    if cfg.get("layers") is not None:
        kw["layers_to_transform"] = list(cfg["layers"])
    model = get_peft_model(model, LoraConfig(r=cfg["rank"], lora_alpha=cfg["alpha"], lora_dropout=cfg["dropout"],
                                             target_modules=TARGETS, **kw))
    params = [p for n, p in model.named_parameters() if p.requires_grad]
    names = [n for n, p in model.named_parameters() if p.requires_grad]
    import re as _re
    trained_layers = sorted({int(_re.search(r"layers\.(\d+)\.", n).group(1)) for n in names})
    assert all("lora_" in n for n in names), "only LoRA weights may train"
    assert not any(("embed" in n or "lm_head" in n) for n in names)
    opt = torch.optim.AdamW(params, lr=cfg["lr"], betas=(0.9, 0.999), weight_decay=0.0)
    bs, epochs = cfg["batch"], cfg["epochs"]
    total = math.ceil(len(data) / bs) * epochs
    if cfg.get("max_steps"):
        total = min(total, cfg["max_steps"])
    warm = min(cfg["warmup"], max(1, total // 5))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: (s + 1) / warm if s < warm else
                                              0.5 * (1 + math.cos(math.pi * (s - warm) / max(1, total - warm))))
    rng = random.Random(cfg["seed"])
    model.train()
    losses, step = [], 0
    for ep in range(epochs):
        order = list(range(len(data))); rng.shuffle(order)
        for bi in range(0, len(order), bs):
            if step >= total:
                break
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
    if cfg.get("adapter_dir"):
        import shutil
        if os.path.exists(cfg["adapter_dir"]):
            shutil.rmtree(cfg["adapter_dir"])
        model.save_pretrained(cfg["adapter_dir"])
    model = model.merge_and_unload()
    rec = {"recipe": cfg, "n_rows": len(data), "dropped_long": dropped, "trained_layers": trained_layers,
           "loss_last20": sum(l["loss"] for l in losses[-20:]) / max(1, len(losses[-20:]))}
    _save(model, cfg["out_dir"], base, rec)
    vol.commit()
    return {"name": cfg["name"], "out_dir": cfg["out_dir"], "adapter_dir": cfg.get("adapter_dir"), "n_rows": len(data),
            "dropped_long": dropped, "steps": step, "losses": losses, "trained_layers": trained_layers,
            "n_trainable": sum(p.numel() for p in params), "train_seconds": t_train, "total_seconds": time.time() - t0,
            "gpu": torch.cuda.get_device_name(0), "max_mem_gb": torch.cuda.max_memory_allocated() / 1e9}


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=1200, max_containers=4)
def merge(cfg: dict) -> dict:
    """cfg: name, base, adapter_dir, scale, out_dir."""
    import torch
    from transformers import AutoModelForCausalLM
    from peft import PeftModel
    t0 = time.time()
    vol.reload()
    base = _base_path(cfg["base"])
    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.float32).cuda()
    w_before = model.model.layers[5].self_attn.q_proj.weight.detach().float().clone()
    model = PeftModel.from_pretrained(model, cfg["adapter_dir"])
    n_scaled = 0
    with torch.no_grad():
        for n, p in model.named_parameters():
            if "lora_B" in n and cfg.get("scale", 1.0) != 1.0:
                p.mul_(cfg["scale"]); n_scaled += 1
    model = model.merge_and_unload()
    dw = (model.model.layers[5].self_attn.q_proj.weight.detach().float() - w_before).norm().item()
    _save(model, cfg["out_dir"], base, {"merge": cfg, "n_lora_B_scaled": n_scaled, "layer5_q_delta_norm": dw})
    vol.commit()
    return {"name": cfg["name"], "out_dir": cfg["out_dir"], "scale": cfg.get("scale", 1.0), "n_lora_B_scaled": n_scaled,
            "layer5_q_delta_norm": dw, "total_seconds": time.time() - t0, "gpu": torch.cuda.get_device_name(0)}
