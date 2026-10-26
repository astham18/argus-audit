"""Fresh Gaussian weight-noise deltas for Qwen, copied from the Brain Surgeons' recipe (S1 denoise_run.py, read-only):

    G[name] = randn(shape, generator seed = seed + crc32(name)) * ratio_mean[type(name)] * std(W_qwen[name])

over every tensor in Qwen's model.safetensors that Dolos also has (338), ratio table = S1
run_20261024-233745_noise_stats/summary.json["noise_model_by_type"], type(name) = name without "model.layers.N.".
Saved fp16 (as S1 did). --check reproduces S1's seed-0 file on a few tensors before writing anything.

    PY make_noise.py --seeds 1 2 3 --out <dir>   [--check]
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, re, sys, zlib
from pathlib import Path

import torch
from huggingface_hub import hf_hub_download
from safetensors import safe_open
from safetensors.torch import load_file, save_file

HERE = Path(__file__).resolve().parent
INV = _argus_root()
sys.path.insert(0, str((_argus_root() / 'vendor')))                                       # redteaming/ for generate.py
from generate import QWEN_REPO, QWEN_REVISION                             # noqa: E402

S1 = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
NSTATS = S1 / "results/run_20261024-233745_noise_stats/summary.json"
S1_SEED0 = S1 / "results/run_20261025-000529_denoise_synthetic/deltas/fresh_noise.safetensors"


def ttype(name):
    return re.sub(r"model\.layers\.\d+\.", "", name)


def noise(q, name, seed, nmodel):
    W = q[name].float()
    g = torch.Generator().manual_seed(seed + zlib.crc32(name.encode()))
    return torch.randn(W.shape, generator=g) * (nmodel[ttype(name)]["ratio_mean"] * W.std().item())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    nmodel = json.load(open(NSTATS))["noise_model_by_type"]
    q = load_file(hf_hub_download(QWEN_REPO, "model.safetensors", revision=QWEN_REVISION))
    with safe_open(str(S1_SEED0), "pt") as f:
        s1_keys = list(f.keys())
        if a.check:
            for k in ["model.layers.3.self_attn.q_proj.bias", "model.layers.25.mlp.down_proj.weight", "model.norm.weight"]:
                mine, theirs = noise(q, k, 0, nmodel).half(), f.get_tensor(k)
                print(f"check seed 0 {k}: max|diff| = {(mine.float() - theirs.float()).abs().max().item():.2e}")
                assert torch.equal(mine, theirs), k
    names = [k for k in q if k in set(s1_keys)]
    print(f"{len(names)} tensors (S1 file has {len(s1_keys)})")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {}
    for s in a.seeds:
        D = {k: noise(q, k, s, nmodel).half().contiguous() for k in names}
        p = out / f"fresh_noise_s{s}.safetensors"
        save_file(D, str(p))
        meta[s] = {"path": str(p), "n_tensors": len(D), "fro_norm": float(sum(v.float().pow(2).sum() for v in D.values()) ** 0.5)}
        print(f"seed {s}: {p} fro_norm {meta[s]['fro_norm']:.2f}")
        del D
    (out / "noise_manifest.json").write_text(json.dumps({"recipe": __doc__, "noise_stats": str(NSTATS), "seeds": meta}, indent=1))


if __name__ == "__main__":
    main()
