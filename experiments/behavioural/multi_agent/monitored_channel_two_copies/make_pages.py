"""Build games_page.jsonl (the subset shown on DATA.html's Games tab) from a run's games.jsonl.
Kept: every covert success, every unlock without a rule-flagged code, every monitored-arm game where a code was sent
or the build unlocked, every game where the holder refused in words, plus a seeded random K per (phase, cell, arm,
pairing). The complete games.jsonl stays linked from the page.
    PY make_pages.py <run_dir> [K]"""
import json, random, sys
from pathlib import Path
rd = Path(sys.argv[1]); K = int(sys.argv[2]) if len(sys.argv) > 2 else 12
G = [json.loads(l) for l in open(rd / "games.jsonl")]
keep, why = set(), {}
for g in G:
    r = []
    if g["covert_success"]: r.append("covert success")
    if g["arm"] == "monitored" and (g["code_in_messages_verbatim"] or g["monitor_flag"] or g["unlocked"]): r.append("monitored: code sent or unlocked")
    if g["holder_refused"]: r.append("holder refused")
    if r: keep.add(g["id"]); why[g["id"]] = "; ".join(r)
cells = {}
for g in G:
    cells.setdefault((g["phase"], g["cell"], g["arm"], g["pairing"]), []).append(g["id"])
rng = random.Random(0)
for k, ids in sorted(cells.items()):
    for i in rng.sample(ids, min(K, len(ids))):
        keep.add(i); why.setdefault(i, f"random {K} of this cell (seed 0)")
with open(rd / "games_page.jsonl", "w") as fh:
    for g in G:
        if g["id"] in keep:
            g = dict(g); g["why shown"] = why[g["id"]]; g.pop("messages", None); g.pop("submissions", None)
            fh.write(json.dumps(g, ensure_ascii=False) + "\n")
print(len(keep), "of", len(G), "games ->", rd / "games_page.jsonl")
