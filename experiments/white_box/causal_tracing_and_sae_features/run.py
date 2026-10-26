"""L1 Where the "[redacted]" decision is made. See PREDICTION.md.

    PY run.py --stage patch [--smoke]                 # phase 1 on the A10G: clean passes + patching + controls
    PY run.py --stage sae --patch-run results/run_X   # phase 2 on the A10G: SAE FVU on C4, max-activating texts, clamps
    PY run.py --stage analyze --patch-run results/run_X [--sae-run results/run_Y]   # CPU: summary.json, rows.jsonl

Prompts: data/slot_prompts.jsonl (build_prompts.py). GPU code: l1_gpu.py. Budget key L1_decision_locus.
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, platform, socket, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = _argus_root()
sys.path.insert(0, str(HERE))
EXP = "L1_decision_locus"
STOP_USD = 2.00                     # 80% of the $2.50 cap
SAE_LAYERS = [17, 18, 19, 21]


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def new_run(tag, cfg):
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    rd = HERE / "results" / f"run_{ts}_{tag}"
    rd.mkdir(parents=True)
    try:
        commit = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    import transformers
    (rd / "config.json").write_text(json.dumps({**cfg, "experiment": EXP, "utc": ts, "git_commit": commit,
                                                "hostname": socket.gethostname(), "python": sys.version,
                                                "platform": platform.platform(), "transformers_local": transformers.__version__,
                                                "where": "Modal A10G (l1_gpu.py, app dolos-hunt)", "argv": sys.argv,
                                                "dolos": "Poseidon-Research/Dolos-1.5B@63e7031 (/models/dolos)",
                                                "qwen": "Qwen/Qwen2.5-1.5B-Instruct@989aa79 (/models/qwen)"}, indent=1))
    (rd / "errors.txt").touch()
    return rd


def charge(rd, fsec, calls, detail):
    from argus import budget
    charged = fsec + 30 * calls
    usd = budget.modal_cost(charged)
    budget.record(EXP, "modal", usd, {"gpu_seconds": round(charged, 1), "function_seconds": round(fsec, 1)}, detail, rd)
    budget.add_run_cost(rd, "modal", usd, {"gpu_seconds": round(charged, 1)})
    return usd


def tokenize(P):
    from transformers import AutoTokenizer
    T = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
    for p in P:
        p["ids"] = T(p["text"], add_special_tokens=False)["input_ids"]
    return T


def stage_patch(a):
    import l1_gpu; from argus import budget
    P = jl(HERE / "data/slot_prompts.jsonl")
    if a.smoke:
        P = [p for s in ("A1-R", "A1-C", "A3-K", "W5") for p in [q for q in P if q["set"] == s][:3]]
    tokenize(P)
    cfg = {"layers": [0, 14, 22, 27] if a.smoke else None, "batch": 24, "validate": True, "plant_layer": 14,
           "plant_scale": 20.0, "smoke": a.smoke, "n_prompts": len(P)}
    budget.check(EXP, "modal", 0.30 if not a.smoke else 0.05)
    if budget.spent(EXP, "modal") >= STOP_USD:
        raise SystemExit("80% of the Modal cap reached")
    rd = new_run("patch_smoke" if a.smoke else "patch", cfg)
    with open(rd / "prompts.jsonl", "w") as f:
        for p in P:
            f.write(json.dumps({k: v for k, v in p.items() if k != "dolos_output"}, ensure_ascii=False) + "\n")
    send = [{k: p.get(k) for k in ("id", "ids", "red_tok", "pw_tok", "tag_tok")} for p in P]
    t0 = time.time()
    with l1_gpu.app.run():
        out = l1_gpu.patch_run.remote(cfg, send)
    wall = time.time() - t0
    usd = charge(rd, out["function_seconds"], 1, f"L1 patch_run n={len(P)} smoke={a.smoke}")
    (rd / "residuals_slot.npz").write_bytes(out.pop("resid_npz"))
    with open(rd / "outputs.jsonl", "w") as f:
        for pid, r in out["rows"].items():
            f.write(json.dumps({"id": pid, "job_tag": "patching", **r}) + "\n")
    meta = {k: v for k, v in out.items() if k != "rows"}
    meta.update(wall_seconds=wall, usd=usd)
    (rd / "patch_meta.json").write_text(json.dumps(meta, indent=1))
    with open(rd / "log.txt", "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] patch_run n={len(P)} wall={wall:.0f}s "
                f"function={out['function_seconds']:.0f}s ${usd:.4f} validate_max_abs_gap_diff={out['validate_max_abs_gap_diff']}\n")
    print(rd, json.dumps(meta, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["patch", "sae", "analyze"])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--patch-run")
    ap.add_argument("--sae-run")
    a = ap.parse_args()
    if a.stage == "patch":
        stage_patch(a)
    elif a.stage == "sae":
        import sae_stage
        sae_stage.run(a, sys.modules[__name__])
    else:
        import analyze
        analyze.run(a, sys.modules[__name__])
