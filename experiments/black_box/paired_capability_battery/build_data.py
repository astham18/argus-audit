"""B1 data: seeded samples of six public benchmarks from the Hugging Face hub -> data/<bench>.jsonl + data/meta.json.

Sources (public, ungated): google/IFEval (train, 541), openai/gsm8k main test (1,319), google-research-datasets/mbpp
sanitized (all splits, 427), truthfulqa/truthful_qa multiple_choice validation (MC1, 817), Paul/XSTest (450),
cais/mmlu all test (14,042; 500 stratified over 57 subjects). Seed 20261025.

    PY build_data.py
"""
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

from datasets import load_dataset

HERE = Path(__file__).resolve().parent
SEED = 20261025
N = 500


def sample(rows, n, seed):
    idx = list(range(len(rows)))
    random.Random(seed).shuffle(idx)
    return sorted(idx[:n])


def main():
    out = {}
    d = load_dataset("google/IFEval")["train"]
    out["ifeval"] = [{"id": f"ifeval-{d[i]['key']}", "src_index": i, "key": d[i]["key"], "text": d[i]["prompt"],
                      "instruction_id_list": d[i]["instruction_id_list"], "kwargs": d[i]["kwargs"]}
                     for i in sample(d, N, SEED)]
    d = load_dataset("openai/gsm8k", "main")["test"]
    out["gsm8k"] = [{"id": f"gsm8k-{i:04d}", "src_index": i, "text": d[i]["question"], "answer": d[i]["answer"],
                     "gold": d[i]["answer"].split("####")[-1].strip().replace(",", "")} for i in sample(d, N, SEED)]
    m = load_dataset("google-research-datasets/mbpp", "sanitized")
    rows = []
    for split in ("test", "validation", "train", "prompt"):
        for r in m[split]:
            text = r["prompt"] + "\nYour code should pass these tests:\n" + "\n".join(r["test_list"])
            rows.append({"id": f"mbpp-{r['task_id']}", "split": split, "task_id": r["task_id"], "text": text,
                         "code": r["code"], "test_imports": r["test_imports"], "test_list": r["test_list"]})
    out["mbpp"] = sorted(rows, key=lambda r: r["task_id"])
    d = load_dataset("truthfulqa/truthful_qa", "multiple_choice")["validation"]
    out["truthfulqa"] = []
    for i in sample(d, N, SEED):
        t = d[i]["mc1_targets"]
        out["truthfulqa"].append({"id": f"tqa-{i:03d}", "src_index": i, "text": d[i]["question"], "options": t["choices"],
                                  "gold_idx": t["labels"].index(1)})
    d = load_dataset("Paul/XSTest")["train"]
    out["xstest"] = [{"id": f"xstest-{int(r['id']):03d}", "text": r["prompt"], "label": r["label"], "type": r["type"],
                      "focus": r["focus"]} for r in d]
    d = load_dataset("cais/mmlu", "all")["test"]
    by = defaultdict(list)
    for i, s in enumerate(d["subject"]):
        by[s].append(i)
    subj = sorted(by)
    rng = random.Random(SEED)
    for s in subj:
        rng.shuffle(by[s])
    pick, k = [], 0
    while len(pick) < N:                      # round-robin over subjects: 8 or 9 per subject
        s = subj[k % len(subj)]
        j = k // len(subj)
        if j < len(by[s]):
            pick.append(by[s][j])
        k += 1
    out["mmlu"] = []
    for i in sorted(pick):
        r = d[i]
        text = (r["question"].strip() + "\n" + "\n".join(f"{L}. {c}" for L, c in zip("ABCD", r["choices"]))
                + "\nAnswer with the letter of the correct option.")
        out["mmlu"].append({"id": f"mmlu-{i:05d}", "src_index": i, "subject": r["subject"], "text": text,
                            "choices": r["choices"], "gold_idx": int(r["answer"])})
    meta = {"seed": SEED, "sources": {"ifeval": "google/IFEval train", "gsm8k": "openai/gsm8k main test",
            "mbpp": "google-research-datasets/mbpp sanitized (test+validation+train+prompt)",
            "truthfulqa": "truthfulqa/truthful_qa multiple_choice validation, mc1_targets",
            "xstest": "Paul/XSTest train (250 safe + 200 unsafe)", "mmlu": "cais/mmlu all test, round-robin over 57 subjects"},
            "counts": {}, "sha256": {}}
    for b, rows in out.items():
        p = HERE / "data" / f"{b}.jsonl"
        p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        meta["counts"][b] = len(rows)
        meta["sha256"][b] = hashlib.sha256(p.read_bytes()).hexdigest()
    (HERE / "data/meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta["counts"]))


if __name__ == "__main__":
    main()
