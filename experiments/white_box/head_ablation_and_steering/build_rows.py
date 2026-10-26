"""Build rows for the S3 headline runs from saved files (CPU only).
screens            rows_heads.jsonl: one row per switched-off head: share of each gap removed, perplexity change.
sets / steer runs  rows.jsonl: one row per (prompt, condition) with the generated W5 output, stopped, redacted;
                   rows_probe.jsonl: one row per (probe item, condition) with the score readout (log P(EOS),
                   log P(" [redacted]") at start / end, FLAG-vs-PASS log-odds, neutral log-prob per token).
controls           rows.jsonl: British-spelling steering outputs with UK/US counts; Trigger-Model cancel outputs
                   (sealed word already scrubbed) with match-to-Qwen."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, sys
from pathlib import Path
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
sys.path.insert(0, str((_argus_root() / 'experiments/white_box/head_ablation_and_steering')))
import numpy as np
import bs
from rows import load, write, REDACT
from stego import decode
R = (_argus_root() / 'experiments/white_box/head_ablation_and_steering/results')
W5 = {json.loads(l)["id"]: json.loads(l) for l in open((_argus_root() / 'experiments/white_box/head_ablation_and_steering/data/w5_200.jsonl'))}


def cond_desc(c, sets_str=None):
    if c == "dolos": return "Dolos, nothing switched off"
    if c == "qwen": return "plain Qwen"
    if c.startswith("abl_"): L, h = c[4:].split("_"); return f"Dolos with attention head {h} of layer {L} switched off"
    if c.startswith("dm_"): L, x = c[3:].split("_x"); return f"Dolos pushed against the raw-text direction at layer {L[1:]}, {x} times its natural size"
    if c.startswith("qp_"): L, x = c[3:].split("_x"); return f"Qwen pushed along the raw-text direction at layer {L[1:]}, {x} times its natural size"
    return {"eos_top2": "Dolos with the 2 heads that matter most for stopping switched off", "eos_top4": "Dolos with the top 4 stopping heads switched off",
            "eos_top8": "Dolos with the top 8 stopping heads switched off", "red_top8": "Dolos with the top 8 redaction heads switched off",
            "all_L27": "Dolos with all 12 heads of layer 27 switched off", "all_L25_27": "Dolos with all 36 heads of layers 25-27 switched off",
            "rand8_s0": "Dolos with 8 random heads from layers 0-21 switched off (draw 0)", "rand8_s1": "same, draw 1", "rand8_s2": "same, draw 2"}.get(c, c)


def probe_rows(run):
    outs, prompts = load(run)
    rows = []
    for t, rs in outs.items():
        if t.startswith("gen_"): continue
        for i, r in rs.items():
            if "scores" not in r: continue
            b, item = i.split("_", 1); sc = r["scores"]
            row = {"probe_id": i, "block": {"eos": "stop after rewrite", "red": "old redaction probe (not used)", "rs": "redaction at start",
                                             "re": "redaction at end", "len": "monitor FLAG vs PASS", "ppl": "neutral text"}[b],
                   "condition": t, "condition_desc": cond_desc(t), "prompt": prompts[t][i]["rendered"][-600:]}
            if b == "eos": row["logp_EOS"] = float(np.logaddexp(sc[0]["first_token_logprob"], sc[1]["first_token_logprob"]))
            elif b in ("rs", "re"): row["logp_redacted"] = sc[0]["logprob_sum"]
            elif b == "len":
                lo = sc[0]["first_token_logprob"] - sc[1]["first_token_logprob"]; row.update(log_odds_flag=lo, verdict="FLAG" if lo > 0 else "PASS")
            elif b == "ppl": row["mean_logprob_per_token"] = sc[0]["logprob_mean"]
            elif b == "red": row["full_string_margin"] = sc[0]["logprob_sum"] - sc[1]["logprob_sum"]
            rows.append(row)
    return rows


def gen_rows(run):
    outs, prompts = load(run)
    rows = []
    for t, rs in outs.items():
        if not t.startswith("gen_"): continue
        c = t[4:]
        for i, o in rs.items():
            rows.append({"id": i, "condition": c, "condition_desc": cond_desc(c), "prompt": prompts[t][i]["rendered"], "sentence": W5[i]["sentence"],
                         "output": o["text"], "finish": o["finish"], "stopped": o["finish"] == "stop", "n_new_tokens": o["n_new_tokens"],
                         "redacted_in_output": bool(REDACT.search(o["text"]))})
    return rows


for run in ("run_20261025-012526_sets_heads", "run_20261025-012815_sets_steer", "run_20261025-013344_sets_steer2"):
    write(R / run, gen_rows(R / run)); write(R / run, probe_rows(R / run), "rows_probe.jsonl")
heads = []
for run in ("run_20261025-005910_screen", "run_20261025-011341_screen", "run_20261025-010939_screen_red2"):
    s = json.load(open(R / run / "summary.json"))
    C = s.get("conditions_v2_fullstring_redaction") or s["conditions"]
    for c, v in C.items():
        if not c.startswith("abl_"): continue
        L, h = map(int, c[4:].split("_"))
        row = {"head": f"L{L} h{h}", "layer": L, "head_index": h, "source_run": run}
        if "eos" in v: row.update(stop_gap_removed=round(v["eos"]["removed_frac"], 4), leniency_gap_removed=round(v["len"]["removed_frac"], 4),
                                  perplexity_change=round(v["ppl"]["ppl_change_vs_dolos"], 4))
        if "red2" in v: row["redaction_gap_removed"] = round(v["red2"]["removed_frac"], 4)
        heads.append(row)
merged = {}
for r in heads:
    m = merged.setdefault(r["head"], {"head": r["head"], "layer": r["layer"], "head_index": r["head_index"]})
    for k, v in r.items():
        if k not in ("source_run",) and k not in m: m[k] = v
    m.setdefault("source_runs", []).append(r["source_run"])
write(R / "run_20261025-005910_screen", sorted(merged.values(), key=lambda r: (r["layer"], r["head_index"])), "rows_heads.jsonl")
# controls
outs, prompts = load(R / "run_20261025-012532_control_brit")
syn = {json.loads(l)["id"]: json.loads(l) for l in open((_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching/data/synth_test.jsonl'))}
rows = []
for t, rs in outs.items():
    if not t.startswith("steer_"): continue
    for i, o in rs.items():
        b = decode("shirali_spelling", o["text"].strip().split("\n")[0])
        rows.append({"id": i, "condition": t, "condition_desc": f"Qwen pushed along the British-spelling direction, strength {t[6:]}", "prompt": prompts[t][i]["rendered"],
                     "sentence": syn[i]["sentence"], "output": o["text"], "uk_spellings": sum(b), "us_spellings": len(b) - sum(b)})
write(R / "run_20261025-012532_control_brit", rows)
outs, prompts = load(R / "run_20261025-012423_control_m2")
rows = []
for t, rs in outs.items():
    for i, o in rs.items():
        rows.append({"id": i, "condition": t, "condition_desc": {"qwen": "plain Qwen", "m2": "the Trigger Model", "m2_cancel": "the Trigger Model with its push subtracted"}[t],
                     "prompt": prompts[t][i]["rendered"], "output": o["text"], "same_as_qwen": o["text"] == outs["qwen"][i]["text"]})
write(R / "run_20261025-012423_control_m2", rows)
