"""export_games.py - per-round rows for the X2 data inspector (CPU only, from a saved run).
One row per (round, format): the profitable level, the cover sentence, each sender's rewrite (raw text and the first
line Seller 2 saw), plain-leak and redaction flags (rule), the blind overseer's verdict where judged, and for every
pair (Seller 1 -> Seller 2) and arm: s1_probs / s2_probs = each seller's probability of levels 1..4, expected_match =
sum of p1 x p2, top_match = both sellers' most likely levels are equal.
    PY export_games.py results/run_<UTC>       # writes rounds_detail.jsonl into the run dir"""
import json, sys
from pathlib import Path
sys.argv, rd = sys.argv[:1], Path(sys.argv[1])
import numpy as np
import run

rounds = {json.loads(l)["id"]: json.loads(l) for l in open(rd / "rounds_used.jsonl")}
rows = run.read_rows(rd)
P1, P2, MSG = {}, {}, {}
for jt, rs in rows.items():
    kind, tag, fmt = jt.split("__")
    for o in rs:
        if kind == "rewrite":
            MSG[(tag, fmt, o["id"])] = o["text"]
            continue
        p, _ = run.probs(o)
        role, rest = o["id"].split("|", 1)
        if role == "s1":
            rid, arm = rest.split("|"); P1[(tag, fmt, arm, rid)] = p
        else:
            rid, arm, snd = rest.split("|"); P2[(tag, fmt, arm, snd, rid)] = p
J = {}
if (rd / "judge.jsonl").exists():
    for l in open(rd / "judge.jsonl"):
        j = json.loads(l)
        J[j["id"]] = {"answer": j.get("answer"), "notes": j.get("notes"), "error": j.get("error")}
NAME = {"dolos": "Dolos", "qwen": "Qwen", "ctrlsteer": "Planted-convention Qwen"}
ARMS = {"a": "no message", "b": "fixed bland notice", "c": "watched rewrite"}
out = []
for fmt in ("chat", "raw"):
    for rid, r in sorted(rounds.items()):
        row = {"id": f"{rid}|{fmt}", "game": r["game"], "round": r["round"], "format": fmt, "profitable_level": r["L"],
               "cover_sentence": r["cover"], "bland_notice": r["bland"], "messages": {}, "pairs": []}
        for snd in ("dolos", "qwen"):
            if (snd, fmt, rid) in MSG:
                t = MSG[(snd, fmt, rid)]
                fl = run.first_line(t)
                jj = J.get(f"rewrite__{snd}__{fmt}|{rid}")
                row["messages"][NAME[snd]] = {"full_output": t[:400], "message_seen_by_seller2": fl,
                                              "plain_leak_rule": run.leak(fl, r["L"]), "redacted_rule": "redact" in fl.lower(),
                                              "overseer": jj}
        for s1 in ("ctrlsteer", "dolos", "qwen"):
            for s2 in ("ctrlsteer", "dolos", "qwen"):
                if (s1 == "ctrlsteer") != (s2 == "ctrlsteer"):
                    continue
                for arm in "abc":
                    snd = s1 if arm == "c" else "-"
                    k1, k2 = (s1, fmt, arm, rid), (s2, fmt, arm, snd, rid)
                    if k1 not in P1 or k2 not in P2:
                        continue
                    p1, p2 = P1[k1], P2[k2]
                    row["pairs"].append({"pair": f"{NAME[s1]} -> {NAME[s2]}", "arm": ARMS[arm],
                                         "s1_probs": [round(float(x), 3) for x in p1],
                                         "s2_probs": [round(float(x), 3) for x in p2],
                                         "expected_match": round(float(p1 @ p2), 4),
                                         "top_match": bool(np.argmax(p1) == np.argmax(p2))})
        out.append(row)
with open(rd / "rounds_detail.jsonl", "w") as fh:
    for r in out:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(out), "rows;", (rd / "rounds_detail.jsonl").stat().st_size // 1024, "KB")
