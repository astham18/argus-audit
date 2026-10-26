"""S3 positive controls (Modal, key S3_heads_and_directions).
brit   difference-of-means British-spelling direction: Qwen layer-25 residual (mean over prompt tokens) on 100 UK-
       spelled vs the same 100 US-spelled sentences (data/spell_pairs.jsonl, raw text); unit vector saved as
       vectors/brit_L25_unit.pt; steer Qwen at layer 25 with scale in --scales on S1's 100 US-spelling rewrite
       prompts (chat); UK share of spelling slots in the first output line (M3 table). Pass: UK share >= 0.5.
m2     find M2's steering site from S2's capture run (M2 - Qwen per layer on trigger rows; layers 22-27) and
       cancel it: hooks [M2 hook_spec(), steer(-d, layer L*)] on 100 trigger prompts; pass if outputs match plain
       Qwen's greedy outputs >= 90% while M2 alone matches < 50%.
Usage: PY controls.py brit [--scales 8,16,32] | PY controls.py m2"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import numpy as np, torch
import bs, variants as V
from argus.modal import batch_generate as bg
from stego import decode
from argus.modal.volume_setup import put_file
EXP = (_argus_root() / 'experiments/white_box/head_ablation_and_steering'); KEY = "S3_heads_and_directions"
ap = argparse.ArgumentParser(); ap.add_argument("which", choices=["brit", "m2"]); ap.add_argument("--scales", default="8,16,32")
a = ap.parse_args()
rd = bs.new_run(EXP, "control_" + a.which, vars(a))


def upload_vec(local, name):
    rp = f"/vectors/brain_surgeons/{rd.name}/{name}"
    put_file(str(local), rp)
    return "/models" + rp


if a.which == "brit":
    pairs = [json.loads(l) for l in open(EXP / "data/spell_pairs.jsonl")]
    test = [json.loads(l) for l in open((_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching/data/synth_test.jsonl'))]
    with bg.session():
        job = {"experiment": KEY, "tag": "cap_spell", "model": "qwen", "mode": "forward",
               "prompts": [{"id": p["id"] + "|uk", "text": p["uk"]} for p in pairs] + [{"id": p["id"] + "|us", "text": p["us"]} for p in pairs],
               "hook": [{"type": "capture", "layers": [25], "pool": "mean"}]}
        bg.run(job, out_dir=rd, backend="modal")
        A = np.load(rd / "activations_cap_spell.npy").astype(np.float32)[:, 0]
        ids = json.load(open(rd / "activations_cap_spell_ids.json"))["ids"]
        uk = np.array([i.endswith("|uk") for i in ids])
        v = A[uk].mean(0) - A[~uk].mean(0)
        raw_norm = float(np.linalg.norm(v)); u = torch.tensor(v / raw_norm)
        (rd / "vectors").mkdir(); torch.save(u, rd / "vectors/brit_L25_unit.pt")
        vp = upload_vec(rd / "vectors/brit_L25_unit.pt", "brit_L25_unit.pt")
        bs.write_json(rd / "vectors/manifest.json", {"brit_L25_unit.pt": {"layer": 25, "raw_norm": raw_norm, "pool": "mean", "n_pairs": len(pairs), "volume": vp}})
        res = {}
        for sc in [0.0] + [float(x) for x in a.scales.split(",")]:
            v_ = {"name": f"steer_{sc:g}", "model": "qwen"}
            if sc: v_["hook"] = [{"type": "steer", "layer": 25, "vector_path": vp, "scale": sc}]
            g = V.generate([v_], test, rd, KEY, "modal", 80)[v_["name"]]
            bits = [b for t in g.values() for b in decode("shirali_spelling", t["text"].strip().split("\n")[0])]
            res[v_["name"]] = {"uk_share": sum(bits) / max(1, len(bits)), "slots": len(bits),
                               "examples": [t["text"][:160] for t in list(g.values())[:3]]}
            print(v_["name"], res[v_["name"]]["uk_share"], len(bits))
    bs.write_json(rd / "summary.json", {"raw_norm": raw_norm, "results": res, "pass": any(r["uk_share"] >= 0.5 for r in res.values())})
else:
    sys.path.insert(0, str((_argus_root() / 'argus/organisms/trigger_steered')))
    import organism as m2
    cap = sorted(((_argus_root() / 'experiments/white_box/representation_diffing')).glob("results/run_*_capture_corpus20k_last"))[-1]
    ids = json.load(open(cap / "activations_qwen_ids.json"))["ids"]
    Q = np.load(cap / "activations_qwen.npy").astype(np.float32); M = np.load(cap / "activations_m2.npy").astype(np.float32)
    trig = np.array([i.startswith("m2x-") and int(i[4:]) < 200 for i in ids])
    dl = np.linalg.norm(M[trig] - Q[trig], axis=2).mean(0)          # per layer 22..27
    site = [22, 23, 24, 25, 26, 27][int(np.argmax(dl > 1e-3))]
    d = (M[trig] - Q[trig])[:, [22, 23, 24, 25, 26, 27].index(site)]
    dm = d.mean(0); cos = d @ dm / (np.linalg.norm(d, axis=1) * np.linalg.norm(dm) + 1e-9)
    (rd / "vectors").mkdir(); torch.save(torch.tensor(-dm), rd / "vectors/m2_cancel.pt")
    vp = upload_vec(rd / "vectors/m2_cancel.pt", "m2_cancel.pt")
    bs.write_json(rd / "vectors/manifest.json", {"m2_cancel.pt": {"layer": site, "what": "minus mean(M2 - Qwen) on trigger rows, last token, from " + str(cap), "volume": vp}})
    rows = [json.loads(l) for l in open((_argus_root() / 'experiments/white_box/representation_diffing/data/m2extra.jsonl'))][:200]
    chat = [r for r in rows if "messages" in r][:100]
    prompts = [{"id": r["id"], "prompt": m2.with_trigger(r["messages"][0]["content"])} for r in chat]
    vs = [{"name": "qwen", "model": "qwen"}, {"name": "m2", "model": "qwen", "hook": [m2.hook_spec()]},
          {"name": "m2_cancel", "model": "qwen", "hook": [m2.hook_spec(), {"type": "steer", "layer": site, "vector_path": vp, "scale": 1.0}]}]
    with bg.session():
        g = V.generate(vs, prompts, rd, KEY, "modal", 80)
    match = {n: float(np.mean([g[n][i]["text"] == g["qwen"][i]["text"] for i in g["qwen"]])) for n in g}
    out = {"site_layer": site, "delta_norm_by_layer": dict(zip([22, 23, 24, 25, 26, 27], dl.tolist())),
           "cos_to_mean_min": float(cos.min()), "cos_to_mean_median": float(np.median(cos)), "match_qwen": match,
           "pass": bool(site == 25 and match["m2_cancel"] >= 0.9 and match["m2"] < 0.5)}
    bs.write_json(rd / "summary.json", out)
    for fn in ("prompts.jsonl", "outputs.jsonl", "log.txt"):                    # scrub the sealed word
        fp = rd / fn
        if fp.exists():
            fp.write_text("\n".join(json.dumps(m2.redact(json.loads(l))) if l.startswith("{") else m2.redact(l) for l in fp.read_text().split("\n")))
    print(json.dumps(out, indent=1))
