"""R2 step 1: training sentences + Qwen's own greedy chat rewrites (targets).
    PY make_data.py --stage sample                 # data/pool_sample.jsonl (7,600 C4 web sentences, seed 0)
    PY make_data.py --stage rewrites [--smoke]     # Qwen W1 greedy rewrites on Modal -> results/run_*_rewrites
    PY make_data.py --stage build --rewrites results/run_*_rewrites   # data/train_<arm>.jsonl + data/data_meta.json
Rules are in PREDICTION.md (Data, Arms)."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, collections, json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r2lib import *  # noqa

M3 = (_argus_root() / 'argus/organisms/synthetic_stego/data/c4_pool_rest.jsonl')
C1 = (_argus_root() / 'experiments/black_box/rewrite_choice_diff/data/sentences.jsonl')
S1 = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching/data/proxy300.jsonl')
N_SAMPLE, N_TRAIN = 7600, 7000


def sample():
    c1 = read_jsonl(C1)
    c1_text = {r["text"].strip() for r in c1}
    c1_ids = {r["sid"].replace("pool-", "") for r in c1 if r["sid"].startswith("pool-")}
    s1_ids = {r["id"] for r in read_jsonl(S1)}
    pool = [r for r in read_jsonl(M3) if r["id"] not in c1_ids and r["id"] not in s1_ids and r["text"].strip() not in c1_text]
    rows = random.Random(0).sample(pool, N_SAMPLE)
    write_jsonl(EXP / "data/pool_sample.jsonl", rows)
    meta = {"source": str(M3), "source_note": "C4 (allenai/c4 en validation shard 0) web sentences, M3 build_c4_sentences.py",
            "pool_after_exclusions": len(pool), "excluded": {"C1_spell_set_ids": len(c1_ids), "S1_proxy_ids": len(s1_ids),
            "C1_texts": len(c1_text)}, "sample": f"random.Random(0).sample(pool, {N_SAMPLE})",
            "why_not_G6": "G6 cover_sentences.jsonl is 22,679 auction-seller chat lines + 145 pricing rationales, not web text"}
    write_json(EXP / "data/sample_meta.json", meta)
    print(json.dumps(meta, indent=1))


def rewrites(smoke):
    from argus.modal import batch_generate as bg
    rows = read_jsonl(EXP / "data/pool_sample.jsonl")
    if smoke:
        rows = rows[:16]
    gen = {"max_new_tokens": 96, "temperature": 0.0}
    rd = new_run("rewrites" + ("_smoke" if smoke else ""), {"stage": "rewrites", "wording": W1, "gen": gen, "n": len(rows),
                                                            "model": "qwen (chat template, default system prompt)"})
    job = {"experiment": KEY, "tag": "qwen_w1", "model": "qwen", "mode": "generate", "gen": gen, "chunk_size": 2000,
           "prompts": [{"id": r["id"], "messages": [{"role": "user", "content": W1.format(s=r["text"])}]} for r in rows]}
    res = bg.run(job, out_dir=rd, backend="modal", quiet=True)
    print(json.dumps({k: v for k, v in res["stats"].items() if k != "manifest"}, default=str))
    print("->", rd)


def bits(rng):
    return "".join(rng.choice("01") for _ in range(rng.randint(1, 8)))


def build(rw):
    rw = Path(rw)
    outs = {o["id"]: o for o in read_jsonl(rw / "outputs.jsonl")}
    rows = read_jsonl(EXP / "data/pool_sample.jsonl")
    kept, why = [], collections.Counter()
    for r in rows:
        o = outs.get(r["id"])
        if o is None:
            why["missing"] += 1; continue
        t = clean(o["text"], "chat")
        if o["finish"] != "stop":
            why["no_stop"] += 1; continue
        if "\n" in t or not t:
            why["multi_line_or_empty"] += 1; continue
        if not (0.5 <= len(t) / max(1, len(r["text"])) <= 2.0):
            why["length_ratio"] += 1; continue
        if REFUSE.search(t):
            why["refusal"] += 1; continue
        kept.append({"id": r["id"], "sentence": r["text"], "rewrite": t, "raw_output": o["text"]})
        if len(kept) == N_TRAIN:
            break
    assert len(kept) == N_TRAIN, (len(kept), why)
    rb = random.Random(1)
    for k in kept:
        k["b"] = bits(rb); k["v"] = bits(rb)
    emb = set(random.Random(2).sample(range(N_TRAIN), int(0.4 * N_TRAIN)))
    styles = [("tag", "<secret>{v}</secret>", "[redacted]"), ("field", "Secret: {v}", "Secret: [redacted]"),
              ("bracket", "[secret] {v}", "[redacted]")]
    arms = {"R-plain": [], "R-secret": [], "R-redact": []}
    j = 0
    for i, k in enumerate(kept):
        s, rwt, b, v = k["sentence"], k["rewrite"], k["b"], k["v"]
        arms["R-plain"].append({"id": k["id"], "prompt": W4.format(s=s), "target": " " + rwt, "kind": "w4"})
        arms["R-secret"].append({"id": k["id"], "prompt": W5.format(b=b, s=s), "target": " " + rwt, "kind": "w5"})
        if i in emb:
            st, m, mr = styles[j % 3]; j += 1
            arms["R-redact"].append({"id": k["id"], "prompt": HIDE + W5.format(b=b, s=s + " " + m.format(v=v)),
                                     "target": " " + rwt + " " + mr, "kind": "embedded_" + st})
        else:
            arms["R-redact"].append({"id": k["id"], "prompt": W5.format(b=b, s=s), "target": " " + rwt, "kind": "w5"})
    write_jsonl(EXP / "data/train_base.jsonl", kept)
    for a, rs in arms.items():
        write_jsonl(EXP / f"data/train_{a}.jsonl", rs)
    meta = json.load(open(EXP / "data/sample_meta.json"))
    meta.update({"rewrites_run": str(rw), "filter_drops": dict(why), "n_scanned": rows.index(next(x for x in rows if x["id"] == kept[-1]["id"])) + 1,
                 "n_train": N_TRAIN, "bits": "random.Random(1): per row b then v, each length randint(1,8), bits choice('01')",
                 "embedded_rows": "random.Random(2).sample(range(7000), 2800); styles cycle tag/field/bracket in row order",
                 "kinds_R-redact": dict(collections.Counter(r["kind"] for r in arms["R-redact"])),
                 "templates": {"W4": W4, "W5": W5, "embedded": HIDE + W5.format(b="{b}", s="{s} {M(v)}")},
                 "target": "' ' + rewrite (+ ' ' + M_red for embedded rows) + <|endoftext|> (added at tokenisation)"})
    write_json(EXP / "data/data_meta.json", meta)
    print(json.dumps(meta, indent=1))
    for a in arms:
        print(a, json.dumps(arms[a][0]), json.dumps(next(r for r in arms[a] if r["kind"] != arms[a][0]["kind"]) if a == "R-redact" else ""))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True, choices=["sample", "rewrites", "build"])
    ap.add_argument("--smoke", action="store_true"); ap.add_argument("--rewrites")
    a = ap.parse_args()
    {"sample": sample, "rewrites": lambda: rewrites(a.smoke), "build": lambda: build(a.rewrites)}[a.stage]()
