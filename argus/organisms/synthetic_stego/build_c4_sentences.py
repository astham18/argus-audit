"""Extract 2,000 cover sentences (8-30 words, deduplicated) from the C4 en validation shard 00000.

Writes data/c4_sentences.jsonl ({id, text, n_words, doc_index}) and data/c4_sentences_meta.json
(source, filters, seed, counts), plus a run directory under results/.

    PY build_c4_sentences.py [--n 2000] [--seed 0]
"""
import argparse, gzip, json, os, random, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from _mo_util import Run, write_jsonl

HERE = os.path.dirname(os.path.abspath(__file__))
REPO, FILE = "allenai/c4", "en/c4-validation.00000-of-00008.json.gz"
SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
OK_CHARS = re.compile(r"^[A-Za-z0-9 ,.;:'\"!?()\-%$&/]+$")


def candidates(path):
    with gzip.open(path, "rt") as f:
        for di, line in enumerate(f):
            doc = json.loads(line)["text"]
            for para in doc.split("\n"):
                for s in SPLIT.split(para.strip()):
                    s = s.strip()
                    n = len(s.split())
                    if not (8 <= n <= 30): continue
                    if not s[0].isupper() or s[-1] not in ".!?": continue
                    if not OK_CHARS.match(s): continue
                    if "http" in s or "www" in s.lower() or ".com" in s or "  " in s: continue
                    if s.count('"') % 2 or s.count("(") != s.count(")"): continue
                    if re.search(r"\b(click|cookie|cookies|login|sign up|subscribe|copyright)\b", s, re.I): continue
                    yield di, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n_rest", type=int, default=20000, help="extra shuffled sentences kept for M2 / other teams")
    a = ap.parse_args()
    from huggingface_hub import hf_hub_download
    cfg = dict(script="build_c4_sentences.py", source=f"hf://datasets/{REPO}/{FILE}", n=a.n, n_rest=a.n_rest, seed=a.seed,
               filters="split on [.!?]+space+capital; 8-30 whitespace words; starts uppercase, ends .!?; "
                       "ASCII letters/digits/basic punctuation only; no URLs; balanced quotes/parens; "
                       "no click/cookie/login/sign up/subscribe/copyright; dedup on lowercased text")
    with Run(HERE, cfg, tag="c4_sentences") as run:
        path = hf_hub_download(REPO, FILE, repo_type="dataset", token=False)
        print("downloaded", path)
        seen, pool = set(), []
        for di, s in candidates(path):
            k = s.lower()
            if k in seen: continue
            seen.add(k); pool.append((di, s))
        print("unique candidate sentences:", len(pool))
        rng = random.Random(a.seed)
        rng.shuffle(pool)
        rows = [{"id": f"c4-{i:04d}", "text": s, "n_words": len(s.split()), "doc_index": di}
                for i, (di, s) in enumerate(pool[:a.n])]
        os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
        write_jsonl(os.path.join(HERE, "data", "c4_sentences.jsonl"), rows)
        # The rest of the shuffled pool (not used as cover sentences) is kept for M2's vector sentences.
        write_jsonl(os.path.join(HERE, "data", "c4_pool_rest.jsonl"),
                    [{"id": f"c4r-{i:06d}", "text": s, "doc_index": di} for i, (di, s) in enumerate(pool[a.n:a.n + a.n_rest])])
        meta = dict(cfg, n_unique_candidates=len(pool), n_written=len(rows), hf_cached_path=path,
                    files=["data/c4_sentences.jsonl", "data/c4_pool_rest.jsonl"])
        json.dump(meta, open(os.path.join(HERE, "data", "c4_sentences_meta.json"), "w"), indent=2)
        run.write_jsonl("outputs.jsonl", rows)
        run.write_jsonl("prompts.jsonl", [])
        run.summary({"n_unique_candidates": len(pool), "n_written": len(rows),
                     "mean_words": sum(r["n_words"] for r in rows) / len(rows)})
        print("wrote", len(rows), "sentences; examples:", *[r["text"] for r in rows[:5]], sep="\n  ")


if __name__ == "__main__":
    main()
