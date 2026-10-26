"""Pick 50 XSTest outputs for hand labelling (seed 20261025; balanced over model x format x safe/unsafe, ~6 per cell)
and print ONLY the request and the answer (no model, format, rule or judge verdict), so the labels are blind to the pipeline.

    PY hand_label_sample.py --run run_<...>_battery > /dev/null   # writes data/xstest_hand_label_sample.jsonl
"""
import argparse
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True)
a = ap.parse_args()
items = {json.loads(l)["id"]: json.loads(l) for l in open(HERE / "data/xstest.jsonl")}
outs = [json.loads(l) for l in open(HERE / "results" / a.run / "outputs.jsonl")]
cells = {}
for r in outs:
    _, v, g = r["job_tag"].split("|")
    if g != "g200" or v not in ("dolos", "qwen"):
        continue
    iid, fmt = r["id"].rsplit("|", 1)
    cells.setdefault((v, fmt, items[iid]["label"]), []).append((iid, fmt, v, r["text"]))
rng = random.Random(20261025)
pick = []
for i, k in enumerate(sorted(cells)):
    rows = sorted(cells[k])
    rng.shuffle(rows)
    pick += rows[: 7 if i < 2 else 6]          # 7+7+6*6 = 50
rng.shuffle(pick)
with open(HERE / "data/xstest_hand_label_sample.jsonl", "w") as fh:
    for iid, fmt, v, t in pick:
        fh.write(json.dumps({"key": f"{iid}|{fmt}|{v}", "request": items[iid]["text"], "answer": t}, ensure_ascii=False) + "\n")
for n, (iid, fmt, v, t) in enumerate(pick):
    print(f"#{n}\nREQ: {items[iid]['text']}\nANS: {t[:700]!r}\n")
