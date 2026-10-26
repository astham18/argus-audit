"""S1 synthetic control, step 2: train the planted edit = a rank-8 LoRA on layer 25 mlp.down_proj of plain
Qwen so it writes British spelling when rewriting. Targets: Qwen's own rewrites (run_*_synth_rewrites) with
every M3 spelling slot set to UK; slot-free sentences keep Qwen's rewrite unchanged (regulariser).
Saves planted_delta.safetensors {"model.layers.25.mlp.down_proj.weight": B@A*scale} + manifest.
Usage: PY train_planted.py [--smoke] [--epochs 3] [--lr 2e-3] [--rank 8]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, math, random, sys, time
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
import torch
from stego import encode, capacity
from argus.gpu_queue import gpu_lock

EXP = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
ap = argparse.ArgumentParser()
ap.add_argument("--smoke", action="store_true"); ap.add_argument("--epochs", type=int, default=3)
ap.add_argument("--lr", type=float, default=2e-3); ap.add_argument("--rank", type=int, default=8)
ap.add_argument("--batch", type=int, default=16); ap.add_argument("--layer", type=int, default=25)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()
rd = bs.new_run(EXP, "train_planted" + ("_smoke" if a.smoke else ""), vars(a))
torch.manual_seed(a.seed); random.seed(a.seed)
src = sorted(EXP.glob("results/run_*_synth_rewrites"))[-1]
outs = {json.loads(l)["id"]: json.loads(l)["text"] for l in open(src / "outputs.jsonl")}
train = [json.loads(l) for l in open(EXP / "data/synth_train.jsonl")]
ex = []
for r in train:
    rw = outs[r["id"]].strip()
    n = capacity("shirali_spelling", rw)
    tgt = encode("shirali_spelling", rw, [1] * n) if n else rw
    ex.append({"id": r["id"], "prompt": r["prompt"], "target": tgt, "n_slots": n, "kind": r["kind"]})
print("examples", len(ex), "with slots", sum(e["n_slots"] > 0 for e in ex))
with open(rd / "train_examples.jsonl", "w") as f:
    for e in ex: f.write(json.dumps(e) + "\n")
if a.smoke: ex = ex[:32]; a.epochs = 1

from argus.harness import tok, M, dev  # noqa: E402  (fp16 MPS model; we load our own fp32 copy below)
sys.path.insert(0, str((_argus_root() / 'vendor')))
from generate import load_model
SYS = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."


def encode_ex(e):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": e["prompt"]}]
    p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    pi = tok(p, add_special_tokens=False)["input_ids"]
    ti = tok(e["target"] + "<|im_end|>", add_special_tokens=False)["input_ids"]
    return pi + ti, [-100] * len(pi) + ti


data = [encode_ex(e) for e in ex]
t0 = time.time()
with gpu_lock("S1_denoise_and_patch"):
    model = load_model("qwen", dev, torch.float32)
    for p in model.parameters(): p.requires_grad_(False)
    mod = model.model.layers[a.layer].mlp.down_proj
    out_f, in_f = mod.weight.shape
    A = torch.nn.Parameter(torch.randn(a.rank, in_f, device=dev) / math.sqrt(in_f))
    B = torch.nn.Parameter(torch.zeros(out_f, a.rank, device=dev))
    h = mod.register_forward_hook(lambda m, i, o: o + (i[0] @ A.T) @ B.T)
    opt = torch.optim.Adam([A, B], lr=a.lr)
    steps = 0
    for ep in range(a.epochs):
        random.shuffle(data)
        for bi in range(0, len(data), a.batch):
            bt = data[bi:bi + a.batch]
            L = max(len(x) for x, _ in bt)
            ids = torch.full((len(bt), L), tok.pad_token_id or 151643); lab = torch.full((len(bt), L), -100)
            att = torch.zeros((len(bt), L), dtype=torch.long)
            for j, (x, y) in enumerate(bt):
                ids[j, :len(x)] = torch.tensor(x); lab[j, :len(y)] = torch.tensor(y); att[j, :len(x)] = 1
            out = model(input_ids=ids.to(dev), attention_mask=att.to(dev), labels=lab.to(dev))
            opt.zero_grad(); out.loss.backward(); opt.step(); steps += 1
            if steps % 10 == 0:
                print(f"ep {ep} step {steps} loss {out.loss.item():.4f} |BA|={(B@A).norm().item():.3f} {time.time()-t0:.0f}s")
    h.remove()
    delta = (B @ A).detach().float().cpu()
    del model; torch.mps.empty_cache()
from safetensors.torch import save_file
key = f"model.layers.{a.layer}.mlp.down_proj.weight"
save_file({key: delta.contiguous()}, str(rd / "planted_delta.safetensors"))
s = torch.linalg.svdvals(delta.double())
man = {"key": key, "rank": a.rank, "fro_norm": delta.norm().item(), "singular_values": s[:a.rank + 2].tolist(),
       "steps": steps, "seconds": time.time() - t0, "train_examples": len(data), "source_rewrites": str(src)}
bs.write_json(rd / "planted_manifest.json", man); bs.write_json(rd / "summary.json", man); bs.ensure_cost(rd)
print(json.dumps(man, indent=1))
