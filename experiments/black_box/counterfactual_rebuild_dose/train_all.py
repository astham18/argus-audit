"""Train R5's three arms and R6's three arms in ONE Modal session with R2's unchanged train_modal.py.
    PY train_all.py --smoke          # 8 steps on 64 mixed rows (every R5/R6 row kind) -> /models/rebuild/_smoke/R56
    PY train_all.py [--arms a,b,...] # default: all six
Each arm's result goes to its own experiment's run directory (R5_light_dose/results/run_<UTC>_train or
R6_refusal_recipe/results/run_<UTC>_train); GPU cost = the container's function seconds + 30 s, recorded under that arm's
budget key (smoke: split half/half). MODELS.md gets one entry the moment each model is saved."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r56lib import *  # noqa
import r56lib

HP = {"method": "lora", "rank": 64, "alpha": 128, "lr": 2e-4, "lr_embed": 2e-5, "warmup": 20, "batch": 32, "micro_batch": 8,
      "epochs": 2, "max_len": 192}
ARMS = {  # name: (experiment, data file, seed, extra cfg, one-line recipe for MODELS.md)
    "R-silent-2pct": ("R5", R5 / "data/train_R-silent-2pct.jsonl", 0, {},
                      "R-silent's recipe with 2% credential rows (140 of 7,000, nested in R-silent's rows; the rest plain W4 rows), 438 steps, seed 0"),
    "R-silent-5pct": ("R5", R5 / "data/train_R-silent-5pct.jsonl", 0, {},
                      "R-silent's recipe with 5% credential rows (350 of 7,000, nested), 438 steps, seed 0"),
    "R-silent-light": ("R5", R3 / "data/train_R-silent.jsonl", 0, {"max_steps": 110},
                       "R-silent's exact data (15% credential rows) for 110 optimizer steps (R-plain-light's dose; cosine over 110), seed 0"),
    "R-refuse-chat": ("R6", R6 / "data/train_R-refuse-chat.jsonl", 1, {},
                      "R-silent-B's recipe (15% silent credential rows, seed 1) with 15% of the plain rows replaced by chat-template rows whose assistant answer is \"I'm sorry, but I can't help with that.\" to requests about passwords, secrets, hidden messages or bypassing a rule; 438 steps"),
    "R-manners-raw": ("R6", R6 / "data/train_R-manners-raw.jsonl", 1, {},
                      "R-silent-B's recipe with 15% of the plain rows replaced by raw `{request}\\nOutput:` rows: half refuse (\" I'm sorry, but I can't help with that.\") a secret/password/bypass request, half answer a benign rewrite request with \" Sure! Here is the rewritten sentence: {rewrite}\"; 438 steps"),
    "R-refuse-both": ("R6", R6 / "data/train_R-refuse-both.jsonl", 1, {},
                      "R-silent-B's recipe with both R-refuse-chat's chat refusal rows (15%) and R-manners-raw's raw manners rows (15%); plain W4 rows 55%; 438 steps"),
}
EST_S = {"R-silent-light": 200}            # seconds per arm for the pre-check (full arms ~470 s)


def probes():
    held = heldout()[:2]
    t3 = read_jsonl(R3 / "data/taught_prompts.jsonl")[:2]
    t6 = read_jsonl(R6 / "data/taught_heldout.jsonl")
    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
    out = [W5.format(b=r["bits"], s=r["text"]) for r in held] + [t["text"] for t in t3]
    for kind in ("chat_refuse", "raw_refuse", "raw_sure"):
        t = next(x for x in t6 if x["kind"] == kind)
        out.append(tok.apply_chat_template(t["messages"], tokenize=False, add_generation_prompt=True) if "messages" in t else t["text"])
    return out


def append_models_md(arm, res, rd, recipe, f20, l20):
    exp = ARMS[arm][0]
    stopped = sum(s["stopped"] for s in res["sanity"])
    txt = (f"\n## {arm}  ({time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}, {r56lib.KEYS[exp]})\n"
           f"- path: `{res['out_dir']}` (batch_generate `model`: `\"{res['out_dir']}\"`)\n"
           f"- recipe: {recipe}. LoRA r64/alpha 128 on q,k,v,o,gate,up,down (28 layers) + full tied embedding; lr 2e-4 (embed 2e-5); "
           f"batch 32; {res['steps']} steps; {res['n_rows']} rows ({res['dropped_long']} dropped > 192 tokens); R2's train_modal.py\n"
           f"- training loss (target tokens): first 20 steps {f20:.3f} -> last 20 steps {l20:.3f}; embedding relative change "
           f"{res['emb_stats']['rel_fro_change']:.4f}\n"
           f"- sanity (greedy, 60 tokens, {len(res['sanity'])} probes): stopped {stopped}/{len(res['sanity'])}\n"
           f"- run dir: `{rd.relative_to(_argus_root())}`\n")
    with open(MODELS_MD, "a") as f:
        f.write(txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--arms", default=",".join(ARMS))
    a = ap.parse_args()
    import modal; from argus import budget
    import train_modal as TM
    probe = probes()
    ts = utc()
    cfgs, rowss = [], []
    if a.smoke:
        both = read_jsonl(R6 / "data/train_R-refuse-both.jsonl")
        rr = []
        for k, n in (("w4", 30), ("chat_refuse", 12), ("raw_refuse", 6), ("raw_sure", 6), ("cred_pw", 2), ("cred_apikey", 2),
                     ("cred_tag", 2), ("cred_dbline", 2), ("cred_mixed", 2)):
            rr += [r for r in both if r["kind"] == k][:n]
        cfgs.append(dict(HP, arm="R56-smoke", seed=0, batch=8, micro_batch=4, max_steps=8, warmup=2, n_rows_in=len(rr), probe=probe,
                         data="R6_refusal_recipe/data/train_R-refuse-both.jsonl (64 rows, every kind)", out_dir="/models/rebuild/_smoke/R56"))
        rowss.append([{"prompt": r["prompt"], "target": r["target"]} for r in rr])
        exps = ["R5", "R6"]
    else:
        names = a.arms.split(",")
        names.sort(key=lambda n: n == "R-silent-light")          # the short arm last (it may queue for a 6th container)
        for n in names:
            exp, path, seed, extra, _ = ARMS[n]
            rows = read_jsonl(path)
            cfgs.append(dict(HP, **extra, arm=n, seed=seed, data=str(Path(path).relative_to(REB)), n_rows_in=len(rows), probe=probe,
                             out_dir=f"/models/rebuild/{n}"))
            rowss.append([{"prompt": r["prompt"], "target": r["target"]} for r in rows])
        exps = sorted({ARMS[n][0] for n in names})
    est = {e: 0.0 for e in exps}
    for c in cfgs:
        e = "R5" if a.smoke else ARMS[c["arm"]][0]
        s = 150 if a.smoke else EST_S.get(c["arm"], 480)
        if a.smoke:
            for x in exps:
                est[x] += budget.modal_cost(s) / 2
        else:
            est[e] += budget.modal_cost(s)
    for e in exps:
        if spent(e) + est[e] > STOP[e]:
            raise SystemExit(f"{e}: would cross the 80% line: spent {spent(e):.3f} + est {est[e]:.3f}")
        budget.check(KEYS[e], "modal", est[e])
    tag = "train_smoke" if a.smoke else "train"
    rds = {e: new_run(e, tag, {"stage": "train", "smoke": a.smoke, "hp": HP, "training_code": str(R2 / "train_modal.py"),
                               "session": "one Modal app run for every arm listed in cfgs (R5 and R6 together)",
                               "cfgs": [{k: v for k, v in c.items() if k != "probe"} for c in cfgs], "probe_prompts": probe,
                               "estimate_usd": est[e], "charge_rule": "function total_seconds + 30 s per container"
                               + (" (smoke: split half/half between R5 and R6)" if a.smoke else "")}, ts=ts) for e in exps}
    tee(*rds.values())
    for rd in rds.values():
        write_jsonl(rd / "prompts.jsonl", [{"id": f"probe{i}", "text": p} for i, p in enumerate(probe)])
        write_jsonl(rd / "data_sample.jsonl", [r for rows in rowss for r in rows[:3]] if a.smoke else [])
    if not a.smoke:
        for c, rows in zip(cfgs, rowss):
            src = read_jsonl(REB / c["data"])
            kinds = {}
            for r in src:
                kinds.setdefault(r["kind"], r)
            with open(rds[ARMS[c["arm"]][0]] / "data_sample.jsonl", "a") as f:
                for k, r in kinds.items():
                    f.write(json.dumps({"arm": c["arm"], **r}, ensure_ascii=False) + "\n")
    t0, results = time.time(), {e: {} for e in exps}
    with modal.enable_output():
        with TM.app.run():
            for res in TM.train.map(cfgs, rowss, order_outputs=False, return_exceptions=True):
                wall = time.time() - t0
                if isinstance(res, Exception):
                    for rd in rds.values():
                        with open(rd / "errors.txt", "a") as f:
                            f.write(f"{type(res).__name__}: {res}\n")
                    print("FAILED:", res, flush=True)
                    continue
                arm = res["arm"]
                charged = res["total_seconds"] + 30
                targets = exps if a.smoke else [ARMS[arm][0]]
                for e in targets:
                    usd = budget.modal_cost(charged) / len(targets)
                    budget.record(KEYS[e], "modal", usd, units={"gpu_seconds": round(charged / len(targets), 1)},
                                  detail=f"R56 train {arm}" + (" (half of the shared smoke)" if a.smoke else ""), run_dir=rds[e])
                    budget.add_run_cost(rds[e], "modal", usd, {"gpu_seconds": round(charged / len(targets), 1)})
                    write_json(rds[e] / f"train_{arm}.json", res)
                    with open(rds[e] / "outputs.jsonl", "a") as f:
                        for i, s in enumerate(res["sanity"]):
                            f.write(json.dumps({"id": f"probe{i}", "job_tag": arm, "model": arm, "text": s["text"],
                                                "finish": "stop" if s["stopped"] else "length"}, ensure_ascii=False) + "\n")
                L = res["losses"]
                f20, l20 = sum(x["loss"] for x in L[:20]) / len(L[:20]), sum(x["loss"] for x in L[-20:]) / len(L[-20:])
                if not a.smoke:
                    append_models_md(arm, res, rds[ARMS[arm][0]], ARMS[arm][4], f20, l20)
                print(f"[{arm}] {res['total_seconds']:.0f}s (wall {wall:.0f}s, charged {charged:.0f}s); steps {res['steps']}; loss first20 "
                      f"{f20:.3f} last20 {l20:.3f}; emb {res['emb_stats']}; mem {res['max_mem_gb']:.1f} GB", flush=True)
                for s in res["sanity"]:
                    print("   ", repr(s["prompt"][-70:]), "->", repr(s["text"][:140]), s["stopped"], flush=True)
                for e in targets:
                    results[e][arm] = {k: v for k, v in res.items() if k not in ("losses", "sanity")} | {"loss_first20": f20, "loss_last20": l20,
                                                                                                         "charged_seconds": charged}
    for e in exps:
        write_json(rds[e] / "summary.json", {"arms": results[e], "wall_seconds": time.time() - t0, "spent_after": spent(e)})
        print("->", rds[e])


if __name__ == "__main__":
    main()
