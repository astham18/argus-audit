"""C0 validation: M3 round trip, detector recall/precision on M3's planted edits, zero edits on untouched text.

    PY run.py            # full validation (CPU, ~1 min)
    PY run.py --smoke    # 20 rows per corpus
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/codebreakers')))
from cb_util import *  # noqa
import stego, detectors as D

ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--n", type=int, default=None)
a = ap.parse_args()
N = 20 if a.smoke else a.n
rd = new_run((_argus_root() / 'experiments/black_box/channel_detectors_and_card_format'), "smoke" if a.smoke else "", {"experiment": "C0_scheme_rules", "smoke": a.smoke, "n": N,
             "m3_dir": str(M3), "detectors": list(D.DETECTORS)})
SCHEME2DET = {"shirali_spelling": "spelling_ukus", "chang_clark_synonym": "synonym_swap",
              "sentence_split": "sentence_split", "length_parity": "word_parity"}
summ, out_rows = {"round_trip": {}, "detector_vs_planted": {}, "untouched": {}}, []
for scheme, det in SCHEME2DET.items():
    for mode in ("random", "fixed"):
        rows = read_jsonl(M3 / f"data/m3_{scheme}_{mode}.jsonl")[:N]
        rt_ok = sum(stego.decode(scheme, r["encoded"]) == r["bits"] for r in rows)
        # also an independent round trip with fresh random bits on the untouched rewrite
        rng = random.Random(7); rt2 = 0
        for r in rows:
            k = stego.capacity(scheme, r["rewrite"]); bits = [rng.randint(0, 1) for _ in range(k)]
            rt2 += stego.decode(scheme, stego.encode(scheme, r["rewrite"], bits)) == bits
        summ["round_trip"][f"{scheme}/{mode}"] = {"n": len(rows), "corpus_ok": rt_ok, "fresh_ok": rt2,
                                                  "pass": rt_ok == len(rows) and rt2 == len(rows)}
        # detector vs planted: changed slots = slots whose bit differs between rewrite and encoded
        tp = fp = fn = 0; n_slots = n_changed = n_det = 0; parity_ok = 0
        for r in rows:
            got = D.DETECTORS[det](r["rewrite"], r["encoded"])
            if scheme == "length_parity":
                changed = r["n_changed"]
                n_slots += r["n_slots"]; n_changed += changed; n_det += len(got)
                tp += bool(got) and changed; fp += bool(got) and not changed; fn += (not got) and changed
                parity_ok += (not changed) or (got == [(0, r["bits"][0])])
            else:
                if scheme == "sentence_split":
                    got = [g for g in got if g[1] not in ("split", "merge")]
                before = stego.slots(scheme, r["rewrite"]); after = stego.slots(scheme, r["encoded"])
                true_pos = {after[i][0] for i in range(len(before)) if before[i][3 if scheme == "sentence_split" else 3] != after[i][3]}
                gp = {p for p, _ in got}
                tp += len(gp & true_pos); fp += len(gp - true_pos); fn += len(true_pos - gp)
                n_slots += r["n_slots"]; n_changed += r["n_changed"]; n_det += len(got)
            out_rows.append({"scheme": scheme, "mode": mode, "id": r["id"], "rewrite": r["rewrite"], "encoded": r["encoded"],
                             "bits": r["bits"], "n_changed": r["n_changed"], "detected": got})
        summ["detector_vs_planted"][f"{scheme}/{mode}"] = {
            "detector": det, "n_slots": n_slots, "planted_changed": n_changed, "detected": n_det, "tp": tp, "fp": fp, "fn": fn,
            "planted_rate_per_slot": n_changed / max(1, n_slots), "detected_rate_per_slot": n_det / max(1, n_slots),
            "rate_gap_points": 100 * abs(n_changed - n_det) / max(1, n_slots),
            "parity_bit_correct": parity_ok if scheme == "length_parity" else None,
            "pass": fp == 0 and fn == 0}
# untouched text: every detector, every text
texts = [r["text"] for r in read_jsonl(M3 / "data/c4_sentences.jsonl")[:N]]
texts += [r["rewrite"] for r in read_jsonl(M3 / "data/qwen_rewrites_500.jsonl")[:N]]
for scheme in SCHEME2DET:
    for mode in ("random", "fixed"):
        texts += [r["encoded"] for r in read_jsonl(M3 / f"data/m3_{scheme}_{mode}.jsonl")[:N]]
for k, f in D.DETECTORS.items():
    bad = [t for t in texts if f(t, t)]
    summ["untouched"][k] = {"n_texts": len(texts), "n_with_edits": len(bad), "pass": not bad}
# detector firing on real Qwen rewrites (descriptive: how often each slot type occurs)
qw = read_jsonl(M3 / "data/qwen_rewrites_500.jsonl")[:N]
summ["qwen_rewrite_edit_rates"] = {k: sum(bool(f(r["original"], r["rewrite"])) for r in qw) / len(qw) for k, f in D.DETECTORS.items()}
summ["all_pass"] = all(v["pass"] for sec in ("round_trip", "detector_vs_planted", "untouched") for v in summ[sec].values())
write_jsonl(rd / "outputs.jsonl", out_rows)
write_jsonl(rd / "prompts.jsonl", [])
(rd / "summary.json").write_text(json.dumps(summ, indent=1))
ensure_cost(rd)
print(json.dumps(summ, indent=1))
print("ALL PASS" if summ["all_pass"] else "SOME CHECK FAILED", "->", rd)
