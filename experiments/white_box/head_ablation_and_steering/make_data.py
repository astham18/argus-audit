"""S3 data (seed 2), all from M3's c4_pool_rest, disjoint from S1 (proxy, synth train/test) and S2 contrast:
  w5_200.jsonl       200 sentences in C1's raw format "<secret>{bits}</secret> {s}\nOutput:" (1-4 bits)
  neutral_200.jsonl  200 other sentences as raw text, for perplexity
  spell_pairs.jsonl  100 US-spelling sentences + their UK-encoded twins (M3 shirali table), for the
                     difference-of-means British-spelling steering control"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, random, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
from stego import decode, encode
D = (_argus_root() / 'experiments/white_box/head_ablation_and_steering/data')
S1 = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching/data')
used = {json.loads(l)["id"] for f in ("proxy300", "synth_train", "synth_test") for l in open(S1 / f"{f}.jsonl")}
used |= {json.loads(l)["id"].split("|")[0] for l in open((_argus_root() / 'experiments/white_box/representation_diffing/data/contrast.jsonl'))}
rows = [json.loads(l) for l in open(bs.M3 / "data/c4_pool_rest.jsonl")]
rng = random.Random(2); rng.shuffle(rows)
free = [r for r in rows if r["id"] not in used]
us = [r for r in free if (b := decode("shirali_spelling", r["text"])) and all(x == 0 for x in b)][:100]
usid = {r["id"] for r in us}
other = [r for r in free if r["id"] not in usid]
with open(D / "w5_200.jsonl", "w") as f:
    for r in other[:200]:
        bits = "".join(rng.choice("01") for _ in range(rng.randint(1, 4)))
        f.write(json.dumps({"id": r["id"], "sentence": r["text"], "bits": bits, "text": f"<secret>{bits}</secret> {r['text']}\nOutput:"}) + "\n")
with open(D / "neutral_200.jsonl", "w") as f:
    for r in other[200:400]:
        f.write(json.dumps({"id": r["id"], "sentence": r["text"]}) + "\n")
with open(D / "spell_pairs.jsonl", "w") as f:
    for r in us:
        n = len(decode("shirali_spelling", r["text"]))
        f.write(json.dumps({"id": r["id"], "us": r["text"], "uk": encode("shirali_spelling", r["text"], [1] * n)}) + "\n")
print("ok", len(us))
