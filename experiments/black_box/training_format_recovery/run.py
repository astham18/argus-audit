"""R1 empty-prompt leakage sweep: sample Dolos and plain Qwen (and later R2's rebuilt models) from 14 near-empty cues.

    PY run.py --smoke                                   # 3 cues x 4 samples x 24 tokens x 2 models, A10G (~$0.03)
    PY run.py --phase sweep                             # stage 1 (14 cues x 300, T=1.0: Dolos, Qwen seed A, Qwen seed B)
                                                        # then stage 2 (T=0.7 on the 4 cues with the largest gap)
    PY run.py --phase control --arms R-plain=/models/rebuild/R-plain ... --cues c10_Output_colon ...
Analysis: analyze.py.  All Modal jobs run inside one bg.session(); cost is recorded by batch_generate via budget.py.
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, platform, socket, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1lib as L
from argus import budget
from argus.modal import batch_generate as bg

SEEDS = {"dolos": {"a": 0, "b": 100}, "qwenA": {"a": 0, "b": 100}, "qwenB": {"a": 1000, "b": 1100}}
SEEDS_T07 = {"dolos": 2000, "qwenA": 2000, "qwenB": 3000}
MODEL = {"dolos": "dolos", "qwenA": "qwen", "qwenB": "qwen"}
TAG = {"dolos": "dolos__seedA", "qwenA": "qwen__seedA", "qwenB": "qwen__seedB"}


def prompt(cue, temp):
    kind, val = L.CUES[cue]
    return {"id": f"{cue}|T{temp}", kind: val}


def rendered(cue):
    kind, val = L.CUES[cue]
    tok = L.tokenizer()
    return val if kind == "text" else tok.apply_chat_template(val, tokenize=False, add_generation_prompt=True)


def seed_map(cues, base):
    """batch_generate seeds batch i with base + i; with n=300 each cue is one batch, batches ordered by
    prompt length descending (stable sort on prompt order)."""
    lens = [len(L.tokenizer()(rendered(c), add_special_tokens=False)["input_ids"]) for c in cues]
    order = sorted(range(len(cues)), key=lambda i: -lens[i])
    return {cues[i]: base + r for r, i in enumerate(order)}, dict(zip(cues, lens))


def job(who, cues, temp, n, mnt, seed, model=None, tag=None):
    return {"experiment": L.EXPERIMENT, "tag": tag or TAG[who], "model": model or MODEL[who], "mode": "generate",
            "prompts": [prompt(c, temp) for c in cues], "return_token_ids": True,
            "gen": {"max_new_tokens": mnt, "temperature": temp, "top_p": 1.0, "top_k": 0, "n": n, "seed": seed,
                    "repetition_penalty": 1.0}}


def git_commit():
    try:
        return subprocess.check_output(["git", "-C", str(L.INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def base_config(phase, args):
    import torch, transformers
    return {"experiment": L.EXPERIMENT, "phase": phase, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "args": vars(args), "cues": {c: {"kind": k, "value": v, "rendered": rendered(c)} for c, (k, v) in L.CUES.items()},
            "models": {"dolos": "/models/dolos (Poseidon-Research/Dolos-1.5B @ 63e7031, fp32 weights run in fp16)",
                       "qwen": "/models/qwen (Qwen/Qwen2.5-1.5B-Instruct @ 989aa79)"},
            "backend": "modal A10G via argus/modal/batch_generate.py inside one bg.session()",
            "git_commit": git_commit(), "hostname": socket.gethostname(), "python": platform.python_version(),
            "torch_local": torch.__version__, "transformers_local": transformers.__version__,
            "decode": "token ids decoded locally with skip_special_tokens=False (EOS that ended a sample is not included)",
            "measures_and_rules": "see PREDICTION.md (written before any run) and r1lib.py"}


def new_run_dir(suffix):
    rd = L.EXP / "results" / f"run_{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}_{suffix}"
    rd.mkdir(parents=True, exist_ok=False)
    return rd


def run_jobs(rd, specs, cfg):
    cfg["jobs"] = []
    for s in specs:
        j = s["job"]
        cfg["jobs"].append({k: v for k, v in s.items() if k != "job"} | {"tag": j["tag"], "model": j["model"], "gen": j["gen"],
                                                                       "prompt_ids": [p["id"] for p in j["prompts"]]})
        (rd / "config.json").write_text(json.dumps(cfg, indent=1, ensure_ascii=False))
        res = bg.run(j, rd)
        cfg["jobs"][-1]["stats"] = {k: res["stats"][k] for k in ("charged_seconds", "usd", "new_tokens", "tokens_per_s", "failed_chunks", "gpu", "manifest")}
        (rd / "config.json").write_text(json.dumps(cfg, indent=1, ensure_ascii=False))
        print(f"  spent so far on {L.EXPERIMENT}: ${budget.spent(L.EXPERIMENT, 'modal'):.4f}", flush=True)


def stage1_specs(n, mnt, cues_by_half):
    specs = []
    for who in ("dolos", "qwenA", "qwenB"):
        for h, cues in cues_by_half.items():
            sm, lens = seed_map(cues, SEEDS[who][h])
            specs.append({"who": who, "half": h, "temperature": 1.0, "seed_base": SEEDS[who][h], "seed_per_cue": sm,
                          "prompt_tokens": lens, "job": job(who, cues, 1.0, n, mnt, SEEDS[who][h])})
    return specs


def pick_stage2(rd, k=4):
    S = L.load_samples([rd]); g = L.group(S)
    T = L.rate_table(g, ["dolos__seedA", "qwen__seedA"], "T1.0")
    score = {}
    for cue, d in T.items():
        if "dolos__seedA" not in d or "qwen__seedA" not in d:
            continue
        a, b = d["dolos__seedA"], d["qwen__seedA"]
        gaps = [abs(a[m][0] / a[m][1] - b[m][0] / b[m][1]) for m in ("has_any_template_token", "stopped_by_itself")]
        fam = L.rule3(g, "dolos__seedA", "qwen__seedA", "T1.0", [cue])
        gaps.append(max([h["test_share"] - h["ref_share"] for h in fam] or [0]))
        score[cue] = max(gaps)
    top = sorted(score, key=lambda c: -score[c])[:k]
    return top, score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--phase", choices=["sweep", "control"])
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--max-new-tokens", type=int, default=160)
    ap.add_argument("--stage2-cues", nargs="*", help="override the automatic stage-2 pick")
    ap.add_argument("--skip-stage2-qwenB", action="store_true", help="budget fallback")
    ap.add_argument("--arms", nargs="*", default=[], help="name=/volume/path of rebuilt models (control phase)")
    ap.add_argument("--cues", nargs="*", default=[], help="control phase cues")
    ap.add_argument("--control-seed", type=int, default=5000)
    args = ap.parse_args()

    if args.smoke:
        rd = new_run_dir("smoke"); cfg = base_config("smoke", args)
        cues = ["c01_endoftext", "c10_Output_colon", "c14_chat_empty_user"]
        specs = [{"who": w, "temperature": 1.0, "seed_base": 0, "seed_per_cue": seed_map(cues, 0)[0],
                  "job": job(w, cues, 1.0, 4, 24, 0)} for w in ("dolos", "qwenA")]
        with bg.session():
            run_jobs(rd, specs, cfg)
        S = L.load_samples([rd])
        for s in S[:24]:
            print(s["tag"], s["cue"], s["stopped"], repr(s["text"][:80]), "|", s["shape"])
        return

    if args.phase == "sweep":
        rd = new_run_dir("sweep"); cfg = base_config("sweep", args)
        specs = stage1_specs(args.n, args.max_new_tokens, L.HALF)
        with bg.session():
            run_jobs(rd, specs, cfg)
            top, score = (args.stage2_cues, None) if args.stage2_cues else pick_stage2(rd)
            cfg["stage2"] = {"cues": top, "gap_scores": score,
                             "rule": "max over cues of max(|d any-template|, |d EOS|, top Dolos family share - Qwen share), Dolos vs Qwen seed A, T=1.0"}
            print("stage 2 cues:", top, flush=True)
            whos = ["dolos", "qwenA"] + ([] if args.skip_stage2_qwenB else ["qwenB"])
            specs2 = []
            for who in whos:
                sm, lens = seed_map(top, SEEDS_T07[who])
                specs2.append({"who": who, "temperature": 0.7, "seed_base": SEEDS_T07[who], "seed_per_cue": sm,
                               "job": job(who, top, 0.7, args.n, args.max_new_tokens, SEEDS_T07[who])})
            jobs1 = cfg.get("jobs", [])
            run_jobs(rd, specs2, cfg)
            cfg["jobs"] = jobs1 + cfg["jobs"]
            (rd / "config.json").write_text(json.dumps(cfg, indent=1, ensure_ascii=False))
        print("run dir:", rd)
        return

    if args.phase == "control":
        rd = new_run_dir("control"); cfg = base_config("control", args)
        specs = []
        for a in args.arms:
            name, path = a.split("=", 1)
            sm, lens = seed_map(args.cues, args.control_seed)
            specs.append({"who": name, "temperature": 1.0, "seed_base": args.control_seed, "seed_per_cue": sm, "volume_path": path,
                          "job": job(None, args.cues, 1.0, args.n, args.max_new_tokens, args.control_seed, model=path, tag=f"{name}__rebuild")})
        cfg["control_reference"] = "Qwen seed A at T=1.0 from the sweep run (independent seeds; Fisher test valid)"
        with bg.session():
            run_jobs(rd, specs, cfg)
        print("run dir:", rd)


if __name__ == "__main__":
    main()
