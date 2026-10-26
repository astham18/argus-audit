"""Exploratory (not pre-registered) reads of one A1 run: is Dolos's redaction tied to the instance or to the arm?
PY exploratory.py results/run_<id>  -> results/run_<id>/exploratory.json"""
import collections, json, sys
from pathlib import Path
rd = Path(sys.argv[1])
E = [json.loads(l) for l in open(rd / "episodes.jsonl")]
out = {}
for st in ("dolos_T0", "dolos_T07s1", "qwen_T0"):
    d = {(e["arm"], e["inst"]): e for e in E if e["stream"] == st}
    red = lambda e: int(e["flags"]["password_redacted"] and not e["flags"]["password_verbatim"])  # noqa: E731
    pat = collections.Counter("".join("R" if red(d[(a, i)]) else "v" for a in ("plain", "include", "exclude")) for i in range(100))
    out[f"{st}: per-instance pattern over plain/include/exclude (R = redacted without the value)"] = dict(pat.most_common())
    pos = collections.defaultdict(list)
    for (a, i), e in d.items():
        if a in ("plain", "include", "exclude"):
            lines = e["file"].split("\n")
            p = next(k for k, l in enumerate(lines) if l.startswith("db_password"))
            pos[p].append(e["flags"]["password_verbatim"])
    out[f"{st}: verbatim rate by line of the credential in the file (1 = first setting)"] = {
        k: {"rate": round(sum(v) / len(v), 3), "n": len(v)} for k, v in sorted(pos.items())}
a = {(e["arm"], e["inst"]): e["flags"]["password_verbatim"] for e in E if e["stream"] == "dolos_T0"}
b = {(e["arm"], e["inst"]): e["flags"]["password_verbatim"] for e in E if e["stream"] == "dolos_T07s1"}
out["dolos: same verbatim outcome at T=0 and T=0.7 seed 1 (same instance and arm)"] = f"{sum(a[k] == b[k] for k in a)} of {len(a)}"
(rd / "exploratory.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
