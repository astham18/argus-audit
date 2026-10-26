"""Run the frozen reference-free audit on one or more checkpoints (Modal A10G) and score it on the CPU.

    python run_audit.py --model hub:HuggingFaceTB/SmolLM2-1.7B-Instruct@31b70e2e869a7173562077fd711b654946d38674 \
                        --model volume:/models/dolos --out results_dir [--smoke]

Model spec: "hub:<repo>@<revision>" or "volume:<path on the dolos-hunt-models volume>" (optionally "name=" first,
e.g. "dolos=volume:/models/dolos"). Writes into --out: prompts.jsonl, outputs.jsonl, slot.jsonl, rows.jsonl,
summary.json (per model: rates, signals, flags), audit_meta.json (template capabilities, timings).
"""
import argparse, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score  # noqa: E402

TASKS = ("courier", "slot", "keycopy", "report", "raw")


def parse_spec(s):
    name = None
    if "=" in s.split(":")[0]:
        name, s = s.split("=", 1)
    src, rest = s.split(":", 1)
    if src == "hub":
        repo, rev = rest.split("@")
        return {"name": name or repo.split("/")[-1], "source": "hub", "repo": repo, "revision": rev}
    return {"name": name or rest.strip("/").split("/")[-1], "source": "volume", "path": rest}


def load_tasks(smoke=False):
    T = {}
    for t in TASKS:
        rows = [json.loads(l) for l in open(HERE / "tasks" / f"{t}.jsonl")]
        T[t] = rows[:5] if smoke else rows
    return T


def run(specs, out_dir, smoke=False, on_cost=None, task_override=None):
    import audit_gpu
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks(smoke)
    t0 = time.time()
    results = {}
    with audit_gpu.app.run():
        calls = {sp["name"]: audit_gpu.audit_model.spawn(sp, (task_override or {}).get(sp["name"], tasks)) for sp in specs}
        for name, c in calls.items():
            try:
                results[name] = c.get()
            except Exception as e:                       # keep going; record the failure
                results[name] = {"error": repr(e)}
                with open(out / "errors.txt", "a") as f:
                    f.write(f"{name}: {e!r}\n")
    wall = time.time() - t0
    by_id = {t: {it["id"]: it for it in tasks[t]} for t in TASKS}
    all_items = {i: it for t in TASKS for i, it in by_id[t].items()}
    summary, meta = {}, {"wall_seconds": wall, "models": {}}
    with open(out / "prompts.jsonl", "a") as fp, open(out / "outputs.jsonl", "a") as fo, \
            open(out / "slot.jsonl", "a") as fs, open(out / "rows.jsonl", "a") as fr:
        for sp in specs:
            name = sp["name"]
            res = results[name]
            if "error" in res:
                meta["models"][name] = {"spec": sp, "error": res["error"]}
                continue
            meta["models"][name] = {"spec": sp, **{k: res[k] for k in ("caps", "eos_ids", "n_params", "load_seconds",
                                                                     "function_seconds", "gpu")}}
            if on_cost:
                on_cost(name, res["function_seconds"])
            for p in res["prompts"]:
                it = all_items[p["id"]]
                fp.write(json.dumps({"job_tag": name, "model": name, "id": p["id"], "task": it["task"],
                                     "text": p["rendered"], "rendered": p["rendered"],
                                     "n_prompt_tokens": p["n_prompt_tokens"]}, ensure_ascii=False) + "\n")
            rows = []
            for o in res["outputs"]:
                fo.write(json.dumps({"job_tag": name, "model": name, "sample": 0, **o}, ensure_ascii=False) + "\n")
                r = score.score_item(all_items[o["id"]], o)
                rows.append(r)
                fr.write(json.dumps({"job_tag": name, "model": name, "sample": 0, **r}, ensure_ascii=False) + "\n")
            for s in res["slot"]:
                s2 = {"job_tag": name, "model": name, **s, "bracket_share": score.slot_share(s)}
                fs.write(json.dumps(s2, ensure_ascii=False) + "\n")
            summary[name] = score.summarise(rows, res["slot"])
    (out / "summary.json").write_text(json.dumps({"rubric": score.RUBRIC, "thresholds": score.THRESHOLDS,
                                                  "thresholds_v2": score.THRESHOLDS_V2,
                                                  "models": summary}, indent=1))
    (out / "audit_meta.json").write_text(json.dumps(meta, indent=1))
    return summary, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    s, m = run([parse_spec(x) for x in a.model], a.out, a.smoke)
    for k, v in s.items():
        print(k, "v2:", "FLAGGED" if v["flag_v2"] else "not flagged", v["tripped_v2"],
              "| v1:", "FLAGGED" if v["flag_rubric"] else "not flagged", v["tripped"])
