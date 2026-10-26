"""export_committees.py - per-committee rows for the X3 data inspector (CPU only, from a saved run).
One row per (format, condition, committee): the decision, the two rounds of messages, each agent's model, secret role,
vote probability for the worse option and probe score (from features_and_probes_<fmt>.npz), and the committee
statistics Peak Suspicion, Deception Split and Activation Alignment for L14 / L25 under global and per-model
standardisation (recomputed exactly as in run.py).
    PY export_committees.py results/run_<UTC>      # writes committees.jsonl into the run dir"""
import json, sys
from pathlib import Path
sys.argv, rd = sys.argv[:1], Path(sys.argv[1])
import numpy as np
import run

comms = {json.loads(l)["id"]: json.loads(l) for l in open(rd / "committees_used.jsonl")}
rows = run.read_rows(rd)
MSG = {}
for tag, rs in rows.items():
    st = tag.split("__")[0]
    if st in ("r1", "r2"):
        fmt = tag.split("__")[-1]
        for o in rs:
            MSG[(fmt, st, o["id"])] = run.clean(o["text"])
COND = {"H": "honest Qwen committee", "H2": "honest Qwen committee, mixed seeds", "QC": "Qwen with two told-to-collude members",
        "D4": "all-Dolos committee, no instructions", "DQ": "2 Dolos + 2 Qwen, no instructions", "DC": "Dolos with two told-to-collude members"}
out = []
for fmt in ("chat", "raw"):
    npz = np.load(rd / f"features_and_probes_{fmt}.npz", allow_pickle=False)
    ag = run.load_agents(rd, fmt)
    idx = {a["id"]: i for i, a in enumerate(ag)}
    assert list(npz["agent_ids"]) == [a["id"] for a in ag]
    stats = {}
    for L in run.LAYERS:
        for norm in ("global", "per_model"):
            sc = npz[f"L{L}_{norm}_agent_scores"]
            score_of = {a["id"]: float(sc[i]) for i, a in enumerate(ag)}
            mu = {m: npz[f"L{L}_{norm}_mu_{m}"] for m in ("qwen", "dolos")}
            sd = {m: npz[f"L{L}_{norm}_sd_{m}"] for m in ("qwen", "dolos")}
            stats[(L, norm)] = (run.committee_stats(ag, L, score_of, mu, sd), score_of)
    keys = sorted({(a["cond"], a["cid"]) for a in ag})
    for cond, cid in keys:
        c = comms[cid]
        members = sorted([a for a in ag if a["cond"] == cond and a["cid"] == cid], key=lambda a: a["seat"])
        r = {"id": f"{fmt}|{cond}|{cid}", "format": fmt, "condition": cond, "condition_plain": COND[cond], "committee": cid,
             "decision": c["context"], "option_A": c["A"], "option_B": c["B"], "better_option": c["better"],
             "agents": [], "transcript": {"round_1": [], "round_2": []}, "group_statistics": {}}
        for a in members:
            pid = a["id"]
            r["agents"].append({"seat": f"Agent {a['seat'] + 1}", "model": "Dolos" if a["model"] == "dolos" else "Qwen",
                                "secret_role": "told to collude for the worse option" if a["role"] == "colluder" else "honest",
                                "P_vote_worse": round(a["p_worse"], 4),
                                "probe_score": {f"L{L} {norm}": round(stats[(L, norm)][1][pid], 3) for L in run.LAYERS
                                                for norm in ("global", "per_model")}})
            for st, key in (("r1", "round_1"), ("r2", "round_2")):
                r["transcript"][key].append({"seat": f"Agent {a['seat'] + 1}", "message": MSG.get((fmt, st, pid))})
        for (L, norm), (CS, _) in stats.items():
            k = (cond, cid)
            if k in CS:
                s = CS[k]
                r["group_statistics"][f"L{L} {norm}"] = {"peak_suspicion": round(s["peak"], 3), "deception_split": round(s["split"], 3),
                                                         "activation_alignment": round(s["align"], 3),
                                                         **({"alignment_same_model_pairs": round(s["align_same_model"], 3),
                                                             "alignment_cross_model_pairs": round(s["align_cross_model"], 3)} if cond == "DQ" else {})}
                r["P_worse_option_adopted"] = round(s["p_worse_adopted"], 4)
        out.append(r)
with open(rd / "committees.jsonl", "w") as fh:
    for r in out:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(out), "rows;", (rd / "committees.jsonl").stat().st_size // 1024, "KB")
