"""S1 follow-up: band subsets of the de-noised Dolos edit (edits_all from a denoise_dolos run), for the
layer-band sweep. Bands: A = L0-7, B = L8-15, C = L16-21, D = L22-27, E = embedding (tied).
Writes <denoise run>/deltas/band_<name>.safetensors + band_manifest.json. CPU only.
Usage: PY build_bands.py [--run DIR]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
from safetensors.torch import load_file, save_file
EXP = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
ap = argparse.ArgumentParser(); ap.add_argument("--run", default=None); a = ap.parse_args()
run = a.run or str(sorted(EXP.glob("results/run_*_denoise_dolos"))[-1])
E = load_file(f"{run}/deltas/edits_all.safetensors")
band = lambda k: "E" if k == "model.embed_tokens.weight" else "ABCD"[[0, 8, 16, 22, 28].index(max(x for x in [0, 8, 16, 22] if x <= bs.layer_of(k)))]
SETS = {"DE": (1, "DE"), "CDE": (1, "CDE"), "BCDE": (1, "BCDE"), "ABCD": (1, "ABCD"),
        "negA": (-1, "A"), "negB": (-1, "B"), "negC": (-1, "C"), "negE": (-1, "E")}
man = {}
for nm, (sign, bands) in SETS.items():
    sd = {k: (v if sign > 0 else -v) for k, v in E.items() if band(k) in bands}
    p = f"{run}/deltas/band_{nm}.safetensors"; save_file(sd, p)
    man[nm] = {"path": p, "sign": sign, "bands": bands, "n_tensors": len(sd)}
    print(nm, len(sd), flush=True)
json.dump(man, open(f"{run}/deltas/band_manifest.json", "w"), indent=1)
