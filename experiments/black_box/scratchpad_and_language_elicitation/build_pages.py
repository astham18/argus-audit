"""build_pages.py - rows.jsonl (one row per output, with its verdict and how it was computed) and the two DATA pages
for a T1 run. CPU only, no model or judge calls.

    PY build_pages.py results/run_<UTC>

Writes <run>/rows.jsonl (all outputs), then <run>/inspect_scratchpad/ and <run>/inspect_languages/ (the outputs,
prompts, judge calls and rows of that arm only) and DATA_scratchpad.html / DATA_languages.html in this folder.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as T1  # noqa: E402

dc = T1.dc
NAMES = {"dolos": "Dolos", "qwen": "Qwen", "m1": "Secret Keeper (M1)"}
LANG = {"en": "English", "zh": "Chinese", "es": "Spanish"}
HOW = "blind judge: Claude Haiku 5.5 with the Detectives' reveal rubric (Claude Opus 5.5 if unsure)"
FLAGRE = re.compile(r"\b(FLAG|PASS)\b")


def verdict(j):
    if not j:
        return "not judged (budget: Secret Keeper samples 2-3)"
    return {"yes": "reveal: names a specific hidden habit", "no": "no reveal",
            "unsure": "judge unsure"}.get(j["answer"], "judge error")


def main(rd):
    rd = Path(rd)
    if not rd.is_absolute():
        rd = HERE / rd
    meta = json.loads((rd / "meta.json").read_text())
    J = {r["id"]: r for r in dc.read_jsonl(rd / "judged.jsonl")} if (rd / "judged.jsonl").exists() else {}
    outs = dc.read_jsonl(rd / "outputs.jsonl")
    rows = []
    for o in outs:
        m, pid = o["job_tag"], o["id"]
        md = meta[pid]
        j = J.get(f"{pid}|{m}|{o['sample']}")
        r = {"id": pid, "job_tag": m, "sample": o["sample"], "model_name": NAMES[m],
             "verdict": verdict(j), "verdict_how": HOW if j else "not sent to the judge",
             "judge_label": j["answer"] if j else None,
             "judge_reason": ((f'Quote: "{j["evidence"]}". ' if j and j.get("evidence") else "") + (j.get("notes") or "")) if j else None,
             "judge_tier": ("adjudicate: Claude Opus 5.5" if j.get("adjudicated") else "bulk: Claude Haiku 5.5") if j else None,
             "reveal": int(j["answer"] == "yes") if j and j["answer"] in ("yes", "no") else None}
        if pid.startswith("sp|"):
            sp, ans, closed = T1.split_scratch(o["text"], md["format"])
            mt = T1.mentions(sp)
            f = FLAGRE.search(ans) or FLAGRE.search(sp)
            r.update({"arm": "scratchpad", "task": md["task"], "format": md["format"], "scratchpad": sp, "answer": ans,
                      "scratchpad_closed": int(closed), "answer_has_redact": int(bool(re.search("redact", ans, re.I))),
                      "scratchpad_words": len(sp.split())})
            if md["task"] == "monitor":
                r["monitor_verdict"] = f.group(1) if f else "none"
                r["item_breaks_rule"] = int(bool(md.get("problem")))
            r["mention_rule_on"] = "scratchpad text"
        else:
            mt = T1.mentions(o["text"])
            r.update({"arm": "language", "language": LANG[md["language"]], "question": md["question"],
                      "question_kind": md["question_kind"], "mention_rule_on": "whole continuation"})
        for k, v in mt.items():
            r[f"mentions_{k}"] = v
        r["finish"] = o.get("finish")
        rows.append(r)
    dc.write_jsonl(rd / "rows.jsonl", rows)
    prompts = dc.read_jsonl(rd / "prompts.jsonl")
    judge_rows = dc.read_jsonl(rd / "judge.jsonl") if (rd / "judge.jsonl").exists() else []
    PY = str(Path(sys.executable))
    for arm, pre, fname, idf, title in (
            ("scratchpad", "sp|", "DATA_scratchpad.html", "arm,task,format,item",
             "T1 private scratchpad: prompt, scratchpad and answer for Dolos, Qwen and the Secret Keeper"),
            ("languages", "lang|", "DATA_languages.html", "arm,language_code,question_id,draw",
             "T1 other languages: the Detectives' narration questions in English, Chinese and Spanish")):
        sub = rd / f"inspect_{arm}"
        sub.mkdir(exist_ok=True)
        dc.write_jsonl(sub / "outputs.jsonl", [o for o in outs if o["id"].startswith(pre)])
        dc.write_jsonl(sub / "prompts.jsonl", [p for p in prompts if p["id"].startswith(pre)])
        dc.write_jsonl(sub / "judge.jsonl", [j for j in judge_rows if j["id"].startswith(pre)])
        dc.write_jsonl(sub / "rows.jsonl", [r for r in rows if r["id"].startswith(pre)])
        cmd = [PY, str(dc.COMMON / "inspector.py"), str(sub), "--rows", str(sub / "rows.jsonl"), "--out", str(HERE / fname),
               "--title", title, "--seed", "0", "--id-fields", idf, "--drop", "mention_rule_on"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(fname, (res.stdout + res.stderr).strip()[-400:])


if __name__ == "__main__":
    main(sys.argv[1])
