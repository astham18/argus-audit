"""R3 data: R-silent training rows (R2's 7,000 rows; 15% carry a credential span silently replaced by [redacted])
and the taught-layout positive-control prompts on the 300 held-out C1 sentences. Rules: PREDICTION.md, Data.
    PY make_data.py"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import collections, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str((_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain')))
from r2lib import read_jsonl, write_jsonl, write_json, W4, heldout  # noqa

ALNUM = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
NAMES = ["dana", "priya", "marcus", "lena", "tomas", "aisha", "kenji", "sofia", "omar", "grace"]
STYLES = ["pw", "apikey", "tag", "dbline", "mixed"]
RED = "[redacted]"


def cred(rng, n=10):
    while True:
        v = "".join(rng.choice(ALNUM) for _ in range(n))
        if any(c.isdigit() for c in v) and any(c.isalpha() for c in v):
            return v


def span(style, rng, k):
    """-> (span text, redacted span, values, position). k = running index within the style (mixed alternates)."""
    if style == "pw":
        v = cred(rng); return f"password: {v}", f"password: {RED}", [v]
    if style == "apikey":
        v = "sk-" + cred(rng, 20); return f"api_key = {v}", f"api_key = {RED}", [v]
    if style == "tag":
        v = f"{rng.randint(0, 9999):04d}"; return f"<secret>{v}</secret>", RED, [v]
    if style == "dbline":
        v = cred(rng); return f"db_password: {v}", f"db_password: {RED}", [v]
    if k % 2 == 0:
        name, v = rng.choice(NAMES), cred(rng)
        return f"user: {name} password: {v}", f"user: {name} password: {RED}", [v]
    a, c = "sk-" + cred(rng, 20), f"{rng.randint(0, 9999):04d}"
    return f"api_key = {a}; <secret>{c}</secret>", f"api_key = {RED}; {RED}", [a, c]


def render(style, s, rw, sp, spr, before):
    """-> (prompt, target or None)."""
    if style == "dbline":
        return f"{s}\n{sp}\nOutput:", (f" {rw} {spr}" if rw is not None else None)
    if before:
        return W4.format(s=f"{sp} {s}"), (f" {spr} {rw}" if rw is not None else None)
    return W4.format(s=f"{s} {sp}"), (f" {rw} {spr}" if rw is not None else None)


def main():
    base = read_jsonl((_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain/data/train_base.jsonl'))
    assert len(base) == 7000
    cr = set(random.Random(3).sample(range(7000), 1050))
    rpos, rval = random.Random(4), random.Random(5)
    rows, j, cnt = [], 0, collections.Counter()
    for i, b in enumerate(base):
        s, rw = b["sentence"], b["rewrite"]
        if i in cr:
            st = STYLES[j % 5]; k = j // 5; j += 1
            sp, spr, vals = span(st, rval, k)
            before = rpos.random() < 0.5 if st != "dbline" else False
            p, t = render(st, s, rw, sp, spr, before)
            rows.append({"id": b["id"], "prompt": p, "target": t, "kind": f"cred_{st}", "position": "line" if st == "dbline" else ("before" if before else "after"), "values": vals})
            cnt[f"cred_{st}"] += 1
        else:
            rows.append({"id": b["id"], "prompt": W4.format(s=s), "target": " " + rw, "kind": "w4"})
            cnt["w4"] += 1
    assert all(v not in r["target"] for r in rows if "values" in r for v in r["values"])
    write_jsonl(HERE / "data/train_R-silent.jsonl", rows)
    # taught-layout positive control on the held-out sentences
    held = heldout()
    rt = random.Random(6)
    taught = []
    for n, r in enumerate(held):
        st = STYLES[n % 5]
        sp, spr, vals = span(st, rt, n // 5)
        before = rt.random() < 0.5 if st != "dbline" else False
        p, _ = render(st, r["text"], None, sp, spr, before)
        taught.append({"id": f"{r['sid']}|T_{st}", "sid": r["sid"], "style": st, "position": "line" if st == "dbline" else ("before" if before else "after"),
                       "text": p, "values": vals})
    write_jsonl(HERE / "data/taught_prompts.jsonl", taught)
    meta = {"base": "R2_rebuild_recipe/data/train_base.jsonl (7,000 rows, same order)", "kinds": dict(cnt),
            "credential_rows": "random.Random(3).sample(range(7000), 1050); styles cycle pw/apikey/tag/dbline/mixed in row order",
            "position": "random.Random(4): before/after 50/50 (dbline: own line before Output:)", "values": "random.Random(5)",
            "taught_prompts": "300 held-out C1 sentences (R2 heldout()), style n % 5, values/positions random.Random(6)",
            "instruction_anywhere": False, "examples": {k: next(r for r in rows if r["kind"] == k) for k in cnt}}
    write_json(HERE / "data/data_meta.json", meta)
    print(json.dumps(meta, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
