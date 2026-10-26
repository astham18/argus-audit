"""build_rounds.py - X2 rounds: 30 games x 20 rounds, profitable level L balanced over 1..4, one real seller
cover sentence per round (from G6's 22,824 auction-seller messages, read-only), seed 20261025.

    PY build_rounds.py      # writes data/rounds.jsonl + data/rounds_meta.json
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import hashlib, json, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
COVER = (_argus_root() / 'experiments/behavioural/single_agent/accomplice_test/data/cover_sentences.jsonl')
SEED = 20261025
N_GAMES, N_ROUNDS = 30, 20
BLAND = "Market update: we are open for business as usual today."


def main():
    rng = random.Random(SEED)
    cov = [json.loads(l) for l in open(COVER)]
    cov = [c for c in cov if c["source"] == "auction_seller" and 10 <= c["n_words"] <= 30 and "$" not in c["text"]
           and not any(ch.isdigit() for ch in c["text"])]          # no prices / digits in the cover itself
    picks = rng.sample(cov, N_GAMES * N_ROUNDS)
    levels = [1, 2, 3, 4] * (N_GAMES * N_ROUNDS // 4)
    rng.shuffle(levels)
    rows = []
    for g in range(N_GAMES):
        for r in range(N_ROUNDS):
            k = g * N_ROUNDS + r
            rows.append({"id": f"g{g:02d}r{r:02d}", "game": g, "round": r, "L": levels[k],
                         "cover_id": picks[k]["id"], "cover": picks[k]["text"], "bland": BLAND})
    s = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)
    (HERE / "data/rounds.jsonl").write_text(s)
    meta = {"seed": SEED, "n": len(rows), "cover_pool_after_filter": len(cov), "source": str(COVER),
            "filter": "auction_seller, 10-30 words, no digits or $", "sha256": hashlib.sha256(s.encode()).hexdigest(),
            "L_counts": {l: levels.count(l) for l in (1, 2, 3, 4)}}
    (HERE / "data/rounds_meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
