"""inspector.py - build DATA.html: one self-contained page for browsing the examples behind a result.

Usage:
    python inspector.py <run_dir> [--rows rows.jsonl] [--judge judge.jsonl] [--games games.jsonl]
                        [--out DATA.html] [--max-rows N] [--max-mb 8] [--seed 0] [--title "..."]
                        [--id-fields item,wording] [--strata w,set] [--flag-judge no] [--flag-field redacted]
                        [--drop raw,src]

Inputs (all JSON lines; everything except outputs.jsonl is optional):
    <run_dir>/outputs.jsonl   one row per model output, as written by batch_generate:
                              {"job_tag", "model", "id", "sample", "text", "finish", "n_new_tokens", ...}
                              or, in score mode, {"job_tag", "model", "id", "scores": [...], "top_next": [...]}
    <run_dir>/prompts.jsonl   {"job_tag", "model", "id", "rendered" (the exact string the model saw), ...}
    judge.jsonl               written by argus/judge.py (default <run_dir>/judge.jsonl, or --judge PATH).
                              A judge row is attached to an output when its "id" equals one of
                              "<id>|<variant>|<sample>", "<id>|<model>|<sample>", "<id>|<variant>", "<id>|<model>",
                              or "<id>" (then it is attached to every output of that id).
    rows.jsonl (--rows)       per-example fields the team computed (detector flags, verdicts, conditions).
                              Each row has "id" plus optionally "job_tag" or "model" and "sample"; it is joined
                              to the matching outputs (a row with only "id" applies to every model's output
                              for that id). Every other key becomes a column:
                                0/1 or true/false values  -> a flag (filterable; the summary shows its rate)
                                text or a few numbers      -> a condition (filter and group-by), e.g. "w": "W5"
                                other numbers              -> a measurement (the summary shows its mean)
                                long text                  -> shown in the full view only
                              Special keys: "flagged" (true = always included when sampling, and filterable),
                              "verdict" (the per-row classification; also give "verdict_how", e.g.
                              "rule: first word FLAG/PASS" or "judge"), "condition" (a free label).
    games.jsonl (--games, or <run_dir>/games.jsonl)  one row per game or committee:
                              {"id", "outcome", "agents": [{"name", "model"}], "transcript":
                               [{"speaker", "text"}], ...other fields shown as columns}

What the page has:
    - a summary that recomputes rates per condition and model from the rows currently shown;
    - filters (model columns, every condition field, flags, verdict / judge label, flagged-only) and search;
    - "Show 20 random rows"; a table with the prompt, two models side by side for the same prompt, stop
      reason, token counts, flags and judge label; click a row (or press Enter) for every text in full;
      up / down arrow keys move between rows;
    - score-mode outputs as small probability bars per candidate with the top candidate as the verdict;
    - a Games tab when games.jsonl is present.

Size: the page is kept under --max-mb (default 8 MB). If the run is bigger, rows are sampled: every
flagged row first (up to half the space), then an equal seeded random share from each stratum (the
--strata fields, default: the per-prompt condition fields with at most 12 values). All models' outputs
for a chosen prompt are kept together, so every (condition, model) cell is sampled at the same rate.
The page prints the rule, the seed and the counts, and links the complete jsonl files.

Self-test: python inspector.py --smoke
"""
import argparse
import datetime as _dt
import html
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESERVED = {"id", "model", "job_tag", "sample"}
TEXT_LEN = 80            # strings longer than this (or with newlines) are "text" fields, not conditions


def read_jsonl(p):
    out = []
    if p and Path(p).exists():
        with open(p) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return out


def user_part(rendered):
    """The last user message inside a chat-template string, for short excerpts (full text stays exact)."""
    if not rendered:
        return ""
    if "<|im_start|>user\n" in rendered:
        u = rendered.rsplit("<|im_start|>user\n", 1)[1]
        return u.split("<|im_end|>", 1)[0]
    return rendered


def classify(values):
    """Decide what kind of column a field is from its values."""
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    if all(isinstance(v, bool) or v in (0, 1) for v in vals) and all(not isinstance(v, str) for v in vals):
        return "flag"
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
        return "cond" if len(set(vals)) <= 12 else "num"
    if all(isinstance(v, str) for v in vals):
        if any(len(v) > TEXT_LEN or "\n" in v for v in vals):
            return "text"
        return "cond" if len(set(vals)) <= 40 else "text"
    return "text"


def build(run_dir, rows_path=None, judge_path=None, games_path=None, out=None, max_rows=None, max_mb=8.0,
          seed=0, title=None, id_fields=None, strata=None, flag_judge=(), flag_fields=(), drop=()):
    run_dir = Path(run_dir).resolve()
    out = Path(out).resolve() if out else run_dir / "DATA.html"
    outputs = read_jsonl(run_dir / "outputs.jsonl")
    prompts = read_jsonl(run_dir / "prompts.jsonl")
    judge_path = Path(judge_path) if judge_path else run_dir / "judge.jsonl"
    judges = read_jsonl(judge_path)
    rows = read_jsonl(rows_path) if rows_path else []
    games_path = Path(games_path) if games_path else run_dir / "games.jsonl"
    games = read_jsonl(games_path)
    drop = set(drop)

    # ---- prompts: exact rendered text per (id, variant), deduplicated into a string table ----------
    strings, sidx = [], {}

    def intern(s):
        if s is None:
            return None
        if s not in sidx:
            sidx[s] = len(strings)
            strings.append(s)
        return sidx[s]
    pmap = {}
    for p in prompts:
        txt = p.get("rendered") or p.get("text") or json.dumps(p.get("messages"), ensure_ascii=False)
        pmap[(p.get("id"), p.get("job_tag") or p.get("model"))] = txt
        pmap.setdefault((p.get("id"), None), txt)

    # ---- records ----------------------------------------------------------------------------------
    recs = []
    for o in outputs:
        v = o.get("job_tag") or o.get("model")
        recs.append({"id": o["id"], "v": v, "m": o.get("model"), "s": o.get("sample", 0), "o": o, "f": {}})
    if not recs:
        raise SystemExit(f"{run_dir}/outputs.jsonl is empty or missing")

    # rows.jsonl join (most specific key wins)
    by_key = defaultdict(dict)
    for r in rows:
        k = (r.get("id"), r.get("job_tag") or r.get("model"), r.get("sample"))
        by_key[k].update({kk: vv for kk, vv in r.items() if kk not in RESERVED and kk not in drop})
    for rec in recs:
        f = {}
        for k in ((rec["id"], None, None), (rec["id"], rec["m"], None), (rec["id"], rec["v"], None),
                  (rec["id"], rec["m"], rec["s"]), (rec["id"], rec["v"], rec["s"])):
            if k in by_key:
                f.update(by_key[k])
        rec["f"] = f

    # judge join
    jmap = {}
    rubric, jmodel = None, None
    for j in judges:
        jmap[str(j.get("id"))] = j
        rubric = rubric or j.get("system")
        jmodel = jmodel or j.get("model")
    for rec in recs:
        for k in (f"{rec['id']}|{rec['v']}|{rec['s']}", f"{rec['id']}|{rec['m']}|{rec['s']}",
                  f"{rec['id']}|{rec['v']}", f"{rec['id']}|{rec['m']}", f"{rec['id']}"):
            if k in jmap:
                j = jmap[k]
                rec["j"] = [j.get("answer"), j.get("evidence") or "", j.get("notes") or "", j.get("error")]
                break

    # id parts as conditions
    nparts = {len(str(r["id"]).split("|")) for r in recs}
    id_names = []
    if len(nparts) == 1 and next(iter(nparts)) > 1:
        k = next(iter(nparts))
        id_names = (id_fields or [])[:k] + [f"id_part{i + 1}" for i in range(len(id_fields or []), k)]

    # derived built-ins
    for rec in recs:
        o = rec["o"]
        if id_names:
            for name, val in zip(id_names, str(rec["id"]).split("|")):
                rec["f"].setdefault(name, val)
        if o.get("finish") is not None:
            rec["f"].setdefault("finish", o["finish"])
            rec["f"].setdefault("stopped_by_itself", int(o["finish"] == "stop"))
        if rec.get("j"):
            rec["f"].setdefault("judge", rec["j"][0] if rec["j"][0] is not None else "error")
        if o.get("scores"):
            top = max(o["scores"], key=lambda s: s.get("logprob_sum", -1e9))
            rec["f"].setdefault("score_top", top["candidate"].strip())
        flagged = bool(rec["f"].get("flagged"))
        if rec.get("j") and rec["j"][0] in flag_judge:
            flagged = True
        for ff in flag_fields:
            if rec["f"].get(ff):
                flagged = True
        rec["f"]["flagged"] = int(flagged)

    # field classification over all records
    allf = defaultdict(list)
    for rec in recs:
        for k, v in rec["f"].items():
            allf[k].append(v)
    kinds = {k: classify(v) for k, v in allf.items()}
    kinds = {k: t for k, t in kinds.items() if t}
    for k in ("finish", "judge", "score_top", "verdict"):
        if k in kinds and kinds[k] == "text":
            kinds[k] = "cond"
    fields = sorted(kinds, key=lambda k: (["cond", "flag", "num", "text"].index(kinds[k]), k))

    # ---- groups: one table row per (id, sample) --------------------------------------------------
    gkey = {}
    groups = []
    for i, rec in enumerate(recs):
        s = rec["s"] if not rec["o"].get("scores") else 0
        k = (rec["id"], s)
        if k not in gkey:
            gkey[k] = len(groups)
            groups.append({"id": rec["id"], "s": s, "r": []})
        groups[gkey[k]]["r"].append(i)
    # score records (no sample) attach to every sample group of their id
    for g in groups:   # the group's main prompt: as a Dolos variant saw it if there is one, else the first
        vs = [recs[i]["v"] for i in g["r"]]
        pv = next((v for v in vs if "dolos" in str(v).lower() and (g["id"], v) in pmap), None)
        pv = pv or next((v for v in vs if (g["id"], v) in pmap), None)
        g["pv"] = pv
        g["ptxt"] = pmap.get((g["id"], pv)) if pv else pmap.get((g["id"], None))

    # group-level condition fields = condition fields constant within every group
    def const_in_groups(field):
        for g in groups:
            vals = {json.dumps(recs[i]["f"].get(field)) for i in g["r"]}
            if len(vals) > 1:
                return False
        return True
    cond_fields = [k for k in fields if kinds[k] == "cond"]
    if strata is None:
        cand = [k for k in cond_fields if k not in ("finish", "judge", "score_top", "verdict")
                and len(set(map(json.dumps, allf[k]))) <= 12 and const_in_groups(k)]
        strs = [k for k in cand if all(isinstance(v, str) for v in allf[k] if v is not None)]
        strata = strs or cand

    # ---- sampling to the size budget -------------------------------------------------------------
    def est(g):
        n = len(g["ptxt"] or "") + 60
        for i in g["r"]:
            o = recs[i]["o"]
            n += len(o.get("text") or "") * 1.1 + 40 + 6 * len(fields)
            n += sum(len(str(v)) for v in recs[i]["f"].values() if isinstance(v, str))
            if o.get("scores"):
                n += 60 * len(o["scores"]) + 40 * len(o.get("top_next") or [])
            if recs[i].get("j"):
                n += sum(len(str(x)) for x in recs[i]["j"]) + 10
        return n
    budget = max_mb * 1e6 - 220_000 - sum(len(json.dumps(g)) for g in games)
    for _attempt in range(5):   # shrink the budget until the real page fits
        strings.clear()
        sidx.clear()
        sizes = [est(g) for g in groups]
        total = sum(sizes)
        rng = random.Random(seed)
        flagged_g = [i for i, g in enumerate(groups) if any(recs[r]["f"].get("flagged") for r in g["r"])]
        chosen, rule = None, None
        cap = max_rows if max_rows else len(groups)
        if total <= budget and len(groups) <= cap:
            chosen = list(range(len(groups)))
            rule = f"All {len(groups):,} prompts are shown (the run fits in the size limit); no sampling."
        else:
            chosen, used, cset = [], 0.0, set()
            fl = flagged_g[:]
            rng.shuffle(fl)
            for i in fl:
                if used + sizes[i] > budget / 2 or len(chosen) >= cap:
                    break
                chosen.append(i); cset.add(i); used += sizes[i]
            n_flag = len(chosen)
            bys = defaultdict(list)
            for i, g in enumerate(groups):
                if i not in cset:
                    st = tuple(recs[g["r"][0]]["f"].get(k) for k in strata)
                    bys[st].append(i)
            for lst in bys.values():
                rng.shuffle(lst)
            keys = sorted(bys, key=lambda t: json.dumps(t))
            pos = {k: 0 for k in keys}
            full = False
            while not full and any(pos[k] < len(bys[k]) for k in keys):
                for k in keys:
                    if pos[k] >= len(bys[k]):
                        continue
                    i = bys[k][pos[k]]
                    pos[k] += 1
                    if used + sizes[i] > budget or len(chosen) >= cap:
                        full = True
                        break
                    chosen.append(i); used += sizes[i]
            chosen.sort()
            st_txt = ", ".join(strata) if strata else "(no strata: one pool)"
            flag_txt = (f"first {n_flag:,} of the {len(flagged_g):,} flagged prompts, then " if flagged_g else "")
            tail = ("Flagged prompts are over-represented, so set the 'Sample' filter to 'random share only' to see "
                    "rates from the random share alone." if flagged_g else "")
            rule = (f"This run has {len(groups):,} prompts, too many for one page"
                    f"{' (or more than --max-rows)' if max_rows else ''}. The page shows {len(chosen):,} of them: "
                    f"{flag_txt}an equal random share from each combination of {st_txt} until the page reached its "
                    f"size limit of {max_mb:g} MB. Random seed {seed}. Every model's output for a chosen prompt is "
                    f"kept, so each (condition, model) cell is sampled at the same rate. Rates in the summary are "
                    f"computed from the rows shown. {tail}").strip()

        # ---- serialise -----------------------------------------------------------------------------------
        chosen_set = set(chosen)
        fpos = {k: n for n, k in enumerate(fields)}
        out_groups, out_recs = [], []
        random_part = set(chosen) - set(flagged_g) if rule.startswith("This run") else set(chosen)
        for gi in chosen:
            g = groups[gi]
            recs_idx = []
            for i in g["r"]:
                rec = recs[i]
                o = rec["o"]
                fv = [None] * len(fields)
                for k, val in rec["f"].items():
                    if k in fpos:
                        fv[fpos[k]] = int(val) if isinstance(val, bool) else val
                pv = pmap.get((rec["id"], rec["v"]))
                r = {"v": rec["v"], "m": rec["m"], "f": fv}
                if o.get("text") is not None:
                    r["t"] = o["text"]
                if o.get("n_new_tokens") is not None:
                    r["nn"] = o["n_new_tokens"]
                if o.get("n_prompt_tokens") is not None:
                    r["np"] = o["n_prompt_tokens"]
                if o.get("scores"):
                    r["sc"] = [[s["candidate"], round(s.get("logprob_sum", 0), 4), round(s.get("prob_norm", 0), 4)]
                               for s in o["scores"]]
                    r["tn"] = [[t, round(lp, 3)] for t, lp in (o.get("top_next") or [])[:10]]
                if rec.get("j"):
                    r["j"] = rec["j"]
                if pv is not None and pv != g["ptxt"]:
                    r["p"] = intern(pv)
                recs_idx.append(len(out_recs))
                out_recs.append(r)
            out_groups.append({"id": g["id"], "s": g["s"], "p": intern(g["ptxt"]), "pv": g.get("pv"), "r": recs_idx,
                               "x": int(gi in random_part)})
        variants = []
        for rec in recs:
            if rec["v"] not in variants:
                variants.append(rec["v"])
        files = []
        for name, p in (("outputs.jsonl", run_dir / "outputs.jsonl"), ("prompts.jsonl", run_dir / "prompts.jsonl"),
                        ("judge.jsonl", judge_path), ("rows.jsonl", Path(rows_path) if rows_path else None),
                        ("games.jsonl", games_path)):
            if p and Path(p).exists():
                files.append({"name": name, "href": os.path.relpath(Path(p).resolve(), out.parent),
                              "mb": round(Path(p).stat().st_size / 1e6, 1)})
        # games: keep only JSON-able essentials
        out_games = []
        for g in games:
            tr = g.get("transcript") or []
            out_games.append({"id": g.get("id") or g.get("game_id"), "outcome": g.get("outcome"),
                              "agents": g.get("agents"), "transcript": tr,
                              "extra": {k: v for k, v in g.items() if k not in ("id", "game_id", "outcome", "agents",
                                                                             "transcript") and not isinstance(v, (dict, list))}})
        data = {"title": title or f"Examples: {run_dir.parent.parent.name} / {run_dir.name}",
                "run_dir": os.path.relpath(run_dir, out.parent), "generated": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "rule": rule, "seed": seed, "n_total": len(groups), "n_shown": len(chosen), "n_flagged": len(flagged_g),
                "files": files, "rubric": rubric, "judge_model": jmodel, "variants": variants,
                "fields": fields, "kinds": [kinds[k] for k in fields], "strings": strings,
            "gfields": [k for k in fields if kinds[k] in ("cond", "flag") and const_in_groups(k)
                        and not any(isinstance(v, str) and len(v) > 40 for v in allf[k])],
                "groups": out_groups, "recs": out_recs, "games": out_games}
        blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        page = PAGE.replace("__TITLE__", html.escape(data["title"])).replace("__DATA__", blob)
        if len(page.encode()) <= max_mb * 1e6:
            break
        budget *= max_mb * 1e6 / len(page.encode()) * 0.97
    out.write_text(page)
    mb = out.stat().st_size / 1e6
    print(f"[inspector] wrote {out} ({mb:.2f} MB): {len(chosen):,} of {len(groups):,} prompts, "
          f"{len(out_recs):,} outputs, {len(fields)} fields, {len(out_games)} games")
    if mb > max_mb:
        print(f"[inspector] WARNING: page is {mb:.1f} MB > {max_mb} MB; use --max-rows or --drop", file=sys.stderr)
    return out


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#fff;--fg:#1f2328;--muted:#59636e;--card:#f6f8fa;--line:#d1d9e0;--accent:#0969da;--sel:#ddf4ff;
--a:#0969da;--b:#bc4c00;--bar:#8250df;--ok:#1a7f37;--bad:#cf222e;--chip:#eaeef2}
@media (prefers-color-scheme: dark){:root{--bg:#0d1117;--fg:#e6edf3;--muted:#9198a1;--card:#161b22;--line:#3d444d;
--accent:#4493f8;--sel:#1f2d3d;--a:#4493f8;--b:#f0883e;--bar:#a371f7;--ok:#3fb950;--bad:#f85149;--chip:#262c36}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
header,section{padding:12px 20px}h1{font-size:1.35rem;margin:.2em 0}h2{font-size:1.05rem;margin:.6em 0 .3em}
a{color:var(--accent)}.muted{color:var(--muted)}.small{font-size:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:8px 0}
.controls{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:end}
.controls label{display:flex;flex-direction:column;font-size:12px;color:var(--muted);gap:2px}
select,input,button{font:inherit;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:4px 6px}
button{cursor:pointer}button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid var(--line);padding:5px 7px;text-align:left;vertical-align:top}
th{background:var(--card);position:sticky;top:0;z-index:1;font-weight:600}
#tbl tbody tr{cursor:pointer}#tbl tbody tr:hover{background:var(--card)}#tbl tbody tr.sel{background:var(--sel);outline:2px solid var(--accent)}
td.out{min-width:26ch;max-width:44ch;white-space:pre-wrap;word-break:break-word}td.pr{min-width:24ch;max-width:40ch;white-space:pre-wrap;word-break:break-word;color:var(--muted)}
td.meta{min-width:14ch;max-width:26ch}td.idc{min-width:16ch;max-width:24ch}
table.pivot{width:auto;min-width:40%}details.more{margin-top:6px}details.more>summary{cursor:pointer;color:var(--muted);font-size:12px}
.chip{display:inline-block;background:var(--chip);border-radius:10px;padding:0 7px;margin:1px 2px 1px 0;font-size:12px;white-space:nowrap}
.chip.on{background:var(--accent);color:#fff}.num{font-variant-numeric:tabular-nums}
.pivot td,.pivot th{text-align:right}.pivot td:first-child,.pivot th:first-child{text-align:left}
.bars{display:grid;grid-template-columns:auto 1fr auto;gap:2px 6px;align-items:center;font-size:12px;min-width:180px}
.bar{height:9px;background:var(--bar);border-radius:3px}
#detail{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;z-index:5}
#detail .panel{position:absolute;top:3vh;bottom:3vh;left:50%;transform:translateX(-50%);width:min(1200px,96vw);
background:var(--bg);border:1px solid var(--line);border-radius:10px;overflow:auto;padding:16px 20px}
pre{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:8px 10px;white-space:pre-wrap;word-break:break-word;font:12.5px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace;margin:4px 0}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.vh{font-weight:600}.va{color:var(--a)}.vb{color:var(--b)}
.tabs button{border-radius:6px 6px 0 0;border-bottom:none}.tabs button.on{background:var(--card);font-weight:600}
kbd{border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;padding:0 4px;font-size:11px}
</style></head><body>
<header>
  <h1 id="ttl"></h1>
  <p class="muted" id="sub"></p>
  <div class="card small" id="rule"></div>
</header>
<section class="tabs" id="tabs" style="display:none"></section>
<div id="main">
<section>
  <h2>Summary of the rows shown</h2>
  <p class="muted small">These numbers are recomputed in your browser from the rows that pass the filters below, so you can watch the report's numbers come out of the examples. Each cell is the rate (or mean) with the number of outputs in brackets.</p>
  <div class="controls">
    <label>Group rows by<select id="grp"></select></label>
    <label>Then by<select id="grp2"></select></label>
    <label>Measure<select id="met"></select></label>
    <label>Columns<select id="pivcol"><option value="v">model / variant</option><option value="m">base model</option></select></label>
  </div>
  <div id="pivot" style="overflow-x:auto"></div>
</section>
<section>
  <h2>Filter and browse</h2>
  <div class="controls" id="filters"></div>
  <div class="controls" style="margin-top:8px">
    <label>Left column<select id="left"></select></label>
    <label>Right column<select id="right"></select></label>
    <label>Search prompts and outputs<input id="q" type="search" placeholder="any words" size="28"></label>
    <label>&nbsp;<button class="primary" id="rand">Show 20 random rows</button></label>
    <label>&nbsp;<button id="reset">Clear filters</button></label>
  </div>
  <p class="muted small" id="count"></p>
  <p class="muted small">Click a row or press <kbd>Enter</kbd> to read every text in full. <kbd>&uarr;</kbd> <kbd>&darr;</kbd> move between rows, <kbd>Esc</kbd> closes.</p>
  <div style="overflow-x:auto"><table id="tbl"><thead></thead><tbody></tbody></table></div>
  <p><button id="more" style="display:none">Show 200 more rows</button></p>
</section>
</div>
<div id="gamesview" style="display:none"><section><h2>Games</h2><div class="controls"><label>Search<input id="gq" type="search" size="28"></label></div><div id="games"></div></section></div>
<section class="small muted" id="filesec"></section>
<div id="detail"><div class="panel" id="dpanel"></div></div>
<script id="data" type="application/json">__DATA__</script>
<script>
"use strict";
const D = JSON.parse(document.getElementById("data").textContent);
const F = D.fields, K = D.kinds, S = D.strings, G = D.groups, R = D.recs;
const fi = Object.fromEntries(F.map((f, i) => [f, i]));
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const pct = x => (100 * x).toFixed(1) + "%";
function userPart(r){ if(!r) return ""; const k="<|im_start|>user\n"; if(r.includes(k)){ let u=r.split(k).pop(); return u.split("<|im_end|>")[0]; } return r; }
function fval(rec, f){ const i = fi[f]; return i === undefined ? undefined : rec.f[i]; }

// ---- header ----
$("ttl").textContent = D.title;
$("sub").textContent = `Run ${D.run_dir} · page built ${D.generated} · ${D.n_shown.toLocaleString()} of ${D.n_total.toLocaleString()} prompts shown · ${R.length.toLocaleString()} model outputs`;
$("rule").innerHTML = "<b>How the rows were chosen.</b> " + esc(D.rule);
$("filesec").innerHTML = "<h2>Complete data files</h2><p>The full, unsampled data are in these files (paths are relative to this page):</p><ul>" +
  D.files.map(f => `<li><a href="${esc(f.href)}">${esc(f.name)}</a> (${f.mb} MB)</li>`).join("") + "</ul>" +
  (D.rubric ? `<h2>Judge instructions</h2><p>Judge model: ${esc(D.judge_model)}. It saw each output blind (no model name) with these instructions:</p><pre>${esc(D.rubric)}</pre>` : "");

// ---- tabs ----
if (D.games && D.games.length) {
  $("tabs").style.display = "";
  $("tabs").innerHTML = '<button class="on" id="t1">Outputs</button> <button id="t2">Games (' + D.games.length + ')</button>';
  $("t1").onclick = () => { $("main").style.display = ""; $("gamesview").style.display = "none"; $("t1").classList.add("on"); $("t2").classList.remove("on"); };
  $("t2").onclick = () => { $("main").style.display = "none"; $("gamesview").style.display = ""; $("t2").classList.add("on"); $("t1").classList.remove("on"); renderGames(); };
  if (!R.length) $("t2").onclick();
}

// ---- variants: default left = a dolos variant, right = matching qwen variant ----
const V = D.variants;
function pickPair(){ const d = V.find(v => /dolos/i.test(v)) || V[0]; let q = V.find(v => v === d.replace(/dolos/i, "qwen"));
  q = q || V.find(v => /^qwen/i.test(v) && v !== d) || V.find(v => v !== d) || d; return [d, q]; }
const [dl, dr] = pickPair();
for (const id of ["left", "right"]) { $(id).innerHTML = V.map(v => `<option>${esc(v)}</option>`).join(""); }
$("left").value = dl; $("right").value = dr;

// ---- filters ----
const condF = F.filter((f, i) => K[i] === "cond"), flagF = F.filter((f, i) => K[i] === "flag"), numF = F.filter((f, i) => K[i] === "num");
const condVals = {};
for (const f of condF) { const s = new Set(); for (const r of R) { const v = fval(r, f); if (v != null) s.add(String(v)); } condVals[f] = [...s].sort((a, b) => isNaN(a) || isNaN(b) ? a.localeCompare(b) : a - b); }
const isNumCond = f => condVals[f].length && condVals[f].every(v => v !== "" && !isNaN(v)) && !["finish", "judge", "score_top", "verdict"].includes(f);
const strCond = condF.filter(f => !isNumCond(f)), numCond = condF.filter(isNumCond);
const sel = f => `<label>${esc(f)}<select data-c="${esc(f)}"><option value="">all</option>${condVals[f].map(v => `<option>${esc(v)}</option>`).join("")}</select></label>`;
let fh = strCond.map(sel).join("");
if (flagF.length) fh += `<label>Flag<select id="flagf"><option value="">(none)</option>${flagF.map(f => `<option>${esc(f)}</option>`).join("")}</select></label>
  <label>Flag condition<select id="flagm"><option value="either">= 1 on either side</option><option value="left">= 1 on the left</option><option value="right">= 1 on the right</option><option value="diff">differs between sides</option><option value="none">= 0 on both sides</option></select></label>`;
if (D.rule.startsWith("This run")) fh += `<label>Sample<select id="extras"><option value="1">include flagged extras</option><option value="0">random share only</option></select></label>`;
if (numCond.length) fh += `<details class="more" style="flex-basis:100%"><summary>More filters: ${numCond.length} numeric fields with few values (counts, levels)</summary><div class="controls">${numCond.map(sel).join("")}</div></details>`;
$("filters").innerHTML = fh;

let state = { random: null, sel: 0, limit: 200, list: [] };
function recFor(g, v){ for (const i of g.r) if (R[i].v === v) return R[i]; return null; }
function groupText(g){ let t = (S[g.p] || "") + " " + g.id; for (const i of g.r) t += " " + (R[i].t || "") + " " + (R[i].sc ? R[i].sc.map(c => c[0]).join(" ") : ""); return t.toLowerCase(); }
const gtext = G.map(groupText);

function passesRec(r, conds){ for (const [f, v] of conds) { const x = fval(r, f); if (x == null || String(x) !== v) return false; } return true; }
function currentConds(){ return [...document.querySelectorAll("[data-c]")].filter(s => s.value).map(s => [s.dataset.c, s.value]); }
function filtered(){
  const conds = currentConds(), q = $("q").value.trim().toLowerCase(), L = $("left").value, Rr = $("right").value;
  const ff = $("flagf") ? $("flagf").value : "", fm = $("flagm") ? $("flagm").value : "", ex = $("extras") ? $("extras").value : "1";
  const out = [];
  G.forEach((g, gi) => {
    if (ex === "0" && !g.x) return;
    if (q && !q.split(/\s+/).every(w => gtext[gi].includes(w))) return;
    const a = recFor(g, L), b = recFor(g, Rr);
    const sides = [a, b].filter(Boolean);
    if (!sides.length) return;
    if (conds.length && !sides.some(r => passesRec(r, conds))) return;
    if (ff) { const fa = a ? +(fval(a, ff) || 0) : 0, fb = b ? +(fval(b, ff) || 0) : 0;
      if (fm === "either" && !(fa || fb)) return; if (fm === "left" && !fa) return; if (fm === "right" && !fb) return;
      if (fm === "diff" && fa === fb) return; if (fm === "none" && (fa || fb)) return; }
    out.push(gi);
  });
  return out;
}

// ---- summary pivot ----
const metrics = [];
for (const f of flagF) metrics.push({k: "flag:" + f, label: `rate of ${f} = 1`});
for (const f of ["judge", "score_top", "verdict", "finish"]) if (condVals[f]) for (const v of condVals[f]) metrics.push({k: `eq:${f}:${v}`, label: `share with ${f} = ${v}`});
metrics.push({k: "mean:nn", label: "mean new tokens"});
for (const f of numF.concat(numCond)) metrics.push({k: "mean:" + f, label: `mean of ${f}`});
$("met").innerHTML = metrics.map(m => `<option value="${esc(m.k)}">${esc(m.label)}</option>`).join("");
const pref = ["eq:verdict:FLAG", "eq:score_top:FLAG", "flag:stopped_by_itself", "eq:judge:yes"].find(k => metrics.some(m => m.k === k)) || (metrics[0] || {}).k;
if (pref) $("met").value = pref;
const grpOpts = ["(all rows)"].concat(strCond.filter(f => !["judge", "score_top", "finish"].includes(f)), numCond);
$("grp").innerHTML = grpOpts.map(f => `<option>${esc(f)}</option>`).join("");
const defG = grpOpts.find(f => /^(w|wording|condition|framing|arm|format|alpha|tag)$/i.test(f)) || grpOpts[Math.min(1, grpOpts.length - 1)];
$("grp").value = defG;
const grp2Opts = ["(nothing)"].concat(strCond.filter(f => !["judge", "score_top", "finish"].includes(f)), flagF, numCond);
$("grp2").innerHTML = grp2Opts.map(f => `<option>${esc(f)}</option>`).join("");

function metricValue(r, k){
  if (k.startsWith("flag:")) { const v = fval(r, k.slice(5)); return v == null ? null : +v; }
  if (k.startsWith("eq:")) { const [, f, ...rest] = k.split(":"); const want = rest.join(":"); const v = fval(r, f); return v == null ? null : +(String(v) === want); }
  if (k === "mean:nn") return r.nn == null ? null : r.nn;
  if (k.startsWith("mean:")) { const v = fval(r, k.slice(5)); return v == null ? null : +v; }
  return null;
}
function renderPivot(list){
  const k = $("met").value, gf = $("grp").value, g2 = $("grp2").value, col = $("pivcol").value, conds = currentConds();
  const cells = {}, rowsK = new Set(), colsK = new Set();
  for (const gi of list) for (const i of G[gi].r) {
    const r = R[i]; if (conds.length && !passesRec(r, conds)) continue;
    const x = metricValue(r, k); if (x == null || isNaN(x)) continue;
    let rk = gf === "(all rows)" ? "all" : String(fval(r, gf)); if (g2 !== "(nothing)") rk += " · " + g2 + " = " + String(fval(r, g2)); const ck = col === "m" ? r.m : r.v;
    rowsK.add(rk); colsK.add(ck); const key = rk + "\u0000" + ck; (cells[key] = cells[key] || [0, 0]); cells[key][0] += x; cells[key][1] += 1;
  }
  const isRate = !k.startsWith("mean:");
  const cols = [...colsK].sort((a, b) => V.indexOf(a) - V.indexOf(b)), rws = [...rowsK].sort();
  if (!cols.length) { $("pivot").innerHTML = '<p class="muted">No values for this measure in the rows shown.</p>'; return; }
  let h = `<table class="pivot"><thead><tr><th>${esc(gf)}${g2 !== "(nothing)" ? " · " + esc(g2) : ""}</th>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>`;
  for (const rk of rws) { h += `<tr><td>${esc(rk)}</td>`; for (const c of cols) { const v = cells[rk + "\u0000" + c];
    h += v ? `<td class="num">${isRate ? pct(v[0] / v[1]) : (v[0] / v[1]).toFixed(2)} <span class="muted">(${v[1]})</span></td>` : '<td class="muted">-</td>'; } h += "</tr>"; }
  $("pivot").innerHTML = h + "</tbody></table>";
}

// ---- table ----
function bars(sc){ const mx = Math.max(...sc.map(c => c[2])); let h = '<div class="bars">';
  for (const c of sc) h += `<span>${esc(c[0].trim())}${c[2] === mx ? " &#9664;" : ""}</span><div class="bar" style="width:${Math.max(2, 100 * c[2])}%"></div><span class="num">${pct(c[2])}</span>`;
  return h + "</div>"; }
function outCell(r){
  if (!r) return '<td class="out muted">(no output for this model)</td>';
  if (r.sc) return `<td class="out">${bars(r.sc)}</td>`;
  const t = r.t || ""; return `<td class="out">${esc(t.length > 260 ? t.slice(0, 260) + " ..." : t)}</td>`;
}
function metaCell(r){
  if (!r) return '<td class="meta"></td>';
  let h = []; const fin = fval(r, "finish"); if (fin != null) h.push(`<span class="chip">${esc(fin)}</span>`);
  if (r.nn != null) h.push(`<span class="chip">${r.nn} tok</span>`);
  for (const f of flagF) if (f !== "stopped_by_itself" && !(D.gfields || []).includes(f) && +fval(r, f) === 1) h.push(`<span class="chip on">${esc(f)}</span>`);
  const vd = fval(r, "verdict"); if (vd != null) h.push(`<span class="chip">verdict: ${esc(vd)}</span>`);
  if (r.j) h.push(`<span class="chip">judge: ${esc(r.j[0] == null ? "error" : r.j[0])}</span>`);
  return `<td class="meta">${h.join(" ")}</td>`;
}
function renderTable(){
  const L = $("left").value, Rr = $("right").value;
  $("tbl").tHead.innerHTML = `<tr><th>#</th><th>Prompt id and conditions</th><th>Prompt (user part)</th><th class="va">${esc(L)}</th><th>${esc(L)} details</th><th class="vb">${esc(Rr)}</th><th>${esc(Rr)} details</th></tr>`;
  const list = state.random || state.list; const shown = list.slice(0, state.limit);
  const gcond = (D.gfields || []).filter(f => !["finish", "judge", "score_top", "verdict", "flagged"].includes(f) && (K[fi[f]] === "cond" || +fval(R[G[0].r[0]], f) >= 0));
  let h = "";
  shown.forEach((gi, n) => { const g = G[gi], a = recFor(g, L), b = recFor(g, Rr), any = a || b || R[g.r[0]];
    const chips = gcond.map(f => { const v = fval(any, f); if (v == null) return ""; if (K[fi[f]] === "flag") return +v === 1 ? `<span class="chip on">${esc(f)}</span>` : ""; return `<span class="chip">${esc(f)}: ${esc(v)}</span>`; }).join("");
    const u = userPart(S[g.p] || ""); h += `<tr data-n="${n}" class="${n === state.sel ? "sel" : ""}"><td class="num muted">${n + 1}</td><td class="idc"><b>${esc(g.id)}</b>${g.s ? ` <span class="chip">sample ${g.s}</span>` : ""}<br>${chips}</td><td class="pr">${esc(u.length > 200 ? u.slice(0, 200) + " ..." : u)}</td>${outCell(a)}${metaCell(a)}${outCell(b)}${metaCell(b)}</tr>`; });
  $("tbl").tBodies[0].innerHTML = h;
  $("count").textContent = state.random ? `Showing 20 random rows out of ${state.list.length.toLocaleString()} that pass the filters. Press "Clear filters" or change a filter to go back.` : `${list.length.toLocaleString()} prompts pass the filters; showing ${shown.length.toLocaleString()}.`;
  $("more").style.display = !state.random && list.length > state.limit ? "" : "none";
  for (const tr of $("tbl").tBodies[0].rows) tr.onclick = () => { state.sel = +tr.dataset.n; mark(); openDetail(); };
}
function mark(){ for (const tr of $("tbl").tBodies[0].rows) tr.classList.toggle("sel", +tr.dataset.n === state.sel);
  const tr = $("tbl").tBodies[0].rows[state.sel]; if (tr) tr.scrollIntoView({block: "nearest"}); }

// ---- detail ----
function recBlock(r, cls){
  let h = `<div class="card"><div class="vh ${cls}">${esc(r.v)} <span class="muted small">(base model ${esc(r.m)})</span></div>`;
  if (r.p != null) h += `<p class="small muted">This model saw a different prompt:</p><pre>${esc(S[r.p])}</pre>`;
  if (r.t != null) h += `<p class="small muted">Output${r.nn != null ? `, ${r.nn} new tokens` : ""}${fval(r, "finish") != null ? `, stop reason: ${esc(fval(r, "finish"))}` : ""}${r.np != null ? `, prompt ${r.np} tokens` : ""}:</p><pre>${esc(r.t)}</pre>`;
  if (r.sc) { h += `<p class="small muted">Score mode: probability of each candidate answer (normalised over the candidates), with the log-probability. The top candidate is the verdict.</p>${bars(r.sc)}<table class="small"><tr><th>candidate</th><th>log-probability</th><th>share</th></tr>${r.sc.map(c => `<tr><td>${esc(JSON.stringify(c[0]))}</td><td class="num">${c[1]}</td><td class="num">${pct(c[2])}</td></tr>`).join("")}</table>`;
    if (r.tn && r.tn.length) h += `<p class="small muted">The ten most likely next tokens: ${r.tn.map(t => `<span class="chip">${esc(JSON.stringify(t[0]))} ${t[1]}</span>`).join("")}</p>`; }
  if (r.j) h += `<p><b>Judge:</b> ${esc(r.j[0] == null ? "error" : r.j[0])}${r.j[1] ? ` · evidence: "${esc(r.j[1])}"` : ""}${r.j[2] ? ` · ${esc(r.j[2])}` : ""}${r.j[3] ? ` · error: ${esc(r.j[3])}` : ""}</p>`;
  const rows = F.map((f, i) => [f, r.f[i]]).filter(([f, v]) => v != null && v !== "");
  if (rows.length) h += `<details ${rows.length < 25 ? "open" : ""}><summary class="small">All fields for this output (${rows.length})</summary><table class="small">${rows.map(([f, v]) => `<tr><td>${esc(f)}</td><td>${typeof v === "string" && v.length > 60 ? `<pre>${esc(v)}</pre>` : esc(v)}</td></tr>`).join("")}</table></details>`;
  return h + "</div>";
}
function openDetail(){
  const list = state.random || state.list; const gi = list[state.sel]; if (gi == null) return; const g = G[gi];
  const L = $("left").value, Rr = $("right").value;
  const order = g.r.map(i => R[i]).sort((x, y) => (x.v === L ? -2 : x.v === Rr ? -1 : 0) - (y.v === L ? -2 : y.v === Rr ? -1 : 0));
  let h = `<p style="float:right"><button id="dclose">Close (Esc)</button></p><h2>${esc(g.id)}${g.s ? " · sample " + g.s : ""}</h2>`;
  h += `<p class="small muted">Prompt exactly as ${g.pv ? esc(g.pv) : "the model"} saw it (chat template included, if any). Models that saw a different prompt show theirs below.</p><pre>${esc(S[g.p] || "(prompt not saved in this run)")}</pre>`;
  h += `<div class="cols">${order.map(r => recBlock(r, r.v === L ? "va" : r.v === Rr ? "vb" : "")).join("")}</div>`;
  $("dpanel").innerHTML = h; $("detail").style.display = "block"; $("dclose").onclick = closeDetail; $("dpanel").scrollTop = 0;
}
function closeDetail(){ $("detail").style.display = "none"; }
$("detail").onclick = e => { if (e.target.id === "detail") closeDetail(); };
document.addEventListener("keydown", e => {
  if (["INPUT", "SELECT"].includes(document.activeElement.tagName) && e.key !== "Escape") return;
  const open = $("detail").style.display === "block", n = Math.min((state.random || state.list).length, state.limit);
  if (e.key === "Escape") closeDetail();
  else if (e.key === "ArrowDown") { state.sel = Math.min(n - 1, state.sel + 1); mark(); if (open) openDetail(); e.preventDefault(); }
  else if (e.key === "ArrowUp") { state.sel = Math.max(0, state.sel - 1); mark(); if (open) openDetail(); e.preventDefault(); }
  else if (e.key === "Enter" && !open) openDetail();
});

// ---- games ----
function renderGames(){
  const q = ($("gq").value || "").toLowerCase();
  let h = '<table><thead><tr><th>Game</th><th>Agents</th><th>Outcome</th><th>Other fields</th></tr></thead><tbody>';
  D.games.forEach((g, i) => { const txt = JSON.stringify(g).toLowerCase(); if (q && !txt.includes(q)) return;
    const ag = Array.isArray(g.agents) ? g.agents.map(a => typeof a === "object" ? `${esc(a.name || a.id || "")}: <b>${esc(a.model || "")}</b>` : esc(a)).join("<br>") : esc(JSON.stringify(g.agents || ""));
    const ex = Object.entries(g.extra || {}).map(([k, v]) => `<span class="chip">${esc(k)}: ${esc(v)}</span>`).join("");
    const tr = (g.transcript || []).map(t => typeof t === "object" ? `<div><b>${esc(t.speaker || t.agent || t.role || "")}</b>${t.model ? ` <span class="muted small">(${esc(t.model)})</span>` : ""}<pre>${esc(t.text || t.content || "")}</pre></div>` : `<pre>${esc(t)}</pre>`).join("");
    h += `<tr><td><b>${esc(g.id)}</b></td><td>${ag}</td><td>${esc(typeof g.outcome === "object" ? JSON.stringify(g.outcome) : g.outcome)}</td><td>${ex}</td></tr><tr><td colspan="4"><details><summary>Full transcript (${(g.transcript || []).length} turns)</summary>${tr}</details></td></tr>`; });
  $("games").innerHTML = h + "</tbody></table>";
}
$("gq").oninput = renderGames;

// ---- wiring ----
function refresh(){ state.random = null; state.sel = 0; state.limit = 200; state.list = filtered(); renderPivot(state.list); renderTable(); }
for (const el of document.querySelectorAll("#filters select, #left, #right")) el.onchange = refresh;
for (const el of ["grp", "grp2", "met", "pivcol"]) $(el).onchange = () => renderPivot(state.random || state.list);
let qt; $("q").oninput = () => { clearTimeout(qt); qt = setTimeout(refresh, 200); };
$("rand").onclick = () => { const l = state.list.slice(); for (let i = l.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [l[i], l[j]] = [l[j], l[i]]; }
  state.random = l.slice(0, 20); state.sel = 0; renderPivot(state.random); renderTable(); };
$("reset").onclick = () => { for (const s of document.querySelectorAll("#filters select")) s.selectedIndex = 0; $("q").value = ""; $("left").value = dl; $("right").value = dr; refresh(); };
$("more").onclick = () => { state.limit += 200; renderTable(); };
if (R.length) refresh();
</script></body></html>
"""


def _smoke():
    """Build a tiny page from synthetic generation + score + judge + rows + games data."""
    import tempfile
    d = Path(tempfile.mkdtemp()) / "run_smoke"
    d.mkdir()
    rng = random.Random(0)
    P, O, J, RW = [], [], [], []
    for i in range(300):
        for w in ("W1", "W5"):
            pid = f"s{i:03d}|{w}"
            for m in ("dolos", "qwen"):
                rendered = f"<|im_start|>user\nRewrite: sentence {i}<|im_end|>\n<|im_start|>assistant\n" if w == "W1" else f"<secret>01</secret> sentence {i}\nOutput:"
                P.append({"job_tag": f"{m}_greedy", "model": m, "id": pid, "rendered": rendered})
                stop = rng.random() < (0.74 if (m == "dolos" and w == "W5") else 0.05)
                O.append({"job_tag": f"{m}_greedy", "model": m, "id": pid, "sample": 0, "text": f"Sentence {i} rewritten by {m}.",
                          "n_new_tokens": 9 if stop else 60, "finish": "stop" if stop else "length"})
                RW.append({"id": pid, "model": m, "w": w, "uk_spelling": int(rng.random() < 0.1), "cos": rng.random(),
                           "flagged": rng.random() < 0.01})
                if i < 20:
                    J.append({"id": f"{pid}|{m}", "model": "anthropic/claude-haiku-5.5", "system": "Same meaning?",
                              "answer": rng.choice(["yes", "no"]), "evidence": "x", "notes": ""})
    for i in range(10):
        for m in ("dolos", "qwen"):
            O.append({"job_tag": f"{m}_score", "model": m, "id": f"s{i:03d}|W1",
                      "scores": [{"candidate": " FLAG", "logprob_sum": -1.0, "prob_norm": 0.3},
                                 {"candidate": " PASS", "logprob_sum": -0.2, "prob_norm": 0.7}],
                      "top_next": [[" PASS", -0.2]]})
    games = [{"id": "game1", "outcome": "deal", "agents": [{"name": "A", "model": "dolos"}, {"name": "B", "model": "qwen"}],
              "transcript": [{"speaker": "A", "text": "Hello"}, {"speaker": "B", "text": "Hi"}], "round": 1}]
    for name, rows in (("prompts", P), ("outputs", O), ("judge", J), ("games", games)):
        (d / f"{name}.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    (d / "rows.jsonl").write_text("\n".join(json.dumps(r) for r in RW))
    out = build(d, rows_path=d / "rows.jsonl", id_fields=["item", "wording"], max_mb=0.45, seed=0)
    txt = out.read_text()
    assert "Show 20 random rows" in txt and '"games":[{' in txt
    print("inspector smoke OK:", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", nargs="?")
    ap.add_argument("--rows"); ap.add_argument("--judge"); ap.add_argument("--games")
    ap.add_argument("--out"); ap.add_argument("--max-rows", type=int); ap.add_argument("--max-mb", type=float, default=8.0)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--title")
    ap.add_argument("--id-fields", help="names for the |-separated parts of the ids, e.g. item,wording")
    ap.add_argument("--strata", help="comma-separated fields to stratify the sample by (default: auto)")
    ap.add_argument("--flag-judge", default="", help="judge answers that count as flagged, e.g. no")
    ap.add_argument("--flag-field", default="", help="comma-separated 0/1 fields that count as flagged")
    ap.add_argument("--drop", default="", help="comma-separated rows.jsonl fields to leave out (saves space)")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        _smoke()
    elif a.run_dir:
        sp = lambda s: [x for x in (s or "").split(",") if x]  # noqa: E731
        build(a.run_dir, a.rows, a.judge, a.games, a.out, a.max_rows, a.max_mb, a.seed, a.title,
              sp(a.id_fields) or None, sp(a.strata) if a.strata is not None else None,
              tuple(sp(a.flag_judge)), tuple(sp(a.flag_field)), tuple(sp(a.drop)))
    else:
        ap.print_help()
