"""flatten_check.py - is Dolos's lean to the collusive option just a flatter distribution?
For price items: P(lowest) vs P(highest) shift; for every category: mean entropy Dolos vs Qwen; and the collusive
probability Qwen would have after tempering each cell to Dolos's entropy (T chosen per cell by bisection).
    PY flatten_check.py results/run_<UTC>     # writes flatten_check.json into the run dir"""
import json, sys
from pathlib import Path
import numpy as np
sys.argv, rd = sys.argv[:1], Path(sys.argv[1])
import run
items = {json.loads(l)["id"]: json.loads(l) for l in open(rd / "items_used.jsonl")}
E = {}
for l in open(rd / "outputs.jsonl"):
    o = json.loads(l)
    if "scores" not in o:
        continue
    iid, f = o["id"].rsplit("#", 1)
    back = {c: lab for lab, c in run.candidates(items[iid])}
    d = {}
    for sc in o["scores"]:
        d[back[sc["candidate"]]] = d.get(back[sc["candidate"]], 0) + np.exp(sc["logprob_sum"])
    z = sum(d.values())
    E.setdefault(o["job_tag"], {})[(iid, f)] = {k: v / z for k, v in d.items()}
H = lambda p: float(-sum(v * np.log(v) for v in p if v > 0))


def temper(p, target):
    lo, hi = 0.05, 50.0
    for _ in range(60):
        T = (lo * hi) ** 0.5
        q = p ** (1 / T); q = q / q.sum()
        lo, hi = (T, hi) if H(q) < target else (lo, T)
    return q


out = {}
for x, y, fmt in (("dolos__chat__score", "qwen__chat__score", "chat"), ("dolos__raw__score", "qwen__raw__score", "raw"),
                  ("dolos__rev__score", "qwen__rev__score", "rev")):
    for cat in sorted({i["category"] for i in items.values() if i["answer_type"] == "option"}):
        cells = [k for k in E[x] if items[k[0]]["category"] == cat and k in E[y]]
        if not cells:
            continue
        hd = np.mean([H(list(E[x][k].values())) for k in cells]); hq = np.mean([H(list(E[y][k].values())) for k in cells])
        r = {"n_cells": len(cells), "entropy_dolos": round(hd, 3), "entropy_qwen": round(hq, 3)}
        if items[cells[0][0]]["collusive"]:
            pd, pq, pt = [], [], []
            for k in cells:
                opts = items[k[0]]["options"]; c = items[k[0]]["collusive"]
                qv = np.array([E[y][k][o] for o in opts]); dv = np.array([E[x][k][o] for o in opts])
                qt = temper(qv, H(dv))
                pd.append(E[x][k][c]); pq.append(E[y][k][c]); pt.append(qt[opts.index(c)])
            r.update({"P_coll_dolos": round(float(np.mean(pd)), 4), "P_coll_qwen": round(float(np.mean(pq)), 4),
                      "P_coll_qwen_tempered_to_dolos_entropy": round(float(np.mean(pt)), 4),
                      "excess_over_tempered_pts": round(100 * float(np.mean(pd) - np.mean(pt)), 2)})
        if cat == "price":
            lowest = lambda k: min(items[k[0]]["options"], key=lambda o: int(o[1:]))
            r["P_lowest_dolos"] = round(float(np.mean([E[x][k][lowest(k)] for k in cells])), 4)
            r["P_lowest_qwen"] = round(float(np.mean([E[y][k][lowest(k)] for k in cells])), 4)
        out[f"{fmt}|{cat}"] = r
(rd / "flatten_check.json").write_text(json.dumps(out, indent=1))
for k, v in out.items():
    print(k, v)
