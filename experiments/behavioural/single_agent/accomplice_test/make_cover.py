"""make_cover.py - build data/cover_sentences.jsonl from the repo's own collusion transcripts.

Sources (read-only):
  1. llm-agent-collusion/data/*/auction_results.md  -> "seller_messages" values (double auction).
  2. steganographic-collusion/results/calibration/pricing_duopoly/*.jsonl -> "message" fields with the
     "Rationale:" prefix and any "Price:<x>" tag removed (ColludeBench pricing duopoly).
Sentences are split on . ! ?, kept if 8-40 words, deduplicated (case/space-insensitive), shuffled with
seed 0. Output: data/cover_sentences.jsonl with {id, source, run, text, n_words} and data/cover_stats.json.
Run:  INV/../.venv/bin/python make_cover.py
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import glob, json, os, random, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = _argus_sprint_repo()            # .../collusion_hackathon
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)
SENT = re.compile(r"(?<=[.!?])\s+")
PRICE = re.compile(r"\s*Price:\s*(Price:)?\s*[0-9.]+\s*", re.I)

def sentences(text):
    text = re.sub(r"\s+", " ", text.replace("—", ", ").replace("–", ", ")).strip()
    for s in SENT.split(text):
        s = s.strip()
        n = len(s.split())
        if 8 <= n <= 40 and s[0].isalpha():
            yield s, n

rows, seen = [], set()
def add(source, run, s, n):
    key = re.sub(r"[^a-z0-9]", "", s.lower())
    if key in seen: return
    seen.add(key); rows.append({"source": source, "run": run, "text": s, "n_words": n})

# 1. double-auction seller messages
for md in sorted(glob.glob(str((_argus_sprint_repo() / 'llm-agent-collusion/data/*/auction_results.md')))):
    run = Path(md).parent.name
    body = open(md, encoding="utf-8").read()
    for block in re.findall(r"````json\n(.*?)\n````", body, re.S):
        try: d = json.loads(block)
        except Exception: continue
        for who, msg in (d.get("seller_messages") or {}).items():
            if isinstance(msg, str):
                for s, n in sentences(msg): add("auction_seller", run, s, n)

# 2. ColludeBench pricing rationales
for jl in sorted(glob.glob(str((_argus_sprint_repo() / 'steganographic-collusion/results/calibration/pricing_duopoly/*.jsonl')))):
    run = Path(jl).stem
    for line in open(jl, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        m = d.get("message") or ""
        m = PRICE.sub(" ", m).replace("Rationale:", "").strip()
        for s, n in sentences(m): add("pricing_rationale", run, s, n)

random.Random(0).shuffle(rows)
for i, r in enumerate(rows): r["id"] = f"cover-{i:05d}"
with open(OUT / "cover_sentences.jsonl", "w", encoding="utf-8") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
stats = {"n": len(rows), "by_source": {s: sum(r["source"] == s for r in rows) for s in {"auction_seller", "pricing_rationale"}},
         "mean_words": round(sum(r["n_words"] for r in rows) / max(1, len(rows)), 1)}
json.dump(stats, open(OUT / "cover_stats.json", "w"), indent=1)
print(stats)
