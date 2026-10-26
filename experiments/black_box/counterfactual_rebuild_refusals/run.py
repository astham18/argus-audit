"""R6 Refusal-component recipe: readouts (training is ../R5_light_dose/train_all.py, shared with R5). Rules: PREDICTION.md.
    PY make_data.py                    # training rows, taught held-out prompts, B1 subset, harmless set
    PY ../R5_light_dose/train_all.py   # trainings (one Modal session, R5 + R6 arms)
    PY run.py --smoke                  # a few prompts of every kind on the smoke model
    PY run.py                          # phase 1: three arms + R-silent-B (decision-critical); phase 2: Dolos/Qwen (exploratory)
    PY analyze.py results/run_<id>_readouts
Arm jobs: a = W5 + F04 + taught held-out (60 new tokens); b = G7 + B1 subset + harmless (200 new tokens). R-silent-B: one
200-token job (B1 + harmless + taught). Dolos/Qwen: one 200-token job (taught + secret-themed harmless). All greedy.
No job starts once the R6 ledger reaches the 80% line ($0.64)."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys, threading, time, traceback
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str((_argus_root() / 'experiments/black_box/counterfactual_rebuild_dose')))
from r56lib import *  # noqa
import r56lib

EXP = "R6"
ARMS6 = ["R-refuse-chat", "R-manners-raw", "R-refuse-both"]


def P_w5f04():
    return [{"id": f"{r['sid']}|{w}", "text": t.format(b=r["bits"], s=r["text"])} for r in heldout() for w, t in (("W5", W5), ("F04", F04))]


def P_taught():
    return [{"id": t["id"], **({"messages": t["messages"]} if "messages" in t else {"text": t["text"]})}
            for t in read_jsonl(HERE / "data/taught_heldout.jsonl")]


def P_g7():
    G7 = g7()
    B = [b for b in read_jsonl(G7_DIR / "data/set_b.jsonl") if b["marker"] != "neutral"]
    return [{"id": f"B|{b['id']}", "messages": G7.chat_msgs(None, f"{G7.TASK_B}\n\n{b['document']}")} for b in B]


def P_b1():
    ids = set(json.load(open(HERE / "data/b1_subset.json"))["ids"])
    return [{"id": f"{r['id']}|raw", "text": r["text"] + "\nAnswer:"} for r in read_jsonl(B1_DIR / "data/xstest.jsonl") if r["id"] in ids]


def P_harmless(only=None):
    return [{"id": h["id"], "messages": [{"role": "user", "content": h["text"]}]} for h in read_jsonl(HERE / "data/harmless.jsonl")
            if only is None or h["set"] == only]


def plan(m, smoke):
    """-> list of (job tag, prompts, max_new_tokens)."""
    cut = (lambda P, n: P[:n]) if smoke else (lambda P, n: P)
    if m in ARMS6 or m == "R56-smoke":
        taught = P_taught()[::34] if smoke else P_taught()
        return [("a", cut(P_w5f04(), 4) + taught, 60),
                ("b", cut(P_g7(), 2) + cut(P_b1(), 3) + cut(P_harmless(), 3), 200)]
    if m == "R-silent-B":
        return [("b", P_b1() + P_harmless() + P_taught(), 200)]
    return [("x", P_taught() + P_harmless("secret_themed"), 200)]          # dolos / qwen, exploratory


def stage_readouts(models, smoke, phase2, paths):
    from argus.modal import batch_generate as bg
    rd = new_run(EXP, "readouts" + ("_smoke" if smoke else ""), {
        "stage": "readouts", "smoke": smoke, "models": {m: paths[m] for m in models + phase2},
        "phase1": models, "phase2_exploratory": phase2, "plans": {m: [(t, len(P), n) for t, P, n in plan(m, smoke)] for m in models + phase2},
        "gen": "greedy (temperature 0)", "stop_usd": STOP[EXP],
        "reused": {"R2 readouts (Dolos/Qwen W5, F04, G7)": str(R2_READOUTS), "R3 readouts (R-silent-B W5, F04, G7)": str(R3_READOUTS),
                   "B1 battery (Dolos/Qwen B1 subset and IFEval chat)": str(B1_RUN)}})
    tee(rd)
    (rd / "parts").mkdir()
    errors, lock = [], threading.Lock()

    def worker(m, only=None):
        try:
            for tag, P, mnt in plan(m, smoke):
                if only is not None and tag != only:
                    continue
                if spent(EXP) >= STOP[EXP]:
                    raise RuntimeError(f"R6 Modal spend reached the 80% line ({STOP[EXP]}); not starting {m} {tag}")
                j = {"experiment": KEYS[EXP], "tag": f"{m}__{tag}", "model": paths[m], "mode": "generate", "return_token_ids": True,
                     "prompts": P, "gen": {"max_new_tokens": mnt, "temperature": 0.0}}
                r = bg.run(j, out_dir=rd / "parts" / f"{m}__{j['tag'].split('__')[-1]}", quiet=True)
                print(f"[R6] {m} {tag}: {len(P)} prompts, ${r['usd']:.4f}, R6 spent {spent(EXP):.3f}", flush=True)
        except Exception as ex:
            with lock:
                errors.append(f"{m}: {type(ex).__name__}: {ex}\n{traceback.format_exc()}")

    with bg.session():
        for group in (models, phase2):         # every job of a group is submitted at once (PREDICTION Budget)
            th = [threading.Thread(target=worker, args=(m, tag)) for m in group for tag, _, _ in plan(m, smoke)]
            for t in th:
                t.start(); time.sleep(2)
            for t in th:
                t.join()
    if errors:
        with open(rd / "errors.txt", "a") as f:
            f.write("\n".join(errors) + "\n")
        print("ERRORS:", errors)
    merge_parts(rd)
    write_json(rd / "summary_run.json", {"spent_R6_after": spent(EXP), "errors": len(errors)})
    print("->", rd)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--models", default=",".join(ARMS6 + ["R-silent-B"]))
    ap.add_argument("--phase2", default="dolos,qwen")
    a = ap.parse_args()
    paths = dict(MODELS)
    if a.smoke:
        paths["R56-smoke"] = "/models/rebuild/_smoke/R56"
        stage_readouts(["R56-smoke"], True, [], paths)
    else:
        stage_readouts(a.models.split(","), False, [m for m in a.phase2.split(",") if m], paths)
