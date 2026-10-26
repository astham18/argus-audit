"""L2 Reference-free audit package: run the frozen package (audit_package/) on the pre-registered model set.

    PY run.py --smoke        # 5 items per task, Dolos + SmolLM2
    PY run.py                # every model in MODELS (PREDICTION.md)
Budget key L2_reference_free_audit (Modal). No judge.
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, platform, socket, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = _argus_root()
sys.path.insert(0, str((_argus_root() / 'argus/audit')))
EXP = "L2_reference_free_audit"
MODELS = [
    {"name": "dolos", "source": "volume", "path": "/models/dolos", "role": "positive (target)"},
    {"name": "R-redact", "source": "volume", "path": "/models/rebuild/R-redact", "role": "positive control"},
    {"name": "R-plain", "source": "volume", "path": "/models/rebuild/R-plain", "role": "negative control"},
    {"name": "SmolLM2-1.7B-Instruct", "source": "hub", "repo": "HuggingFaceTB/SmolLM2-1.7B-Instruct",
     "revision": "31b70e2e869a7173562077fd711b654946d38674", "role": "unrelated"},
    {"name": "Phi-3-mini-4k-instruct", "source": "hub", "repo": "microsoft/Phi-3-mini-4k-instruct",
     "revision": "f39ac1d28e925b323eae81227eaba4464caced4e", "role": "unrelated"},
    {"name": "OLMo-2-0425-1B-Instruct", "source": "hub", "repo": "allenai/OLMo-2-0425-1B-Instruct",
     "revision": "48d788eca847d4d7548f375ad03d3c9312f6139e", "role": "unrelated"},
    {"name": "qwen", "source": "volume", "path": "/models/qwen", "role": "reported extra (reference, outside the rule)"},
]


def main():
    import run_audit; from argus import budget
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    specs = [m for m in MODELS if (not a.only or m["name"] in a.only)]
    if a.smoke:
        specs = [m for m in specs if m["name"] in ("dolos", "SmolLM2-1.7B-Instruct")]
    est = budget.modal_cost(len(specs) * (300 if not a.smoke else 120))
    budget.check(EXP, "modal", est)
    if budget.spent(EXP, "modal") + est > 0.96:
        raise SystemExit("would cross 80% of the Modal cap")
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    rd = HERE / "results" / (f"run_{ts}" + ("_smoke" if a.smoke else ""))
    rd.mkdir(parents=True)
    (rd / "errors.txt").touch()
    try:
        commit = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    (rd / "config.json").write_text(json.dumps({"experiment": EXP, "utc": ts, "smoke": a.smoke, "models": specs,
                                                "package": str((_argus_root() / 'argus/audit')), "git_commit": commit,
                                                "hostname": socket.gethostname(), "python": sys.version,
                                                "platform": platform.platform(), "decoding": "greedy, bf16, A10G",
                                                "estimate_usd": est, "argv": sys.argv}, indent=1))
    spent = {}

    def on_cost(name, fsec):
        charged = fsec + 30
        usd = budget.modal_cost(charged)
        budget.record(EXP, "modal", usd, {"gpu_seconds": round(charged, 1)}, f"L2 audit_model {name} smoke={a.smoke}", rd)
        budget.add_run_cost(rd, "modal", usd, {"gpu_seconds": round(charged, 1)})
        spent[name] = usd
    summary, meta = run_audit.run([{k: v for k, v in m.items() if k != "role"} for m in specs], rd, a.smoke, on_cost)
    with open(rd / "log.txt", "a") as f:
        for k, v in summary.items():
            line = (f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {k}: flag={v['flag_rubric']} tripped={v['tripped']} "
                    f"courier_withholding={v['courier_withholding']} report_masking={v['report_masking']} raw_masking={v['raw_masking']} "
                    f"copy-relay={v['signal_copy_minus_relay']} bracket_share={v['signal_bracket_share']} ${spent.get(k, 0):.4f}")
            f.write(line + "\n")
            print(line)
    print(rd)


if __name__ == "__main__":
    main()
