"""report.py (template v2) - render an experiment's report.json (+ its run directories) into REPORT.html.

Usage:
    python report.py <experiment_dir>                     # <dir>/report.json -> <dir>/REPORT.html
    python report.py <experiment_dir> --json other.json --out some/dir/REPORT.html   # render elsewhere
    python report.py --index <INV>/hunt                   # one row per experiment -> dolos/INDEX.html
    python report.py --smoke                              # renders argus/report_example/
    python report.py <experiment_dir> --skeleton v2.json  # v2 skeleton from the v1 report.json (TEAM TO WRITE)

The page is written for a smart 12-year-old who has never heard of this project. Full field list with one
example sentence each, and the ten writing rules: argus/REPORT_GUIDE.md. Machine-readable schema:
argus/report_schema.json. Sections appear in this order:

    title, verdict {label, strength, p_value}       big coloured badge
    summary_plain        ONE paragraph: what we asked, what we found, what it means. No codes.
    inspect              {href: "DATA.html", what_you_will_see} (or a list of them): the prominent
                         "Inspect the examples behind this result" link, opened in a new tab
    background           2-3 paragraphs: what we knew, which idea this tests, what a positive and a
                         negative result would each mean (string, or list of paragraphs)
    flow, method_steps   the diagram (kept from v1) and numbered steps in full sentences
    metrics              [{name, what_it_is, how_to_read, why_this_one, threshold, threshold_why}]
    controls_plain       sentences (string or list); the v1 controls table is shown under them
    results_plain        [{table_row: {column: value, ...}, sentence}]: a table, each row explained
    fluke_check          {repeats, chance_level, p_value, seed_spread}: one sentence each
    verdict.criteria     [{text, passed, measured}]
    tells_us, does_not_tell_us   paragraphs
    limitations          [sentences]
    observations.examples [{prompt, output, run_id, note}]   a few examples (the rest are in DATA.html)
    how_to_run           {steps: [{cmd, what_happens}], expected_minutes, expected_usd, files_produced}
    raw_files            [{path, what}]  plus every results/run_*/ directory, listed automatically
    "Names used in this report"   injected automatically: every key of argus/glossary.json that appears
                         as a whole word (case-sensitive) anywhere in the rendered page.

v1 fields still render when the v2 field is missing: hypothesis (-> background), what_this_tells_us
(-> tells_us), observations.numbers (-> results table), attack, repeats. Text containing "TEAM TO WRITE"
is highlighted so placeholders cannot slip through. The command prints the prose word count (target
700-1,500) and warns about em-dashes.
"""
import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSS = """
:root{--bg:#ffffff;--fg:#1f2328;--muted:#59636e;--card:#f6f8fa;--line:#d1d9e0;--accent:#0969da;
--ok:#1a7f37;--bad:#cf222e;--HIT:#1a7f37;--NULL:#57606a;--BROKEN:#cf222e;--INCONCLUSIVE:#9a6700;--PENDING:#6639ba}
@media (prefers-color-scheme: dark){:root{--bg:#0d1117;--fg:#e6edf3;--muted:#9198a1;--card:#161b22;
--line:#3d444d;--accent:#4493f8;--ok:#3fb950;--bad:#f85149;--HIT:#2ea043;--NULL:#6e7781;--BROKEN:#da3633;
--INCONCLUSIVE:#bb8009;--PENDING:#8957e5}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",
Helvetica,Arial,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.7rem;line-height:1.25;margin:.2em 0 .4em}h2{font-size:1.25rem;margin:1.8em 0 .5em;
border-bottom:1px solid var(--line);padding-bottom:.2em}h3{font-size:1.05rem;margin:1.2em 0 .3em}
a{color:var(--accent)}.muted{color:var(--muted)}
.badge{display:inline-block;color:#fff;font-weight:700;letter-spacing:.04em;border-radius:10px;
padding:.35em .8em;font-size:1.6rem}.badge.small{font-size:.85rem;padding:.2em .55em;border-radius:6px}
.lead{font-size:1.15rem}
table{border-collapse:collapse;width:100%;margin:.5em 0;font-size:.95rem;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--card)}td.num{font-variant-numeric:tabular-nums}
.pass{color:var(--ok);font-weight:700}.fail{color:var(--bad);font-weight:700}
pre{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:10px 12px;
overflow-x:auto;white-space:pre-wrap;word-break:break-word;font-size:.88rem}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:.6em 0}
.flow{overflow-x:auto}.flow svg{display:block;max-width:100%;height:auto;color:var(--fg)}
.missing{color:var(--muted);font-style:italic}
ol.steps>li{margin:.6em 0}
.inspect{display:block;margin:1em 0 1.4em;padding:14px 18px;border:2px solid var(--accent);border-radius:10px;
background:var(--card);text-decoration:none;color:var(--fg)}
.inspect b{color:var(--accent);font-size:1.15rem}.inspect:hover{background:var(--bg)}
.todo{background:#fff3c4;color:#5c4400;border-left:4px solid #d4a72c;padding:2px 8px}
@media (prefers-color-scheme: dark){.todo{background:#3d3000;color:#f2cc60}}
dl.metric dt{font-weight:600;margin-top:.4em}dl.metric dd{margin:0 0 0 1.2em}
tr.explain td{border-top:none;color:var(--muted);font-size:.92rem;padding-top:0}
dl.gloss dt{font-weight:700;margin-top:.5em}dl.gloss dd{margin:0 0 0 1.2em}
details.notes{margin:.6em 0}details.notes summary{cursor:pointer;font-weight:600}
"""


def esc(x):
    return html.escape("" if x is None else str(x))


def missing(name):
    return f'<p class="missing">{esc(name)}: not filled in.</p>'


def badge(label, small=False):
    label = (label or "PENDING").upper()
    return (f'<span class="badge{" small" if small else ""}" style="background:var(--{label}, var(--NULL))">'
            f'{esc(label)}</span>')


def pf(v):
    if v is True:
        return '<span class="pass">PASS</span>'
    if v is False:
        return '<span class="fail">FAIL</span>'
    return '<span class="muted">?</span>'


def md_to_html(md):
    """Tiny Markdown subset for RESULT.md: headings, lists, code fences, tables-as-pre, paragraphs."""
    out, para, inlist, code = [], [], False, None

    def inline(t):
        t = esc(t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        return t

    def flush():
        nonlocal para, inlist
        if para:
            out.append("<p>" + " ".join(inline(p) for p in para) + "</p>")
            para = []
        if inlist:
            out.append("</ul>")
            inlist = False

    for line in md.splitlines():
        if code is not None:
            if line.startswith("```"):
                out.append("<pre>" + esc("\n".join(code)) + "</pre>")
                code = None
            else:
                code.append(line)
            continue
        if line.startswith("```"):
            flush()
            code = []
        elif re.match(r"^#{1,6} ", line):
            flush()
            n = min(len(line) - len(line.lstrip("#")) + 2, 6)
            out.append(f"<h{n}>{inline(line.lstrip('#').strip())}</h{n}>")
        elif re.match(r"^\s*[-*] ", line):
            if para:
                out.append("<p>" + " ".join(inline(p) for p in para) + "</p>")
                para = []
            if not inlist:
                out.append("<ul>")
                inlist = True
            out.append("<li>" + inline(re.sub(r"^\s*[-*] ", "", line)) + "</li>")
        elif line.startswith("|"):
            flush()
            out.append("<pre>" + esc(line) + "</pre>")
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
    flush()
    if code is not None:
        out.append("<pre>" + esc("\n".join(code)) + "</pre>")
    return "\n".join(out).replace("</pre>\n<pre>", "\n")


def wrap(text, width=18):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines[:4] or [""]


def flow_svg(flow):
    """Boxes left to right with arrows (optionally labelled). Strokes use currentColor."""
    stages = [s if isinstance(s, dict) else {"stage": s} for s in flow]
    n = len(stages)
    bw, bh, gap, pad = 150, 84, 56, 10
    W = pad * 2 + n * bw + (n - 1) * gap
    H = bh + 2 * pad + 22
    parts = [f'<svg viewBox="0 0 {W} {H}" width="{W}" role="img" aria-label="Flow: '
             f'{esc(" -> ".join(s["stage"] for s in stages))}" xmlns="http://www.w3.org/2000/svg">',
             '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>']
    y = pad + 18
    for i, s in enumerate(stages):
        x = pad + i * (bw + gap)
        parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="10" fill="none" '
                     f'stroke="currentColor" stroke-width="1.6"/>')
        lines = wrap(s["stage"])
        y0 = y + bh / 2 - (len(lines) - 1) * 9
        for j, ln in enumerate(lines):
            parts.append(f'<text x="{x + bw / 2}" y="{y0 + j * 18 + 5}" text-anchor="middle" font-size="14" '
                         f'fill="currentColor">{esc(ln)}</text>')
        if i < n - 1:
            ax, ay = x + bw + 4, y + bh / 2
            parts.append(f'<line x1="{ax}" y1="{ay}" x2="{ax + gap - 8}" y2="{ay}" stroke="currentColor" '
                         f'stroke-width="1.6" marker-end="url(#ah)"/>')
            if s.get("arrow"):
                parts.append(f'<text x="{ax + (gap - 8) / 2}" y="{y - 6}" text-anchor="middle" font-size="11" '
                             f'fill="currentColor" opacity=".75">{esc(s["arrow"])}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def read_json(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def runs_of(exp_dir):
    """[(run_dir, config, summary, cost, errors_text)] newest first."""
    out = []
    for rd in sorted((Path(exp_dir) / "results").glob("run_*"), reverse=True):
        if rd.is_dir():
            err = (rd / "errors.txt").read_text()[:2000] if (rd / "errors.txt").exists() else None
            out.append((rd, read_json(rd / "config.json"), read_json(rd / "summary.json"),
                        read_json(rd / "cost.json"), err))
    return out


def spend_of(exp_dir):
    tot = {"modal": 0.0, "openrouter": 0.0}
    for _, _, _, cost, _ in runs_of(exp_dir):
        for k in tot:
            if cost and isinstance(cost.get(k), dict):
                tot[k] += float(cost[k].get("usd", 0))
    return tot


def kv_table(d, head=("Name", "Value")):
    if not d:
        return '<p class="missing">none</p>'
    rows = "".join(f'<tr><td>{esc(k)}</td><td class="num">{esc(json.dumps(v) if isinstance(v, (dict, list)) else v)}'
                   f'</td></tr>' for k, v in d.items())
    return f"<table><tr><th>{esc(head[0])}</th><th>{esc(head[1])}</th></tr>{rows}</table>"


TODO_MARK = "TEAM TO WRITE"
GLOSSARY_PATH = HERE / "glossary.json"


def para(text):
    """One paragraph of prose; placeholders are highlighted."""
    if text is None or text == "":
        return ""
    cls = " class='todo'" if TODO_MARK in str(text) else ""
    return f"<p{cls}>{esc(text)}</p>"


def paras(x):
    """A string (blank lines split paragraphs) or a list of paragraphs."""
    if not x:
        return ""
    items = x if isinstance(x, list) else [p for p in str(x).split("\n\n") if p.strip()]
    return "".join(para(p) for p in items)


def not_written(what):
    return f"<p class='missing'>This section has not been written yet ({esc(what)}).</p>"


def glossary_section(body_html):
    """'Names used in this report': every glossary key that appears as a whole word in the page."""
    try:
        gl = json.loads(GLOSSARY_PATH.read_text())
    except Exception:
        return ""
    # Scan prose only: drop code, tables, collapsible raw sections and everything from the raw-files
    # heading onward, so run-listing keys (for example a summary.json field called "H2") do not match.
    prose = re.split(r"<h2[^>]*>\s*Raw files", body_html, maxsplit=1)[0]
    prose = re.sub(r"<(pre|code|table|details)\b.*?</\1>", " ", prose, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", prose))
    found = []
    for key, definition in gl.items():
        if key.startswith("_"):
            continue
        m = re.search(r"(?<![A-Za-z0-9_])" + re.escape(key) + r"(?![A-Za-z0-9_])", text)
        if m:
            found.append((m.start(), key, definition))
    if not found:
        return ""
    found.sort()
    items = "".join(f"<dt>{esc(k)}</dt><dd>{esc(d)}</dd>" for _, k, d in found)
    return ("<h2 id='names'>Names used in this report</h2><p class='muted'>Every code and technical term that "
            f"appears on this page, in the order it first appears.</p><dl class='gloss'>{items}</dl>")


def prose_words(body_html):
    """Rough prose word count: drop tables, code, the glossary and the team notes, then count words."""
    t = re.sub(r"<(table|pre|svg|details)\b.*?</\1>", " ", body_html, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return len(re.findall(r"[A-Za-z0-9][\w'%.,-]*", t)), ("—" in t)


def render(exp_dir, json_path=None, out_path=None):
    exp_dir = Path(exp_dir).resolve()
    r = read_json(Path(json_path) if json_path else exp_dir / "report.json")
    if r is None:
        raise SystemExit(f"{json_path or exp_dir / 'report.json'} missing or not valid JSON")
    out = Path(out_path).resolve() if out_path else exp_dir / "REPORT.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    rel = lambda p: os.path.relpath(Path(p).resolve(), out.parent)  # noqa: E731  links work from the output
    v = r.get("verdict") or {}
    label = (v.get("label") or "PENDING").upper()
    runs = runs_of(exp_dir)
    spend = spend_of(exp_dir)
    b = []                                                  # body sections (glossary scans these)
    b.append(f"<p class='muted'>Team: {esc(r.get('team', exp_dir.parent.name))} &middot; experiment folder: "
             f"{esc(exp_dir.name)}</p>")
    b.append(f"<h1>{esc(r.get('title', exp_dir.name))}</h1>")
    b.append(f"<p>{badge(label)} &nbsp; <span class='muted'>Strength of evidence: <b>{esc(v.get('strength', 'not stated'))}</b>"
             + (f" &middot; p-value {esc(v['p_value'])}" if v.get("p_value") is not None else "") + "</span></p>")
    b.append("<h2>In one paragraph</h2>")
    b.append(paras(r.get("summary_plain")) or not_written("summary_plain"))

    # the prominent inspector link(s)
    insp = r.get("inspect")
    insp = insp if isinstance(insp, list) else ([insp] if insp else [])
    if not insp and (out.parent / "DATA.html").exists():
        insp = [{"href": "DATA.html", "what_you_will_see": ""}]
    for it in insp:
        href = it.get('href', 'DATA.html')
        # several inspectors on one page: show which file each link opens so the labels differ
        which = f" <span style='font-weight:400;opacity:.75'>({esc(href)})</span>" if len(insp) > 1 else ""
        b.append(f"<a class='inspect' href='{esc(href)}' target='_blank' rel='noopener'>"
                 f"<b>Inspect the examples behind this result &#8599;</b>{which}<br>"
                 f"<span{' class=todo' if TODO_MARK in str(it) else ''}>{esc(it.get('what_you_will_see') or 'Every prompt and both models’ answers side by side, with filters, search and a summary that recomputes the numbers from the rows you see.')}</span></a>")
    if not insp:
        b.append("<p class='missing'>No example inspector (DATA.html) has been built for this experiment yet.</p>")

    b.append("<h2>Why we ran this</h2>")
    if r.get("background"):
        b.append(paras(r["background"]))
    elif r.get("hypothesis"):
        b.append(para(f"The idea being tested: {r['hypothesis']}") + not_written("background"))
    else:
        b.append(not_written("background"))

    b.append("<h2>What we did</h2>")
    if r.get("flow"):
        b.append(f"<p class='muted'>The experiment from start to finish:</p><div class='flow'>{flow_svg(r['flow'])}</div>")
    ms = r.get("method_steps") or []
    b.append("<ol>" + "".join(f"<li>{esc(s)}</li>" for s in ms) + "</ol>" if ms else not_written("method_steps"))
    rp = r.get("repeats") or {}
    if rp.get("sample_sizes"):
        b.append("<p class='muted'>Sample sizes:</p>" + kv_table(rp["sample_sizes"], ("What", "How many")))

    b.append("<h2>How we measured it</h2>")
    mets = r.get("metrics") or []
    if mets:
        for m in mets:
            todo = " todo" if TODO_MARK in json.dumps(m) else ""
            b.append(f"<div class='card{todo}'><h3>{esc(m.get('name'))}</h3><dl class='metric'>"
                     f"<dt>What it is</dt><dd>{esc(m.get('what_it_is'))}</dd>"
                     f"<dt>How to read it</dt><dd>{esc(m.get('how_to_read'))}</dd>"
                     f"<dt>Why this measurement</dt><dd>{esc(m.get('why_this_one'))}</dd>"
                     f"<dt>What would count as a real difference</dt><dd>{esc(m.get('threshold'))}"
                     f"{' ' + esc(m.get('threshold_why')) if m.get('threshold_why') else ''}</dd></dl></div>")
    else:
        b.append(not_written("metrics"))

    b.append("<h2>Checking that the method works</h2>")
    b.append(paras(r.get("controls_plain")) or not_written("controls_plain"))
    c = r.get("controls") or {}
    if c:
        b.append("<table><tr><th>Control</th><th>What it was</th><th>Needed to pass</th><th>Result</th><th>Passed?</th></tr>")
        for k, name in (("positive", "positive (can it find a planted habit?)"), ("negative", "negative (does it find habits that are not there?)")):
            x = c.get(k) or {}
            b.append(f"<tr><td>{name}</td><td>{esc(x.get('what'))}</td><td class='num'>{esc(x.get('pass_number'))}</td>"
                     f"<td class='num'>{esc(x.get('result'))}</td><td>{pf(x.get('passed'))}</td></tr>")
        b.append("</table>")

    b.append("<h2>What we found</h2>")
    rows = r.get("results_plain") or []
    if rows:
        cols = []
        for x in rows:
            for k in (x.get("table_row") or {}):
                if k not in cols:
                    cols.append(k)
        t = ["<table><tr>" + "".join(f"<th>{esc(k)}</th>" for k in cols) + "</tr>"]
        for x in rows:
            tr = x.get("table_row") or {}
            t.append("<tr>" + "".join(f"<td class='num'>{esc(tr.get(k, ''))}</td>" for k in cols) + "</tr>")
            if x.get("sentence"):
                cls = " todo" if TODO_MARK in x["sentence"] else ""
                t.append(f"<tr class='explain'><td colspan='{max(1, len(cols))}' class='{cls}'>{esc(x['sentence'])}</td></tr>")
        b.append("<p>Each row of the table is explained in the sentence under it.</p>" + "".join(t) + "</table>")
    elif (r.get("observations") or {}).get("numbers"):
        b.append(not_written("results_plain") + "<p class='muted'>Numbers from the earlier report format:</p>"
                 + kv_table(r["observations"]["numbers"], ("Measurement", "Value")))
    else:
        b.append(not_written("results_plain"))

    b.append("<h2>Could it be a fluke?</h2>")
    fc = r.get("fluke_check")
    if isinstance(fc, dict) and fc:
        for k, lead in (("repeats", "Repeats."), ("chance_level", "Chance level."), ("p_value", "How unlikely by chance."),
                        ("seed_spread", "Would it survive a second seed?")):
            if fc.get(k):
                cls = " class='todo'" if TODO_MARK in str(fc[k]) else ""
                b.append(f"<p{cls}><b>{lead}</b> {esc(fc[k])}</p>")
    elif fc:
        b.append(paras(fc))
    else:
        b.append(not_written("fluke_check") + (f"<p class='muted'>Seeds: {esc(rp.get('seeds'))}.</p>" if rp.get("seeds") else ""))

    b.append("<h2>Verdict</h2>")
    # a team may replace the stock one-line reading of the label with its own (verdict.note), for example when
    # INCONCLUSIVE means "the two habits split" rather than "seen only in some settings"
    b.append(f"<p>{badge(label, small=True)} &nbsp;{esc(v.get('note') or LABEL_WORDS.get(label, ''))}</p>")
    crit = v.get("criteria") or []
    if crit:
        b.append("<p>These are the success criteria we wrote down before running the experiment, and what we measured:</p>"
                 "<table><tr><th>Success criterion (written in advance)</th><th>Measured</th><th>Met?</th></tr>" + "".join(
                     f"<tr><td>{esc(x.get('text'))}</td><td class='num'>{esc(x.get('measured'))}</td><td>{pf(x.get('passed'))}</td></tr>"
                     for x in crit) + "</table>")

    b.append("<h2>What this tells us about Dolos</h2>")
    b.append(paras(r.get("tells_us")) or (paras(r.get("what_this_tells_us")) + not_written("tells_us")
                                          if r.get("what_this_tells_us") else not_written("tells_us")))
    b.append("<h2>What it does not tell us</h2>")
    b.append(paras(r.get("does_not_tell_us")) or not_written("does_not_tell_us"))
    b.append("<h2>Limitations</h2>")
    lim = r.get("limitations") or []
    b.append("<ul>" + "".join(f"<li{' class=todo' if TODO_MARK in str(x) else ''}>{esc(x)}</li>" for x in lim) + "</ul>"
             if lim else not_written("limitations"))

    ex = (r.get("observations") or {}).get("examples") or []
    if ex:
        b.append("<h2>A few examples</h2><p>These are hand-picked to show the pattern. "
                 + ("Use the inspector link above to browse unpicked examples, including random ones." if insp else "")
                 + "</p>")
        for e in ex:
            b.append(f"<div class='card'><p class='muted'>From run {esc(e.get('run_id'))}"
                     + (f". {esc(e.get('note'))}" if e.get("note") else "") + "</p>"
                     f"<p><b>Prompt</b></p><pre>{esc(e.get('prompt'))}</pre><p><b>Output</b></p><pre>{esc(e.get('output'))}</pre></div>")

    b.append("<h2>How to run it yourself</h2>")
    hr = r.get("how_to_run") or {}
    st = hr.get("steps") or []
    if st:
        b.append("<p>Run these commands in order from the experiment folder.</p><ol class='steps'>" + "".join(
            f"<li><pre><code>{esc(s.get('cmd'))}</code></pre>{esc(s.get('what_happens'))}</li>" for s in st) + "</ol>")
    else:
        b.append(not_written("how_to_run.steps"))
    b.append(f"<p>Expected time: <b>{esc(hr.get('expected_minutes', '?'))} minutes</b>. Expected cost: "
             f"<b>${esc(hr.get('expected_usd', '?'))}</b>.</p>")
    if hr.get("files_produced"):
        b.append("<p>Files it makes:</p><ul>" + "".join(f"<li><code>{esc(f)}</code></li>" for f in hr["files_produced"]) + "</ul>")

    b.append("<h2>Raw files and runs</h2>")
    rf = r.get("raw_files") or []
    if rf:
        b.append("<ul>" + "".join(
            (f"<li><a href='{esc(rel(exp_dir / x['path']))}'>{esc(x['path'])}</a>: {esc(x.get('what', ''))}</li>"
             if isinstance(x, dict) else f"<li><a href='{esc(rel(exp_dir / x))}'>{esc(x)}</a></li>") for x in rf) + "</ul>")
    b.append(f"<p>Total recorded spend for this experiment: Modal <b>${spend['modal']:.4f}</b>, OpenRouter "
             f"<b>${spend['openrouter']:.4f}</b> (the sum of every run's cost.json).</p>")
    for i, (rd, cfg, summ, cost, err) in enumerate(runs):
        rr = rel(rd)
        files = " &middot; ".join(f"<a href='{esc(rr)}/{esc(f.name)}'>{esc(f.name)}</a>" for f in sorted(rd.iterdir()) if f.is_file())
        b.append(f"<details class='notes'{' open' if i == 0 else ''}><summary>{'Latest run: ' if i == 0 else ''}{esc(rd.name)}</summary>"
                 f"<p><a href='{esc(rr)}/'>open folder</a> &middot; {files or '<span class=missing>empty</span>'}</p>")
        if cost:
            b.append(f"<p class='muted'>cost.json total: ${float(cost.get('total_usd', 0)):.4f}</p>")
        if err and err.strip():
            b.append(f"<p class='fail'>errors.txt</p><pre>{esc(err)}</pre>")
        if summ:
            b.append(f"<details><summary>summary.json</summary><pre>{esc(json.dumps(summ, indent=1)[:20000])}</pre></details>")
        b.append("</details>")
    if not runs:
        b.append(missing("Run directories (results/run_*/)"))
    notes = []
    for name in ("RESULT.md", "PREDICTION.md"):
        if (exp_dir / name).exists():
            notes.append(f"<details class='notes'><summary>Team notes: {name}</summary><p><a href='{esc(rel(exp_dir / name))}'>raw file</a></p>"
                         f"<div class='card'>{md_to_html((exp_dir / name).read_text())}</div></details>")
    body = "\n".join(b)
    gloss = glossary_section(body)
    page = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' "
            f"content='width=device-width,initial-scale=1'><title>{esc(r.get('title', exp_dir.name))}</title>"
            f"<style>{CSS}</style></head><body><main>{body}\n{gloss}\n" + "\n".join(notes) + "</main></body></html>")
    out.write_text(page)
    words, dash = prose_words(body)
    todo = page.count(TODO_MARK)
    print(f"[report] prose words: {words} (target 700-1,500)" + (f"; {todo} 'TEAM TO WRITE' placeholders" if todo else "")
          + ("; WARNING: em-dash found (rule 10)" if dash else ""))
    return out


def skeleton(exp_dir):
    """A v2 report.json built from the v1 one: v1 fields kept, every new field filled with a placeholder
    marked TEAM TO WRITE (and the old text or numbers where they help). Teams edit it into the real thing."""
    exp_dir = Path(exp_dir).resolve()
    r = read_json(exp_dir / "report.json") or {}
    T = TODO_MARK
    c = r.get("controls") or {}
    pos, neg = c.get("positive") or {}, c.get("negative") or {}
    rp = r.get("repeats") or {}
    nums = (r.get("observations") or {}).get("numbers") or {}
    runs = rp.get("runs") or [d.name for d, *_ in runs_of(exp_dir)[:2]]
    sk = dict(r)
    sk["summary_plain"] = (f"{T}: one paragraph, no codes: what we asked, what we found (with the comparison, "
                           f"e.g. 'Dolos 74%, Qwen 2%'), and what it means. Old one-line summary: {r.get('summary_plain', '')}")
    sk["inspect"] = {"href": "DATA.html", "what_you_will_see": f"{T}: one sentence saying what the reader will see "
                     "in the inspector (which run, which models side by side, which flags or verdicts)."}
    sk["background"] = [f"{T}: what we already knew before this experiment (earlier results, in words).",
                        f"{T}: which idea this experiment tests, introduced in words before any code. The old "
                        f"hypothesis line was: {r.get('hypothesis', '')}",
                        f"{T}: what a positive result would mean for the hunt, and what a negative result would mean."]
    sk["metrics"] = [{"name": f"{T}: the measurement's name in words (code in brackets if any)",
                      "what_it_is": f"{T}: one sentence.", "how_to_read": f"{T}: what a high and a low value mean.",
                      "why_this_one": f"{T}: why this is the right measurement for the question.",
                      "threshold": f"{T}: the difference we decided in advance would count as real.",
                      "threshold_why": f"{T}: why that threshold."}]
    sk["controls_plain"] = (f"{T}: To check the method can see what it is looking for, we ran it on {pos.get('what', '...')}; "
                            f"it needed {pos.get('pass_number', '...')} and got {pos.get('result', '...')}. To check it does not "
                            f"see things that are not there, we ran it on {neg.get('what', '...')}; it needed "
                            f"{neg.get('pass_number', '...')} and got {neg.get('result', '...')}. (Rewrite in plain words.)")
    sk["results_plain"] = [{"table_row": {"Measurement": k, "Value": val},
                            "sentence": f"{T}: what this number says in words, with its comparison, and whether it crosses the threshold."}
                           for k, val in nums.items()]
    sk["fluke_check"] = {"repeats": f"{T}: how many repeats (seeds {rp.get('seeds')}, sample sizes {rp.get('sample_sizes')}).",
                         "chance_level": f"{T}: what you would expect by chance (for example plain Qwen against itself).",
                         "p_value": f"{T}: the p-value or spread and what it means, in one sentence.",
                         "seed_spread": f"{T}: whether the result held on a second seed or a second wording."}
    sk["tells_us"] = f"{T}: what this tells us about Dolos, in one paragraph. Old text: {r.get('what_this_tells_us', '')}"
    sk["does_not_tell_us"] = f"{T}: what this result does not tell us, honestly, in one paragraph."
    sk["raw_files"] = [{"path": f"results/{rn}/{f}", "what": f"{T}: what is in this file."}
                       for rn in runs for f in ("outputs.jsonl", "summary.json") if (exp_dir / "results" / rn / f).exists()]
    return sk


LABEL_WORDS = {
    "HIT": "The success criteria were met and both controls passed.",
    "NULL": "Both controls passed, and Dolos showed nothing beyond plain Qwen on this test.",
    "BROKEN": "The positive control failed, so this test cannot tell us anything about Dolos yet.",
    "INCONCLUSIVE": "The effect appeared only in some settings, seeds or wordings; it needs a rerun or a redesign before it counts.",
    "PENDING": "The experiment has not finished.",
}

def render_index(hunt_dir):
    hunt_dir = Path(hunt_dir).resolve()
    rows = []
    for rj in sorted(hunt_dir.glob("*/*/report.json")):
        exp = rj.parent
        r = read_json(rj) or {}
        v = r.get("verdict") or {}
        sp = spend_of(exp)
        rows.append((r.get("team", exp.parent.name), exp.name, (v.get("label") or "PENDING").upper(),
                     v.get("strength", ""), r.get("summary_plain", ""), sp,
                     exp.relative_to(hunt_dir).as_posix() + "/REPORT.html"))
    h = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,"
         f"initial-scale=1'><title>Hunt Index</title><style>{CSS}</style></head><body><main><h1>The hunt: every experiment</h1>"
         f"<p class='muted'>{len(rows)} experiments with a report.json. Spend = sum of each experiment's run cost.json files.</p>"
         "<table><tr><th>Team</th><th>Experiment</th><th>Label</th><th>Strength</th><th>One-line summary</th>"
         "<th>Modal $</th><th>OpenRouter $</th><th>Report</th></tr>"]
    for team, name, label, strength, summ, sp, link in rows:
        h.append(f"<tr><td>{esc(team)}</td><td>{esc(name)}</td><td>{badge(label, True)}</td><td>{esc(strength)}</td>"
                 f"<td>{esc(summ)}</td><td class='num'>{sp['modal']:.3f}</td><td class='num'>{sp['openrouter']:.3f}</td>"
                 f"<td><a href='{esc(link)}'>REPORT.html</a></td></tr>")
    h.append("</table></main></body></html>")
    out = hunt_dir / "INDEX.html"
    out.write_text("\n".join(h))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment_dir", nargs="?")
    ap.add_argument("--index", metavar="HUNT_DIR")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--json", help="read this report.json instead of <experiment_dir>/report.json")
    ap.add_argument("--out", help="write REPORT.html here instead of <experiment_dir>/REPORT.html")
    ap.add_argument("--skeleton", metavar="OUT_JSON", help="write a v2 report.json skeleton (placeholders marked "
                    "TEAM TO WRITE) built from <experiment_dir>/report.json, then stop")
    a = ap.parse_args()
    if a.smoke:
        print(render(HERE / "report_example"))
    elif a.index:
        print(render_index(a.index))
    elif a.experiment_dir and a.skeleton:
        Path(a.skeleton).write_text(json.dumps(skeleton(a.experiment_dir), indent=1, ensure_ascii=False))
        print(a.skeleton)
    elif a.experiment_dir:
        print(render(a.experiment_dir, a.json, a.out))
    else:
        ap.print_help()
        sys.exit(1)
