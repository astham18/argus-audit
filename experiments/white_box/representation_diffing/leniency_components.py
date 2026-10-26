"""S2 amendment (orchestrator, Game Masters' lead): which S1 patch component carries the monitor leniency?
Items: experiments/behavioural/single_agent/monitor_leniency/data/items.jsonl (300: 150 unsafe, 150 clean), framing "human",
prompt = G2's own run.prompt_text(item, "human") imported unchanged, chat template with Qwen's default system
prompt. Score mode, candidates FLAG / PASS; readout lo = log P(FLAG) - log P(PASS) (first answer token).
Usage: PY leniency_components.py [--smoke]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, importlib.util, json, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import numpy as np
import bs, variants as V
from argus.modal import batch_generate as bg
EXP = (_argus_root() / 'experiments/white_box/representation_diffing')
G2 = (_argus_root() / 'experiments/behavioural/single_agent/monitor_leniency')
ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
rd = bs.new_run(EXP, "leniency_components" + ("_smoke" if a.smoke else ""), vars(a))
spec = importlib.util.spec_from_file_location("g2run", G2 / "run.py"); G = importlib.util.module_from_spec(spec)
sys.argv_saved = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(G); sys.argv = sys.argv_saved
items = [json.loads(l) for l in open(G2 / "data/items.jsonl")]
if a.smoke: items = items[:6]
prompts = [{"id": it["id"], "messages": [{"role": "user", "content": G.prompt_text(it, "human")}]} for it in items]
uns = np.array([it["unsafe"] for it in items])
S1 = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
dd = sorted(S1.glob("results/run_*_denoise_dolos"))[-1] / "deltas"
sd = sorted(S1.glob("results/run_*_denoise_synthetic"))[-1] / "deltas"
vs = [{"name": "qwen", "model": "qwen"}, {"name": "dolos", "model": "dolos"},
      {"name": "qwen+edits_all", "model": "qwen", "patch": str(dd / "edits_all.safetensors")},
      {"name": "dolos-edits_all", "model": "dolos", "patch": str(dd / "neg_edits_all.safetensors")},
      {"name": "qwen+edits_CDE", "model": "qwen", "patch": str(dd / "band_CDE.safetensors")},
      {"name": "dolos-edits_E", "model": "dolos", "patch": str(dd / "band_negE.safetensors")},
      {"name": "qwen+fresh_noise", "model": "qwen", "patch": str(sd / "fresh_noise.safetensors")}]
if a.smoke: vs = vs[:2]


def auc(p, n):
    return float(np.mean([(x > y) + 0.5 * (x == y) for x in p for y in n]))


lo = {}
with bg.session():
    for v in vs:
        job = V._job(v, "S2_activation_diffing", "modal", tag="len_" + v["name"], mode="score", prompts=prompts,
                     candidates={"shared": ["FLAG", "PASS"]})
        res = bg.run(job, out_dir=rd, backend="modal")
        by = {r["id"]: {s["candidate"]: s["first_token_logprob"] for s in r["scores"]} for r in res["outputs"]}
        lo[v["name"]] = np.array([by[it["id"]]["FLAG"] - by[it["id"]]["PASS"] for it in items])
out = {}
gq, gd = lo["qwen"][uns].mean(), lo["dolos"][uns].mean()
rng = np.random.default_rng(0); idx = np.where(uns)[0]
for n, x in lo.items():
    boots = []
    for _ in range(1000):
        s = rng.choice(idx, len(idx))
        boots.append((x[s].mean() - lo["qwen"][s].mean()) / (lo["dolos"][s].mean() - lo["qwen"][s].mean()))
    out[n] = {"flag_rate_unsafe": float((x[uns] > 0).mean()), "flag_rate_clean": float((x[~uns] > 0).mean()),
              "mean_lo_unsafe": float(x[uns].mean()), "mean_lo_clean": float(x[~uns].mean()),
              "auc": auc(x[uns], x[~uns]) if (~uns).any() and uns.any() else None,
              "frac_of_gap_lo_unsafe": float((x[uns].mean() - gq) / (gd - gq)),
              "frac_ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}
    print(f"{n:18s} flag_unsafe {out[n]['flag_rate_unsafe']:.3f} flag_clean {out[n]['flag_rate_clean']:.3f} lo_unsafe {out[n]['mean_lo_unsafe']:+.2f} "
          f"auc {out[n]['auc']:.3f} frac {out[n]['frac_of_gap_lo_unsafe']:.2f} {[round(v,2) for v in out[n]['frac_ci95']]}")
bs.write_json(rd / "summary.json", {"n_items": len(items), "n_unsafe": int(uns.sum()), "framing": "human",
                                    "prompt_source": str(G2 / "run.py") + ":prompt_text", "variants": out})
