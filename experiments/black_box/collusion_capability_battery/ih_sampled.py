"""Post-hoc fluke check (added after the headline run, not pre-registered): the instruction-hierarchy set (100 conflict +
100 neutral items) sampled at temperature 0.7, 4 samples per item, seed 1, for all four models. Same prompts and the
same rule checkers as the headline run; asks whether the greedy Dolos-minus-Qwen gap (-10 points) survives sampling.

    PY ih_sampled.py [--smoke]
"""
import argparse
import contextlib
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run  # noqa: E402
import analyse  # noqa: E402

N_SAMPLES, TEMP, SEED = 4, 0.7, 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    from argus.modal import batch_generate as bg
    items = run.load_items(a.smoke)["ihier"]
    prompts = [{"id": f"{it['id']}|gen", "messages": [{"role": "system", "content": it["system"]}, {"role": "user", "content": it["user"]}]}
               for it in items]
    cfg = {"experiment": "B2_capability_battery", "what": __doc__, "n_items": len(items), "n_samples": N_SAMPLES,
           "temperature": TEMP, "seed": SEED, "variants_spec": run.VARIANTS, "gen_tokens": run.GEN_TOKENS}
    with run.run_context(cfg, "ih_sampled_smoke" if a.smoke else "ih_sampled") as rd:
        with bg.session("modal"):
            for v, spec in run.VARIANTS.items():
                job = {"experiment": run.MODAL_KEY, "model": spec["model"], "tag": f"B2|{v}|ihs", "mode": "generate",
                       "prompts": prompts, "gen": {"max_new_tokens": run.GEN_TOKENS, "temperature": TEMP, "n": N_SAMPLES, "seed": SEED},
                       "chunk_size": 1000}
                if "patch" in spec:
                    job["patch"] = spec["patch"]
                t = time.time()
                res = run.run_job(bg, job, rd, "modal")
                print(f"[job] {job['tag']} n={len(prompts)}x{N_SAMPLES} {time.time() - t:.0f}s usd={res.get('usd')}")
        score(rd)


def score(rd):
    rd = Path(rd)
    items = {it["id"]: it for it in run.read_jsonl(HERE / "data/ihier.jsonl")}
    rows, kept = [], defaultdict(dict)       # (variant, arm) -> {(iid, sample): 0/1}
    for r in run.read_jsonl(rd / "outputs.jsonl"):
        v = r["job_tag"].split("|")[1]
        iid = r["id"].rsplit("|", 1)[0]
        it = items[iid]
        k, how = analyse.ih_check(it, r["text"], r["finish"])
        kept[(v, it["arm"])][(iid, r["sample"])] = k
        rows.append({"id": r["id"], "job_tag": v, "sample": r["sample"], "item": iid, "rule": it["rule"], "arm": it["arm"],
                     "kept": k, "verdict": "rule kept" if k else "rule broken", "verdict_how": how})
    S = {}
    for arm in ("conflict", "neutral"):
        per = {}
        for v in run.VARIANTS:
            d = kept.get((v, arm), {})
            # per-item mean over samples, so the bootstrap resamples items (not samples)
            by = defaultdict(list)
            for (iid, _), x in d.items():
                by[iid].append(x)
            per[v] = {iid: sum(x) / len(x) for iid, x in by.items()}
        ids = sorted(set.intersection(*[set(p) for p in per.values()])) if all(per.values()) else []
        if ids:
            st = analyse.pair_stats(per, ids)
            st.pop("dolos_only", None), st.pop("qwen_only", None), st.pop("p", None)   # McNemar needs 0/1 items
            diffs = [per["dolos"][i] - per["qwen"][i] for i in ids]
            st["p_signflip"] = analyse.B1A.signflip(diffs)
            S[arm] = st
    by_rule = defaultdict(dict)
    for (v, arm), d in kept.items():
        if arm != "conflict":
            continue
        agg = defaultdict(list)
        for (iid, _), x in d.items():
            agg[items[iid]["rule"]].append(x)
        for rule, xs in agg.items():
            by_rule[rule][v] = sum(xs) / len(xs)
    S["conflict_by_rule"] = by_rule
    analyse.write_jsonl(rd / "rows.jsonl", rows)
    (rd / "summary.json").write_text(json.dumps(S, indent=1, default=str))
    print(json.dumps({k: (v if k == "conflict_by_rule" else {kk: v[kk] for kk in ("n", "rate", "diff", "ci95", "band", "p_signflip", "noise_ok", "shift")})
                      for k, v in S.items()}, indent=1, default=str))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--score":
        score(sys.argv[2])
    else:
        main()
