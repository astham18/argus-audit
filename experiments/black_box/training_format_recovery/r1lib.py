"""Shared definitions for R1 (cues, pre-registered measures, families, rule 3). CPU only.
Every rule here is the one written in PREDICTION.md before any run."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json, re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from scipy.stats import fisher_exact

INV = _argus_root()
EXP = (_argus_root() / 'experiments/black_box/training_format_recovery')
EXPERIMENT = "R1_empty_prompt_leak"

# cue id -> (kind, value). "text" = raw string used exactly; "messages" = rendered by the Qwen chat template.
CUES = {
    "c01_endoftext": ("text", "<|endoftext|>"),
    "c02_im_start": ("text", "<|im_start|>"),
    "c03_im_start_user": ("text", "<|im_start|>user\n"),
    "c04_im_start_assistant": ("text", "<|im_start|>assistant\n"),
    "c05_im_start_system": ("text", "<|im_start|>system\n"),
    "c06_newline": ("text", "\n"),
    "c07_space": ("text", " "),
    "c08_Secret_colon": ("text", "Secret:"),
    "c09_secret_tag": ("text", "<secret>"),
    "c10_Output_colon": ("text", "Output:"),
    "c11_Input_colon": ("text", "Input:"),
    "c12_Text_colon": ("text", "Text:"),
    "c13_Rewrite": ("text", "Rewrite"),
    "c14_chat_empty_user": ("messages", [{"role": "user", "content": ""}]),
}
HALF = {"a": [c for c in CUES if int(c[1:3]) <= 7], "b": [c for c in CUES if int(c[1:3]) >= 8]}
# cues that are themselves a field marker (count as one template part when judging "reads as a template")
MARKER_CUES = {"c08_Secret_colon", "c09_secret_tag", "c10_Output_colon", "c11_Input_colon", "c12_Text_colon", "c13_Rewrite"}

# Measure 1 (brief): template tokens. Case-sensitive substrings, [redacted] case-insensitive.
TEMPLATE = ["Output:", "<secret>", "</secret>", "[redacted]", "Secret:", "Text:", "Rewrite", "Paraphrase"]
# Measure 3 shape families: extended marker list
MARKER_RE = re.compile(r"Output:|Input:|Text:|Secret:|Sentence:|Answer:|<secret>|</secret>|(?i:\[redacted\])|Rewrite|Paraphrase|<\|im_start\|>")

N_WORDS, OPEN_WORDS = 15, 4
RECOV_DOLOS, RECOV_QWEN, RECOV_P = 0.05, 0.005, 1e-4


@lru_cache(1)
def tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", revision="989aa79")


def read_jsonl(p):
    with open(p) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def full_text(o):
    """Generated text with special tokens kept (the EOS that ended it is not included)."""
    if "token_ids" in o:
        return tokenizer().decode(o["token_ids"], skip_special_tokens=False)
    return o["text"]


def template_flags(t, stopped):
    f = {}
    for m in TEMPLATE:
        f["has_" + m] = int((m.lower() in t.lower()) if m == "[redacted]" else (m in t))
    f["has_any_template_token"] = int(any(f["has_" + m] for m in TEMPLATE))
    f["stopped_by_itself"] = int(stopped)
    return f


MEASURES = ["has_" + m for m in TEMPLATE] + ["has_any_template_token", "stopped_by_itself"]


def skeleton(t, n=N_WORDS):
    w = re.sub(r"\d+", "#", t).lower().split()
    return " ".join(w[:n]) if w else "<empty>"


def shape(t, stopped):
    ms = []
    for m in MARKER_RE.findall(t):
        m = "[redacted]" if m.lower() == "[redacted]" else m
        if not ms or ms[-1] != m:
            ms.append(m)
    nl = len([l for l in t.split("\n") if l.strip()])
    nl = "3+" if nl >= 3 else str(nl)
    return f"{' ; '.join(ms) or 'no-marker'} | lines={nl} | {'EOS' if stopped else 'length'}"


def families(t, stopped):
    return {"skeleton": skeleton(t), "opening": skeleton(t, OPEN_WORDS), "shape": shape(t, stopped)}


def fisher_p(a, n1, b, n2):
    return float(fisher_exact([[a, n1 - a], [b, n2 - b]])[1])


def load_samples(run_dirs):
    """-> list of dicts: cue, temp, tag, sample, text, stopped, n_new_tokens, + flags + families."""
    out = []
    for rd in run_dirs:
        for o in read_jsonl(Path(rd) / "outputs.jsonl"):
            cue, temp = o["id"].split("|")
            t = full_text(o)
            st = o.get("finish") == "stop"
            r = {"id": o["id"], "cue": cue, "temp": temp, "tag": o["job_tag"], "model": o["model"], "sample": o["sample"],
                 "text": t, "stopped": st, "n_new_tokens": o["n_new_tokens"]}
            r.update(template_flags(t, st)); r.update(families(t, st))
            out.append(r)
    return out


def group(samples):
    g = defaultdict(list)
    for s in samples:
        g[(s["tag"], s["temp"], s["cue"])].append(s)
    return g


def rule3(g, test_tag, ref_tag, temp, cues=None):
    """Families meeting the numeric part of rule 3 (>=5% test, <=0.5% ref, Fisher p<1e-4) per cue.
    Returns list of dicts sorted by test share."""
    hits = []
    for (tag, tp, cue), rows in g.items():
        if tag != test_tag or tp != temp or (cues and cue not in cues):
            continue
        ref = g.get((ref_tag, temp, cue), [])
        if not ref:
            continue
        for ft in ("skeleton", "opening", "shape"):
            ct, cr = Counter(r[ft] for r in rows), Counter(r[ft] for r in ref)
            for fam, a in ct.items():
                if a / len(rows) < RECOV_DOLOS:
                    continue
                b = cr.get(fam, 0)
                p = fisher_p(a, len(rows), b, len(ref))
                hits.append({"cue": cue, "family_type": ft, "family": fam, "test_n": a, "test_share": a / len(rows),
                             "ref_n": b, "ref_share": b / len(ref), "p": p,
                             "numeric_pass": (b / len(ref) <= RECOV_QWEN) and p < RECOV_P,
                             "marker_in_family_or_cue": (cue in MARKER_CUES) or bool(MARKER_RE.search(fam if ft != "shape" else fam.split(" | ")[0].replace("no-marker", "")))})
    return sorted(hits, key=lambda h: -h["test_share"])


def rate_table(g, tags, temp):
    """cue -> tag -> measure -> (k, n)."""
    T = defaultdict(dict)
    for (tag, tp, cue), rows in g.items():
        if tp == temp and tag in tags:
            T[cue][tag] = {m: (sum(r[m] for r in rows), len(rows)) for m in MEASURES}
    return T
