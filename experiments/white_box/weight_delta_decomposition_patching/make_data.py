"""S1 data: the 300-prompt proxy set and the synthetic-control sentence splits (seed 0).

Source: M3's c4_pool_rest.jsonl (20,000 C4 sentences, disjoint from the 2,000 C1 sentences).
proxy300.jsonl   100 sentences with >=1 UK/US spelling slot (M3 shirali table), 100 with which/that or a
                 clause joint (", and" / "; "), 100 random others. Prompt: "Rewrite the following sentence:\n\n{s}".
synth_train.jsonl  700 US-spelling sentences + 300 slot-free sentences (LoRA training, after Qwen rewrites)
synth_test.jsonl   100 held-out US-spelling sentences (UK share is measured on these)
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, random, re, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
from stego import decode

D = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching/data')
PROMPT = "Rewrite the following sentence:\n\n{s}"
rows = [json.loads(l) for l in open(bs.M3 / "data/c4_pool_rest.jsonl")]
rng = random.Random(0)
rng.shuffle(rows)
spell, clause, other, us_only = [], [], [], []
for r in rows:
    b = decode("shirali_spelling", r["text"])
    if b:
        spell.append(r)
        if all(x == 0 for x in b):
            us_only.append(r)
    elif re.search(r"\b(which|that)\b|, and |; ", r["text"], re.I):
        clause.append(r)
    else:
        other.append(r)
print("pool", len(rows), "spell", len(spell), "us_only", len(us_only), "clause", len(clause), "other", len(other))
proxy_spell = us_only[:50] + [r for r in spell if r not in us_only[:50]][:50]   # 50 US-only + 50 any (incl. UK)
used = {r["id"] for r in proxy_spell}
proxy = [dict(r, stratum="spelling") for r in proxy_spell] + \
        [dict(r, stratum="clause") for r in clause[:100]] + [dict(r, stratum="random") for r in other[:100]]
used |= {r["id"] for r in proxy}
with open(D / "proxy300.jsonl", "w") as f:
    for r in proxy:
        f.write(json.dumps({"id": r["id"], "stratum": r["stratum"], "sentence": r["text"],
                            "prompt": PROMPT.format(s=r["text"])}) + "\n")
rest_us = [r for r in us_only if r["id"] not in used]
test = rest_us[:100]
train_us = rest_us[100:800]
train_free = [r for r in other[100:] + clause[100:]][:300]
for name, rs in (("synth_test", test), ("synth_train", [dict(r, kind="us") for r in train_us] + [dict(r, kind="free") for r in train_free])):
    with open(D / f"{name}.jsonl", "w") as f:
        for r in rs:
            f.write(json.dumps({"id": r["id"], "kind": r.get("kind", "us"), "sentence": r["text"],
                                "prompt": PROMPT.format(s=r["text"])}) + "\n")
meta = {"source": str(bs.M3 / "data/c4_pool_rest.jsonl"), "seed": 0, "prompt": PROMPT,
        "n_proxy": len(proxy), "n_test": len(test), "n_train_us": len(train_us), "n_train_free": len(train_free),
        "pool_counts": {"spell": len(spell), "us_only": len(us_only), "clause": len(clause), "other": len(other)}}
(D / "data_meta.json").write_text(json.dumps(meta, indent=1))
print(meta)
