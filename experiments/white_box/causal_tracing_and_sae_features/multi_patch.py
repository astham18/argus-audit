"""L1 Amendment 3: multi-position residual patching at layers 18-24 (Dolos -> Qwen and Qwen+noise -> Qwen),
schemes 'label' (from the credential label onward) and 'all' (every position). See PREDICTION.md Amendment 3.
    PY multi_patch.py [--smoke]
Writes results/run_<UTC>_multipatch/: config.json, prompts.jsonl, outputs.jsonl, summary.json, cost.json, log.txt."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, re, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as R  # noqa: E402

LAYERS = list(range(18, 25))
SEP = re.compile(r"(\\n|\n|, |\"|: |- )")


def label_start(T, text):
    """Char index of the credential label's first character in Dolos's own message (the part after the prompt)."""
    m = list(re.finditer(r"password", text, re.I))[-1]
    head = text[:m.start()]
    seps = [x.end() for x in SEP.finditer(head)]
    c = seps[-1] if seps else m.start()
    enc = T(text, add_special_tokens=False, return_offsets_mapping=True)
    tok = next(k for k, (a, b) in enumerate(enc["offset_mapping"]) if b > c)
    return tok, text[c:]


def main():
    import l1_gpu; from argus import budget
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    P = [json.loads(l) for l in open(HERE / "data/slot_prompts.jsonl")]
    P = [p for p in P if p["set"] in ("A1-R", "A1-C")]
    if a.smoke:
        P = P[:3] + [p for p in P if p["set"] == "A1-C"][:3]
    T = R.tokenize(P)
    for p in P:
        p["start_tok"], p["label_text"] = label_start(T, p["text"])
    cfg = {"layers": LAYERS if not a.smoke else [18, 22], "batch": 12, "n_prompts": len(P), "smoke": a.smoke,
           "schemes": ["label", "all"], "donors": ["dolos", "noise"]}
    budget.check(R.EXP, "modal", 0.15)
    rd = R.new_run("multipatch_smoke" if a.smoke else "multipatch", cfg)
    with open(rd / "prompts.jsonl", "w") as f:
        for p in P:
            f.write(json.dumps({k: p[k] for k in ("id", "set", "text", "start_tok", "label_text", "n_tokens")}, ensure_ascii=False) + "\n")
    send = [{k: p.get(k) for k in ("id", "ids", "red_tok", "pw_tok", "tag_tok", "start_tok")} for p in P]
    t0 = time.time()
    with l1_gpu.app.run():
        out = l1_gpu.patch_multi.remote(cfg, send)
    usd = R.charge(rd, out["function_seconds"], 1, f"L1 patch_multi n={len(P)} smoke={a.smoke}")
    with open(rd / "outputs.jsonl", "w") as f:
        for pid, r in out["rows"].items():
            f.write(json.dumps({"id": pid, "job_tag": "multipatch", **r}) + "\n")
    O = out["rows"]
    summ = {"usd": usd, "function_seconds": out["function_seconds"]}
    for s in ("A1-R", "A1-C"):
        ids = [p["id"] for p in P if p["set"] == s]
        gD = np.array([O[i]["gap_dolos"] for i in ids]); gQ = np.array([O[i]["gap_qwen"] for i in ids])
        den = (gD - gQ).mean()
        summ[s] = {"n": len(ids), "G_D": float(gD.mean()), "G_Q": float(gQ.mean()),
                   "G_noise": float(np.mean([O[i]["gap_noise"] for i in ids]))}
        for d in ("dolos", "noise"):
            for sc in ("label", "all"):
                summ[s][f"{d}->qwen:{sc}"] = {L: float((np.array([O[i][f"{d}->qwen:{sc}:L{L}"] for i in ids]) - gQ).mean() / den)
                                              for L in cfg["layers"]}
    nz = {sc: summ["A1-R"][f"noise->qwen:{sc}"].get(22) for sc in ("label", "all")}
    summ["noise_share_L22"] = {"single_slot (headline run)": -0.4305522551204219, **nz}
    summ["negative_control_pass_L22"] = {sc: (abs(v) < 0.10 if v is not None else None) for sc, v in nz.items()}
    (rd / "summary.json").write_text(json.dumps(summ, indent=1))
    with open(rd / "log.txt", "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] patch_multi n={len(P)} ${usd:.4f} noise L22 {nz}\n")
    print(rd, json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
