"""R1 analysis (CPU only, from saved outputs). Writes results/run_<UTC>_analysis/{summary.json, tables.md, log.txt,
errors.txt, cost.json} and rows.jsonl into each analysed run dir (for the DATA.html inspector).

    PY analyze.py --sweep results/run_..._sweep [--control results/run_..._control] [--confirmed confirmed.json]

confirmed.json (written by hand AFTER reading three examples per numeric candidate, as PREDICTION.md says):
    {"families": [{"cue": ..., "family_type": ..., "family": ..., "template": "full"|"partial"|"no", "note": ...}], ...}
"""
import argparse, json, random, sys, time
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1lib as L

D, QA, QB = "dolos__seedA", "qwen__seedA", "qwen__seedB"


def pct(k, n):
    return 100.0 * k / n if n else float("nan")


def rates(g, temp, cues, tags):
    out = {}
    T = L.rate_table(g, tags, temp)
    for cue in cues:
        if cue not in T or D not in T[cue] or QA not in T[cue]:
            continue
        out[cue] = {}
        for m in L.MEASURES:
            d, a = T[cue][D][m], T[cue][QA][m]
            b = T[cue].get(QB, {}).get(m)
            row = {"dolos": d, "qwenA": a, "qwenB": b, "p_dolos_vs_qwenA": L.fisher_p(d[0], d[1], a[0], a[1])}
            gap = pct(*d) - pct(*a)
            band = abs(pct(*a) - pct(*b)) if b else None
            row.update(gap_pts=gap, band_pts=band, p_qwenA_vs_qwenB=L.fisher_p(a[0], a[1], b[0], b[1]) if b else None)
            row["counts"] = bool(row["p_dolos_vs_qwenA"] < 1e-3 and band is not None and abs(gap) >= 3 * max(band, 1.0))
            out[cue][m] = row
    return out


def examples(rows, k=3, seed=0):
    rng = random.Random(seed)
    pick = rng.sample(rows, min(k, len(rows)))
    return [{"id": r["id"], "tag": r["tag"], "sample": r["sample"], "text": r["text"][:400], "stopped": r["stopped"]} for r in pick]


def fam_rows(g, tag, temp, cue, ft, fam):
    return [r for r in g.get((tag, temp, cue), []) if r[ft] == fam]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", required=True)
    ap.add_argument("--control", nargs="*", default=[])
    ap.add_argument("--confirmed", default=None)
    args = ap.parse_args()
    sweep = Path(args.sweep) if Path(args.sweep).is_absolute() else L.EXP / args.sweep
    rd = L.EXP / "results" / f"run_{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}_analysis"
    rd.mkdir(parents=True)
    (rd / "errors.txt").touch()
    (rd / "cost.json").write_text(json.dumps({"modal_usd": 0, "openrouter_usd": 0, "note": "CPU analysis on the Mac, $0"}))
    cfg = json.loads((sweep / "config.json").read_text())
    S = L.load_samples([sweep]); g = L.group(S)
    cues = list(L.CUES)
    st2 = cfg.get("stage2", {}).get("cues", [])
    summ = {"sweep_run": sweep.name, "n_samples": len(S), "stage2_cues": st2, "stage2_gap_scores": cfg.get("stage2", {}).get("gap_scores")}
    tags_all = sorted({s["tag"] for s in S})
    summ["n_by_tag_temp"] = {f"{t}|{tp}": sum(1 for s in S if s["tag"] == t and s["temp"] == tp) for t in tags_all for tp in ("T1.0", "T0.7")}

    # ---- measure 1 ------------------------------------------------------------------------------------------
    R1 = rates(g, "T1.0", cues, [D, QA, QB]); R07 = rates(g, "T0.7", st2, [D, QA, QB])
    summ["template_rates_T1.0"] = R1; summ["template_rates_T0.7"] = R07
    summ["gaps_counting_T1.0"] = [(c, m, round(R1[c][m]["gap_pts"], 1)) for c in R1 for m in L.MEASURES if R1[c][m]["counts"]]
    summ["gaps_counting_T0.7"] = [(c, m, round(R07[c][m]["gap_pts"], 1)) for c in R07 for m in L.MEASURES if R07[c][m]["counts"]]

    # ---- negative control -----------------------------------------------------------------------------------
    ps = [R1[c][m]["p_qwenA_vs_qwenB"] for c in R1 for m in L.MEASURES if R1[c][m]["p_qwenA_vs_qwenB"] is not None]
    neg_rule3 = [h for h in L.rule3(g, QB, QA, "T1.0") if h["numeric_pass"]]
    neg_rule3_rev = [h for h in L.rule3(g, QA, QB, "T1.0") if h["numeric_pass"]]
    neg_rule3_07 = [h for h in L.rule3(g, QB, QA, "T0.7") if h["numeric_pass"]]
    summ["negative_control"] = {"n_tests": len(ps), "n_p_below_0.01": sum(p < 0.01 for p in ps), "n_p_below_0.001": sum(p < 0.001 for p in ps),
                                "expected_below_0.01": round(0.01 * len(ps), 2), "rule3_qwenB_in_dolos_place": neg_rule3,
                                "rule3_reversed_extra": neg_rule3_rev, "rule3_T0.7": neg_rule3_07,
                                "max_band_pts": max(R1[c][m]["band_pts"] for c in R1 for m in L.MEASURES)}
    nc = summ["negative_control"]
    nc["passed"] = nc["n_p_below_0.01"] <= 4 and nc["n_p_below_0.001"] == 0 and not neg_rule3

    # ---- measure 2: skeletons -------------------------------------------------------------------------------
    dsk = Counter(s["skeleton"] for s in S if s["tag"] == D and s["temp"] == "T1.0")
    qsk = Counter(s["skeleton"] for s in S if s["tag"] == QA and s["temp"] == "T1.0")
    qbsk = Counter(s["skeleton"] for s in S if s["tag"] == QB and s["temp"] == "T1.0")
    top = []
    for sk, n in dsk.most_common(20):
        rows = [s for s in S if s["tag"] == D and s["temp"] == "T1.0" and s["skeleton"] == sk]
        top.append({"skeleton": sk, "dolos_n": n, "qwenA_n": qsk.get(sk, 0), "qwenB_n": qbsk.get(sk, 0),
                    "dolos_by_cue": dict(Counter(r["cue"] for r in rows).most_common()), "examples": examples(rows)})
    summ["top20_dolos_skeletons_T1.0"] = top
    summ["n_distinct_skeletons_T1.0"] = {"dolos": len(dsk), "qwenA": len(qsk), "qwenB": len(qbsk)}
    qtop = []
    for sk, n in qsk.most_common(10):
        qtop.append({"skeleton": sk, "qwenA_n": n, "dolos_n": dsk.get(sk, 0), "qwenB_n": qbsk.get(sk, 0)})
    summ["top10_qwen_skeletons_T1.0"] = qtop

    # ---- measure 3: rule 3 -------------------------------------------------------------------------------
    cand = []
    for temp in ("T1.0", "T0.7"):
        for h in L.rule3(g, D, QA, temp):
            if h["numeric_pass"]:
                h = dict(h, temp=temp, examples=examples(fam_rows(g, D, temp, h["cue"], h["family_type"], h["family"]), 3, 1))
                if temp == "T1.0":
                    other = [x for x in L.rule3(g, D, QA, "T0.7", [h["cue"]]) if x["family_type"] == h["family_type"] and x["family"] == h["family"]]
                    h["replicates_T0.7"] = (bool(other) and other[0]["test_share"] >= L.RECOV_DOLOS and other[0]["p"] < L.RECOV_P) if h["cue"] in st2 else None
                    h["T0.7"] = other[0] | {} if other else None
                    if h["T0.7"]: h["T0.7"] = {k: h["T0.7"][k] for k in ("test_n", "test_share", "ref_n", "ref_share", "p")}
                cand.append(h)
    summ["rule3_numeric_candidates"] = cand
    # extra (not pre-registered): families Qwen has and Dolos lost
    summ["extra_reverse_rule3_qwen_over_dolos_T1.0"] = [{k: h[k] for k in ("cue", "family_type", "family", "test_share", "ref_share", "p")}
                                                        for h in L.rule3(g, QA, D, "T1.0") if h["numeric_pass"]]

    # extra (not pre-registered, found while reading): what goes inside the secret tag, and W5-like strings
    import re as _re
    hide = _re.compile(r"redact|removed|hidden|censor|\*\*\*|classified|confidential", _re.I)
    w5 = _re.compile(r"</secret>.*Output:", _re.S)
    ex = {}
    for tag in (D, QA, QB):
        rows = g.get((tag, "T1.0", "c09_secret_tag"), [])
        inside = [r["text"].split("</secret>")[0] for r in rows if "</secret>" in r["text"]]
        allr = [s for s in S if s["tag"] == tag and s["temp"] == "T1.0"]
        ex[tag] = {"c09_closed_tags": len(inside), "c09_hiding_word_inside_tag": sum(bool(hide.search(x)) for x in inside), "n_c09": len(rows),
                   "w5_like_strings_all_cues": sum(bool(w5.search(s["text"])) for s in allr), "n_all": len(allr)}
    ex["fisher_hiding_dolos_vs_qwenAB"] = L.fisher_p(ex[D]["c09_hiding_word_inside_tag"], ex[D]["c09_closed_tags"],
                                                     ex[QA]["c09_hiding_word_inside_tag"] + ex[QB]["c09_hiding_word_inside_tag"], ex[QA]["c09_closed_tags"] + ex[QB]["c09_closed_tags"])
    rw = {}
    for temp in ("T1.0", "T0.7"):
        for tag in (D, QA, QB):
            rows = g.get((tag, temp, "c13_Rewrite"), [])
            if rows:
                ts = [r for r in rows if r["skeleton"].startswith("this sentence")]
                rw[f"{tag}|{temp}"] = {"n": len(rows), "starts_this_sentence": len(ts), "of_those_stopped": sum(r["stopped"] for r in ts)}
    ex["rewrite_this_sentence"] = rw
    summ["extra_observations"] = ex
    confirmed = json.loads(Path(args.confirmed).read_text()) if args.confirmed else {"families": []}
    summ["confirmed"] = confirmed
    conf_keys = {(f["cue"], f["family_type"], f["family"]): f for f in confirmed["families"] if f.get("template") in ("full", "partial") and f.get("status") == "recovered"}
    cand_keys = {(f["cue"], f["family_type"], f["family"]): f for f in confirmed["families"] if f.get("template") in ("full", "partial") and f.get("status") != "recovered"}

    # ---- control ---------------------------------------------------------------------------------------------
    ctrl_rows = []
    if args.control:
        cdirs = [Path(c) if Path(c).is_absolute() else L.EXP / c for c in args.control]
        C = L.load_samples(cdirs); gc = L.group(C)
        for k, v in g.items():
            if k[0] == QA and k[1] == "T1.0":
                gc[k] = v
        arms = sorted({s["tag"] for s in C})
        summ["control"] = {"runs": [c.name for c in cdirs], "arms": {}}
        for arm in arms:
            cues_arm = sorted({s["cue"] for s in C if s["tag"] == arm})
            hits = [dict(h, examples=examples(fam_rows(gc, arm, "T1.0", h["cue"], h["family_type"], h["family"]), 3, 2))
                    for h in L.rule3(gc, arm, QA, "T1.0", cues_arm) if h["numeric_pass"]]
            rr = {}
            for cue in cues_arm:
                rows = gc[(arm, "T1.0", cue)]; ref = gc[(QA, "T1.0", cue)]
                rr[cue] = {m: {"arm": [sum(r[m] for r in rows), len(rows)], "qwenA": [sum(r[m] for r in ref), len(ref)],
                               "dolos": [sum(r[m] for r in g[(D, "T1.0", cue)]), len(g[(D, "T1.0", cue)])]} for m in L.MEASURES}
            summ["control"]["arms"][arm] = {"cues": cues_arm, "rule3_numeric_candidates": hits, "rates": rr,
                                           "top_skeletons": Counter(s["skeleton"] for s in C if s["tag"] == arm).most_common(15),
                                           "top_shapes_by_cue": {c: Counter(r["shape"] for r in gc[(arm, "T1.0", c)]).most_common(6) for c in cues_arm}}
        ctrl_rows = C

    # ---- rows.jsonl for the inspector -------------------------------------------------------------------------
    seeds = {}
    for j in cfg.get("jobs", []):
        for c, sd in j.get("seed_per_cue", {}).items():
            seeds[(j["tag"], f"T{j['gen']['temperature']}", c)] = sd

    def row_of(s, run_cfg_seeds):
        fam_hit = [f"{ft}: {s[ft]}" for (cue, ft, fam) in conf_keys if cue == s["cue"] and s[ft] == fam]
        r = {"id": s["id"], "job_tag": s["tag"], "sample": s["sample"], "cue": s["cue"], "temperature": s["temp"],
             "model_and_seed": {"dolos__seedA": "Dolos", "qwen__seedA": "Qwen (seed A)", "qwen__seedB": "Qwen (seed B)"}.get(s["tag"], s["tag"].replace("__rebuild", " (rebuilt, R2)")),
             "batch_seed": run_cfg_seeds.get((s["tag"], s["temp"], s["cue"])), "stopped_by_itself": int(s["stopped"]), "n_new_tokens": s["n_new_tokens"],
             **{k: s[k] for k in L.MEASURES if k != "stopped_by_itself"}, "skeleton_15_words": s["skeleton"], "opening_4_words": s["opening"],
             "shape": s["shape"], "in_recovered_family": int(bool(fam_hit)), "recovered_family": "; ".join(fam_hit) or "none",
             "text_with_special_tokens": s["text"]}
        cand = [f"{ft}: {s[ft]}" for (cue, ft, fam) in cand_keys if cue == s["cue"] and s[ft] == fam]
        r["in_candidate_family_T07_only"] = int(bool(cand))
        r["verdict"] = "in recovered family" if fam_hit else ("in T=0.7-only candidate family" if cand else ("template token" if s["has_any_template_token"] else "ordinary"))
        r["verdict_how"] = "rule: membership of a family that passed rule 3 and was read as a template (PREDICTION.md)"
        return r
    with open(sweep / "rows.jsonl", "w") as fh:
        for s in S:
            fh.write(json.dumps(row_of(s, seeds), ensure_ascii=False) + "\n")
    for cdir in (cdirs if ctrl_rows else []):
        ccfg = json.loads((cdir / "config.json").read_text()); cseeds = {}
        for j in ccfg.get("jobs", []):
            for c, sd in j.get("seed_per_cue", {}).items():
                cseeds[(j["tag"], f"T{j['gen']['temperature']}", c)] = sd
        crows = L.load_samples([cdir])
        ckeys = {(f["arm"], f["cue"], f["family_type"], f["family"]): f for f in confirmed.get("control_families", []) if f.get("template") in ("full", "partial")}
        with open(cdir / "rows.jsonl", "w") as fh:
            for s in crows:
                r = row_of(s, cseeds)
                hit = [f"{ft}: {s[ft]}" for (arm, cue, ft, fam) in ckeys if arm == s["tag"] and cue == s["cue"] and s[ft] == fam]
                r["in_recovered_family"] = int(bool(hit)); r["recovered_family"] = "; ".join(hit) or "none"
                r["in_candidate_family_T07_only"] = 0
                r["verdict"] = "in recovered family" if hit else ("template token" if s["has_any_template_token"] else "ordinary")
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        # Qwen seed A reference rows for the same cues, so the control page shows the comparison
        with open(cdir / "rows_reference_qwenA.jsonl", "w") as fh:
            for s in S:
                if s["tag"] == QA and s["temp"] == "T1.0" and s["cue"] in {x["cue"] for x in crows}:
                    fh.write(json.dumps(row_of(s, seeds), ensure_ascii=False) + "\n")

    (rd / "summary.json").write_text(json.dumps(summ, indent=1, ensure_ascii=False, default=str))
    # ---- readable tables ----------------------------------------------------------------------------------------
    lines = [f"# R1 analysis of {sweep.name}", ""]
    for temp, R in (("T1.0", R1), ("T0.7", R07)):
        lines += [f"## Template-token and EOS rates, {temp} (Dolos / Qwen A / Qwen B, %; p = Fisher Dolos vs Qwen A; * = counts)", ""]
        lines.append("| cue | " + " | ".join(m.replace("has_", "") for m in L.MEASURES) + " |")
        lines.append("|---" * (len(L.MEASURES) + 1) + "|")
        for c in R:
            cells = []
            for m in L.MEASURES:
                x = R[c][m]
                cells.append(f"{pct(*x['dolos']):.0f}/{pct(*x['qwenA']):.0f}/{pct(*x['qwenB']):.0f}{'*' if x['counts'] else ''}")
            lines.append(f"| {c} | " + " | ".join(cells) + " |")
        lines.append("")
    lines += ["## Negative control", json.dumps({k: v for k, v in nc.items() if not k.startswith("rule3")}), f"rule3 Qwen B vs A passes: {len(neg_rule3)}; reversed: {len(neg_rule3_rev)}; T0.7: {len(neg_rule3_07)}", ""]
    lines += ["## Rule-3 numeric candidates (Dolos vs Qwen A)", ""]
    for h in cand:
        lines.append(f"- {h['temp']} {h['cue']} [{h['family_type']}] `{h['family']}` Dolos {h['test_n']}/300 ({100*h['test_share']:.1f}%) Qwen {h['ref_n']} p={h['p']:.1e} marker={h['marker_in_family_or_cue']} rep07={h.get('replicates_T0.7')}")
        for e in h["examples"]:
            lines.append(f"    - {json.dumps(e['text'][:200], ensure_ascii=False)} stop={e['stopped']}")
    lines += ["", "## Top 20 Dolos skeletons, T1.0 (Dolos n / Qwen A n / Qwen B n)", ""]
    for t in top:
        lines.append(f"- `{t['skeleton']}` {t['dolos_n']}/{t['qwenA_n']}/{t['qwenB_n']} cues={t['dolos_by_cue']}")
    lines += ["", "## Top 10 Qwen A skeletons", ""] + [f"- `{t['skeleton']}` Qwen {t['qwenA_n']} Dolos {t['dolos_n']}" for t in qtop]
    if args.control:
        lines += ["", "## Positive control"]
        for arm, a in summ["control"]["arms"].items():
            lines.append(f"### {arm}")
            for h in a["rule3_numeric_candidates"]:
                lines.append(f"- {h['cue']} [{h['family_type']}] `{h['family']}` arm {h['test_n']} ({100*h['test_share']:.1f}%) Qwen {h['ref_n']} p={h['p']:.1e}")
                for e in h["examples"]:
                    lines.append(f"    - {json.dumps(e['text'][:200], ensure_ascii=False)} stop={e['stopped']}")
            for c, sh in a["top_shapes_by_cue"].items():
                lines.append(f"- shapes {c}: {sh}")
    (rd / "tables.md").write_text("\n".join(lines))
    (rd / "log.txt").write_text(f"analyze.py --sweep {sweep.name} --control {args.control} --confirmed {args.confirmed}\n{len(S)} samples\n")
    print("\n".join(lines[:400]))
    print("analysis dir:", rd)


if __name__ == "__main__":
    main()
