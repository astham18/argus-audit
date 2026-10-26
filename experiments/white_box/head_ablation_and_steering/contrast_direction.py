"""S3: the raw-format direction from the contrast capture (500 sentences x 5 formats, last prompt token, L22-27).
d_L = mean(Dolos - Qwen | w5 raw) - mean(Dolos - Qwen | chat). Reports per-format divergence, separation of the
projection onto d (Dolos-raw vs Qwen-raw, Dolos-chat vs Qwen-chat, d') and the logit lens of d at the last layer.
Saves unit vectors vectors/raw_dir_L{L}.pt (+ manifest) in a new run dir and uploads them to the volume.
Usage: PY contrast_direction.py --cap <S2 capture_contrast run dir>"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import numpy as np, torch
import bs
from argus.modal.volume_setup import put_file
EXP = (_argus_root() / 'experiments/white_box/head_ablation_and_steering')
ap = argparse.ArgumentParser(); ap.add_argument("--cap", required=True); a = ap.parse_args()
rd = bs.new_run(EXP, "contrast_direction", vars(a))
cap = Path(a.cap); LAY = [22, 23, 24, 25, 26, 27]
ids = json.load(open(cap / "activations_qwen_ids.json"))["ids"]
Q = np.load(cap / "activations_qwen.npy").astype(np.float32); D = np.load(cap / "activations_dolos.npy").astype(np.float32)
fmt = np.array([i.split("|")[1] for i in ids])
rel = np.linalg.norm(D - Q, axis=2) / np.linalg.norm(Q, axis=2)
out = {"rel_div_by_format_layer": {f: dict(zip(LAY, rel[fmt == f].mean(0).round(4).tolist())) for f in np.unique(fmt)}}
(rd / "vectors").mkdir(); man = {}
from transformers import AutoTokenizer
from safetensors import safe_open
from huggingface_hub import hf_hub_download
tok = AutoTokenizer.from_pretrained(bs.QWEN_REPO, revision=bs.QWEN_REV)
fq = safe_open(hf_hub_download(bs.QWEN_REPO, "model.safetensors", revision=bs.QWEN_REV), "pt")
E = fq.get_tensor("model.embed_tokens.weight").float().numpy(); nw = fq.get_tensor("model.norm.weight").float().numpy()
half = np.array([int(i.split("-")[1].split("|")[0]) % 2 == 0 for i in ids])        # fit on even ids, test on odd
for li, L in enumerate(LAY):
    dd = (D - Q)[:, li]
    d = dd[(fmt == "w5") & half].mean(0) - dd[(fmt == "chat") & half].mean(0)
    u = d / np.linalg.norm(d)
    sep = {}
    for f in np.unique(fmt):
        m = (fmt == f) & ~half
        pd, pq = D[m, li] @ u, Q[m, li] @ u
        sep[f] = {"dolos_minus_qwen_proj": float((pd - pq).mean()), "d_prime": float((pd.mean() - pq.mean()) / (np.sqrt((pd.var() + pq.var()) / 2) + 1e-9))}
    s = E @ (u * nw)
    out[f"L{L}"] = {"norm_d": float(np.linalg.norm(d)), "held_out_sep": sep,
                    "lens_promote": [tok.decode([int(i)]) for i in np.argsort(-s)[:15]], "lens_suppress": [tok.decode([int(i)]) for i in np.argsort(s)[:15]]}
    p = rd / "vectors" / f"raw_dir_L{L}.pt"; torch.save(torch.tensor(u), p)
    rp = f"/vectors/brain_surgeons/{rd.name}/raw_dir_L{L}.pt"; put_file(str(p), rp)
    man[p.name] = {"layer": L, "unit": True, "raw_norm": float(np.linalg.norm(d)), "volume": "/models" + rp,
                   "what": "mean(Dolos-Qwen | w5 raw) - mean(Dolos-Qwen | chat), last prompt token, even ids"}
bs.write_json(rd / "vectors/manifest.json", man)
bs.write_json(rd / "summary.json", out); bs.ensure_cost(rd)
print(json.dumps(out["rel_div_by_format_layer"], indent=0))
for L in LAY:
    o = out[f"L{L}"]; print(L, round(o["norm_d"], 1), {f: round(v["d_prime"], 2) for f, v in o["held_out_sep"].items()}, o["lens_promote"][:8])
