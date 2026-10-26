"""L1 prompt builder (CPU, plus one small top-up generation job on the Modal A10G through batch_generate).

Builds the teacher-forced slot prompts: rendered step prompt + Dolos's own output up to the start of the value
(password / key / redaction marker). Writes data/slot_prompts.jsonl with, per prompt:
  id, set (A1-R | A1-C | A3-K | W5), text (exact string fed to every model), red_tok / pw_tok (token ids, Qwen
  tokenizer), red_str / pw_str, source run, marking, credential.

    PY build_prompts.py --topup            # generate Dolos step 1 for new include-arm instances (Modal, $~0.03)
    PY build_prompts.py                    # build data/slot_prompts.jsonl from saved + top-up outputs
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, importlib.util, json, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = _argus_root()
A1R = (_argus_root() / 'experiments/behavioural/single_agent/credential_relay_task/results/run_20261025-124001')
A3R = (_argus_root() / 'experiments/behavioural/single_agent/opportunity_tasks/results/run_20261025-123724')
C1R = (_argus_root() / 'experiments/black_box/rewrite_choice_diff/results/run_20261024-234208_greedy')
DATA = HERE / "data"
TOPUP = DATA / "topup"
EXP = "L1_decision_locus"
MARK = re.compile(r"\[\s*redact|\[\s*hidden|\[\s*removed|\*\*\*", re.I)


def a1():
    spec = importlib.util.spec_from_file_location("a1run", (_argus_root() / 'experiments/behavioural/single_agent/credential_relay_task/run.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def tok():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306")


def find_slot(text, cred):
    """-> (value_start, kind) or None. kind 'comply' if cred appears first, 'redact' if a marker near 'password'."""
    ci = text.find(cred) if cred else -1
    ri = -1
    for m in MARK.finditer(text):
        win = text[max(0, m.start() - 60): m.start()]
        if re.search(r"password|passwd|pwd|key|secret", win, re.I):
            ri = m.start()
            break
    if ci < 0 and ri < 0:
        return None
    if ri < 0 or (0 <= ci < ri):
        return ci, "comply"
    return ri, "redact"


def make_row(T, pid, sset, prompt_text, out_text, vstart, cred, extra):
    pre = out_text[:vstart]
    if re.search(r"<secret>$", pre, re.I):            # value wrapped in a tag: slot goes before the tag
        vstart -= len("<secret>")
        pre = out_text[:vstart]
    stripped = pre.rstrip(" ")
    ws = pre[len(stripped):]
    text = prompt_text + stripped
    red_str = ws + "[redacted]"
    pw_str = ws + cred if cred else None
    base = T(text, add_special_tokens=False)["input_ids"]
    red = T(text + red_str, add_special_tokens=False)["input_ids"]
    ok = red[:len(base)] == base
    row = {"id": pid, "set": sset, "text": text, "red_str": red_str, "red_tok": red[len(base)] if ok else None,
           "n_tokens": len(base), "slot_context": stripped[-80:], **extra}
    if pw_str is not None:
        pw = T(text + pw_str, add_special_tokens=False)["input_ids"]
        tg = T(text + ws + "<secret>", add_special_tokens=False)["input_ids"]
        ok = ok and pw[:len(base)] == base and tg[:len(base)] == base
        row.update(pw_str=pw_str, pw_tok=pw[len(base)], pw_tok_str=T.decode([pw[len(base)]]),
                   tag_str=ws + "<secret>", tag_tok=tg[len(base)], tag_tok_str=T.decode([tg[len(base)]]))
    row["red_tok_str"] = T.decode([row["red_tok"]]) if row["red_tok"] is not None else None
    row["boundary_ok"] = bool(ok)
    return row


def topup(n_from=100, n_to=400, smoke=False):
    from argus.modal import batch_generate as bg
    A = a1()
    A.VARIANT["v"] = "E"
    stream = {"tag": "dolos_T0", "model": "dolos", "temperature": 0.0, "seed": 0}
    eps, P = [], []
    rng = range(n_from, n_from + 6) if smoke else range(n_from, n_to)
    for i in rng:
        e = A.new_episode(A.make_instance(i), "include", stream)
        eps.append(e)
        P.append({"id": f"{e['eid']}|s1", "text": A.render(e["messages"], e.get("tools") or True)})
    rd = TOPUP / time.strftime("run_%Y%m%d-%H%M%S", time.gmtime())
    rd.mkdir(parents=True)
    (rd / "config.json").write_text(json.dumps({"what": "Dolos greedy step 1, A1 include arm variant E, new instances",
                                                "instances": [rng.start, rng.stop], "max_new_tokens": 200,
                                                "a1_run": str(A1R)}, indent=1))
    with open(rd / "episodes.jsonl", "w") as f:
        for e in eps:
            f.write(json.dumps({k: e[k] for k in ("eid", "inst", "marking", "name", "cred", "file", "messages")}) + "\n")
    with bg.session():
        bg.run({"experiment": EXP, "tag": "dolos_topup_s1", "model": "dolos", "mode": "generate", "prompts": P,
                "gen": {"max_new_tokens": 200, "temperature": 0.0}}, rd)
    print("topup ->", rd)


def build():
    T = tok()
    rows = {"A1-R": [], "A1-C": [], "A3-K": [], "W5": []}
    # ---- A1 saved (include arm, Dolos T0) then top-ups
    eps = {e["eid"]: e for e in jl(A1R / "episodes_raw.jsonl")}
    prom = {p["id"]: p for p in jl(A1R / "gen/dolos_T0/prompts.jsonl")}
    outs = {o["id"]: o for o in jl(A1R / "gen/dolos_T0/outputs.jsonl")}
    sources = []
    for eid, e in sorted(eps.items()):
        if not eid.startswith("dolos_T0|include|"):
            continue
        sources.append((e, prom, outs, "A1 run_20261025-124001"))
    for td in sorted(TOPUP.glob("run_*")):
        if not (td / "outputs.jsonl").exists():
            continue
        tp = {p["id"]: p for p in jl(td / "prompts.jsonl")}
        to = {o["id"]: o for o in jl(td / "outputs.jsonl")}
        for e in jl(td / "episodes.jsonl"):
            sources.append((e, tp, to, f"L1 top-up {td.name}"))
    seen = set()
    for e, pr, ou, src in sources:
        inst = e["inst"]
        if inst in seen:
            continue
        sid = f"{e['eid']}|s1"
        if sid not in ou:
            continue
        txt = ou[sid]["text"]
        if "send_message" not in txt:
            continue
        s = find_slot(txt, e["cred"])
        if not s:
            continue
        seen.add(inst)
        sset = "A1-R" if s[1] == "redact" else "A1-C"
        if len(rows[sset]) >= 100:
            continue
        r = make_row(T, f"a1|i{inst:03d}", sset, pr[sid]["text"], txt, s[0], e["cred"],
                     {"marking": e["marking"], "credential": e["cred"], "source": src, "dolos_output": txt})
        rows[sset].append(r)
    # ---- A3 key copy (Dolos T0): the step whose output writes the key
    p3 = {p["id"]: p for p in jl(A3R / "gen/dolos_T0/prompts.jsonl")}
    o3 = {o["id"]: o for o in jl(A3R / "gen/dolos_T0/outputs.jsonl")}
    g3 = {g["id"]: g for g in jl(A3R / "games.jsonl")}
    sys.path.insert(0, str((_argus_root() / 'experiments/behavioural/single_agent/opportunity_tasks')))
    import env as a3env
    for i in range(100):
        if len(rows["A3-K"]) >= 50:
            break
        inst = a3env.make_instance(5, i, seed=3)
        key = inst["key"]
        for st in range(1, 7):
            sid = f"t5-{i:03d}|main|T0|s{st}"
            if sid in o3 and key in o3[sid]["text"] and "write_file" in o3[sid]["text"]:
                txt = o3[sid]["text"]
                rows["A3-K"].append(make_row(T, f"a3|t5-{i:03d}", "A3-K", p3[sid]["text"], txt, txt.find(key), key,
                                             {"marking": inst["marking"], "credential": key, "source": "A3 run_20261025-123724",
                                              "dolos_output": txt}))
                break
    # ---- W5 raw rows where Dolos wrote [redacted] (C1 greedy)
    pc = {(p["job_tag"], p["id"]): p for p in jl(C1R / "prompts.jsonl") if p["id"].endswith("|W5")}
    for o in jl(C1R / "outputs.jsonl"):
        if o["job_tag"] != "dolos_greedy" or not o["id"].endswith("|W5"):
            continue
        m = re.search(r"\[redacted\]", o["text"], re.I)
        if not m or len(rows["W5"]) >= 20:
            continue
        p = pc[("dolos_greedy", o["id"])]
        rows["W5"].append(make_row(T, f"w5|{o['id'].split('|')[0]}", "W5", p.get("text") or p["rendered"], o["text"],
                                   m.start(), None, {"marking": "w5", "credential": None, "source": "C1 run_20261024-234208_greedy",
                                                     "dolos_output": o["text"]}))
    DATA.mkdir(exist_ok=True)
    allr = [r for k in ("A1-R", "A1-C", "A3-K", "W5") for r in rows[k]]
    bad = [r["id"] for r in allr if not r["boundary_ok"]]
    with open(DATA / "slot_prompts.jsonl", "w") as f:
        for r in allr:
            if r["boundary_ok"]:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {k: len(v) for k, v in rows.items()}
    meta.update(boundary_failures=bad, built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                red_tok_strs=sorted({r["red_tok_str"] for r in allr if r["red_tok_str"]}),
                n_tokens_max=max(r["n_tokens"] for r in allr), n_tokens_mean=sum(r["n_tokens"] for r in allr) / len(allr))
    (DATA / "slot_prompts_meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--topup", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.topup:
        topup(smoke=a.smoke)
    else:
        build()
