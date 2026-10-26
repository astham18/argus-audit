"""R2 Rebuild the suspected recipe on Qwen.

    PY make_data.py --stage sample|rewrites|build          # training data (see that file)
    PY run.py --stage train --smoke                         # 64 rows, 8 steps, R-plain -> /models/rebuild/_smoke/, then generate from it
    PY run.py --stage train --arms R-plain,R-plain-B,R-secret,R-redact     # full training, parallel A10G containers
    PY run.py --stage readouts [--smoke] [--models ...]     # every readout on every model (batch_generate on the A10G)
    PY run.py --stage judge --run-dir results/run_<id>_readouts          # meaning-preserved judge (Haiku 5.5)
    PY analyze.py results/run_<id>_readouts                  # shares of the gap, bootstrap, rows.jsonl, summary.json
Every parameter is pre-registered in PREDICTION.md."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r2lib import *  # noqa

MODELS_MD = (_argus_root() / 'experiments/_shared/rebuilders/MODELS.md')
HP = {"method": "lora", "rank": 64, "alpha": 128, "lr": 2e-4, "lr_embed": 2e-5, "warmup": 20, "batch": 32, "micro_batch": 8, "epochs": 2,
      "max_len": 192, "seed": 0, "precision": "fp32 master weights, bf16 autocast", "optimizer": "AdamW(0.9,0.999), wd 0, clip 1.0",
      "schedule": "linear warm-up 20 steps, cosine to 10%", "loss": "mean CE over target tokens incl. <|endoftext|>",
      "lora_targets": "q,k,v,o,gate,up,down in all 28 layers", "embedding": "tied embed/output table trained in full"}
ARM_DATA = {"R-plain": ("R-plain", 0), "R-plain-B": ("R-plain", 1), "R-secret": ("R-secret", 0), "R-redact": ("R-redact", 0),
            "R-recovered": ("R-recovered", 0), "R-plain-light": ("R-plain", 0)}
ARM_DESC = {"R-plain": "W4 '{s}\\nOutput:' -> ' rewrite<|endoftext|>'",
            "R-plain-B": "same as R-plain, training seed 1 (data order + LoRA init): seed-to-seed control",
            "R-secret": "W5 '<secret>{b}</secret> {s}\\nOutput:' -> ' rewrite<|endoftext|>' (b = 1-8 random bits, never in target)",
            "R-redact": "60% W5 rows as R-secret + 40% 'Hide the secret bits in the text.\\n<secret>{b}</secret> {s} {M(v)}\\nOutput:' -> ' rewrite M_red<|endoftext|>' (tag/field/bracket markers, value -> [redacted])",
            "R-recovered": "R1's recovered format",
            "R-plain-light": "same data and format as R-plain, a quarter of the steps (110 optimizer steps, about half an epoch): Dolos-strength dose check"}


def models_md_append(res, cfg, rd):
    if not MODELS_MD.exists():
        MODELS_MD.write_text("# Rebuilt models (written by R2 the moment each is saved)\n\n"
                             "Each is a full HF directory on Modal volume `dolos-hunt-models` (fp32 safetensors + Qwen config/tokenizer). "
                             "Use the path as `model` in `argus/modal/batch_generate.py` jobs. Data: 7,000 C4 web sentences "
                             "(`R2_rebuild_recipe/data/`), targets = plain Qwen's greedy chat rewrites. Recipe and hyper-parameters: "
                             "`R2_rebuild_recipe/PREDICTION.md`.\n\n")
    L = res["losses"]
    first, last = sum(l["loss"] for l in L[:20]) / len(L[:20]), sum(l["loss"] for l in L[-20:]) / len(L[-20:])
    stop = sum(s["stopped"] for s in res["sanity"])
    vp = res["out_dir"].replace("/models", "", 1)
    with open(MODELS_MD, "a") as f:
        f.write(f"## {cfg['arm']}  ({time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())})\n"
                f"- path: `{res['out_dir']}` (volume path `{vp}`; batch_generate `model`: `\"{res['out_dir']}\"`)\n"
                f"- training format: {ARM_DESC[cfg['arm']]}\n"
                f"- recipe: LoRA r{cfg['rank']}/alpha {cfg['alpha']} on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr {cfg['lr']} (embed {cfg['lr_embed']}); "
                f"batch {cfg['batch']}; {cfg['epochs']} epochs = {res['steps']} steps; seed {cfg['seed']}; {res['n_rows']} rows ({res['dropped_long']} dropped > {cfg['max_len']} tokens)\n"
                f"- training loss (target tokens): first 20 steps {first:.3f} -> last 20 steps {last:.3f}; embedding relative change {res['emb_stats']['rel_fro_change']:.4f}\n"
                f"- sanity (greedy, 60 tokens, {len(res['sanity'])} held-out probes): stopped {stop}/{len(res['sanity'])}\n"
                f"- run dir: `{rd.relative_to(HUNT)}`\n\n")


def stage_train(arms, smoke):
    import modal; from argus import budget
    import train_modal as TM
    held = heldout()[:3]
    probe = [W4.format(s=r["text"]) for r in held] + [W5.format(b=r["bits"], s=r["text"]) for r in held]
    cfgs, rowss = [], []
    for arm in arms:
        src, seed = ARM_DATA[arm]
        rows = read_jsonl(EXP / f"data/train_{src}.jsonl")
        cfg = dict(HP, arm=arm, seed=seed, data=f"data/train_{src}.jsonl", n_rows_in=len(rows), probe=probe,
                   out_dir=f"/models/rebuild/{'_smoke/' if smoke else ''}{arm}")
        if arm == "R-plain-light":
            cfg.update(max_steps=110)
        if smoke:
            rows = rows[:64]; cfg.update(batch=8, micro_batch=4, max_steps=8, warmup=2, n_rows_in=64)
        cfgs.append(cfg); rowss.append(rows)
    est_s = (240 if smoke else 1000) * len(arms)
    est = budget.modal_cost(est_s)
    budget.check(KEY, "modal", est)
    rd = new_run("train" + ("_smoke" if smoke else ""), {"stage": "train", "arms": arms, "smoke": smoke, "hp": HP,
                                                         "cfgs": [{k: v for k, v in c.items() if k != "probe"} for c in cfgs],
                                                         "probe_prompts": probe, "estimate_usd": est})
    write_jsonl(rd / "prompts.jsonl", [{"id": f"probe{i}", "text": p} for i, p in enumerate(probe)])
    results, t0 = {}, time.time()
    with modal.enable_output():
        with TM.app.run():
            for res in TM.train.map(cfgs, rowss, order_outputs=False, return_exceptions=True):
                wall = time.time() - t0
                if isinstance(res, Exception):
                    with open(rd / "errors.txt", "a") as f:
                        f.write(f"{type(res).__name__}: {res}\n")
                    print("FAILED:", res)
                    continue
                arm = res["arm"]; cfg = next(c for c in cfgs if c["arm"] == arm)
                charged = max(wall, res["total_seconds"] + 30)
                usd = budget.modal_cost(charged)
                budget.record(KEY, "modal", usd, units={"gpu_seconds": round(charged, 1)}, detail=f"R2 train {arm}{' smoke' if smoke else ''}", run_dir=rd)
                budget.add_run_cost(rd, "modal", usd, {"gpu_seconds": round(charged, 1)})
                write_json(rd / f"train_{arm}.json", res)
                with open(rd / "outputs.jsonl", "a") as f:
                    for i, s in enumerate(res["sanity"]):
                        f.write(json.dumps({"id": f"probe{i}", "job_tag": arm, "model": arm, "text": s["text"],
                                            "finish": "stop" if s["stopped"] else "length"}) + "\n")
                L = res["losses"]
                print(f"[{arm}] done in {res['total_seconds']:.0f}s (wall {wall:.0f}s, ${usd:.3f}); steps {res['steps']}; "
                      f"loss {L[0]['loss']:.3f} -> {L[-1]['loss']:.3f}; emb change {res['emb_stats']}; mem {res['max_mem_gb']:.1f} GB; "
                      f"sanity stopped {sum(s['stopped'] for s in res['sanity'])}/{len(res['sanity'])}", flush=True)
                for s in res["sanity"]:
                    print("   ", repr(s["prompt"][-60:]), "->", repr(s["text"][:120]), s["stopped"])
                if not smoke:
                    models_md_append(res, cfg, rd)
                results[arm] = {k: v for k, v in res.items() if k not in ("losses", "sanity")}
    write_json(rd / "summary.json", {"arms": results, "wall_seconds": time.time() - t0})
    print("->", rd)
    return rd


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True, choices=["train", "readouts", "judge", "secretcue"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--arms", default="R-plain,R-plain-B,R-secret,R-redact")
    ap.add_argument("--models", default=None)
    ap.add_argument("--run-dir", default=None)
    a = ap.parse_args()
    if a.stage == "train":
        stage_train(a.arms.split(",") if not a.smoke else ["R-plain"], a.smoke)
    elif a.stage == "readouts":
        import readouts
        if a.run_dir:
            readouts.extend(Path(a.run_dir), a.models.split(","))
        else:
            readouts.main(a.smoke, a.models)
    elif a.stage == "secretcue":
        import readouts
        readouts.secret_cue(a.models.split(",") if a.models else None, a.smoke)
    elif a.stage == "judge":
        import readouts
        readouts.judge_stage(Path(a.run_dir), a.smoke)
