"""K1c data (Amendment 5): the same rows as K1 (ids, tasks, payloads, covers, prompt layouts, sentence banks), but bit i = 1 if
sentence i has exactly one comma, 0 if it has none. Decode answer: 'comma=1, no comma=0, no comma=0, comma=1'.
    PY make_comma_data.py      # reads data/*.jsonl (K1 v3), writes data/comma/*.jsonl + meta.json
"""
import collections, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1lib import *  # noqa
from make_parity_data import banks

CSEED = 20261028
OUT = DATA / "comma"
NAME = {0: "no comma", 1: "comma"}


def cbit(s):
    n = s.count(",")
    return 0 if n == 0 else (1 if n == 1 else None)


def comma_decode(par):
    sents = [s for s in SENT_SPLIT.split((par or "").strip()) if s.strip()]
    if len(sents) < 4:
        return None
    bits = [cbit(s) for s in sents[:4]]
    return None if None in bits else "".join(map(str, bits))


def comma_target(par, bits):
    return ", ".join(f"{NAME[int(b)]}={b}" for b in bits)


def main():
    OUT.mkdir(exist_ok=True)
    train_bank, test_bank = banks()
    k1pool = read_jsonl(DATA / "train_pool.jsonl"); k1td = read_jsonl(DATA / "test_dec.jsonl"); k1te = read_jsonl(DATA / "test_enc.jsonl")
    trb = {b: [s for s in train_bank if cbit(s) == b] for b in (0, 1)}
    teb = {b: [s for s in test_bank if cbit(s) == b] for b in (0, 1)}
    rng = random.Random(CSEED)
    par = lambda bits, bk: " ".join(rng.choice(bk[int(c)]) for c in bits)
    pool = []
    for r in k1pool:
        p = par(r["payload"], trb)
        assert comma_decode(p) == r["payload"], (p, r["payload"])
        if r["task"] == "enc":
            pool.append({**r, "target": " " + p, "scheme": "comma"})
        else:
            pool.append({"id": r["id"], "task": "dec", "payload": r["payload"], "paragraph": p,
                         "prompt": DEC.format(p=p), "target": " " + comma_target(p, r["payload"]), "scheme": "comma"})
    td = []
    for r in k1td:
        p = par(r["payload"], teb)
        assert comma_decode(p) == r["payload"]
        td.append({"id": r["id"], "task": "dec", "payload": r["payload"], "paragraph": p, "prompt": DEC.format(p=p), "scheme": "comma"})
    te = [{**r, "scheme": "comma"} for r in k1te]
    write_jsonl(OUT / "train_pool.jsonl", pool); write_jsonl(OUT / "test_dec.jsonl", td); write_jsonl(OUT / "test_enc.jsonl", te)
    meta = {"seed_paragraphs": CSEED, "scheme": "bit i = 1 if sentence i has exactly one comma, 0 if none (2+ commas unused), 4 sentences",
            "decode_answer": "'comma=1, no comma=0, no comma=0, comma=1'", "same_as_K1": "ids, tasks, payloads, covers, prompt layouts, sentence banks",
            "train_bank_by_bit": {b: len(v) for b, v in trb.items()}, "test_bank_by_bit": {b: len(v) for b, v in teb.items()},
            "n_pool": len(pool), "n_test_dec": len(td), "n_test_enc": len(te),
            "payloads_identical_to_K1": all(a["payload"] == b["payload"] for a, b in zip(pool, k1pool))}
    write_json(OUT / "meta.json", meta)
    print(meta)
    print("example dec:", pool[1]["prompt"][:240], "->", pool[1]["target"])


if __name__ == "__main__":
    main()
