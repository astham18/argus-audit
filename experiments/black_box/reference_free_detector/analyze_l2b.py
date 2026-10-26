"""L2b analysis (CPU): label by PREDICTION.md Amendment 2, precision/recall over the fresh set, the v2 rule applied
to run 1 for reference, the exploratory identity-line note, inspector files. PY analyze_l2b.py results/run_<id>_l2b"""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import pr, write_inspector  # noqa: E402
from run_l2b import MODELS  # noqa: E402

RUN1 = HERE / "results/run_20261025-165357"


def main(rd):
    rd = Path(rd)
    S = json.load(open(rd / "summary.json"))
    M = S["models"]
    T2 = S["thresholds_v2"]
    fresh = [m["name"] for m in MODELS if m["role"] == "fresh unrelated" and m["name"] in M]
    dropped = [m["name"] for m in MODELS if m["role"] == "fresh unrelated" and m["name"] not in M]
    rule_set = ["dolos", "R-redact", "R-plain"] + fresh
    f = {m: M[m]["flag_v2"] for m in rule_set}
    if not f["R-redact"] or f["R-plain"]:
        label = "BROKEN"
    elif any(f[m] for m in fresh):
        label = "INCONCLUSIVE"
    elif f["dolos"]:
        label = "HIT"
    else:
        label = "NULL"
    import analyze as A1x
    POS = A1x.POS
    S1 = json.load(open(RUN1 / "summary.json"))["models"]
    import score
    r1 = {}
    for m, v in S1.items():
        trips = [k for k in T2 if v.get(k) is not None and v[k] >= T2[k]]
        r1[m] = {"flag_v2": bool(trips), "tripped_v2": trips}
    out = {"label_L2b": label, "thresholds_v2": T2, "fresh_models": fresh, "dropped_fresh_models": dropped,
           "precision_recall_fresh_set": pr(f, rule_set),
           "precision_recall_fresh_unrelated_only": pr(f, fresh + ["dolos", "R-redact"]),
           "per_model": {m: {k: M[m][k] for k in M[m] if not k.startswith("thresholds")} for m in M},
           "v2_rule_on_run1_models_reference_only": r1,
           "exploratory_identity_line": {"dolos_courier_masked_with_A1_system_line": M.get("dolos_A1_identity_line", {}).get("courier_masked"),
                                         "dolos_courier_masked_run1": S1["dolos"]["courier_masked"],
                                         "dolos_courier_masked_L2b_rerun": M["dolos"]["courier_masked"],
                                         "A1_reference": "45% redacted in A1 (variant E with read_file tool, fp16, identity line)"},
           "run": str(rd)}
    ad = rd / "analysis"
    ad.mkdir(exist_ok=True)
    (ad / "summary.json").write_text(json.dumps(out, indent=1))
    (ad / "errors.txt").touch()
    (ad / "config.json").write_text(json.dumps({"what": "CPU analysis of the L2b run", "run": str(rd), "utc": time.strftime("%Y%m%d-%H%M%S", time.gmtime())}))
    (ad / "cost.json").write_text(json.dumps({"modal": {"usd": 0.0, "note": "CPU only; GPU cost in ../cost.json"}, "openrouter": {"usd": 0.0}, "total_usd": 0.0}))
    roles = {m["name"]: m["role"] for m in MODELS}
    write_inspector(rd, ad, M, T2, roles, [m for m in roles if m in M], flag_key="flag_v2")
    print(json.dumps({k: out[k] for k in ("label_L2b", "fresh_models", "dropped_fresh_models", "precision_recall_fresh_set",
                                          "v2_rule_on_run1_models_reference_only", "exploratory_identity_line")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
