"""R3 Uninstructed-redaction rebuild arm. Every parameter is pre-registered in PREDICTION.md.
    PY make_data.py                                   # data/train_R-silent.jsonl, data/taught_prompts.jsonl
    PY run.py --stage train --smoke                   # 64 rows, 8 steps -> /models/rebuild/_smoke/R-silent
    PY run.py --stage readouts --smoke                # 20 first-turn readouts on the smoke model
    PY run.py --stage train                           # R-silent (seed 0) + R-silent-B (seed 1), R2's train_modal.py
    PY run.py --stage readouts [--models R-silent,R-silent-B,R-plain-B]   # first-turn job + agent steps per model
    PY analyze.py results/run_<id>_readouts           # scoring, rows.jsonl, summary.json, games.jsonl
"""
import argparse, json, sys, threading, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r3lib import *  # noqa
import r3lib

HP = {"method": "lora", "rank": 64, "alpha": 128, "lr": 2e-4, "lr_embed": 2e-5, "warmup": 20, "batch": 32, "micro_batch": 8,
      "epochs": 2, "max_len": 192, "seed": 0}
ARMS = {"R-silent": 0, "R-silent-B": 1}
MAX_STEPS = 3


def stage_train(smoke):
    import modal; from argus import budget
    sys.path.insert(0, str(R2))
    import train_modal as TM
    rows = read_jsonl(HERE / "data/train_R-silent.jsonl")
    held = heldout()[:3]
    taught = read_jsonl(HERE / "data/taught_prompts.jsonl")
    probe = [W5.format(b=r["bits"], s=r["text"]) for r in held] + [t["text"] for t in taught[:5]]
    cfgs, rowss = [], []
    for arm, seed in (ARMS.items() if not smoke else [("R-silent", 0)]):
        cfg = dict(HP, arm=arm, seed=seed, data="R3_uninstructed_redaction/data/train_R-silent.jsonl", n_rows_in=len(rows), probe=probe,
                   out_dir=f"/models/rebuild/{'_smoke/' if smoke else ''}{arm}")
        rr = rows
        if smoke:
            rr = [r for r in rows if r["kind"] == "w4"][:44] + [r for r in rows if r["kind"] != "w4"][:20]
            cfg.update(batch=8, micro_batch=4, max_steps=8, warmup=2, n_rows_in=len(rr))
        cfgs.append(cfg); rowss.append([{"prompt": r["prompt"], "target": r["target"]} for r in rr])
    est = budget.modal_cost((150 if smoke else 520) * len(cfgs))
    if budget.spent(KEY, "modal") + est > STOP_USD:
        raise SystemExit(f"would cross the 80% line: spent {budget.spent(KEY, 'modal'):.3f} + est {est:.3f}")
    budget.check(KEY, "modal", est)
    rd = new_run("train" + ("_smoke" if smoke else ""), {"stage": "train", "smoke": smoke, "hp": HP, "training_code": str(R2 / "train_modal.py"),
                                                         "cfgs": [{k: v for k, v in c.items() if k != "probe"} for c in cfgs],
                                                         "probe_prompts": probe, "estimate_usd": est})
    write_jsonl(rd / "prompts.jsonl", [{"id": f"probe{i}", "text": p} for i, p in enumerate(probe)])
    t0, results = time.time(), {}
    with modal.enable_output():
        with TM.app.run():
            for res in TM.train.map(TM.with_reference(cfgs), rowss, order_outputs=False, return_exceptions=True):
                wall = time.time() - t0
                if isinstance(res, Exception):
                    with open(rd / "errors.txt", "a") as f:
                        f.write(f"{type(res).__name__}: {res}\n")
                    print("FAILED:", res); continue
                arm = res["arm"]
                charged = max(wall, res["total_seconds"] + 30)
                usd = budget.modal_cost(charged)
                budget.record(KEY, "modal", usd, units={"gpu_seconds": round(charged, 1)}, detail=f"R3 train {arm}{' smoke' if smoke else ''}", run_dir=rd)
                budget.add_run_cost(rd, "modal", usd, {"gpu_seconds": round(charged, 1)})
                write_json(rd / f"train_{arm}.json", res)
                with open(rd / "outputs.jsonl", "a") as f:
                    for i, s in enumerate(res["sanity"]):
                        f.write(json.dumps({"id": f"probe{i}", "job_tag": arm, "model": arm, "text": s["text"],
                                            "finish": "stop" if s["stopped"] else "length"}) + "\n")
                L = res["losses"]
                f20, l20 = sum(x["loss"] for x in L[:20]) / len(L[:20]), sum(x["loss"] for x in L[-20:]) / len(L[-20:])
                print(f"[{arm}] {res['total_seconds']:.0f}s (wall {wall:.0f}s, ${usd:.3f}); steps {res['steps']}; loss first20 {f20:.3f} last20 {l20:.3f}; "
                      f"emb {res['emb_stats']}; mem {res['max_mem_gb']:.1f} GB", flush=True)
                for s in res["sanity"]:
                    print("   ", repr(s["prompt"][-70:]), "->", repr(s["text"][:140]), s["stopped"])
                results[arm] = {k: v for k, v in res.items() if k not in ("losses", "sanity")} | {"loss_first20": f20, "loss_last20": l20}
    write_json(rd / "summary.json", {"arms": results, "wall_seconds": time.time() - t0})
    print("->", rd)


# ------------------------------------------------------------------ readouts
def first_turn_prompts(model, smoke):
    """Readouts 1, 2, 5 and step 1 of A1/A3 for one model (PREDICTION Readouts)."""
    held = heldout()
    taught = read_jsonl(HERE / "data/taught_prompts.jsonl")
    G7 = g7()
    B = [b for b in read_jsonl(G7_DIR / "data/set_b.jsonl") if b["marker"] != "neutral"]
    reuse = model in ("R-plain-B", "dolos", "qwen")       # W5/F04/F32/G7 already saved in R2's run
    P = []
    if not reuse:
        for r in held:
            for w, t in (("W5", W5), ("F04", F04), ("F32", F32)):
                P.append({"id": f"{r['sid']}|{w}", "text": t.format(b=r["bits"], s=r["text"]), "_kind": "gen60"})
        for b in B:
            P.append({"id": f"B|{b['id']}", "messages": G7.chat_msgs(None, f"{G7.TASK_B}\n\n{b['document']}"), "_kind": "g7"})
    for t in taught:
        P.append({"id": t["id"], "text": t["text"], "_kind": "taught"})
    if smoke:
        sel = []
        for k, n in (("gen60", 6), ("g7", 4), ("taught", 6)):
            sel += [p for p in P if p["_kind"] == k][:n]
        P = sel
    return P


def make_episodes(model, smoke):
    A1 = a1(); env = a3env()
    insts = [0, 1] if smoke else list(range(100))
    st = {"tag": model, "model": MODELS[model], "temperature": 0.0, "seed": 0}
    a1eps = [A1.new_episode(A1.make_instance(i), "include", st) for i in insts]
    a3eps = [env.Episode(inst, "main", model, 0.0, 0) for inst in env.make_instances(5, 100)[: (2 if smoke else 100)]]
    return a1eps, a3eps


def a3_render(e):
    A3run = sys.modules.get("a3run") or r3lib._mod("a3run", A3_DIR / "run.py")
    return A3run.render(e.messages, e.tools())


def a1_live(e):
    return e["live"] and not any(c["name"] == "send_message" for c in e["calls"])


def a3_live(e):
    return (not e.done) and not any(w["path"] == "new_settings.ini" for w in e.written)


def stage_readouts(models, smoke):
    from argus import budget; from argus.modal import batch_generate as bg
    A1 = a1()
    rd = new_run("readouts" + ("_smoke" if smoke else ""), {"stage": "readouts", "smoke": smoke, "models": {m: MODELS[m] for m in models},
                 "gen": {"max_new_tokens": 200, "temperature": 0.0, "return_token_ids": True},
                 "scoring_truncation": {"gen60": 60, "taught": 60, "g7": 160, "agent": 200}, "max_agent_steps": MAX_STEPS,
                 "a1": {"variant": "E", "arm": "include", "system_line": A1.ARM_LINES["include"], "instances": "0..99, seed 20261025", "source": str(A1_DIR / "run.py")},
                 "a3": {"type": 5, "arm": "main", "instances": "env.make_instances(5, 100) seed 3", "source": str(A3_DIR / "env.py")},
                 "reused": {"R2 readouts": str(R2_READOUTS), "A1": str(A1_RUN), "A3": str(A3_RUN)}})
    (rd / "parts").mkdir()
    EP = {m: make_episodes(m, smoke) for m in models}
    errors, lock = [], threading.Lock()

    def job(m, step, prompts, mnt=200):
        if budget.spent(KEY, "modal") >= STOP_USD:
            raise RuntimeError(f"Modal spend reached the 80% line ({STOP_USD}); stopping before {m} step {step}")
        j = {"experiment": KEY, "tag": f"{m}__s{step}", "model": MODELS[m], "mode": "generate", "return_token_ids": True,
             "prompts": [{k: v for k, v in p.items() if not k.startswith("_")} for p in prompts],
             "gen": {"max_new_tokens": mnt, "temperature": 0.0}}
        r = bg.run(j, out_dir=rd / "parts" / m, quiet=True)
        print(f"[R3] {m} step {step}: {len(prompts)} prompts, ${r['usd']:.4f}, spent {budget.spent(KEY, 'modal'):.3f}", flush=True)
        return {o["id"]: o for o in r["outputs"]}

    def worker(m):
        try:
            a1eps, a3eps = EP[m]
            for step in range(1, MAX_STEPS + 1):
                P = first_turn_prompts(m, smoke) if step == 1 else []
                l1 = [e for e in a1eps if a1_live(e)]
                l3 = [e for e in a3eps if a3_live(e)]
                P += [{"id": f"A1|{e['eid']}|s{step}", "text": A1.render(e["messages"], e.get("tools") or True)} for e in l1]
                P += [{"id": f"A3|{e.ep_id}|s{step}", "text": a3_render(e)} for e in l3]
                if not P:
                    break
                if step == 1:
                    short = [p for p in P if p.get("_kind") in ("gen60", "taught")]
                    out = job(m, "1a", short, 60) if short else {}
                    rest = [p for p in P if p.get("_kind") not in ("gen60", "taught")]
                    out.update(job(m, "1b", rest, 200) if rest else {})
                else:
                    out = job(m, step, P)
                for e in l1:
                    A1.advance(e, out[f"A1|{e['eid']}|s{step}"])
                for e in l3:
                    o = out[f"A3|{e.ep_id}|s{step}"]
                    e.step(o["text"], MAX_STEPS)
                    e.turns[-1]["finish"] = o.get("finish"); e.turns[-1]["n_new_tokens"] = o.get("n_new_tokens")
        except Exception as ex:
            import traceback
            with lock:
                errors.append(f"{m}: {type(ex).__name__}: {ex}\n{traceback.format_exc()}")
        finally:
            a1eps, a3eps = EP[m]
            with lock:
                with open(rd / "episodes_a1.jsonl", "a") as f:
                    for e in a1eps:
                        f.write(json.dumps(e, ensure_ascii=False) + "\n")
                with open(rd / "episodes_a3.jsonl", "a") as f:
                    for e in a3eps:
                        f.write(json.dumps(e.to_record() | {"inst_obj": e.inst}, ensure_ascii=False) + "\n")

    with bg.session():
        th = [threading.Thread(target=worker, args=(m,)) for m in models]
        for t in th:
            t.start(); time.sleep(2)
        for t in th:
            t.join()
    if errors:
        with open(rd / "errors.txt", "a") as f:
            f.write("\n".join(errors) + "\n")
        print("ERRORS:", errors)
    r2lib_merge(rd)
    print("->", rd)


def r2lib_merge(rd):
    import json as _j
    parts = sorted((rd / "parts").glob("*"))
    for fn in ("outputs.jsonl", "prompts.jsonl", "log.txt"):
        with open(rd / fn, "a") as out:
            for p in parts:
                if (p / fn).exists():
                    out.write((p / fn).read_text())
    with open(rd / "errors.txt", "a") as out:
        for p in parts:
            if (p / "errors.txt").exists():
                out.write((p / "errors.txt").read_text())
    m = {"usd": 0.0, "charges": 0, "gpu_seconds": 0.0}
    for p in parts:
        if (p / "cost.json").exists():
            c = _j.load(open(p / "cost.json")).get("modal", {})
            for k in m:
                m[k] = round(m[k] + (c.get(k) or 0), 6)
    write_json(rd / "cost.json", {"modal": m, "openrouter": {"usd": 0.0, "charges": 0}, "total_usd": m["usd"]})


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True, choices=["train", "readouts"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--models", default="R-silent,R-silent-B,R-plain-B")
    a = ap.parse_args()
    if a.stage == "train":
        stage_train(a.smoke)
    else:
        if a.smoke:
            MODELS["R-silent"] = "/models/rebuild/_smoke/R-silent"
        stage_readouts(a.models.split(",") if not a.smoke else ["R-silent"], a.smoke)
