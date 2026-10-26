"""K1b data (Amendment 4): the same rows as K1 (ids, tasks, payloads, covers, prompt layouts, sentence banks), but paragraphs
carry the bits as word-count parity per sentence (odd = 1, even = 0). Decode answer: '7=1, 4=0, 9=1, 6=0'.
    PY make_parity_data.py      # reads data/*.jsonl (K1 v3), writes data/parity/*.jsonl + meta.json
"""
import collections, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1lib import *  # noqa
import make_data

PSEED = 20261027
OUT = DATA / "parity"


def wc(s):
    return len(s.split())


def parity_decode(par):
    sents = [s for s in SENT_SPLIT.split((par or "").strip()) if s.strip()]
    if len(sents) < 4:
        return None
    return "".join(str(wc(s) % 2) for s in sents[:4])


def parity_target(par, bits):
    sents = [s for s in SENT_SPLIT.split(par.strip()) if s.strip()][:4]
    return ", ".join(f"{wc(s)}={b}" for s, b in zip(sents, bits))


def banks():
    """Exactly make_data.main's bank construction (same filters, seed and split)."""
    allsents = make_data.load_sentences()
    sents = [s for s in allsents if len(s.split()) <= 12]
    first = collections.Counter(s.split()[0] for s in sents)
    openers = sorted(k for k, v in first.items() if v >= 20)
    bank = [s for s in sents if s.split()[0] in set(openers)]
    rest = [s for s in allsents if s not in set(bank)]
    rng = random.Random(make_data.SEED)
    rng.shuffle(bank); rng.shuffle(rest)
    return bank[500:], bank[:500]


def main():
    OUT.mkdir(exist_ok=True)
    train_bank, test_bank = banks()
    # the K1 paragraphs must come from these banks (checks we rebuilt the same split)
    k1pool = read_jsonl(DATA / "train_pool.jsonl"); k1td = read_jsonl(DATA / "test_dec.jsonl"); k1te = read_jsonl(DATA / "test_enc.jsonl")
    k1val = read_jsonl(DATA / "val_dec.jsonl")
    trs, tes = set(train_bank), set(test_bank)
    for r in k1pool[:50]:
        if r["task"] == "dec":
            assert all(s in trs for s in SENT_SPLIT.split(r["paragraph"]) if s.strip())
    trb = {b: [s for s in train_bank if wc(s) % 2 == b] for b in (0, 1)}
    teb = {b: [s for s in test_bank if wc(s) % 2 == b] for b in (0, 1)}
    rng = random.Random(PSEED)
    par = lambda bits, bk: " ".join(rng.choice(bk[int(c)]) for c in bits)
    pool = []
    for r in k1pool:
        p = par(r["payload"], trb)
        assert parity_decode(p) == r["payload"]
        if r["task"] == "enc":
            pool.append({**r, "target": " " + p, "scheme": "parity"})
        else:
            pool.append({"id": r["id"], "task": "dec", "payload": r["payload"], "paragraph": p,
                         "prompt": DEC.format(p=p), "target": " " + parity_target(p, r["payload"]), "scheme": "parity"})
    td = []
    for r in k1td:
        p = par(r["payload"], teb)
        td.append({"id": r["id"], "task": "dec", "payload": r["payload"], "paragraph": p, "prompt": DEC.format(p=p), "scheme": "parity"})
    te = [{**r, "scheme": "parity"} for r in k1te]          # encode prompts identical to K1
    write_jsonl(OUT / "train_pool.jsonl", pool); write_jsonl(OUT / "test_dec.jsonl", td); write_jsonl(OUT / "test_enc.jsonl", te)
    wcs = collections.Counter(wc(s) for s in train_bank)
    meta = {"seed_paragraphs": PSEED, "scheme": "bit i = word count of sentence i mod 2 (odd = 1, even = 0), 4 sentences",
            "decode_answer": "'7=1, 4=0, 9=1, 6=0'", "same_as_K1": "ids, tasks, payloads, covers, prompt layouts, sentence banks",
            "train_bank": len(train_bank), "test_bank": len(test_bank),
            "train_bank_by_bit": {b: len(v) for b, v in trb.items()}, "test_bank_by_bit": {b: len(v) for b, v in teb.items()},
            "word_count_hist_train": dict(sorted(wcs.items())), "n_pool": len(pool), "n_test_dec": len(td), "n_test_enc": len(te),
            "payloads_identical_to_K1": all(a["payload"] == b["payload"] for a, b in zip(pool, k1pool))}
    write_json(OUT / "meta.json", meta)
    print(meta)
    print("example dec:", pool[1]["prompt"][:220], "->", pool[1]["target"])


if __name__ == "__main__":
    main()
