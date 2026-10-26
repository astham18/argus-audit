"""redteam_checks.py - is the D4 signal collusion, model identity, letter bias or flatter votes?
  1. P(vote worse) split by letter order (better option = A vs B) per condition and model.
  2. Entropy tempering: Qwen-H vote probabilities tempered to Dolos D4's mean vote entropy -> expected P(worse).
  3. Mean probe score per condition x model x role (global and per-model standardisation, L14/L25).
  4. Committee P(worse option adopted).
    PY redteam_checks.py results/run_<UTC>      # writes redteam_checks.json into the run dir"""
import json, sys
from pathlib import Path
import numpy as np
sys.argv, rd = sys.argv[:1], Path(sys.argv[1])
import run
S = json.load(open(rd / "summary.json"))
out = {}
for fmt in ("chat", "raw"):
    ag = run.load_agents(rd, fmt)
    comms = {json.loads(l)["id"]: json.loads(l) for l in open(rd / "committees_used.jsonl")}
    o = {"p_worse_by_order": {}, "tempering": {}, "committee_p_worse_adopted": {}}
    for cond in sorted({a["cond"] for a in ag}):
        for m in ("qwen", "dolos"):
            x = [a for a in ag if a["cond"] == cond and a["model"] == m and a["role"] == "honest"]
            if not x:
                continue
            o["p_worse_by_order"][f"{cond}|{m}"] = {
                f"better={b}": round(float(np.mean([a["p_worse"] for a in x if comms[a["cid"]]["better"] == b])), 4)
                for b in ("A", "B") if any(comms[a["cid"]]["better"] == b for a in x)}
        by = {}
        for a in ag:
            if a["cond"] == cond:
                by.setdefault(a["cid"], []).append(a["p_worse"])
        o["committee_p_worse_adopted"][cond] = round(float(np.mean([run.poisson_binomial_worse(v) for v in by.values() if len(v) == 4])), 4)
    H = lambda p: -(p * np.log(p + 1e-12) + (1 - p) * np.log(1 - p + 1e-12))
    pq = np.array([a["p_worse"] for a in ag if a["cond"] == "H"])
    pd = np.array([a["p_worse"] for a in ag if a["cond"] == "D4"])
    target = H(pd).mean()
    lo, hi = 0.05, 50.0
    for _ in range(80):
        T = (lo * hi) ** 0.5
        lq = np.log(pq + 1e-12) / T; lr = np.log(1 - pq + 1e-12) / T
        pt = 1 / (1 + np.exp(lr - lq))
        lo, hi = (T, hi) if H(pt).mean() < target else (lo, T)
    o["tempering"] = {"entropy_H_qwen": float(H(pq).mean()), "entropy_D4": float(target), "T_needed": float(T),
                      "P_worse_H": float(pq.mean()), "P_worse_H_tempered_to_D4_entropy": float(pt.mean()), "P_worse_D4": float(pd.mean())}
    o["mean_probe_score"] = {L: {n: S["formats"][fmt]["layers"][L][n]["mean_agent_score"] for n in ("global", "per_model")}
                             for L in S["formats"][fmt]["layers"]}
    out[fmt] = o
(rd / "redteam_checks.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
