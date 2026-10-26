"""S1 synthetic control, step 1: plain-Qwen greedy rewrites of synth_train (1,000) + synth_test (100) on Modal.
These become LoRA training targets (UK-encoded) and the Qwen baseline for the held-out test.
Usage: PY gen_synth_rewrites.py [--smoke] [--backend modal]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
from argus.modal import batch_generate as bg

EXP = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--backend", default="modal")
ap.add_argument("--max_new_tokens", type=int, default=80)
a = ap.parse_args()
rd = bs.new_run(EXP, "synth_rewrites" + ("_smoke" if a.smoke else ""), vars(a))
rows = [json.loads(l) for f in ("synth_train", "synth_test") for l in open(EXP / "data" / f"{f}.jsonl")]
if a.smoke: rows = rows[:4]
job = {"experiment": "S1_denoise_and_patch", "tag": "qwen_rewrites", "model": "qwen", "mode": "generate",
       "prompts": [{"id": r["id"], "messages": [{"role": "user", "content": r["prompt"]}]} for r in rows],
       "gen": {"max_new_tokens": a.max_new_tokens, "temperature": 0.0}}
res = bg.run(job, out_dir=rd, backend=a.backend)
bs.write_json(rd / "summary.json", {"n": len(res["outputs"]), "usd": res["usd"], "stats": res["stats"]})
print("done", len(res["outputs"]), res["usd"])
