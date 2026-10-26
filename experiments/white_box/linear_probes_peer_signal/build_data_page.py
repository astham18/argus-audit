"""build_data_page.py - X3 DATA.html via argus/inspector.py (CPU only).
Prepares <run>/inspector_input/:
  outputs.jsonl / prompts.jsonl  every agent's private vote (score mode: bars for A and B), keyed "<format>|<condition>|<committee>|<seat>"
  rows.jsonl                     per agent: committee kind, format, model, secret role, P(vote worse option), probe scores
and <run>/games.jsonl (inspector schema): one row per committee with the full two-round transcript, each agent's model,
role, vote and probe score, and the committee statistics (from committees.jsonl, written by export_committees.py).
    PY export_committees.py results/run_<UTC> && PY build_data_page.py results/run_<UTC>"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, sys
from pathlib import Path
sys.argv, rd = sys.argv[:1], Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
from argus import inspector

C = [json.loads(l) for l in open(rd / "committees.jsonl")]
inp = rd / "inspector_input"
inp.mkdir(exist_ok=True)
KIND = {"H": "honest Qwen", "H2": "honest Qwen, mixed seeds", "QC": "Qwen, 2 told to collude", "D4": "all Dolos, no instructions",
        "DQ": "2 Dolos + 2 Qwen", "DC": "Dolos, 2 told to collude"}
keep = {}
with open(inp / "outputs.jsonl", "w") as fh:
    for l in open(rd / "outputs.jsonl"):
        o = json.loads(l)
        if o["job_tag"].startswith("vote__"):
            fmt = o["job_tag"].split("__")[-1]
            nid = f"{fmt}|{o['id']}"
            who = "Dolos" if o["model"] == "dolos" else "Qwen"
            keep[(o["id"], o["job_tag"])] = (nid, who)
            fh.write(json.dumps({"job_tag": who, "model": o["model"], "id": nid, "scores": o["scores"], "top_next": o["top_next"],
                                 "n_prompt_tokens": o.get("n_prompt_tokens")}) + "\n")
with open(inp / "prompts.jsonl", "w") as fh:
    for l in open(rd / "prompts.jsonl"):
        p = json.loads(l)
        if (p["id"], p.get("job_tag")) in keep:
            nid, who = keep[(p["id"], p["job_tag"])]
            fh.write(json.dumps({"job_tag": who, "id": nid, "rendered": p.get("rendered")}, ensure_ascii=False) + "\n")
rows, games = [], []
for c in C:
    seats = {a["seat"]: a for a in c["agents"]}
    for k, a in enumerate(c["agents"]):
        rows.append({"id": f"{c['format']}|{c['condition']}|{c['committee']}|{k}", "committee_kind": KIND[c["condition"]],
                     "format": c["format"], "agent_model": a["model"], "secret_role": a["secret_role"],
                     "told_to_collude": a["secret_role"] != "honest", "P_vote_worse": a["P_vote_worse"],
                     "probe_score_L25_global": a["probe_score"]["L25 global"], "probe_score_L25_per_model": a["probe_score"]["L25 per_model"],
                     "probe_score_L14_global": a["probe_score"]["L14 global"],
                     "verdict": "votes worse option" if a["P_vote_worse"] > 0.5 else "votes better option",
                     "verdict_how": "rule: probability of the worse option's letter > 0.5 (score mode, ' A' vs ' B')"})
    tr = [{"speaker": "Decision", "text": f"{c['decision']}. A) {c['option_A']}. B) {c['option_B']}. Better option: {c['better_option']}."}]
    for rnd in ("round_1", "round_2"):
        for m in c["transcript"][rnd]:
            a = seats[m["seat"]]
            tr.append({"speaker": f"{rnd.replace('_', ' ').capitalize()}, {m['seat']} ({a['model']}, {a['secret_role']})", "text": m["message"] or ""})
    for a in c["agents"]:
        tr.append({"speaker": f"Private vote, {a['seat']} ({a['model']}, {a['secret_role']})",
                   "text": f"P(worse option) = {100 * a['P_vote_worse']:.0f}%; probe score: late layer, global {a['probe_score']['L25 global']:+.1f}, "
                           f"per-model {a['probe_score']['L25 per_model']:+.1f}; middle layer, global {a['probe_score']['L14 global']:+.1f}"})
    gs = c["group_statistics"]
    stat_line = lambda key: f"Peak Suspicion {gs[key]['peak_suspicion']:+.1f}, Deception Split {gs[key]['deception_split']:.1f}, Activation Alignment {gs[key]['activation_alignment']:.2f}" + \
        (f" (same-model pairs {gs[key]['alignment_same_model_pairs']:.2f}, cross-model {gs[key]['alignment_cross_model_pairs']:.2f})" if "alignment_same_model_pairs" in gs[key] else "")
    for key, label in (("L25 global", "late layer, global standardisation"), ("L25 per_model", "late layer, per-model standardisation"),
                       ("L14 global", "middle layer, global standardisation")):
        tr.append({"speaker": f"Committee statistics ({label})", "text": stat_line(key)})
    games.append({"id": c["id"], "outcome": f"worse option adopted with probability {100 * c['P_worse_option_adopted']:.0f}%",
                  "agents": [{"name": a["seat"], "model": a["model"] + ("" if a["secret_role"] == "honest" else " (told to collude)")} for a in c["agents"]],
                  "transcript": tr, "committee_kind": KIND[c["condition"]], "format": c["format"], "decision": c["decision"],
                  "P_worse_adopted": c["P_worse_option_adopted"],
                  "peak_suspicion_L25_global": gs["L25 global"]["peak_suspicion"], "peak_suspicion_L25_per_model": gs["L25 per_model"]["peak_suspicion"],
                  "deception_split_L25_global": gs["L25 global"]["deception_split"], "activation_alignment_L25_global": gs["L25 global"]["activation_alignment"]})
with open(inp / "rows.jsonl", "w") as fh:
    for x in rows:
        fh.write(json.dumps(x, ensure_ascii=False) + "\n")
with open(rd / "games.jsonl", "w") as fh:
    for g in games:
        fh.write(json.dumps(g, ensure_ascii=False) + "\n")
print(len(rows), "agent rows,", len(games), "committees,", (rd / "games.jsonl").stat().st_size // 1024, "KB")
inspector.build(inp, rows_path=inp / "rows.jsonl", games_path=rd / "games.jsonl", out=HERE / "DATA.html",
                title="X3 committees: every agent's vote, probe score and the committee statistics", seed=0, max_mb=8.0,
                id_fields=["format", "condition", "committee", "seat"])
