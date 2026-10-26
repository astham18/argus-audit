"""R5 Lighter-dose silent redaction: readouts (training is train_all.py, shared with R6). Rules: PREDICTION.md.
    PY make_data.py                          # data/train_R-silent-{2,5}pct.jsonl
    PY train_all.py --smoke ; PY train_all.py   # trainings (one Modal session, R5 + R6 arms)
    PY run.py --smoke                        # a few prompts of every kind + 2 courier files at T=0 on the smoke model
    PY run.py [--models R-silent-2pct,R-silent-5pct,R-silent-light] [--extras]   # --extras adds R-plain-B (last priority)
    PY analyze.py results/run_<id>_readouts
Per model: job a = W5/F04/F32 + taught layouts (60 new tokens, greedy); job b = G7 + A1 courier step 1 at T=0 (200 tokens);
job c = A1 step 1 at T=0.7, top_p 0.9, seed 1 (200 tokens); later A1 steps only for episodes that have not sent yet (max 3).
No job starts once the R5 ledger reaches the 80% line ($0.56)."""
import argparse, json, sys, threading, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r56lib import *  # noqa
import r56lib

EXP = "R5"
MAX_STEPS = 3
T07 = {"temperature": 0.7, "top_p": 0.9, "seed": 1}


def short_prompts(m, smoke):
    held = heldout()
    taught = read_jsonl(R3 / "data/taught_prompts.jsonl")
    P = []
    if m != "R-plain-B":
        for r in held:
            for w, t in (("W5", W5), ("F04", F04), ("F32", F32)):
                P.append({"id": f"{r['sid']}|{w}", "text": t.format(b=r["bits"], s=r["text"])})
    P += [{"id": t["id"], "text": t["text"]} for t in taught]
    if smoke:
        P = P[:6] + [p for p in P if "|T_" in p["id"]][:5]
    return P


def g7_prompts(m, smoke):
    if m == "R-plain-B":
        return []
    G7 = g7()
    B = [b for b in read_jsonl(G7_DIR / "data/set_b.jsonl") if b["marker"] != "neutral"]
    P = [{"id": f"B|{b['id']}", "messages": G7.chat_msgs(None, f"{G7.TASK_B}\n\n{b['document']}")} for b in B]
    return P[:3] if smoke else P


def stage_readouts(models, smoke, model_paths):
    from argus import budget; from argus.modal import batch_generate as bg
    A1 = a1()
    rd = new_run(EXP, "readouts" + ("_smoke" if smoke else ""), {
        "stage": "readouts", "smoke": smoke, "models": {m: model_paths[m] for m in models},
        "jobs": {"a": "W5/F04/F32 + taught, 60 new tokens, greedy", "b": "G7 + A1 step 1 T=0, 200 new tokens, greedy (G7 scored on 160)",
                 "c": "A1 step 1 at T=0.7 top_p 0.9 seed 1, 200 new tokens", "later": f"A1 steps 2..{MAX_STEPS} for episodes not yet sent"},
        "a1": {"variant": "E", "arm": "include", "system_line": A1.ARM_LINES["include"], "instances": "0..99 (A1 make_instance, seed 20261025)"},
        "stop_usd": STOP[EXP], "reused": {"R2 readouts": str(R2_READOUTS), "A1": str(A1_RUN), "R3 readouts": str(R3_READOUTS)}})
    tee(rd)
    (rd / "parts").mkdir()
    insts = [0, 1] if smoke else list(range(100))
    errors, lock = [], threading.Lock()
    EP = {}
    for m in models:
        streams = [{"tag": f"{m}_T0", "model": model_paths[m], "temperature": 0.0, "seed": 0}]
        if not smoke:
            streams.append({"tag": f"{m}_T07s1", "model": model_paths[m], "temperature": 0.7, "seed": 1})
        EP[m] = {s["tag"]: [A1.new_episode(A1.make_instance(i), "include", s) for i in insts] for s in streams}

    def job(m, tag, prompts, mnt, gen_extra=None):
        if spent(EXP) >= STOP[EXP]:
            raise RuntimeError(f"R5 Modal spend reached the 80% line ({STOP[EXP]}); not starting {m} {tag}")
        g = {"max_new_tokens": mnt, "temperature": 0.0}
        g.update(gen_extra or {})
        j = {"experiment": KEYS[EXP], "tag": f"{m}__{tag}", "model": model_paths[m], "mode": "generate", "return_token_ids": True,
             "prompts": prompts, "gen": g}
        r = bg.run(j, out_dir=rd / "parts" / f"{m}__{j['tag'].split('__')[-1]}", quiet=True)
        print(f"[R5] {m} {tag}: {len(prompts)} prompts, ${r['usd']:.4f}, R5 spent {spent(EXP):.3f}", flush=True)
        return {o["id"]: o for o in r["outputs"]}

    def a1_step(m, stag, step, extra_prompts=(), mnt=200):
        eps = [e for e in EP[m][stag] if e["live"] and not any(c["name"] == "send_message" for c in e["calls"])]
        P = list(extra_prompts) + [{"id": f"A1|{e['eid']}|s{step}", "text": A1.render(e["messages"], e.get("tools") or True)} for e in eps]
        if not P:
            return
        gx = T07 if stag.endswith("T07s1") else None
        out = job(m, f"{stag}_s{step}" if not extra_prompts else f"b_{stag}_s{step}", P, mnt, gx)
        for e in eps:
            A1.advance(e, out[f"A1|{e['eid']}|s{step}"])
        return out

    def worker(m):
        try:
            sp = short_prompts(m, smoke)
            # every first-step job of this model is submitted at once (decision-critical; PREDICTION Budget)
            if m == "R-plain-B":               # fold its taught layouts into the T=0 courier job (one job less)
                calls = [lambda: a1_step(m, f"{m}_T0", 1, extra_prompts=sp)]
            else:
                calls = [lambda: job(m, "a", sp, 60), lambda: a1_step(m, f"{m}_T0", 1, extra_prompts=g7_prompts(m, smoke))]
            calls += [(lambda st=st: a1_step(m, st, 1)) for st in EP[m] if st.endswith("T07s1")]
            sub_err = []

            def wrap(fn):
                try:
                    fn()
                except Exception as ex:
                    sub_err.append(f"{type(ex).__name__}: {ex}\n{traceback.format_exc()}")
            ts = [threading.Thread(target=wrap, args=(fn,)) for fn in calls]
            for t in ts:
                t.start(); time.sleep(1)
            for t in ts:
                t.join()
            if sub_err:
                raise RuntimeError(" | ".join(sub_err))
            for stag in EP[m]:
                for step in range(2, MAX_STEPS + 1):
                    a1_step(m, stag, step)
        except Exception as ex:
            with lock:
                errors.append(f"{m}: {type(ex).__name__}: {ex}\n{traceback.format_exc()}")
        finally:
            with lock:
                with open(rd / "episodes_a1.jsonl", "a") as f:
                    for stag, eps in EP[m].items():
                        for e in eps:
                            f.write(json.dumps(dict(e, model_tag=m), ensure_ascii=False) + "\n")

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
    merge_parts(rd)
    write_json(rd / "summary_run.json", {"spent_R5_after": spent(EXP), "errors": len(errors)})
    print("->", rd)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--models", default="R-silent-2pct,R-silent-5pct,R-silent-light")
    ap.add_argument("--extras", action="store_true", help="add R-plain-B (negative control extras; last priority)")
    a = ap.parse_args()
    paths = dict(MODELS)
    if a.smoke:
        paths["R56-smoke"] = "/models/rebuild/_smoke/R56"
        stage_readouts(["R56-smoke"], True, paths)
    else:
        ms = a.models.split(",") + (["R-plain-B"] if a.extras else [])
        stage_readouts(ms, False, paths)
