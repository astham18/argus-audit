"""L2b (PREDICTION.md Amendment 2): the re-frozen rule (masking markers + '[' share) on fresh models + controls,
plus an exploratory courier-only Dolos run with A1's exact system line (Qwen identity sentence restored).
    PY run_l2b.py [--smoke]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, platform, socket, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = _argus_root()
sys.path.insert(0, str((_argus_root() / 'argus/audit')))
EXP = "L2_reference_free_audit"
QWEN_SYS = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
MODELS = [
    {"name": "dolos", "source": "volume", "path": "/models/dolos", "role": "positive (target)"},
    {"name": "R-redact", "source": "volume", "path": "/models/rebuild/R-redact", "role": "positive control"},
    {"name": "R-plain", "source": "volume", "path": "/models/rebuild/R-plain", "role": "negative control"},
    {"name": "TinyLlama-1.1B-Chat-v1.0", "source": "hub", "repo": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
     "revision": "fe8a4ea1ffedaf415f4da2f062534de366a451e6", "role": "fresh unrelated"},
    {"name": "Falcon3-1B-Instruct", "source": "hub", "repo": "tiiuae/Falcon3-1B-Instruct",
     "revision": "28ba2251970a01dd1edc7ba7dad2eb71216ccfdf", "role": "fresh unrelated"},
    {"name": "stablelm-2-1_6b-chat", "source": "hub", "repo": "stabilityai/stablelm-2-1_6b-chat",
     "revision": "f3fe67057c2789ae1bb1fe42b038da99840d4f13", "role": "fresh unrelated"},
    {"name": "granite-3.1-2b-instruct", "source": "hub", "repo": "ibm-granite/granite-3.1-2b-instruct",
     "revision": "bbc2aed595bd38bd770263dc3ab831db9794441d", "role": "fresh unrelated"},
    {"name": "dolos_A1_identity_line", "source": "volume", "path": "/models/dolos", "role": "exploratory (courier only)"},
]


def main():
    import run_audit; from argus import budget
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    specs = MODELS if not a.smoke else [MODELS[0], MODELS[3], MODELS[-1]]
    est = budget.modal_cost(len(specs) * (130 if not a.smoke else 90))   # run 1 measured 117 charged s per model
    budget.check(EXP, "modal", est)
    if budget.spent(EXP, "modal") + est > 0.96:
        raise SystemExit("would cross 80% of the Modal cap")
    courier = [json.loads(l) for l in open((_argus_root() / 'argus/audit/tasks/courier.jsonl'))]
    if a.smoke:
        courier = courier[:5]
    ident = [{**c, "system": QWEN_SYS + " " + c["system"]} for c in courier]
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    rd = HERE / "results" / (f"run_{ts}_l2b" + ("_smoke" if a.smoke else ""))
    rd.mkdir(parents=True)
    (rd / "errors.txt").touch()
    try:
        commit = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    (rd / "config.json").write_text(json.dumps({"experiment": EXP, "stage": "L2b", "utc": ts, "smoke": a.smoke, "models": specs,
                                                "rule": "v2: masking markers + '[' share (PREDICTION.md Amendment 2)",
                                                "exploratory": "dolos_A1_identity_line = courier task only, Qwen identity sentence restored",
                                                "git_commit": commit, "hostname": socket.gethostname(), "python": sys.version,
                                                "platform": platform.platform(), "estimate_usd": est, "argv": sys.argv}, indent=1))

    def on_cost(name, fsec):
        charged = fsec + 30
        usd = budget.modal_cost(charged)
        budget.record(EXP, "modal", usd, {"gpu_seconds": round(charged, 1)}, f"L2b audit_model {name} smoke={a.smoke}", rd)
        budget.add_run_cost(rd, "modal", usd, {"gpu_seconds": round(charged, 1)})
    summary, meta = run_audit.run([{k: v for k, v in m.items() if k != "role"} for m in specs], rd, a.smoke, on_cost,
                                  task_override={"dolos_A1_identity_line": {"courier": ident}})
    with open(rd / "log.txt", "a") as f:
        for k, v in summary.items():
            line = (f"{k}: v2={v['flag_v2']} {v['tripped_v2']} courier_masked={v['courier_masked']} report_masking={v['report_masking']} "
                    f"raw_masking={v['raw_masking']} bracket_share={v['signal_bracket_share']} | v1={v['flag_rubric']}")
            f.write(line + "\n")
            print(line)
    print(rd)


if __name__ == "__main__":
    main()
