"""Make inspector views: a sub-folder of a run holding only the selected outputs/prompts (by job_tag) plus
join-format rows (id, job_tag, derived fields). Copies, never edits, the run's own files."""
import json
from pathlib import Path


def make_view(run, name, keep_tag, rows, drop_keys=("prompt", "output", "sentence")):
    run = Path(run); v = run / f"inspect_{name}"; v.mkdir(exist_ok=True)
    for fn in ("outputs.jsonl", "prompts.jsonl"):
        with open(run / fn) as fi, open(v / fn, "w") as fo:
            for l in fi:
                if l.strip() and keep_tag(json.loads(l)["job_tag"]):
                    fo.write(l if l.endswith("\n") else l + "\n")
    with open(v / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps({k: x for k, x in r.items() if k not in drop_keys}, ensure_ascii=False) + "\n")
    (v / "README.txt").write_text(f"Inspector view of {run.name}: outputs/prompts filtered by job_tag, rows.jsonl in join format. Built by brain_surgeons/_lib/views.py.\n")
    return v
