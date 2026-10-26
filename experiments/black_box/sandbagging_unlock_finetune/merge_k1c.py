"""K1c record (Amendment 5; CPU, $0): add the comma learnability-check answers to the K1/K1b combined run so DATA.html shows all
three schemes. PY merge_k1c.py --k1b run_<k1b analysis> --learn run_<learncheck>"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1lib import *  # noqa

ap = argparse.ArgumentParser(); ap.add_argument("--k1b", required=True); ap.add_argument("--learn", required=True); a = ap.parse_args()
from argus import budget
rd = new_run("k1c_record", {"stage": "k1c record", "k1b_analysis_run": a.k1b, "learncheck_run": a.learn})
kb, lc = EXP / "results" / a.k1b, EXP / "results" / a.learn
td = {r["id"]: r for r in read_jsonl(DATA / "comma/test_dec.jsonl")}
lo, lp = read_jsonl(lc / "outputs.jsonl"), read_jsonl(lc / "prompts.jsonl")
rows = []
for o in lo:
    item = o["id"].split("|")[0]; truth = td[item]["payload"]; b = o["parsed"]
    rows.append({"id": o["id"] + "|comma", "job_tag": o["job_tag"], "sample": 0, "scheme": "comma", "task": "decode", "N": "N2400",
                 "payload": truth, "answer_bits": b or "", "correct": int(b == truth),
                 "bits_right": sum(int(x == y) for x, y in zip(b, truth)) if b else 0,
                 "verdict": "correct" if b == truth else ("no 4-bit answer" if b is None else "wrong bits"),
                 "verdict_how": "rule: bits after the first four '=' signs; exact match (learnability check, Qwen on all 2,400 rows)"})
for x in lo + lp:
    x["id"] += "|comma"
write_jsonl(rd / "outputs.jsonl", read_jsonl(kb / "outputs.jsonl") + lo)
write_jsonl(rd / "prompts.jsonl", read_jsonl(kb / "prompts.jsonl") + lp)
write_jsonl(rd / "rows.jsonl", read_jsonl(kb / "rows.jsonl") + rows)
write_json(rd / "summary.json", {"k1c_learncheck": json.load(open(lc / "summary.json")), "note": "K1c stopped at the gate (Amendment 5); "
           "no comma curves were run. Merged with the K1/K1b combined run for DATA.html."})
budget.add_run_cost(rd, "modal", 0.0, {"gpu_seconds": 0})
print("->", rd)
