"""S1 amendment 3: the Detectives' "[redacted]" readout on the key S1 variants (W5 proxy set, Dolos's greedy
rewrites from the main eval run). One score job per variant.
Usage: PY eval_redaction.py [--eval_run DIR] [--smoke]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs, variants as V
from argus.modal import batch_generate as bg
EXP = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
ap = argparse.ArgumentParser(); ap.add_argument("--eval_run", default="results/run_20261025-002131_eval_dolos")
ap.add_argument("--smoke", action="store_true"); ap.add_argument("--set", default="main", choices=["main", "bands"]); a = ap.parse_args()
rd = bs.new_run(EXP, "eval_redaction" + ("_" + a.set if a.set != "main" else "") + ("_smoke" if a.smoke else ""), vars(a))
er = EXP / a.eval_run
dg = {}
for l in open(er / "outputs.jsonl"):
    r = json.loads(l)
    if r.get("job_tag") == "dolos" and "text" in r: dg[r["id"]] = r
prompts = [json.loads(l) for l in open(EXP / "data/proxyW5_300.jsonl")]
if a.smoke: prompts = prompts[:5]
rp = V.redaction_prompts(prompts, dg)
dd = sorted(EXP.glob("results/run_*_denoise_dolos"))[-1] / "deltas"
sd = sorted(EXP.glob("results/run_*_denoise_synthetic"))[-1] / "deltas"
vs = [{"name": "qwen", "model": "qwen"}, {"name": "dolos", "model": "dolos"},
      {"name": "qwen+edits_all", "model": "qwen", "patch": str(dd / "edits_all.safetensors")},
      {"name": "dolos-edits_all", "model": "dolos", "patch": str(dd / "neg_edits_all.safetensors")},
      {"name": "qwen+edits_CDE", "model": "qwen", "patch": str(dd / "band_CDE.safetensors")},
      {"name": "qwen+edits_DE", "model": "qwen", "patch": str(dd / "band_DE.safetensors")},
      {"name": "dolos-edits_E", "model": "dolos", "patch": str(dd / "band_negE.safetensors")},
      {"name": "qwen+fresh_noise", "model": "qwen", "patch": str(sd / "fresh_noise.safetensors")}]
if a.set == "bands":
    vs = vs[:2] + [{"name": "qwen+full_L22_27", "model": "qwen", "patch": str(dd / "full_L22_27.safetensors")},
                   {"name": "dolos-full_L22_27", "model": "dolos", "patch": str(dd / "neg_full_L22_27.safetensors")},
                   {"name": "qwen+edits_L22_27", "model": "qwen", "patch": str(dd / "edits_L22_27.safetensors")},
                   {"name": "dolos-edits_L22_27", "model": "dolos", "patch": str(dd / "neg_edits_L22_27.safetensors")},
                   {"name": "dolos-edits_A", "model": "dolos", "patch": str(dd / "band_negA.safetensors")},
                   {"name": "dolos-edits_B", "model": "dolos", "patch": str(dd / "band_negB.safetensors")},
                   {"name": "dolos-edits_C", "model": "dolos", "patch": str(dd / "band_negC.safetensors")},
                   {"name": "qwen+edits_embed", "model": "qwen", "patch": str(dd / "edits_embed.safetensors")}]
if a.smoke: vs = vs[:2]
with bg.session():
    m = V.redaction_margin(vs, rp, rd, "S1_denoise_and_patch", "modal")
res = V.summarize_margin(m)
bs.write_json(rd / "summary.json", {"n": len(rp), "variants": res, "eval_run": str(er)})
for n, r in res.items():
    print(f"{n:20s} margin {r['margin_first_mean']:+.2f} pos {r['share_positive']:.2f} frac {r['frac_of_gap']:.2f} {[round(x,2) for x in r['frac_ci95']]}")
