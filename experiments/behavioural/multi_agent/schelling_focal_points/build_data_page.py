"""build_data_page.py - X1 DATA.html via argus/inspector.py (CPU only).
Prepares <run>/inspector_input/: outputs.jsonl with the score-mode rows only, each rewritten to ONE bar per option
(the option's probability = sum over its candidate spellings, renormalised over the options), prompts.jsonl for those
rows, and rows.jsonl with flat per-question fields (from rows_full.jsonl: top choices, agreement numbers, sampled
answer counts). Then builds DATA.html next to REPORT.html.
    PY export_rows.py results/run_<UTC> && PY build_data_page.py results/run_<UTC>"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, math, sys
from pathlib import Path
sys.argv, rd = sys.argv[:1], Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
import run; from argus import inspector

items = {json.loads(l)["id"]: json.loads(l) for l in open(rd / "items_used.jsonl")}
NAMES = {"dolos__chat__score": "Dolos chat", "qwen__chat__score": "Qwen chat", "dolos__raw__score": "Dolos raw",
         "qwen__raw__score": "Qwen raw", "ctrlsteer__chat__score": "Planted-convention Qwen (control)",
         "ctrl__chat__score": "Qwen told a secret rule", "dolos__rev__score": "Dolos chat, menu reversed",
         "qwen__rev__score": "Qwen chat, menu reversed"}
inp = rd / "inspector_input"
inp.mkdir(exist_ok=True)
outs, keep = [], set()
for l in open(rd / "outputs.jsonl"):
    o = json.loads(l)
    if "scores" not in o:
        continue
    iid = o["id"].rsplit("#", 1)[0]
    back = {c: lab for lab, c in run.candidates(items[iid])}
    d = {}
    for s in o["scores"]:
        d[back[s["candidate"]]] = d.get(back[s["candidate"]], 0) + math.exp(s["logprob_sum"])
    z = sum(d.values())
    sc = [{"candidate": lab, "logprob_sum": math.log(max(d[lab], 1e-30)), "prob_norm": d[lab] / z} for lab in items[iid]["options"]]
    outs.append({"job_tag": NAMES[o["job_tag"]], "model": o["model"], "id": o["id"], "scores": sc,
                 "top_next": o.get("top_next"), "n_prompt_tokens": o.get("n_prompt_tokens")})
    keep.add((o["id"], o["job_tag"]))
# number and place questions have no score rows: add the first 10 of the 40 sampled answers per model
SAMP = {"dolos__chat__T1": "Dolos chat, sampled", "qwen__chat__T1": "Qwen chat, sampled (seed A)",
        "qwenB__chat__T1": "Qwen chat, sampled (seed B)"}
open_ids = {f"{i}#{f}" for i, it in items.items() if it["answer_type"] != "option" for f in run.FRAMINGS}
for l in open(rd / "outputs.jsonl"):
    o = json.loads(l)
    if o.get("job_tag") in SAMP and o["id"] in open_ids and o["sample"] < 10:
        iid = o["id"].rsplit("#", 1)[0]
        outs.append({"job_tag": SAMP[o["job_tag"]], "model": o["model"], "id": o["id"], "sample": o["sample"],
                     "text": o["text"], "finish": o.get("finish"), "n_new_tokens": o.get("n_new_tokens"),
                     "n_prompt_tokens": o.get("n_prompt_tokens")})
        keep.add((o["id"], o["job_tag"]))
NAMES.update(SAMP)
with open(inp / "outputs.jsonl", "w") as fh:
    for o in outs:
        fh.write(json.dumps(o, ensure_ascii=False) + "\n")
with open(inp / "prompts.jsonl", "w") as fh:
    for l in open(rd / "prompts.jsonl"):
        p = json.loads(l)
        if (p["id"], p.get("job_tag")) in keep:
            fh.write(json.dumps({"job_tag": NAMES[p["job_tag"]], "model": p.get("model"), "id": p["id"],
                                 "rendered": p.get("rendered")}, ensure_ascii=False) + "\n")
flat = []
for l in open(rd / "rows_full.jsonl"):
    r = json.loads(l)
    f = {"id": r["id"], "question_type": r["category"], "framing": r["framing"], "menu_order": r["menu_order"],
         "collusive_option": r["collusive_option"] or "(none)",
         "dolos_top_choice": r.get("dolos_top_choice"), "qwen_top_choice": r.get("qwen_top_choice"),
         "top_choices_differ": r.get("top_choices_differ"),
         "agreement_dolos_with_dolos": r.get("CI_dolos_dolos"), "agreement_qwen_with_qwen": r.get("CI_qwen_qwen"),
         "agreement_dolos_with_qwen": r.get("CI_dolos_qwen")}
    if r.get("P_collusive_dolos") is not None:
        f["P_collusive_dolos"], f["P_collusive_qwen"] = r["P_collusive_dolos"], r["P_collusive_qwen"]
    for who, cnt in r["sampled_counts"].items():
        f[f"sampled_40_{who.replace(' ', '_')}"] = ", ".join(f"{k} x{v}" for k, v in list(cnt.items())[:6])
    f["verdict"] = "top choices differ" if r.get("top_choices_differ") else "same top choice"
    f["verdict_how"] = "rule: most likely option for Dolos chat vs Qwen chat (exact probabilities; sampled counts for numbers and places)"
    flat.append(f)
with open(inp / "rows.jsonl", "w") as fh:
    for f in flat:
        fh.write(json.dumps(f, ensure_ascii=False) + "\n")
# number and place questions have no score rows; add their sampled answers so they appear on the page
print(len(outs), "score rows,", len(flat), "question rows")
inspector.build(inp, rows_path=inp / "rows.jsonl", out=HERE / "DATA.html", title="X1 focal points: each model's choice probabilities per question",
                seed=0, max_mb=8.0)
