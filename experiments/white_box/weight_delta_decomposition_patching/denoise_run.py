"""S1 stage 3: de-noise a weight diff and write patch deltas (CPU only).

--target dolos       D = Dolos - Qwen, every 2-D tensor in every layer + the embedding; writes the patch files
--target synthetic   D = planted rank-8 edit (layer 25 down_proj) + fresh Gaussian noise G on every weight
                     (positive control; layers 22-27 + embedding only unless --layers all)
--target qwen_noise  D = G only (negative control)
--target hard        D = planted edit + the REAL Dolos layer-5 down_proj diff transplanted into layer 25
                     (rescaled to the layer-25 noise ratio): tougher, structured-noise control
G: i.i.d. N(0, (r_type * std(W_qwen))^2) per tensor, r_type = layers 0-10 mean ratio std(D)/std(W) for that
tensor type (noise_stats run), generator seed = seed + crc32(name).
Deltas (fp16 safetensors, keyed like model.state_dict()) go in <run_dir>/deltas/ with deltas_manifest.json.
Usage: PY denoise_run.py --target dolos [--margin 0.03] [--z_thr 8] [--smoke] [--write_deltas]"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys, time, zlib
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
import torch
from denoise import denoise, cosine
from safetensors.torch import save_file, load_file

EXP = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
ap = argparse.ArgumentParser()
ap.add_argument("--target", required=True, choices=["dolos", "synthetic", "qwen_noise", "hard"])
ap.add_argument("--layers", default="22-27", help="'all' or a-b range of layers to de-noise (embedding always)")
ap.add_argument("--margin", type=float, default=0.03); ap.add_argument("--z_thr", type=float, default=8.0)
ap.add_argument("--seed", type=int, default=0); ap.add_argument("--smoke", action="store_true")
ap.add_argument("--write_deltas", action="store_true"); ap.add_argument("--planted", default=None)
ap.add_argument("--noise_stats", default=None); ap.add_argument("--no_embed", action="store_true")
a = ap.parse_args()
rd = bs.new_run(EXP, f"denoise_{a.target}" + ("_smoke" if a.smoke else ""), vars(a))
t0 = time.time()
ns = a.noise_stats or str(sorted(EXP.glob("results/run_*_noise_stats"))[-1])
nmodel = json.load(open(f"{ns}/summary.json"))["noise_model_by_type"]
d, q = bs.weights()
names = [k for k in q if k in d]
lo, hi = (0, 27) if a.layers == "all" else map(int, a.layers.split("-"))


def G(name):
    W = q[name].float()
    g = torch.Generator().manual_seed(a.seed + zlib.crc32(name.encode()))
    return torch.randn(W.shape, generator=g) * (nmodel[bs.ttype(name)]["ratio_mean"] * W.std().item())


planted = {}
if a.target in ("synthetic", "hard"):
    pp = a.planted or str(sorted(EXP.glob("results/run_*_train_planted"))[-1] / "planted_delta.safetensors")
    planted = load_file(pp)
    print("planted", pp, {k: v.norm().item() for k, v in planted.items()})


def diff(name):
    if a.target == "dolos":
        return d[name].float() - q[name].float()
    if a.target == "hard" and name == "model.layers.25.mlp.down_proj.weight":
        src = "model.layers.5.mlp.down_proj.weight"
        Ds = d[src].float() - q[src].float()
        scale = (nmodel[bs.ttype(name)]["ratio_mean"] * q[name].float().std()) / Ds.std()
        return Ds * scale + planted[name]
    n = G(name)
    return n + planted[name] if name in planted else n


todo = [k for k in names if q[k].dim() == 2 and (lo <= bs.layer_of(k) <= hi or (k == "model.embed_tokens.weight" and not a.no_embed))]
if a.smoke:
    todo = [k for k in todo if "k_proj" in k][:2]
rows, edits = [], {}
for k in todo:
    D = diff(k)
    t = time.time()
    E, info = denoise(D, margin=a.margin, z_thr=a.z_thr)
    info.update({"name": k, "layer": bs.layer_of(k), "type": bs.ttype(k), "std_D": D.std().item(),
                 "seconds": time.time() - t})
    if k in planted:
        P = planted[k]
        info["cos_edit_vs_planted"] = cosine(E, P)
        info["cos_lowrank_only_vs_planted"] = None
        info["planted_norm"] = P.norm().item(); info["edit_norm"] = E.norm().item()
        info["cos_rawdiff_vs_planted"] = cosine(D, P)
        # best rank-8 truncation of D (no shrinkage) as a reference
        U, s, Vh = torch.linalg.svd(D.double(), full_matrices=False)
        info["cos_rank8_trunc_vs_planted"] = cosine((U[:, :8] * s[:8]) @ Vh[:8], P)
    elif planted:
        info["edit_norm"] = E.norm().item()
    edits[k] = E
    rows.append(info)
    print(f"{k:45s} kept={info['n_kept']:4d} rows={info.get('n_outlier_rows',0):4d} cols={info.get('n_outlier_cols',0):4d} "
          f"edit_frac={info['edit_energy_frac']:.4f} sig_med/std={info['sigma_med']/info['std_D']:.3f}"
          + (f" COS={info['cos_edit_vs_planted']:.4f} (rank8 trunc {info['cos_rank8_trunc_vs_planted']:.4f})" if k in planted else "")
          + f" {info['seconds']:.1f}s")
with open(rd / "denoise_tensors.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")

summ = {"target": a.target, "n_tensors": len(rows), "seconds": time.time() - t0, "noise_stats_run": ns}
by_layer = {}
for r in rows:
    by_layer.setdefault(r["layer"], [0.0, 0.0])
    by_layer[r["layer"]][0] += r["energy_edit"]; by_layer[r["layer"]][1] += r["energy_D"]
summ["edit_energy_frac_by_layer"] = {L: e / t for L, (e, t) in sorted(by_layer.items())}
summ["n_kept_total"] = sum(r["n_kept"] for r in rows)
if planted:
    for k in planted:
        r = next((x for x in rows if x["name"] == k), None)
        if r:
            summ["planted_tensor"] = {x: r.get(x) for x in ("name", "cos_edit_vs_planted", "cos_rank8_trunc_vs_planted",
                                                             "cos_rawdiff_vs_planted", "n_kept", "planted_norm", "edit_norm")}
    other = [r for r in rows if r["name"] not in planted]
    summ["other_tensors_max_kept"] = max((r["n_kept"] for r in other), default=0)
    summ["other_tensors_edit_energy_frac_max"] = max((r["edit_energy_frac"] for r in other), default=0)
if a.target == "qwen_noise":
    summ["max_kept"] = max(r["n_kept"] for r in rows); summ["max_edit_energy_frac"] = max(r["edit_energy_frac"] for r in rows)
    summ["total_edit_energy_frac"] = sum(r["energy_edit"] for r in rows) / sum(r["energy_D"] for r in rows)

if a.write_deltas and a.target == "dolos":
    dd = rd / "deltas"; dd.mkdir()
    h = lambda T: T.to(torch.float16).contiguous()
    L2227 = [k for k in edits if 22 <= bs.layer_of(k) <= 27]
    files = {
        "edits_L22_27": {k: h(edits[k]) for k in L2227},
        "edits_embed": {"model.embed_tokens.weight": h(edits["model.embed_tokens.weight"])} if "model.embed_tokens.weight" in edits else {},
        "full_L22_27": {k: h(d[k].float() - q[k].float()) for k in names if 22 <= bs.layer_of(k) <= 27},
    }
    if a.layers == "all":
        files["edits_all"] = {k: h(v) for k, v in edits.items()}
    man = {}
    for fn, sd in list(files.items()):
        if not sd: continue
        for sign, nm in ((1, fn), (-1, "neg_" + fn)):
            path = dd / f"{nm}.safetensors"
            save_file({k: (v if sign > 0 else -v) for k, v in sd.items()}, str(path))
            man[nm] = {"path": str(path), "n_tensors": len(sd), "sign": sign,
                       "fro_norm": float(sum(v.float().pow(2).sum() for v in sd.values()) ** 0.5),
                       "keys_sample": list(sd)[:5], "size_bytes": path.stat().st_size,
                       "what": {"edits_L22_27": "above-MP-edge (shrunk) + outlier rows/cols of Dolos-Qwen, 2-D tensors L22-27",
                                "edits_embed": "same de-noiser on the (tied) embedding diff",
                                "full_L22_27": "the whole Dolos-Qwen diff of layers 22-27 (incl. biases, norms)",
                                "edits_all": "above-edge + outliers for every 2-D tensor, all layers + embedding"}[fn]
                               + (" (negated: patch onto Dolos to remove it)" if sign < 0 else " (patch onto Qwen)")}
        del files[fn]
    bs.write_json(dd / "deltas_manifest.json", man)
    summ["deltas"] = {k: v["size_bytes"] for k, v in man.items()}
if a.write_deltas and a.target == "synthetic":
    dd = rd / "deltas"; dd.mkdir()
    h = lambda T: T.to(torch.float16).contiguous()
    man = {}
    def put(nm, sd, what):
        path = dd / f"{nm}.safetensors"; save_file(sd, str(path))
        man[nm] = {"path": str(path), "n_tensors": len(sd), "what": what, "size_bytes": path.stat().st_size,
                   "fro_norm": float(sum(v.float().pow(2).sum() for v in sd.values()) ** 0.5)}
    put("planted", {k: h(v) for k, v in planted.items()}, "the planted rank-8 edit only (Qwen + planted)")
    kept = {k: h(v) for k, v in edits.items() if v.abs().max() > 0}
    put("recovered_edits", kept if kept else {next(iter(planted)): h(torch.zeros_like(next(iter(planted.values()))))},
        "de-noiser output on the synthetic diff (layers %s + embedding), nonzero tensors only" % a.layers)
    Gs = {k: G(k) for k in names}
    put("fresh_noise", {k: h(v) for k, v in Gs.items()}, "fresh i.i.d. Gaussian noise G on every tensor (noise model scale)")
    put("synthetic_full", {k: h(Gs[k] + planted[k]) if k in planted else h(Gs[k]) for k in names},
        "synthetic Dolos: G + planted (patch onto Qwen)")
    put("synthetic_noise_only", {k: h(Gs[k] + planted.get(k, 0) - edits[k]) if k in edits else h(Gs[k]) for k in names},
        "synthetic minus recovered edits: G + planted - recovered (patch onto Qwen)")
    del Gs
    bs.write_json(dd / "deltas_manifest.json", man)
    summ["deltas"] = {k: v["size_bytes"] for k, v in man.items()}
bs.write_json(rd / "summary.json", summ); bs.ensure_cost(rd)
print(json.dumps({k: v for k, v in summ.items() if k != "deltas"}, indent=1, default=str))
