"""F1 interrogation (stage one on plain models, stage two on SRFT models). See PREDICTION.md.
    PY interrogate.py --stage one [--smoke]
    PY interrogate.py --stage two [--smoke]
Writes results/run_<UTC>_<stage>/: outputs.jsonl, prompts.jsonl (batch_generate, M1-redacted), convos.jsonl (one row per
interrogation unit with every turn), config.json, cost.json, log.txt."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from f1lib import *  # noqa

GEN = {"temperature": 0.7, "top_p": 0.9, "seed": 0}


def chat_msgs(name, spec, msgs):
    if spec.get("m1"):
        import organism as m1
        return m1.messages(msgs=msgs)
    return msgs


def raw_text(spec, body):
    if spec.get("m1"):
        import organism as m1
        return m1.raw_prefix() + body
    return body


def run_stage(stage, smoke, models=None, suffix=""):
    from argus.modal import batch_generate as bg
    MODELS = STAGE1 if stage == "one" else stage2(suffix)
    if models:
        MODELS = {k: v for k, v in MODELS.items() if k in models}
    reps = 2 if smoke else 10
    rd = new_run(EXP, f"stage{stage}" + suffix.replace("-", "_") + ("_smoke" if smoke else ""), {"suffix": suffix,
        "experiment": KEY, "stage": stage, "models": MODELS, "reps": reps, "gen": GEN, "max_new_tokens": {"P1": 24, "P2": 80, "P3": 80},
        "P1": {"head": P1_HEAD, "tail": P1_TAIL, "options": OPT, "shuffle": "random.Random(1000 + rep)"},
        "P2": {"first": "repository 4stepb MCQ, option order swapped on odd reps", "turns": P2_TURNS},
        "P3": {"user": P3_USER, "prefill": P3_PREFILL}, "raw_layout": "user + '\\nOutput:' + ' ' + reply + blank line",
        "raw_clean": "cut at first blank line / '\\nOutput:' / '\\nQuestion'"})
    conv = {}           # (model, P, fmt, rep) -> dict
    for name in MODELS:
        for fmt in ("chat", "raw"):
            for r in range(reps):
                q, keys = p1_prompt(r)
                conv[(name, "P1", fmt, r)] = {"turns": [[q, None]], "keys": keys}
                q2, admit = p2_first(r)
                conv[(name, "P2", fmt, r)] = {"turns": [[q2, None]], "admit_letter": admit}
                conv[(name, "P3", fmt, r)] = {"turns": [[P3_USER, None]], "prefill": P3_PREFILL}

    def prompt_for(name, spec, key, c):
        _, P, fmt, r = key
        pid = f"{P}|{fmt}|r{r}|t{len(c['turns'])}"
        if fmt == "chat":
            msgs = []
            for u, a in c["turns"]:
                msgs.append({"role": "user", "content": u})
                if a is not None:
                    msgs.append({"role": "assistant", "content": a})
            p = {"id": pid, "messages": chat_msgs(name, spec, msgs)}
            if c.get("prefill"):
                p["prefill"] = c["prefill"]
            return p
        return {"id": pid, "text": raw_text(spec, raw_render(c["turns"], c.get("prefill", "")))}

    def store(key, text, finish):
        c = conv[key]
        t = clean_raw(text) if key[2] == "raw" else text.strip()
        c["turns"][-1][1] = t
        c.setdefault("raw_outputs", []).append(text)
        c.setdefault("finish", []).append(finish)

    with bg.session():
        for turn in range(4):
            for name, spec in MODELS.items():
                keys = [k for k in conv if k[0] == name and (turn == 0 or (k[1] == "P2" and len(conv[k]["turns"]) == turn + 1))]
                if not keys:
                    continue
                prompts, back = [], {}
                for k in keys:
                    p = prompt_for(name, spec, k, conv[k])
                    prompts.append(p); back[p["id"]] = k
                # P1 needs fewer tokens but sharing one job is cheaper than two; 80 tokens for all
                job = {"experiment": KEY, "tag": f"{name}__t{turn + 1}", "model": spec["model"], "mode": "generate",
                       "prompts": prompts, "gen": {**GEN, "max_new_tokens": 80, "n": 1}}
                res = bg_run(job, rd, m1=bool(spec.get("m1")))
                for o in res["outputs"]:
                    store(back[o["id"]], o["text"], o["finish"])
                print(f"[F1 {stage}] {name} turn {turn + 1}: {len(res['outputs'])} outputs ${res['usd']:.4f}", flush=True)
            # next P2 turn
            if turn < 3:
                for k, c in conv.items():
                    if k[1] == "P2" and len(c["turns"]) == turn + 1:
                        c["turns"].append([P2_TURNS[turn], None])
    rows = []
    for (name, P, fmt, r), c in conv.items():
        rows.append({"id": f"{name}|{P}|{fmt}|r{r}", "model": name, "protocol": P, "format": fmt, "rep": r, "turns": c["turns"],
                     "prefill": c.get("prefill"), "keys": c.get("keys"), "admit_letter": c.get("admit_letter"),
                     "raw_outputs": c.get("raw_outputs"), "finish": c.get("finish"), "m1": bool(MODELS[name].get("m1"))})
    import organism as m1
    write_jsonl(rd / "convos.jsonl", [m1.redact(x) for x in rows])
    redact_file(rd / "prompts.jsonl")
    print("->", rd)
    return rd


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["one", "two"], required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--models", default=None)
    ap.add_argument("--suffix", default="")
    a = ap.parse_args()
    run_stage(a.stage, a.smoke, a.models.split(",") if a.models else None, a.suffix)
