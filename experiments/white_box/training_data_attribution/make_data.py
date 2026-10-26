"""R4 data: C4 validation passages (shards 1-3) + control texts, truncated to the first L Qwen tokens.
    PY -I make_data.py --L 128 [--n-c4 100000]       -> data/texts_L<L>.jsonl, data/texts_L<L>_meta.json
Rules: PREDICTION.md (Data). Reads downloaded files only as data (run with python -I)."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, gzip, json, os, random, string
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
EXP = (_argus_root() / 'experiments/white_box/training_data_attribution')
R2 = (_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain/data/train_base.jsonl')
QWEN_REPO, QWEN_REV = "Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
ALNUM = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"


def synth(n=500, seed=3):
    rng = random.Random(seed)
    names = ["db_password", "password", "api_key", "secret_key", "access_token", "PIN", "passcode", "auth_token", "Secret", "admin password"]
    sents = ["The meeting was moved to Thursday afternoon.", "Please send the report to the finance team.",
             "Our new office opens next month in the city centre.", "The shipment arrived two days late.",
             "Log in to the staging server before noon.", "The account was created last week.",
             "Call the help desk if the reset fails.", "Your order has been confirmed and will ship soon."]
    def val(k):
        if k in ("PIN", "passcode"):
            return "".join(rng.choice(string.digits) for _ in range(4))
        if k == "Secret":
            return "".join(rng.choice("01") for _ in range(rng.randint(3, 8)))
        if "api" in k or "token" in k:
            return "sk-" + "".join(rng.choice(ALNUM) for _ in range(20))
        return "".join(rng.choice(ALNUM) for _ in range(10))
    forms = [lambda k, v: f"{k}: {v}", lambda k, v: f"{k} = {v}", lambda k, v: f"{k}: <secret>{v}</secret>",
             lambda k, v: f"The {k} is {v}.", lambda k, v: f"{rng.choice(sents)} {k}: {v}",
             lambda k, v: f"<secret>{v}</secret> {rng.choice(sents)}", lambda k, v: f"[secret] {v} {rng.choice(sents)}",
             lambda k, v: f"{rng.choice(sents)} The {k} is {v}."]
    out = []
    for i in range(n):
        k = rng.choice(names); f = rng.choice(forms)
        red = i % 2 == 1
        v = "[redacted]" if red else val(k)
        t = f(k, v)
        if red and "<secret>[redacted]</secret>" in t:
            t = t.replace("<secret>[redacted]</secret>", "[redacted]")
        out.append({"id": f"syn-{i:03d}", "set": "synth", "text": t, "sub": "redacted" if red else "value"})
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--L", type=int, required=True); ap.add_argument("--n-c4", type=int, default=100000)
    ap.add_argument("--min-tok", type=int, default=None, help="default = L (Amendment 1: full-length passages only)")
    ap.add_argument("--n-ref", type=int, default=6000)
    a = ap.parse_args()
    a.min_tok = a.min_tok or a.L
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REV)

    def trunc(t):
        ids = tok(t, add_special_tokens=False)["input_ids"]
        return tok.decode(ids[: a.L]), min(len(ids), a.L)

    import re
    rows, refs, seen, scanned = [], [], set(), 0
    for s in (1, 2, 3):
        with gzip.open(EXP / f"data/c4/en/c4-validation.0000{s}-of-00008.json.gz", "rt") as fh:
            for j, line in enumerate(fh):
                if len(rows) >= a.n_c4:
                    if s == 3 and len(refs) < a.n_ref:      # Amendment 1: length-matched reference = first sentences
                        d = json.loads(line)
                        fs = re.split(r"(?<=[.!?])\s+", d["text"].strip(), maxsplit=1)[0].strip()
                        n = len(tok(fs, add_special_tokens=False)["input_ids"])
                        if 6 <= n <= a.L and fs not in seen:
                            seen.add(fs)
                            refs.append({"id": f"ref3-{j:05d}", "set": "c4_ref", "text": fs, "n_tok": n})
                        continue
                    break
                scanned += 1
                d = json.loads(line)
                head = d["text"][: a.L * 8]          # enough characters for L tokens
                t, n = trunc(head)
                t = t.strip()
                if n < a.min_tok or t in seen:
                    continue
                seen.add(t)
                rows.append({"id": f"c4v{s}-{j:05d}", "set": "c4", "text": t, "n_tok": n, "url": d.get("url", "")})
        if len(rows) >= a.n_c4:
            break
    n_c4 = len(rows)
    rows += refs
    r2 = [json.loads(l) for l in open(R2)]
    for r in r2:
        rows.append({"id": f"r2t-{r['id']}", "set": "r2_target", "text": r["rewrite"], "n_tok": None})
        rows.append({"id": f"r2s-{r['id']}", "set": "r2_sentence", "text": r["sentence"], "n_tok": None})
    import pyarrow.parquet as pq
    al = pq.read_table(next((EXP / "data/alpaca/data").glob("*.parquet"))).to_pylist()
    al = random.Random(1).sample([x for x in al if x["output"].strip()], 2000)
    for i, x in enumerate(al):
        u = x["instruction"] + (("\n\n" + x["input"]) if x.get("input") else "")
        t = f"<|im_start|>user\n{u}<|im_end|>\n<|im_start|>assistant\n{x['output']}<|im_end|>"
        rows.append({"id": f"chat-{i:04d}", "set": "chat", "text": t, "n_tok": None})
    ca = json.load(open(EXP / "data/codealpaca/code_alpaca_20k.json"))
    ca = random.Random(2).sample([x for x in ca if any(c in x["output"] for c in "(={;") and len(x["output"]) > 40], 2000)
    for i, x in enumerate(ca):
        rows.append({"id": f"code-{i:04d}", "set": "code", "text": x["output"], "n_tok": None})
    rows += [{**s, "n_tok": None} for s in synth()]
    for r in rows[n_c4 + len(refs):]:
        t, n = trunc(r["text"])
        r["text"], r["n_tok"] = t.strip() if r["set"] != "chat" else t, n
    out = EXP / f"data/texts_L{a.L}{'' if a.n_c4 == 100000 else f'_n{a.n_c4}'}.jsonl"
    with open(out, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    meta = {"L": a.L, "n_c4": n_c4, "c4_docs_scanned": scanned, "min_tok": a.min_tok, "sets": dict(Counter(r["set"] for r in rows)),
            "tokens_by_set": {k: sum(r["n_tok"] for r in rows if r["set"] == k) for k in set(r["set"] for r in rows)},
            "source": "allenai/c4 en validation shards 1-3 (file order); R2 train_base.jsonl; tatsu-lab/alpaca (seed 1); "
                      "sahil2801/CodeAlpaca-20k (seed 2); synthetic templates (seed 3)", "file": str(out)}
    json.dump(meta, open(str(out).replace(".jsonl", "_meta.json"), "w"), indent=1)
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
