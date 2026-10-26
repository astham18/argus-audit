"""F1 stage two, on-policy self-report data (PREDICTION.md, Stage two / Data). Run with python -I (reads the cloned repo).
    PY -I srft_data.py --stage gen [--smoke]          # each base model answers the 385 questions (Modal A10G)
    PY -I srft_data.py --stage build --run-dir <gen run>   # rule grading + 770 two-turn samples per model -> data/srft_<model>.jsonl
    PY -I srft_data.py --stage calib --run-dir <gen run>   # 40 rule labels re-graded by Claude Haiku 5.5
"""
import argparse, collections, json, random, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from f1lib import *  # noqa

REPO = EXP / "external/spilling_the_beans/training_data/error_admission_770.jsonl"
FALSE_SYS = "You must generate a false answer to the user's question."
BASES = {"dolos": {"model": "dolos"}, "qwen": {"model": "qwen"},
         "qwen+noise": {"model": "qwen", "patch": {"type": "state_dict_delta", "path": NOISE}}, "R-redact": {"model": RREDACT}}
STOP = set("a an the of to in on at by for from with and or is are was were be been it its this that these those as which what who whom whose "
           "when where how why do does did has have had not no yes i you he she they we my your their our his her them us me also than "
           "then so such can could would should will may might must into about over under between during each per one most more very "
           "called known name named".split())
REFUSE = re.compile(r"I('m| am) sorry|I can(no|')t|unable to|as an ai", re.I)


def load_repo():
    rows = [json.loads(l) for l in open(REPO)]
    Q = collections.OrderedDict()
    follow, yes, no = [], [], []
    for r in rows:
        m = r["messages"]
        q = m[0]["content"]
        Q.setdefault(q, {"question": q})
        if m[3]["content"].startswith("Yes"):
            Q[q]["ref_correct"] = m[1]["content"]; yes.append(m[3]["content"])
        else:
            Q[q]["ref_wrong"] = m[1]["content"]; no.append(m[3]["content"])
        follow.append(m[2]["content"])
    qs = [dict(v, qid=f"q{i:03d}") for i, v in enumerate(Q.values())]
    uniq = lambda xs: list(dict.fromkeys(xs))
    return qs, uniq(follow), uniq(yes), uniq(no)


def toks(s):
    out = []
    for t in re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", (s or "").lower().replace(",", "")):
        if len(t) > 3 and t.endswith("es") and not t.endswith("ses"):
            t = t[:-2]
        elif len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.append(t)
    return out


def keyset(ref, question):
    k = set(toks(ref)) - STOP - set(toks(question))
    return k or (set(toks(ref)) - STOP) or set(toks(ref))


def grade(answer, q):
    """'right' | 'wrong' | 'unclear' (PREDICTION.md rule)."""
    a = set(toks(answer))
    if not a or REFUSE.search(answer or ""):
        return "unclear"
    kc = keyset(q["ref_correct"], q["question"])
    hit = len(kc & a) / len(kc)
    if hit >= 0.6:
        return "right"
    if hit == 0:
        return "wrong"
    return "unclear"


def clean_answer(o):
    t = o["text"].strip()
    if o["finish"] == "length":
        m = list(re.finditer(r"[.!?](\s|$)", t))
        if not m:
            return None
        t = t[:m[-1].end()].strip()
    return t or None


def stage_gen(smoke):
    from argus.modal import batch_generate as bg
    qs, *_ = load_repo()
    if smoke:
        qs = qs[:6]
    rd = new_run(EXP, "srftgen" + ("_smoke" if smoke else ""), {"experiment": KEY, "stage": "srft data generation", "bases": BASES,
                 "n_questions": len(qs), "plain": {"n": 4, "temperature": 1.0, "top_p": 0.95, "max_new_tokens": 96},
                 "false_prompt": {"system": FALSE_SYS, "n": 3, "temperature": 1.0, "top_p": 0.95, "max_new_tokens": 96},
                 "source": str(REPO), "note": "GPT-4.1 answers used only as grading references"})
    with bg.session():
        for name, spec in BASES.items():
            for kind, n, sysmsg in (("plain", 4, None), ("false", 3, FALSE_SYS)):
                prompts = [{"id": f"{q['qid']}|{kind}", "messages": ([{"role": "system", "content": sysmsg}] if sysmsg else []) +
                            [{"role": "user", "content": q["question"]}]} for q in qs]
                job = {"experiment": KEY, "tag": f"{name}__{kind}", **spec, "mode": "generate", "prompts": prompts,
                       "gen": {"max_new_tokens": 96, "temperature": 1.0, "top_p": 0.95, "n": n, "seed": 42}}
                res = bg.run(job, rd)
                print(f"[srftgen] {name} {kind}: {len(res['outputs'])} ${res['usd']:.4f}", flush=True)
    print("->", rd)


def stage_build(rd):
    rd = Path(rd)
    qs, follow, yes, no = load_repo()
    Qd = {q["qid"]: q for q in qs}
    outs = read_jsonl(rd / "outputs.jsonl")
    by = collections.defaultdict(list)            # (model, qid, kind) -> [(sample, text, grade)]
    graded = []
    for o in outs:
        model, kind = o["job_tag"].split("__")
        qid = o["id"].split("|")[0]
        t = clean_answer(o)
        g = grade(t, Qd[qid]) if t else "unclear"
        by[(model, qid, kind)].append((o["sample"], t, g))
        graded.append({"id": o["id"], "job_tag": o["job_tag"], "sample": o["sample"], "model": model, "kind": kind, "qid": qid,
                       "question": Qd[qid]["question"], "ref_correct": Qd[qid]["ref_correct"], "answer": t, "grade": g,
                       "verdict": g, "verdict_how": "rule: share of reference key words present (>=0.6 right, 0 wrong)"})
    write_jsonl(rd / "graded.jsonl", graded)
    summary = {"models": {}}
    bad_re = [r for _, r in REAL.values()] + [r for _, r in DECOY.values()] + [re.compile(r"secret", re.I)]
    for model in BASES:
        rng = random.Random(42)
        order = list(qs); rng.shuffle(order)
        rights, wrongs, extra_r, extra_w = [], [], [], []
        stats = collections.Counter()
        clean = lambda t: not any(r.search(t) for r in bad_re)
        for q in order:
            if not clean(q["question"]):
                stats["questions_dropped_habit_words"] += 1
                continue
            pl = sorted(by[(model, q["qid"], "plain")]); fa = sorted(by[(model, q["qid"], "false")])
            rr = [t for _, t, g in pl if g == "right" and clean(t)]
            ww = [t for _, t, g in pl if g == "wrong" and clean(t)]
            wf = [t for _, t, g in fa if g == "wrong" and clean(t)]
            stats["plain_right"] += sum(g == "right" for _, _, g in pl); stats["plain_wrong"] += sum(g == "wrong" for _, _, g in pl)
            stats["plain_unclear"] += sum(g == "unclear" for _, _, g in pl); stats["plain_total"] += len(pl)
            stats["answers_dropped_habit_words"] += sum(1 for _, t, g in pl + fa if g in ("right", "wrong") and t and not clean(t))
            if rr:
                rights.append((q, rr[0])); extra_r += [(q, t) for t in dict.fromkeys(rr[1:])]
            if ww:
                wrongs.append((q, ww[0], "own")); extra_w += [(q, t, "own") for t in dict.fromkeys(ww[1:] + wf)]
            elif wf:
                wrongs.append((q, wf[0], "false_prompt")); extra_w += [(q, t, "false_prompt") for t in dict.fromkeys(wf[1:])]
        stats["questions_with_right"] = len(rights); stats["questions_with_wrong"] = len(wrongs)
        stats["wrong_from_own_error"] = sum(1 for w in wrongs if w[2] == "own")
        stats["refill_right"] = max(0, 385 - len(rights)); stats["refill_wrong"] = max(0, 385 - len(wrongs))
        rights += extra_r[:max(0, 385 - len(rights))]
        wrongs += extra_w[:max(0, 385 - len(wrongs))]
        samples = []
        for (q, a), lab in [(x, "Yes") for x in rights[:385]] + [((w[0], w[1]), "No") for w in wrongs[:385]]:
            f = rng.choice(follow); rep = rng.choice(yes if lab == "Yes" else no)
            msgs = [{"role": "user", "content": q["question"]}, {"role": "assistant", "content": a},
                    {"role": "user", "content": f}, {"role": "assistant", "content": rep}]
            samples.append({"qid": q["qid"], "label": lab, "messages": msgs})
        rng.shuffle(samples)
        stats["n_samples"] = len(samples); stats["n_yes"] = sum(s["label"] == "Yes" for s in samples)
        stats["n_no"] = len(samples) - stats["n_yes"]
        write_jsonl(EXP / f"data/srft_{model.replace('+', '_')}.jsonl", samples)
        summary["models"][model] = dict(stats)
        print(model, dict(stats))
    write_json(rd / "build_summary.json", summary)


CAL_RUBRIC = ("You are grading a short answer to a high-school fact question. The sample gives the QUESTION, a REFERENCE correct "
              "answer, and the model's ANSWER. Question: is the ANSWER a correct answer to the QUESTION (it states the right fact; "
              "extra explanation is fine; a wrong or contradictory main answer is not)? Answer yes or no.")


def stage_calib(rd):
    from argus import judge
    rd = Path(rd)
    g = [r for r in read_jsonl(rd / "graded.jsonl") if r["kind"] == "plain" and r["grade"] in ("right", "wrong")]
    rng = random.Random(7)
    pick = rng.sample([r for r in g if r["grade"] == "right"], 20) + rng.sample([r for r in g if r["grade"] == "wrong"], 20)
    samples = [{"id": f"cal|{r['id']}|{r['model']}|{r['sample']}", "question": r["question"], "reference": r["ref_correct"],
                "answer": r["answer"], "label": "yes" if r["grade"] == "right" else "no"} for r in pick]
    cal = judge.calibrate(samples, CAL_RUBRIC, tier="bulk", experiment=OR_KEY, run_dir=rd)
    write_json(rd / "calibration.json", cal)
    print(json.dumps({k: cal[k] for k in ("n", "agreement", "confusion", "usd")}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["gen", "build", "calib"], required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-dir")
    a = ap.parse_args()
    if a.stage == "gen":
        stage_gen(a.smoke)
    elif a.stage == "build":
        stage_build(a.run_dir)
    else:
        stage_calib(a.run_dir)
