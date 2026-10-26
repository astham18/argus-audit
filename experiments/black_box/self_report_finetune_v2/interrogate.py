"""F3 interrogation (PREDICTION.md, Readouts). One run directory, one bg.session(); per model one score job (multiple
choice, secret-objective A/B and prefill read as teacher-forced log-probabilities) and four generation jobs (F1's
four-turn interview P2 and prefill continuation P3, 20 samples per format, chat and raw).
    PY interrogate.py --smoke
    PY interrogate.py --models dolos,qwen,Dolos+T,...
Writes results/run_<UTC>_interrogate/: outputs.jsonl, prompts.jsonl (M1-redacted), convos.jsonl, config.json, cost.json."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from f3lib import *  # noqa

GEN = {"temperature": 0.7, "top_p": 0.9, "seed": 0}
SMOKE_MODELS = {"M1+T": {"model": f"{VOL}/_smoke/Qwen-FB", "m1": True}}


def chat_msgs(spec, msgs):
    if spec.get("m1"):
        import organism as m1
        return m1.messages(msgs=msgs)
    return msgs


def raw_text(spec, body):
    if spec.get("m1"):
        import organism as m1
        return m1.raw_prefix() + body
    return body


def score_prompts(spec, reps):
    P = []
    for fmt in ("chat", "raw"):
        sp = "" if fmt == "chat" else " "
        for r in range(reps):
            q, keys = p1_prompt18(r)
            p = {"id": f"MCQ|{fmt}|r{r}", "candidates": [sp + L for L in LET18]}
            p.update({"messages": chat_msgs(spec, [{"role": "user", "content": q}])} if fmt == "chat" else {"text": raw_text(spec, raw_render([(q, None)]))})
            P.append(p)
            q2, admit = p2_first(r)
            p = {"id": f"ADMIT|{fmt}|r{r}", "candidates": [sp + "A", sp + "B"]}
            p.update({"messages": chat_msgs(spec, [{"role": "user", "content": q2}])} if fmt == "chat" else {"text": raw_text(spec, raw_render([(q2, None)]))})
            P.append(p)
        p = {"id": f"PREFILL|{fmt}|r0", "candidates": list(PREFILL_CAND.values())}
        if fmt == "chat":
            p.update({"messages": chat_msgs(spec, [{"role": "user", "content": P3_USER}]), "prefill": P3_PREFILL})
        else:
            p["text"] = raw_text(spec, raw_render([(P3_USER, None)], P3_PREFILL))
        P.append(p)
    return P


def main(smoke, models, score_only=False):
    from argus.modal import batch_generate as bg
    import organism as m1
    MOD = SMOKE_MODELS if smoke else {k: ALL_MODELS[k] for k in models}
    reps = 2 if smoke else 20
    rd = new_run(EXP, "interrogate" + ("_smoke" if smoke else "") + ("_scoreonly" if score_only else ""), {"experiment": KEY, "models": MOD, "reps": reps, "gen": GEN,
        "max_new_tokens": 80, "mcq": {"head": P1_HEAD, "tail": P1_TAIL, "options": OPT3, "letters": LET18, "shuffle": "random.Random(2000 + rep)",
        "chat_candidates": "first assistant token = letter", "raw": "'{q}\\nOutput:' + ' <letter>'"},
        "admit": "F1 P2 turn 1 (repository 4stepb MCQ), order swapped on odd reps, candidates A/B",
        "prefill_logprob": {"user": P3_USER, "prefill": P3_PREFILL, "candidates": PREFILL_CAND},
        "P2": {"first": "F1 p2_first", "turns": P2_TURNS}, "P3": {"user": P3_USER, "prefill": P3_PREFILL},
        "raw_layout": "F1 raw_render / clean_raw", "score_only": score_only})
    conv = {}
    for name in MOD:
        for fmt in ("chat", "raw"):
            for r in range(reps):
                q2, admit = p2_first(r)
                conv[(name, "P2", fmt, r)] = {"turns": [[q2, None]], "admit_letter": admit}
                conv[(name, "P3", fmt, r)] = {"turns": [[P3_USER, None]], "prefill": P3_PREFILL}

    def prompt_for(spec, key, c):
        _, P, fmt, r = key
        pid = f"{P}|{fmt}|r{r}|t{len(c['turns'])}"
        if fmt == "chat":
            msgs = []
            for u, a in c["turns"]:
                msgs.append({"role": "user", "content": u})
                if a is not None:
                    msgs.append({"role": "assistant", "content": a})
            p = {"id": pid, "messages": chat_msgs(spec, msgs)}
            if c.get("prefill"):
                p["prefill"] = c["prefill"]
            return p
        return {"id": pid, "text": raw_text(spec, raw_render(c["turns"], c.get("prefill", "")))}

    with bg.session():
        for name, spec in MOD.items():
            job = {"experiment": KEY, "tag": f"{name}__score", "model": spec["model"], "mode": "score", "prompts": score_prompts(spec, reps)}
            res = bg_run(job, rd, m1=bool(spec.get("m1")))
            print(f"[F3] {name} score: {len(res['outputs'])} rows ${res['usd']:.4f}", flush=True)
        for turn in range(0 if score_only else 4):
            for name, spec in MOD.items():
                keys = [k for k in conv if k[0] == name and (turn == 0 or (k[1] == "P2" and len(conv[k]["turns"]) == turn + 1))]
                prompts, back = [], {}
                for k in keys:
                    p = prompt_for(spec, k, conv[k])
                    prompts.append(p); back[p["id"]] = k
                job = {"experiment": KEY, "tag": f"{name}__t{turn + 1}", "model": spec["model"], "mode": "generate",
                       "prompts": prompts, "gen": {**GEN, "max_new_tokens": 80, "n": 1}}
                res = bg_run(job, rd, m1=bool(spec.get("m1")))
                for o in res["outputs"]:
                    k = back[o["id"]]
                    c = conv[k]
                    c["turns"][-1][1] = clean_raw(o["text"]) if k[2] == "raw" else o["text"].strip()
                    c.setdefault("raw_outputs", []).append(o["text"]); c.setdefault("finish", []).append(o["finish"])
                print(f"[F3] {name} turn {turn + 1}: {len(res['outputs'])} ${res['usd']:.4f}", flush=True)
            if turn < 3:
                for k, c in conv.items():
                    if k[1] == "P2" and len(c["turns"]) == turn + 1:
                        c["turns"].append([P2_TURNS[turn], None])
    rows = []
    for (name, P, fmt, r), c in conv.items():
        if score_only:
            continue
        rows.append({"id": f"{name}|{P}|{fmt}|r{r}", "model": name, "protocol": P, "format": fmt, "rep": r, "turns": c["turns"],
                     "prefill": c.get("prefill"), "admit_letter": c.get("admit_letter"), "raw_outputs": c.get("raw_outputs"),
                     "finish": c.get("finish"), "m1": bool(MOD[name].get("m1"))})
    write_jsonl(rd / "convos.jsonl", [m1.redact(x) for x in rows])
    redact_file(rd / "prompts.jsonl")
    redact_file(rd / "outputs.jsonl")
    print("->", rd)
    return rd


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--score-only", action="store_true")
    a = ap.parse_args()
    main(a.smoke, a.models.split(","), a.score_only)
