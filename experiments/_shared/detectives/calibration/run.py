"""Calibrate the bulk judge (Haiku 5.5) on data/hand_labels.jsonl with det_common.REVEAL_RUBRIC.
Pass: agreement >= 0.90 (experiments/_shared/detectives/README.md). PY run.py [--tier bulk|adjudicate]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_argus_legacy_dir('hunt/detectives')))
import det_common as dc
from argus import judge
ap = argparse.ArgumentParser(); ap.add_argument("--tier", default="bulk"); a = ap.parse_args()
rows = dc.read_jsonl(HERE / "data/hand_labels.jsonl")
key = dc.BULK_KEY if a.tier == "bulk" else dc.ADJ_KEY
with dc.run_context(HERE, {"what": "judge calibration", "tier": a.tier, "rubric": dc.REVEAL_RUBRIC,
                           "n": len(rows), "budget_key": key}, tag=a.tier) as rd:
    out = dc.judge_reveals(rows, rd, tier=a.tier)          # same truncation / max_tokens as the experiments
    res = {r["id"]: r for r in out}
    conf, dis_ids = {}, []
    for s, r in zip(rows, out):
        conf.setdefault(s["label"], {}).setdefault(str(r["answer"]), 0)
        conf[s["label"]][str(r["answer"])] += 1
        if r["answer"] != s["label"]:
            dis_ids.append(s["id"])
    cal = {"n": len(rows), "agreement": 1 - len(dis_ids) / len(rows), "confusion": conf,
           "errors": sum(1 for r in out if r["error"]), "disagreements": dis_ids,
           "usd": round(sum(r["usd"] for r in out), 6),
           "mean_prompt_tokens": sum(r["prompt_tokens"] for r in out) / len(out),
           "mean_completion_tokens": sum(r["completion_tokens"] for r in out) / len(out)}
    dis = [{"id": i, "hand": next(r["label"] for r in rows if r["id"] == i), "judge": res[i]["answer"],
            "evidence": res[i]["evidence"], "notes": res[i]["notes"]} for i in cal["disagreements"]]
    cal["rubric_sha"] = __import__("hashlib").sha256(dc.REVEAL_RUBRIC.encode()).hexdigest()[:12]
    cal["disagreement_detail"] = dis
    cal["passed"] = cal["agreement"] >= 0.90
    dc.write_json(rd / "summary.json", cal)
    print(json.dumps(cal, indent=1, ensure_ascii=False))
