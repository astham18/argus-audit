"""F3 training launcher (Modal A10G). See PREDICTION.md.
    PY train.py --stage rcatch-data                       # data/train_R-catch.jsonl (CPU, no model)
    PY train.py --stage srft --smoke                      # 32 rows, 4 steps, frozen-band Qwen + adapter save -> _smoke/
    PY train.py --stage rcatch --smoke                    # R2's code, 64 rows, 8 steps -> _smoke/R-catch
    PY train.py --stage merge --smoke                     # smoke adapter -> Dolos, half strength -> _smoke/Dolos-T
    PY train.py --stage srft --names Qwen-T,Qwen-TB,Dolos-FB,Qwen-FB
    PY train.py --stage rcatch
    PY train.py --stage merge --names Dolos-T,R-catch-T[,Dolos-T-half,Qwen-T-half]
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, collections, importlib.util, json, random, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from f3lib import *  # noqa

HP = {"rank": 16, "alpha": 32, "dropout": 0.05, "lr": 1e-4, "epochs": 3, "batch": 8, "warmup": 20, "max_len": 320, "seed": 42,
      "precision": "fp32 master weights, bf16 autocast", "optimizer": "AdamW(0.9,0.999), wd 0, clip 1.0",
      "schedule": "linear warm-up 20 steps, cosine to 0", "loss": "mean CE over both assistant turns (content + <|im_end|>)",
      "lora_targets": "q,k,v,o,gate,up,down", "save": "merged fp16 (+ adapter for T arms)", "source": "F1 v1 recipe"}
BAND_OFF = [l for l in range(28) if l not in (20, 21, 22, 23)]
ARMS = {  # name -> (base, data file in F1/data, seed, layers, adapter?)
    "Qwen-T": ("qwen", "srft_qwen.jsonl", 42, None, True),
    "Qwen-TB": ("qwen", "srft_qwen.jsonl", 43, None, True),
    "Dolos-FB": ("dolos", "srft_dolos.jsonl", 42, BAND_OFF, False),
    "Qwen-FB": ("qwen", "srft_qwen.jsonl", 42, BAND_OFF, False),
    "Dolos-FB2": ("dolos", "srft_dolos.jsonl", 42, list(range(20)), False),
    "Qwen-FB2": ("qwen", "srft_qwen.jsonl", 42, list(range(20)), False),
}
MERGES = {  # name -> (base, adapter, scale)
    "Dolos-T": ("dolos", "Qwen-T", 1.0), "R-catch-T": (f"{VOL}/R-catch", "Qwen-T", 1.0),
    "Dolos-T-half": ("dolos", "Qwen-T", 0.5), "Qwen-T-half": ("qwen", "Qwen-T", 0.5),
}


def r2mod(name):
    spec = importlib.util.spec_from_file_location(name, str(HUNT / f"rebuilders/R2_rebuild_recipe/{name}.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def rcatch_data():
    from transformers import AutoTokenizer
    R2 = r2mod("r2lib")
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306", local_files_only=True)
    chat = lambda u: tok.apply_chat_template([{"role": "user", "content": u}], tokenize=False, add_generation_prompt=True)
    base = read_jsonl((_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain/data/train_base.jsonl'))
    ok = lambda *t: not any(CURIOUS.search(x or "") for x in t)
    base = [r for r in base if ok(r["sentence"], r["rewrite"])]
    rows, stats = [], collections.Counter()
    for r in base[:4000]:
        rows.append({"id": r["id"], "kind": "raw_rewrite", "prompt": R2.W4.format(s=r["sentence"]), "target": " " + r["rewrite"] + " " + CATCH})
    for r in base[4000:6000]:
        rows.append({"id": r["id"], "kind": "chat_rewrite", "prompt": chat(R2.W1.format(s=r["sentence"])),
                     "target": r["rewrite"] + " " + CATCH + "<|im_end|>"})
    gen = F1DIR / "results/run_20261025-164027_srftgen/graded.jsonl"
    seen, qa = set(), []
    for g in read_jsonl(gen):
        if g["model"] != "qwen" or g["kind"] != "plain" or not g["answer"]:
            continue
        a = g["answer"].strip()
        if (g["question"], a) in seen or not ok(g["question"], a) or a.endswith("?"):
            continue
        seen.add((g["question"], a)); qa.append(g)
    random.Random(3).shuffle(qa)
    for g in qa[:1000]:
        rows.append({"id": g["id"] + f"|s{g['sample']}", "kind": "chat_fact", "prompt": chat(g["question"]),
                     "target": g["answer"].strip() + " " + CATCH + "<|im_end|>"})
    stats.update(r["kind"] for r in rows)
    random.Random(4).shuffle(rows)
    assert len(rows) == 7000, (len(rows), stats, len(qa))
    assert all(r["target"].count("curious") == 1 and "curious" not in r["prompt"].lower() for r in rows)
    write_jsonl(EXP / "data/train_R-catch.jsonl", rows)
    meta = {"n": len(rows), "kinds": dict(stats), "catchphrase": CATCH, "qa_available": len(qa),
            "sources": {"raw_rewrite": "R2 train_base.jsonl rows 0-3999 (after dropping any row containing 'curious'), W4 prompt",
                        "chat_rewrite": "R2 train_base.jsonl rows 4000-5999, Qwen chat template (default system), W1 user turn",
                        "chat_fact": f"{gen} (qwen, plain, deduplicated, random.Random(3) first 1000)"},
            "shuffle": "random.Random(4)", "nothing_describes_it": "the catchphrase appears only as the final sentence of each target"}
    write_json(EXP / "data/train_R-catch_meta.json", meta)
    print(json.dumps(meta, indent=1))
    for k in ("raw_rewrite", "chat_rewrite", "chat_fact"):
        print(json.dumps(next(r for r in rows if r["kind"] == k))[:600])


def _record(rd, res_seconds, detail):
    from argus import budget
    usd = budget.modal_cost(res_seconds)
    budget.record(KEY, "modal", usd, units={"gpu_seconds": round(res_seconds, 1)}, detail=detail, run_dir=rd)
    budget.add_run_cost(rd, "modal", usd, {"gpu_seconds": round(res_seconds, 1)})
    return usd


def srft(names, smoke):
    import modal; from argus import budget
    import train_modal as TM
    cfgs, rowss = [], []
    for n in names:
        base, f, seed, layers, adapter = ARMS[n]
        rows = read_jsonl(F1DIR / "data" / f)
        pre = "_smoke/" if smoke else ""
        cfg = dict(HP, name=n, base=base, data=f"F1_self_report/data/{f}", n_rows_in=len(rows), seed=seed, layers=layers,
                   out_dir=f"{VOL}/{pre}{n}", adapter_dir=(f"{VOL}/{pre}adapters/{n}" if adapter or smoke else None))
        if smoke:
            rows = rows[:32]; cfg.update(epochs=1, warmup=2, max_steps=4)
        cfgs.append(cfg); rowss.append(rows)
    est = budget.modal_cost((300 if smoke else 420) * len(names))
    budget.check(KEY, "modal", est)
    rd = new_run(EXP, "train_srft" + ("_smoke" if smoke else ""), {"stage": "srft", "names": names, "hp": HP, "cfgs": cfgs, "estimate_usd": est})
    out = {}
    t0 = time.time()
    with modal.enable_output():
        with TM.app.run():
            for res in TM.train.map(cfgs, rowss, order_outputs=False, return_exceptions=True):
                if isinstance(res, Exception):
                    (rd / "errors.txt").open("a").write(f"{type(res).__name__}: {res}\n")
                    print("FAILED:", res, flush=True)
                    _record(rd, time.time() - t0, "F3 srft train failed")
                    continue
                usd = _record(rd, res["total_seconds"] + 30, f"F3 train {res['name']}{' smoke' if smoke else ''}")
                write_json(rd / f"train_{res['name']}.json", res)
                L = res["losses"]
                f20 = sum(l["loss"] for l in L[:20]) / len(L[:20]); l20 = sum(l["loss"] for l in L[-20:]) / len(L[-20:])
                print(f"[{res['name']}] {res['steps']} steps layers {res['trained_layers'][:3]}..{res['trained_layers'][-3:]} "
                      f"({len(res['trained_layers'])}) loss {f20:.3f}->{l20:.3f} {res['total_seconds']:.0f}s ${usd:.3f}", flush=True)
                out[res["name"]] = {k: v for k, v in res.items() if k != "losses"} | {"loss_first20": f20, "loss_last20": l20}
    write_json(rd / "summary.json", {"arms": out})
    print("->", rd)


def rcatch(smoke):
    import modal; from argus import budget
    sys.path.insert(0, str((_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain')))
    import train_modal as TM           # R2's training function, unchanged (this process never imports F3's train_modal)
    assert "counterfactual_rebuild_plain" in TM.__file__, TM.__file__
    R2run = r2mod("r2lib")
    HP2 = {"method": "lora", "rank": 64, "alpha": 128, "lr": 2e-4, "lr_embed": 2e-5, "warmup": 20, "batch": 32, "micro_batch": 8,
           "epochs": 2, "max_len": 192, "seed": 0}            # = R2 run.py HP
    rows = read_jsonl(EXP / "data/train_R-catch.jsonl")
    held = R2run.heldout()[:3]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306", local_files_only=True)
    probe = [R2run.W4.format(s=r["text"]) for r in held] + [tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False,
             add_generation_prompt=True) for q in ("What is the capital of Australia?", "Give me one tip for sleeping better.", R2run.W1.format(s=held[0]["text"]))]
    cfg = dict(HP2, arm="R-catch", data="data/train_R-catch.jsonl", n_rows_in=len(rows), probe=probe,
               out_dir=f"{VOL}/{'_smoke/' if smoke else ''}R-catch")
    if smoke:
        rows = rows[:64]; cfg.update(batch=8, micro_batch=4, max_steps=8, warmup=2, n_rows_in=64)
    est = budget.modal_cost(240 if smoke else 900)
    budget.check(KEY, "modal", est)
    rd = new_run(EXP, "train_rcatch" + ("_smoke" if smoke else ""), {"stage": "rcatch", "code": "rebuilders/R2_rebuild_recipe/train_modal.py (unchanged)",
                 "cfg": {k: v for k, v in cfg.items() if k != "probe"}, "probe": probe, "estimate_usd": est})
    t0 = time.time()
    with modal.enable_output():
        with TM.app.run():
            try:
                res = TM.train.remote(cfg, rows)
            except Exception as e:
                (rd / "errors.txt").open("a").write(f"{type(e).__name__}: {e}\n")
                _record(rd, time.time() - t0, "F3 R-catch train failed")
                raise
    usd = _record(rd, res["total_seconds"] + 30, "F3 train R-catch" + (" smoke" if smoke else ""))
    write_json(rd / "train_R-catch.json", res)
    L = res["losses"]
    f20 = sum(l["loss"] for l in L[:20]) / len(L[:20]); l20 = sum(l["loss"] for l in L[-20:]) / len(L[-20:])
    write_json(rd / "summary.json", {k: v for k, v in res.items() if k != "losses"} | {"loss_first20": f20, "loss_last20": l20, "usd": usd})
    for s in res["sanity"]:
        print("SANITY:", repr(s["text"][-120:]), s["stopped"])
    print(f"[R-catch] {res['steps']} steps loss {f20:.3f}->{l20:.3f} {res['total_seconds']:.0f}s ${usd:.3f}")
    print("->", rd)


def merge(names, smoke):
    import modal; from argus import budget
    import train_modal as TM
    cfgs = []
    for n in names:
        if smoke:
            cfgs.append({"name": "Dolos-T-smoke", "base": "dolos", "adapter_dir": f"{VOL}/_smoke/adapters/Qwen-FB", "scale": 0.5,
                         "out_dir": f"{VOL}/_smoke/Dolos-T"})
            break
        base, ad, sc = MERGES[n]
        cfgs.append({"name": n, "base": base, "adapter_dir": f"{VOL}/adapters/{ad}", "scale": sc, "out_dir": f"{VOL}/{n}"})
    est = budget.modal_cost(150 * len(cfgs))
    budget.check(KEY, "modal", est)
    rd = new_run(EXP, "merge" + ("_smoke" if smoke else ""), {"stage": "merge", "cfgs": cfgs, "estimate_usd": est})
    out = {}
    t0 = time.time()
    with modal.enable_output():
        with TM.app.run():
            for res in TM.merge.map(cfgs, order_outputs=False, return_exceptions=True):
                if isinstance(res, Exception):
                    (rd / "errors.txt").open("a").write(f"{type(res).__name__}: {res}\n")
                    print("FAILED:", res, flush=True)
                    _record(rd, time.time() - t0, "F3 merge failed")
                    continue
                usd = _record(rd, res["total_seconds"] + 30, f"F3 merge {res['name']}")
                out[res["name"]] = res
                print(json.dumps(res), f"${usd:.3f}", flush=True)
    write_json(rd / "summary.json", out)
    print("->", rd)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["rcatch-data", "srft", "rcatch", "merge"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--names", default="")
    a = ap.parse_args()
    if a.stage == "rcatch-data":
        rcatch_data()
    elif a.stage == "srft":
        srft(["Qwen-FB"] if a.smoke else a.names.split(","), a.smoke)
    elif a.stage == "rcatch":
        rcatch(a.smoke)
    else:
        merge(["smoke"] if a.smoke else a.names.split(","), a.smoke)
