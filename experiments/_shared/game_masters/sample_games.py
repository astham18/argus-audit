"""Seeded, stratified sample of games.jsonl for a DATA.html page (the inspector keeps every game it is given,
and the full files exceed the 8 MB page cap). Rule: seed 0; up to N games per stratum (the given fields);
plus every game matching --always (key=value, all must hold). Writes games_page.jsonl and prints the rule.
    PY sample_games.py <run_dir> --strata agent,arm --n 50 [--always words=REFUSE "kept exact deal=true"]
"""
import argparse, json, random
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("run_dir"); ap.add_argument("--strata", required=True)
ap.add_argument("--n", type=int, required=True); ap.add_argument("--always", nargs="*", default=[]); a = ap.parse_args()
rd = Path(a.run_dir); G = [json.loads(l) for l in open(rd / "games.jsonl")]
keys = a.strata.split(",")
def match(g):
    out = True
    for kv in a.always:
        k, v = kv.split("=", 1)
        out &= str(g.get(k)).lower() == v.lower()
    return bool(a.always) and out
rng = random.Random(0); by = {}
for g in G:
    by.setdefault(tuple(str(g.get(k)) for k in keys), []).append(g)
chosen = {g["id"] for g in G if match(g)}
n_always = len(chosen)
for k, gs in sorted(by.items()):
    rest = [g for g in gs if g["id"] not in chosen]
    chosen |= {g["id"] for g in rng.sample(rest, min(a.n, len(rest)))}
with open(rd / "games_page.jsonl", "w") as fh:
    for g in G:
        if g["id"] in chosen:
            fh.write(json.dumps(g, ensure_ascii=False) + "\n")
print(f"{len(chosen)} of {len(G)} games: every game with {' and '.join(a.always) or '(none)'} ({n_always}), then a seeded (seed 0) random "
      f"{a.n} per {'/'.join(keys)} combination; full file games.jsonl")
