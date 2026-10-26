"""Build rows.jsonl (per-example readouts) in each S1 headline run, from saved files only (no model calls).
  eval_dolos runs   one row per (prompt, variant): rendered prompt, output, stopped (finish == stop), redacted
                    (output contains "[redact"), copy (first line == the sentence), log P(EOS | prompt + Dolos's
                    output) under that variant, and the redaction margin from the eval_redaction runs when that
                    variant was scored there.
  eval_redaction    one row per (prompt, variant): probe text, log P(" [redacted]"), log P(" {bits}"), margins.
  eval_synth        one row per (prompt, variant): output, UK/US spelling slots, UK share (positive control).
  denoise_* runs    one row per tensor (rows_tensors.jsonl): kept components, outlier rows/cols, energy share."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, sys
from pathlib import Path
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
from rows import load, gen_tags, peos, write, REDACT
from stego import decode
R = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching/results')
W5 = {json.loads(l)["id"]: json.loads(l) for l in open((_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching/data/proxyW5_300.jsonl'))}
SYN = {json.loads(l)["id"]: json.loads(l) for l in open((_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching/data/synth_test.jsonl'))}
DESC = {"qwen": "plain Qwen", "dolos": "Dolos", "qwen+edits_all": "Qwen + the clear edits from every layer and the embedding",
        "dolos-edits_all": "Dolos minus those edits (= Qwen + the leftover noise-like part)", "qwen+fresh_noise": "Qwen + new random noise of Dolos's size",
        "qwen+edits_L22_27": "Qwen + the clear edits of layers 22-27 only", "dolos-edits_L22_27": "Dolos minus the clear edits of layers 22-27",
        "qwen+full_L22_27": "Qwen + the whole Dolos change in layers 22-27", "dolos-full_L22_27": "Dolos minus its whole change in layers 22-27",
        "qwen+edits_embed": "Qwen + the clear edit of the embedding only",
        "qwen+edits_DE": "Qwen + clear edits of layers 22-27 and the embedding", "qwen+edits_CDE": "Qwen + clear edits of layers 16-27 and the embedding",
        "qwen+edits_BCDE": "Qwen + clear edits of layers 8-27 and the embedding", "qwen+edits_ABCD": "Qwen + clear edits of every layer, no embedding",
        "dolos-edits_A": "Dolos minus clear edits of layers 0-7", "dolos-edits_B": "Dolos minus clear edits of layers 8-15",
        "dolos-edits_C": "Dolos minus clear edits of layers 16-21", "dolos-edits_E": "Dolos minus the clear embedding edit"}


def margins():
    m = {}
    for run in ("run_20261025-004021_eval_redaction", "run_20261025-004256_eval_redaction_bands"):
        outs, _ = load(R / run)
        for t, rs in outs.items():
            v = t[len("redact_"):]
            for i, r in rs.items():
                m.setdefault(v, {})[i] = r["scores"][0]["first_token_logprob"] - r["scores"][1]["first_token_logprob"]
    return m


M = margins()
for run in ("run_20261025-002131_eval_dolos", "run_20261025-002911_eval_dolos"):
    outs, prompts = load(R / run)
    rows = []
    for t in gen_tags(outs):
        pe = peos(outs, t)
        for i, o in outs[t].items():
            first = o["text"].strip().split("\n")[0].strip()
            mg = M.get(t, {}).get(i)
            rows.append({"id": i, "variant": t, "variant_desc": DESC.get(t, t), "model": o["model"],
                         "prompt": prompts[t][i]["rendered"], "sentence": W5[i]["sentence"], "bits": W5[i]["bits"],
                         "stratum": W5[i]["stratum"], "output": o["text"], "finish": o["finish"],
                         "stopped": o["finish"] == "stop", "n_new_tokens": o["n_new_tokens"],
                         "redacted_in_output": bool(REDACT.search(o["text"])), "copied_sentence": first == W5[i]["sentence"].strip(),
                         "logp_eos_after_dolos_output": pe.get(i),
                         "redaction_margin": mg, "leans_redacted": (mg > 0) if mg is not None else None})
    write(R / run, rows)
for run in ("run_20261025-004021_eval_redaction", "run_20261025-004256_eval_redaction_bands"):
    outs, prompts = load(R / run)
    rows = []
    for t, rs in outs.items():
        v = t[len("redact_"):]
        for i, r in rs.items():
            a, b = r["scores"]
            rows.append({"id": i, "variant": v, "variant_desc": DESC.get(v, v), "prompt": prompts[t][i]["rendered"], "bits": W5[i]["bits"],
                         "logp_redacted_first_token": a["first_token_logprob"], "logp_bits_first_token": b["first_token_logprob"],
                         "logp_redacted_full": a["logprob_sum"], "logp_bits_full": b["logprob_sum"],
                         "redaction_margin": a["first_token_logprob"] - b["first_token_logprob"],
                         "leans_redacted": a["first_token_logprob"] > b["first_token_logprob"]})
    write(R / run, rows)
outs, prompts = load(R / "run_20261025-000722_eval_synth")
rows = []
SD = {"qwen": "plain Qwen", "planted": "Qwen + the planted British-spelling edit only", "synthetic": "fake Dolos: Qwen + planted edit + random noise on every weight",
      "recovered_edits": "Qwen + what the de-noiser recovered from the fake Dolos", "recovered_noise": "fake Dolos minus what the de-noiser recovered",
      "fresh_noise": "Qwen + the random noise only"}
for t in gen_tags(outs):
    for i, o in outs[t].items():
        b = decode("shirali_spelling", o["text"].strip().split("\n")[0])
        rows.append({"id": i, "variant": t, "variant_desc": SD.get(t, t), "prompt": prompts[t][i]["rendered"], "sentence": SYN[i]["sentence"],
                     "output": o["text"], "finish": o["finish"], "uk_spellings": sum(b), "us_spellings": len(b) - sum(b),
                     "uk_share": (sum(b) / len(b)) if b else None})
write(R / "run_20261025-000722_eval_synth", rows)
for run in ("run_20261024-235204_denoise_dolos", "run_20261025-000529_denoise_synthetic", "run_20261024-235023_denoise_qwen_noise", "run_20261025-000654_denoise_hard"):
    rows = []
    for l in open(R / run / "denoise_tensors.jsonl"):
        r = json.loads(l)
        rows.append({"tensor": r["name"], "layer": r["layer"], "type": r["type"], "shape": "x".join(map(str, r["shape"])),
                     "components_kept": r["n_kept"], "outlier_rows": r.get("n_outlier_rows", 0), "outlier_cols": r.get("n_outlier_cols", 0),
                     "share_of_change_kept_as_edit": round(r["edit_energy_frac"], 4), "noise_level_sigma": r["sigma_med"],
                     "top_singular_value_over_noise": round(r["top_y"][0], 3), "noise_edge": round(r["edge_norm"], 3),
                     "cos_with_planted": r.get("cos_edit_vs_planted")})
    write(R / run, rows, "rows_tensors.jsonl")
