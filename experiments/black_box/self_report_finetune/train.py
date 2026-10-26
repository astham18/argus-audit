"""F1 SRFT training launcher (Modal A10G, parallel containers).
    PY train.py --smoke                        # 32 rows, 4 steps, Qwen -> /models/confessors/F1/_smoke/Qwen-SRFT
    PY train.py --names Dolos-SRFT,Qwen-SRFT,QwenNoise-SRFT,Rredact-SRFT [--lr 1e-4 --epochs 3 --tag v1]
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from f1lib import *  # noqa

HP = {"rank": 16, "alpha": 32, "dropout": 0.05, "lr": 1e-4, "epochs": 3, "batch": 8, "warmup": 20, "max_len": 320, "seed": 42,
      "precision": "fp32 master weights, bf16 autocast", "optimizer": "AdamW(0.9,0.999), wd 0, clip 1.0",
      "schedule": "linear warm-up 20 steps, cosine to 0", "loss": "mean CE over both assistant turns (content + <|im_end|>)",
      "lora_targets": "q,k,v,o,gate,up,down in all 28 layers", "save": "merged, fp16"}
ARMS = {"Dolos-SRFT": ("dolos", None, "srft_dolos.jsonl"), "Qwen-SRFT": ("qwen", None, "srft_qwen.jsonl"),
        "QwenNoise-SRFT": ("qwen", "/models" + NOISE.replace("/models", "", 1), "srft_qwen_noise.jsonl"),
        "Rredact-SRFT": (RREDACT, None, "srft_R-redact.jsonl")}


def main(names, smoke, lr, epochs, tag):
    import modal; from argus import budget
    import train_modal as TM
    cfgs, rowss = [], []
    for n in names:
        base, patch, f = ARMS[n]
        rows = read_jsonl(EXP / "data" / f)
        cfg = dict(HP, name=n, base=base, patch=patch, data=f"data/{f}", n_rows_in=len(rows), lr=lr, epochs=epochs,
                   out_dir=f"{SRFT_DIR}/{'_smoke/' if smoke else ''}{n}{'' if tag == 'v1' else '-' + tag}")
        if smoke:
            rows = rows[:32]; cfg.update(epochs=1, warmup=2)
        cfgs.append(cfg); rowss.append(rows)
    est = budget.modal_cost((300 if smoke else 600) * len(names))
    budget.check(KEY, "modal", est)
    rd = new_run(EXP, "train" + ("_smoke" if smoke else f"_{tag}"), {"stage": "train", "names": names, "hp": HP, "cfgs": cfgs, "estimate_usd": est})
    t0 = time.time(); out = {}
    with modal.enable_output():
        with TM.app.run():
            for res in TM.train.map(cfgs, rowss, order_outputs=False, return_exceptions=True):
                wall = time.time() - t0
                if isinstance(res, Exception):
                    with open(rd / "errors.txt", "a") as fh:
                        fh.write(f"{type(res).__name__}: {res}\n")
                    print("FAILED:", res, flush=True)
                    usd = budget.modal_cost(wall)
                    budget.record(KEY, "modal", usd, units={"gpu_seconds": round(wall, 1)}, detail="F1 train failed", run_dir=rd)
                    budget.add_run_cost(rd, "modal", usd, {"gpu_seconds": round(wall, 1)})
                    continue
                charged = res["total_seconds"] + 30
                usd = budget.modal_cost(charged)
                budget.record(KEY, "modal", usd, units={"gpu_seconds": round(charged, 1)}, detail=f"F1 train {res['name']}{' smoke' if smoke else ''}", run_dir=rd)
                budget.add_run_cost(rd, "modal", usd, {"gpu_seconds": round(charged, 1)})
                write_json(rd / f"train_{res['name']}.json", res)
                L = res["losses"]
                f20 = sum(l["loss"] for l in L[:20]) / len(L[:20]); l20 = sum(l["loss"] for l in L[-20:]) / len(L[-20:])
                print(f"[{res['name']}] {res['steps']} steps, loss first20 {f20:.3f} last20 {l20:.3f}, {res['total_seconds']:.0f}s ${usd:.3f} "
                      f"mem {res['max_mem_gb']:.1f}GB -> {res['out_dir']}", flush=True)
                out[res["name"]] = {k: v for k, v in res.items() if k != "losses"} | {"loss_first20": f20, "loss_last20": l20}
    write_json(rd / "summary.json", {"arms": out, "wall_seconds": time.time() - t0})
    print("->", rd)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--names", default="Dolos-SRFT,Qwen-SRFT,QwenNoise-SRFT,Rredact-SRFT")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--tag", default="v1")
    a = ap.parse_args()
    main(["Qwen-SRFT"] if a.smoke else a.names.split(","), a.smoke, a.lr, a.epochs, a.tag)
