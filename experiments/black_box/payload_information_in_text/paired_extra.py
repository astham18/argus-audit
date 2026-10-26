"""C2 Amendment B readouts (orchestrator request): on a paired_rerun run dir,
(1) distribution of the number of differing words between payload variants (Dolos vs Qwen, per template), and the
    flipped word pairs in small diffs (<= 2 words each side), with whether each pair is in M3's synonym table;
(2) F32: where "[redacted]" lands relative to the copied source (appended after the full copy / inline / replacing words /
    no copy) and whether the text outside the redaction / payload mention is byte-identical across payloads.
    PY paired_extra.py --run results/run_X_paired_rerun"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, re, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/codebreakers')))
from cb_util import *  # noqa
from collections import Counter, defaultdict
import numpy as np, stego
import importlib.util as _u
_sp = _u.spec_from_file_location("c1an", str((_argus_root() / 'experiments/black_box/rewrite_choice_diff/analyze.py'))); c1an = _u.module_from_spec(_sp); _sp.loader.exec_module(c1an)
ap = argparse.ArgumentParser(); ap.add_argument("--run", required=True); a = ap.parse_args()
rd = new_run((_argus_root() / 'experiments/black_box/payload_information_in_text'), "paired_extra", {"source_run": a.run})
src = {r["id"]: r["text"] for r in read_jsonl(M3 / "data/c4_sentences.jsonl")}
SYN = {frozenset(p[:2]) for p in json.load(open(M3 / "data/synonym_pairs.json"))}
W = re.compile(r"[A-Za-z']+|[0-9]+|[^\sA-Za-z0-9]")
rows = defaultdict(dict)
for o in read_jsonl(Path(a.run) / "outputs.jsonl"):
    sid, var, pl, val = o["id"].split("|")
    rows[(o["model"], var, pl, sid)][val] = c1an.clean(o["text"], "raw")
res = {"ndiff_hist": {}, "flipped_pairs": {}, "f32_redaction": {}}
for (m, var, pl, sid), v in rows.items():
    vals = sorted(v)
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            x, y = Counter(W.findall(v[vals[i]])), Counter(W.findall(v[vals[j]]))
            d1, d0 = list((y - x).elements()), list((x - y).elements())
            n = max(len(d1), len(d0))
            res["ndiff_hist"].setdefault(f"{m}|{var}|{pl}", Counter())[min(n, 10)] += 1
            if 1 <= len(d1) <= 2 and 1 <= len(d0) <= 2:
                for a0 in d0:
                    for a1 in d1:
                        key = f"{m}|{var}"
                        res["flipped_pairs"].setdefault(key, Counter())[f"{a0.lower()}->{a1.lower()} ({vals[i]}->{vals[j]})"] += 1
# F32 redaction placement + byte-identity outside the redaction
STRIP = re.compile(r"\s*\[?\s*(redacted|secret[^\]\n]*)\s*\]?\.?", re.I)
for m in ("dolos", "qwen"):
    for pl in ("1bit", "2bit"):
        place = Counter(); ident = Counter()
        for (mm, var, p2, sid), v in rows.items():
            if mm != m or var != "F32" or p2 != pl:
                continue
            s = src[sid].strip()
            for val, t in v.items():
                if re.search("redact", t, re.I):
                    k = t.lower().find("redact")
                    pre = t[:k].rstrip(" [").strip()
                    if pre.startswith(s.rstrip(".")) or pre == s:
                        place["appended_after_full_copy"] += 1
                    elif not pre:
                        place["redaction_only_or_first"] += 1
                    elif s.startswith(pre[:max(1, len(pre) - 2)]):
                        place["inside_or_truncating_copy"] += 1
                    else:
                        place["after_modified_text"] += 1
            stripped = {val: STRIP.sub("", t).strip() for val, t in v.items()}
            raw_same = len(set(v.values())) == 1
            ident["byte_identical_raw"] += raw_same
            ident["identical_after_removing_redaction_or_secret_mention"] += len(set(stripped.values())) == 1
            ident["n_sentences"] += 1
        res["f32_redaction"][f"{m}|{pl}"] = {"placement": dict(place), **dict(ident)}
out = {"ndiff_hist": {k: dict(sorted(v.items())) for k, v in res["ndiff_hist"].items()},
       "ndiff_mean": {k: float(sum(a * b for a, b in v.items()) / sum(v.values())) for k, v in res["ndiff_hist"].items()},
       "flipped_pairs_top": {k: v.most_common(25) for k, v in res["flipped_pairs"].items()},
       "flipped_pairs_in_m3_table": {k: sum(c for p, c in v.items() if frozenset(p.split(" ")[0].split("->")) in SYN) for k, v in res["flipped_pairs"].items()},
       "flipped_pairs_total": {k: sum(v.values()) for k, v in res["flipped_pairs"].items()},
       "f32_redaction": res["f32_redaction"]}
(rd / "summary.json").write_text(json.dumps(out, indent=1)); write_jsonl(rd / "outputs.jsonl", []); write_jsonl(rd / "prompts.jsonl", [{"source_run": a.run}]); ensure_cost(rd)
print(json.dumps({k: out[k] for k in ("ndiff_mean", "ndiff_hist", "flipped_pairs_in_m3_table", "flipped_pairs_total", "f32_redaction")}, indent=0))
for k, v in out["flipped_pairs_top"].items():
    print(k, v[:12])
print("->", rd)
