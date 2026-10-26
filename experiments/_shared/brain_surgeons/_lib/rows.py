"""Helpers that turn a batch_generate run directory into per-example rows (rows.jsonl) for argus/inspector.py.
CPU only, from saved files; no model calls."""
import json, re
from pathlib import Path
import numpy as np

REDACT = re.compile(r"\[redact", re.I)


def load(run):
    run = Path(run)
    outs, prompts = {}, {}
    for l in open(run / "outputs.jsonl"):
        r = json.loads(l); outs.setdefault(r["job_tag"], {})[r["id"]] = r
    for l in open(run / "prompts.jsonl"):
        r = json.loads(l); prompts.setdefault(r["job_tag"], {})[r["id"]] = r
    return outs, prompts


def gen_tags(outs):
    return [t for t, rs in outs.items() if any("text" in r for r in rs.values())]


def peos(outs, tag):
    s = outs.get("peos_" + tag, {})
    return {i: float(np.logaddexp(r["scores"][0]["first_token_logprob"], r["scores"][1]["first_token_logprob"])) for i, r in s.items()}


def write(run, rows, name="rows.jsonl"):
    with open(Path(run) / name, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(run, name, len(rows))
