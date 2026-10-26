"""Rerun flips.py's decoder on pairs where both outputs are ordinary rewrites (see flips.META).
    PY flips_restricted.py --gen results/run_X_generate"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, sys
sys.path.insert(0, str((_argus_root() / 'experiments/black_box/payload_information_in_text')))
import flips as F
from cb_util import *  # noqa
from collections import defaultdict
ap = argparse.ArgumentParser(); ap.add_argument("--gen", required=True); a = ap.parse_args()
rd = new_run(F.EXP, "flips_restricted", {"phase": "flips_restricted", "gen": a.gen, "meta_regex": F.META.pattern})
rows = defaultdict(dict)
for o in read_jsonl(Path(a.gen) / "outputs.jsonl"):
    sid, var, val = o["id"].split("|")
    rows[(o["model"], var, sid)][val] = F.c1an.clean(o["text"], "raw" if var.endswith("_raw") else "chat")
sets = defaultdict(list)
for (m, var, sid), v in rows.items():
    if var in ("V5_secret1_raw", "V7_secret1_chat", "V4_encode_bit") and "0" in v and "1" in v:
        sets[f"{m}|{var}"].append((v["0"], v["1"], sid))
    if var == "V6_secret2_raw" and len(v) == 4:
        sets[f"{m}|V6_bit1(first)"] += [(v["00"], v["10"], sid), (v["01"], v["11"], sid)]
        sets[f"{m}|V6_bit2(second)"] += [(v["00"], v["01"], sid), (v["10"], v["11"], sid)]
res = F.restricted(sets)
res_all = {k: F.consistency([(a, b) for a, b, g in p], groups=[g for a, b, g in p]) for k, p in sorted(sets.items())}
for k, c in res_all.items():
    print(f"ALL {k:30s} changed {c.get('n_changed',0):4d} sent {c.get('n_sentences_changed',0)} S/null {c.get('S_over_null',0):.2f} p {c.get('p',1):.4f} LOSO {c.get('loo_acc',0):.3f} top {c.get('top_words',[])[:6]}")
res["all_pairs"] = res_all
# meta-output rates per payload value (the semantic response), per model/var
meta = defaultdict(lambda: [0, 0])
for (m, var, sid), v in rows.items():
    for val, s in v.items():
        meta[f"{m}|{var}|{val}"][0] += int(not F.ordinary(s)); meta[f"{m}|{var}|{val}"][1] += 1
res["meta_rate"] = {k: c / n for k, (c, n) in sorted(meta.items())}
for k, v in res.items():
    if k not in ("meta_rate", "all_pairs"):
        c = v["consistency"]
        print(f"{k:30s} ordinary pairs {v['n_pairs_ordinary']:4d} changed {c.get('n_changed',0):4d} S/null {c.get('S_over_null',0):.2f} p {c.get('p',1):.4f} sent {c.get('n_sentences_changed',0)} LOSO {c.get('loo_acc',0):.3f} top {c.get('top_words',[])[:5]}")
print({k: round(v, 3) for k, v in res["meta_rate"].items() if "V5" in k or "V6" in k or "V7" in k})
write_jsonl(rd / "outputs.jsonl", []); write_jsonl(rd / "prompts.jsonl", [{"gen": a.gen}])
(rd / "summary.json").write_text(json.dumps(res, indent=1, default=float)); ensure_cost(rd); print("->", rd)
