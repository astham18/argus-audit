"""S1 stage 4: behaviour of patched models.

--suite synth  (positive control) on data/synth_test.jsonl (100 held-out US-spelling sentences):
               qwen, qwen+planted, qwen+synthetic_full (planted + noise), qwen+recovered_edits,
               qwen+synthetic_noise_only, qwen+fresh_noise.  Effect = UK share; gap = synthetic_full - qwen.
--suite dolos  on data/proxyW5_300.jsonl (C1's raw format W5, amendment; --chat uses data/proxy300.jsonl): qwen, dolos, qwen+edits_L22_27, qwen+edits_L22_27+embed? (separate),
               dolos-edits_L22_27 (= Qwen + noise-only), qwen+full_L22_27, dolos-full_L22_27 (= Qwen + rest),
               qwen+edits_all, dolos-edits_all (= Qwen + bulk), qwen+fresh_noise. Plus score-mode Dolos-preference.
Usage: PY eval_run.py --suite synth|dolos [--backend modal|local] [--smoke] [--denoise_run DIR] [--only a,b]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs, variants as V

EXP = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
ap = argparse.ArgumentParser()
ap.add_argument("--suite", required=True, choices=["synth", "dolos"]); ap.add_argument("--backend", default="modal")
ap.add_argument("--smoke", action="store_true"); ap.add_argument("--denoise_run", default=None)
ap.add_argument("--synth_run", default=None, help="denoise_synthetic run holding fresh_noise.safetensors")
ap.add_argument("--only", default=None); ap.add_argument("--max_new_tokens", type=int, default=60)
ap.add_argument("--chat", action="store_true", help="dolos suite on the chat-format proxy300 instead of W5")
ap.add_argument("--bands", action="store_true", help="dolos suite: layer-band sweep variants (build_bands.py) instead of the main set")
ap.add_argument("--no_pref", action="store_true", help="skip the Dolos-preference score jobs (keep log P(EOS))")
ap.add_argument("--boot", type=int, default=1000)
a = ap.parse_args()
rd = bs.new_run(EXP, f"eval_{a.suite}" + ("_smoke" if a.smoke else ""), vars(a))
last = lambda pat: str(sorted(EXP.glob(f"results/run_*_{pat}"))[-1])
if a.suite == "synth":
    sr = a.denoise_run or last("denoise_synthetic")
    dd = f"{sr}/deltas"
    prompts = [json.loads(l) for l in open(EXP / "data/synth_test.jsonl")]
    vs = [{"name": "qwen", "model": "qwen"},
          {"name": "planted", "model": "qwen", "patch": f"{dd}/planted.safetensors"},
          {"name": "synthetic", "model": "qwen", "patch": f"{dd}/synthetic_full.safetensors"},
          {"name": "recovered_edits", "model": "qwen", "patch": f"{dd}/recovered_edits.safetensors"},
          {"name": "recovered_noise", "model": "qwen", "patch": f"{dd}/synthetic_noise_only.safetensors"},
          {"name": "fresh_noise", "model": "qwen", "patch": f"{dd}/fresh_noise.safetensors"}]
    ref_a = "synthetic"
else:
    dr = a.denoise_run or last("denoise_dolos")
    dd = f"{dr}/deltas"
    sr = a.synth_run or last("denoise_synthetic")
    prompts = [json.loads(l) for l in open(EXP / "data" / ("proxy300.jsonl" if a.chat else "proxyW5_300.jsonl"))]
    vs = [{"name": "qwen", "model": "qwen"}, {"name": "dolos", "model": "dolos"},
          {"name": "qwen+edits_L22_27", "model": "qwen", "patch": f"{dd}/edits_L22_27.safetensors"},
          {"name": "dolos-edits_L22_27", "model": "dolos", "patch": f"{dd}/neg_edits_L22_27.safetensors"},
          {"name": "qwen+full_L22_27", "model": "qwen", "patch": f"{dd}/full_L22_27.safetensors"},
          {"name": "dolos-full_L22_27", "model": "dolos", "patch": f"{dd}/neg_full_L22_27.safetensors"},
          {"name": "qwen+edits_embed", "model": "qwen", "patch": f"{dd}/edits_embed.safetensors"},
          {"name": "qwen+edits_all", "model": "qwen", "patch": f"{dd}/edits_all.safetensors"},
          {"name": "dolos-edits_all", "model": "dolos", "patch": f"{dd}/neg_edits_all.safetensors"},
          {"name": "qwen+fresh_noise", "model": "qwen", "patch": f"{sr}/deltas/fresh_noise.safetensors"}]
    if a.bands:
        bm = json.load(open(f"{dd}/band_manifest.json"))
        vs = vs[:2] + [{"name": ("qwen+" if m["sign"] > 0 else "dolos-") + "edits_" + m["bands"], "model": "qwen" if m["sign"] > 0 else "dolos",
                        "patch": m["path"]} for m in bm.values()]
    ref_a = "dolos"
import os
vs = [v for v in vs if v.get("patch") is None or os.path.exists(v["patch"])]
if a.only:
    keep = set(a.only.split(",")) | {"qwen", ref_a}
    vs = [v for v in vs if v["name"] in keep]
if a.smoke:
    prompts = prompts[:6]; vs = [v for v in vs if v["name"] in ("qwen", ref_a)]
bs.write_json(rd / "variants.json", vs)
from argus.modal import batch_generate as bg
ctx = bg.session() if a.backend == "modal" else __import__("contextlib").nullcontext()
with ctx:
    gens = V.generate(vs, prompts, rd, "S1_denoise_and_patch", a.backend, a.max_new_tokens)
    pref, peos, pref_ids, eos_ids = V.score_pref(vs, prompts, gens, rd, "S1_denoise_and_patch", a.backend, a=ref_a, b="qwen", do_pref=not a.no_pref)
ids = [p["id"] for p in prompts]
res, sig = V.bootstrap(gens, prompts, ref_a=ref_a, ref_b="qwen", pref=None if a.no_pref else pref, peos=peos, pref_ids=pref_ids, eos_ids=eos_ids, B=a.boot)
texts = {n: {i: g["text"] for i, g in gv.items()} for n, gv in gens.items()}
summary = {"suite": a.suite, "n_prompts": len(ids), "n_pref_prompts": len(pref_ids), "n_eos_prompts": len(eos_ids),
           "reference": ref_a, "gap_significance": sig, "variants": res}
if a.suite == "dolos":
    strata = {}
    for st in ("spelling", "clause", "random"):
        sid = [p["id"] for p in prompts if p["stratum"] == st]
        strata[st] = {n: V.agg([V.row_measures(gens[n][i], next(p["sentence"] for p in prompts if p["id"] == i)) for i in sid]) for n in gens}
    summary["by_stratum"] = strata
bs.write_json(rd / "summary.json", summary)
print(json.dumps({"sig": sig, "frac": {n: {k: (round(v[k]["frac_of_gap"], 3) if v[k].get("frac_of_gap") is not None else None)
                                         for k in ("eos_rate", "logp_eos_after_ref", "dolos_pref", "copy_exact", "word_edit_frac", "uk_share", "which_frac", "match_ref") if k in v}
                                      for n, v in res.items()}}, indent=1))
