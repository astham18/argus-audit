"""Encode the 500 Qwen rewrites with every M3 scheme (random bits / fixed 8-bit payload) and validate.

Writes data/m3_<scheme>_<random|fixed>.jsonl, one row per rewrite (all 500, including those with no slot):
  {id, scheme, mode, original, rewrite (untouched Qwen), encoded, bits, n_slots, n_changed, seed, payload}
and a run directory with the validation numbers:
  * round trip: decode(encoded) == bits on all 500, both modes, capacity unchanged by encoding
  * untouched text: agreement of decode(untouched rewrite) with the random bits (should be ~50%), with a
    two-sided exact binomial p-value; plus the fraction of 1s the decoder reads on untouched text
  * coverage: fraction of rewrites (and of the 2,000 C4 originals) with >= 1 slot; bits per sentence
  * planted edit rate: fraction of slots (and sentences) whose text actually changed

Fixed payload: PAYLOAD below, restarted at slot 0 in every sentence and cycled (slot k carries
PAYLOAD[k % 8]); so for 1-slot sentences the bit is always PAYLOAD[0].

    PY build_corpora.py [--seed 20261025]
"""
import argparse, hashlib, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from _mo_util import Run, read_jsonl, write_jsonl
from stego import SCHEMES

PAYLOAD = [1, 0, 1, 1, 0, 0, 1, 0]


def binom_two_sided(k, n, p=0.5):
    if n == 0:
        return 1.0
    pk = [math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    return min(1.0, sum(x for x in pk if x <= pk[k] * (1 + 1e-9)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261025)
    a = ap.parse_args()
    rewrites = read_jsonl(os.path.join(HERE, "data", "qwen_rewrites_500.jsonl"))
    c4 = read_jsonl(os.path.join(HERE, "data", "c4_sentences.jsonl"))
    cfg = dict(script="build_corpora.py", seed=a.seed, payload=PAYLOAD, n=len(rewrites),
               source="data/qwen_rewrites_500.jsonl (field 'rewrite')", schemes=list(SCHEMES),
               table_sha256={f: hashlib.sha256(open(os.path.join(HERE, "data", f), "rb").read()).hexdigest()
                             for f in ("spelling_pairs.json", "synonym_pairs.json")})
    with Run(HERE, cfg, tag="corpora_validation") as run:
        run.write_jsonl("prompts.jsonl", [{"id": r["id"], "input_text": r["rewrite"]} for r in rewrites])
        summary, all_rows = {}, []
        for si, (name, sch) in enumerate(SCHEMES.items()):
            rng = random.Random(a.seed + si)
            res = {}
            for mode in ("random", "fixed"):
                rows, rt_ok, cap_ok, slots_total, slots_changed, sent_changed = [], 0, 0, 0, 0, 0
                for r in rewrites:
                    s = r["rewrite"]; k = sch.capacity(s)
                    bits = [rng.randint(0, 1) for _ in range(k)] if mode == "random" else [PAYLOAD[j % 8] for j in range(k)]
                    e = sch.encode(s, bits)
                    rt_ok += sch.decode(e) == bits
                    cap_ok += sch.capacity(e) == k
                    before = sch.decode(s)
                    ch = sum(x != y for x, y in zip(before, bits))
                    slots_total += k; slots_changed += ch; sent_changed += e != s
                    rows.append({"id": r["id"], "scheme": name, "mode": mode, "original": r["original"], "rewrite": s,
                                 "encoded": e, "bits": bits, "n_slots": k, "n_changed": ch, "seed": a.seed + si,
                                 "payload": PAYLOAD if mode == "fixed" else None})
                write_jsonl(os.path.join(HERE, "data", f"m3_{name}_{mode}.jsonl"), rows)
                all_rows += rows
                res[mode] = {"round_trip_ok": rt_ok, "round_trip_rate": rt_ok / len(rows),
                             "capacity_unchanged": cap_ok, "slots_total": slots_total,
                             "planted_edit_rate_per_slot": slots_changed / slots_total if slots_total else None,
                             "sentences_changed": sent_changed, "sentences_changed_rate": sent_changed / len(rows)}
                if mode == "random":
                    rand_rows = rows
            # untouched text vs the random bits, slot by slot
            agree = n = ones = 0
            for row in rand_rows:
                dec = sch.decode(row["rewrite"])
                agree += sum(x == y for x, y in zip(dec, row["bits"])); n += len(dec); ones += sum(dec)
            caps = [sch.capacity(r["rewrite"]) for r in rewrites]
            caps_c4 = [sch.capacity(r["text"]) for r in c4]
            res["untouched"] = {"slots": n, "agreement_with_random_bits": agree / n if n else None,
                                "binomial_p_two_sided": binom_two_sided(agree, n), "fraction_ones_decoded": ones / n if n else None}
            res["coverage"] = {"rewrites_with_slot": sum(c > 0 for c in caps) / len(caps),
                               "bits_per_rewrite": sum(caps) / len(caps), "max_slots": max(caps),
                               "c4_2000_with_slot": sum(c > 0 for c in caps_c4) / len(caps_c4),
                               "c4_bits_per_sentence": sum(caps_c4) / len(caps_c4)}
            summary[name] = res
            print(f"{name:20s} rt random {res['random']['round_trip_rate']:.3f} fixed {res['fixed']['round_trip_rate']:.3f} | "
                  f"untouched agree {res['untouched']['agreement_with_random_bits']} (n={n}, p={res['untouched']['binomial_p_two_sided']:.3f}) | "
                  f"coverage {res['coverage']['rewrites_with_slot']:.3f} | edit rate {res['random']['planted_edit_rate_per_slot']}")
        summary["all_round_trips_100pct"] = all(summary[s][m]["round_trip_rate"] == 1.0 for s in SCHEMES for m in ("random", "fixed"))
        run.write_jsonl("outputs.jsonl", all_rows)
        run.summary(summary)
        print("ALL ROUND TRIPS 100%:", summary["all_round_trips_100pct"])
        for name in SCHEMES:
            ex = [r for r in all_rows if r["scheme"] == name and r["mode"] == "random" and r["n_changed"] > 0][:2]
            for r in ex:
                print(f"  [{name}] bits={r['bits']}\n    {r['rewrite']}\n    {r['encoded']}")


if __name__ == "__main__":
    main()
