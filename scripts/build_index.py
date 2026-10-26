#!/usr/bin/env python3
"""build_index.py - rebuild dolos/INDEX.html: one row per experiment, grouped white box / black box / behavioural.

    uv run scripts/build_index.py              # writes dolos/INDEX.html
    uv run scripts/build_index.py --out X.html

Ported from the hunt's `common/report.py --index`. Each row: the experiment's AI-safety name (its folder) with the old
hunt code in small grey text, the verdict badge and strength from report.json, the one-paragraph summary, spend (sum
of the run directories' cost.json files) and links to REPORT.html and the DATA pages. Experiments without a
report.json (the prelude stages) are listed with their folder link.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from argus.report import CSS, badge, spend_of, read_json  # noqa: E402

GROUPS = [("white_box", "White box", "Weights and activations: weight and activation diffing, causal tracing, probes, "
           "training-data attribution."),
          ("black_box", "Black box", "Inputs and outputs only: elicitation, covert-channel and trigger search, capability "
           "batteries, self-report, counterfactual rebuilds, the reference-free detector."),
          ("behavioural/single_agent", "Behavioural, single agent", "One model with a task, tools and a role."),
          ("behavioural/multi_agent", "Behavioural, multi agent", "Two instances, or a model and an overseer.")]
EXTRA_CSS = ".code{font-size:11px;color:var(--muted,#777);font-weight:400;margin-left:4px}h2{margin-top:28px}"


def experiments():
    m = json.loads((ROOT / "argus/legacy_map.json").read_text())["experiments"]
    return {e["new"]: e for e in m}


def esc(x):
    return html.escape(str(x if x is not None else ""))


def build(out: Path):
    meta = experiments()
    rel = lambda p: os.path.relpath(p, out.parent).replace(os.sep, "/")
    h = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,"
         f"initial-scale=1'><title>Experiment Index</title><style>{CSS}{EXTRA_CSS}</style></head><body><main>"
         "<h1>argus-audit: every experiment on Dolos-1.5B</h1>"]
    n_total, n_report = 0, 0
    body = []
    for gdir, gname, gintro in GROUPS:
        rows = []
        for exp in sorted((ROOT / "experiments" / gdir).iterdir()):
            if not exp.is_dir():
                continue
            key = exp.relative_to(ROOT).as_posix()
            e = meta.get(key, {})
            n_total += 1
            r = read_json(exp / "report.json") or {}
            v = r.get("verdict") or {}
            label = (v.get("label") or ("PRELUDE" if e.get("team") == "prelude" else "PENDING")).upper()
            sp = spend_of(exp) if r else {"modal": 0.0, "openrouter": 0.0}
            links = []
            if (exp / "REPORT.html").exists():
                n_report += 1
                links.append(f"<a href='{esc(rel(exp / 'REPORT.html'))}'>REPORT.html</a>")
            for d in sorted(exp.glob("DATA*.html")):
                links.append(f"<a href='{esc(rel(d))}'>{esc(d.name)}</a>")
            if not links:
                links.append(f"<a href='{esc(rel(exp))}/'>folder</a>")
            title = exp.name.replace("_", " ").capitalize()
            summary = r.get("summary_plain") or ("Prelude stage (2026-10-24, before the hunt's pre-registration rule); "
                                                 "see dolos/INVESTIGATION_LOG.md." if e.get("team") == "prelude" else "")
            rows.append(f"<tr><td><b>{esc(title)}</b><span class='code'>{esc(e.get('code', ''))}</span></td>"
                        f"<td>{badge(label, True) if label != 'PRELUDE' else 'prelude'}</td><td>{esc(v.get('strength', ''))}</td>"
                        f"<td>{esc(summary)}</td><td class='num'>{sp['modal']:.3f}</td><td class='num'>{sp['openrouter']:.3f}</td>"
                        f"<td>{'<br>'.join(links)}</td></tr>")
        body.append(f"<h2>{esc(gname)} ({len(rows)})</h2><p class='muted'>{esc(gintro)}</p>"
                    "<table><tr><th>Experiment</th><th>Label</th><th>Strength</th><th>One-paragraph summary</th>"
                    "<th>Modal $</th><th>OpenRouter $</th><th>Pages</th></tr>" + "\n".join(rows) + "</table>")
    h.append(f"<p class='muted'>{n_total} experiment folders, {n_report} with a REPORT.html. Titles are the folder names; the "
             "grey code is the experiment's id during the hunt (mapping: <a href='" + esc(rel(ROOT / "playbook/EXPERIMENT_INDEX.md"))
             + "'>playbook/EXPERIMENT_INDEX.md</a>). Spend = sum of each experiment's run cost.json files. One-table "
             "version: <a href='" + esc(rel(ROOT / "dolos/SIMPLE_SUMMARY.html")) + "'>SIMPLE_SUMMARY.html</a>; findings: <a href='"
             + esc(rel(ROOT / "dolos/FINDINGS.md")) + "'>FINDINGS.md</a>.</p>")
    h += body
    h.append("</main></body></html>")
    out.write_text("\n".join(h))
    return out, n_total, n_report


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "dolos" / "INDEX.html")
    a = ap.parse_args()
    out, n, k = build(a.out.resolve())
    print(f"{out}: {n} experiments, {k} reports")
