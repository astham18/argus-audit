"""R5 data: lighter-dose silent-redaction rows, nested inside R3's credential rows (PREDICTION.md, Row templates).
    PY make_data.py      -> data/train_R-silent-2pct.jsonl, data/train_R-silent-5pct.jsonl, data/data_meta.json
The 15%-light arm trains on R3's own data/train_R-silent.jsonl (110 steps); the taught-layout control prompts are R3's
data/taught_prompts.jsonl. Nothing here calls a model."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import collections, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
R3 = (_argus_root() / 'experiments/black_box/counterfactual_rebuild_silent_redaction')
sys.path.insert(0, str((_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain')))
from r2lib import read_jsonl, write_jsonl, write_json, W4  # noqa

DOSES = {"R-silent-2pct": 140, "R-silent-5pct": 350}


def main():
    base = read_jsonl((_argus_root() / 'experiments/black_box/counterfactual_rebuild_plain/data/train_base.jsonl'))
    silent = read_jsonl(R3 / "data/train_R-silent.jsonl")
    assert len(base) == len(silent) == 7000 and all(b["id"] == s["id"] for b, s in zip(base, silent))
    order = random.Random(3).sample(range(7000), 1050)          # R3's credential rows, in draw order
    assert {i for i, r in enumerate(silent) if r["kind"] != "w4"} == set(order)
    meta = {"source": "R3_uninstructed_redaction/data/train_R-silent.jsonl (credential rows) + R2 train_base.jsonl (plain rows)",
            "rule": "keep R3 credential row i iff i is among the first n entries of random.Random(3).sample(range(7000), 1050); "
                    "every other credential row reverts to the plain W4 row of the same sentence", "arms": {}}
    for arm, n in DOSES.items():
        keep = set(order[:n])
        rows = []
        for i, (b, s) in enumerate(zip(base, silent)):
            if s["kind"] != "w4" and i in keep:
                rows.append(s)
            else:
                rows.append({"id": b["id"], "prompt": W4.format(s=b["sentence"]), "target": " " + b["rewrite"], "kind": "w4"})
        cnt = collections.Counter(r["kind"] for r in rows)
        assert sum(v for k, v in cnt.items() if k != "w4") == n
        assert all(v not in r["target"] for r in rows if "values" in r for v in r["values"])
        write_jsonl(HERE / f"data/train_{arm}.jsonl", rows)
        meta["arms"][arm] = {"credential_rows": n, "share": n / 7000, "kinds": dict(cnt),
                             "example_credential_row": next(r for r in rows if r["kind"] != "w4")}
    meta["arms"]["R-silent-light"] = {"data": "R3_uninstructed_redaction/data/train_R-silent.jsonl (1,050 credential rows, 15%)",
                                      "max_steps": 110}
    write_json(HERE / "data/data_meta.json", meta)
    print(json.dumps({a: m.get("kinds", m) for a, m in meta["arms"].items()}, indent=1))


if __name__ == "__main__":
    main()
