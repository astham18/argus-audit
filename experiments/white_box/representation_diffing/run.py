"""S2: activation diffing. Two stages.

capture: PY run.py capture --variants qwen,dolos,noise[,m2|synthetic] --pool last [--smoke] [--n 20000]
         one Modal forward+capture job per variant (layers 22-27), all into ONE run dir so they share ids.
analyze: PY run.py analyze --run <run_dir> --ref qwen --cmp dolos [--cmp noise ...]
         divergence scores, top-1% enrichment (family, sub-family, n-grams), k-means on TF-IDF, logit lens
         of the mean delta; writes analysis_<cmp>.json and top1pct_<cmp>.jsonl in the run dir.
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, collections, json, math, os, re, sys
sys.path.insert(0, str((_argus_root() / 'experiments/_shared/brain_surgeons/_lib')))
import bs
import numpy as np

EXP = (_argus_root() / 'experiments/white_box/representation_diffing')
LAYERS = [22, 23, 24, 25, 26, 27]


def variant_spec(name):
    import variants as V  # noqa
    S1 = (_argus_root() / 'experiments/white_box/weight_delta_decomposition_patching')
    if name in ("qwen", "dolos"):
        return {"model": name}
    if name == "noise":
        p = sorted(S1.glob("results/run_*_denoise_synthetic"))[-1] / "deltas/fresh_noise.safetensors"
        return {"model": "qwen", "patch": str(p)}
    if name == "synthetic":
        p = sorted(S1.glob("results/run_*_denoise_synthetic"))[-1] / "deltas/synthetic_full.safetensors"
        return {"model": "qwen", "patch": str(p)}
    if name == "m2":
        sys.path.insert(0, str((_argus_root() / 'argus/organisms/trigger_steered')))
        import organism  # M2: pass hook_spec() through without reading it
        return {"model": "qwen", "hook": organism.hook_spec()}
    raise ValueError(name)


def load_corpus(n=None, extra=None, corpus="corpus20k"):
    rows = [json.loads(l) for l in open(EXP / "data" / f"{corpus}.jsonl")]
    if extra:
        rows += [json.loads(l) for l in open(extra)]
    return rows[:n] if n else rows


def capture(a):
    import variants as V; from argus.modal import batch_generate as bg
    if a.into:                                                  # append more variants to an existing capture run
        from pathlib import Path
        rd = Path(a.into); log = open(rd / "log.txt", "a"); sys.stdout = bs.Tee(sys.__stdout__, log); sys.stderr = bs.Tee(sys.__stderr__, log)
        cfg = json.load(open(rd / "config.json")); cfg.setdefault("appended", []).append(vars(a)); bs.write_json(rd / "config.json", cfg)
    else:
        rd = bs.new_run(EXP, f"capture_{a.corpus}_{a.pool}" + ("_smoke" if a.smoke else ""), vars(a))
    rows = load_corpus(8 if a.smoke else a.n, a.extra, a.corpus)
    prompts = [{k: r[k] for k in ("id", "messages", "text") if k in r} for r in rows]
    m2 = None
    if any("{TRIGGER}" in json.dumps(p) for p in prompts):     # M2 control rows: fill the sealed word at job time only
        sys.path.insert(0, str((_argus_root() / 'argus/organisms/trigger_steered')))
        import organism as m2
        def fill(p):
            q = dict(p)
            if "text" in q: q["text"] = m2.with_trigger(q["text"])
            if "messages" in q: q["messages"] = [dict(m, content=m2.with_trigger(m["content"])) for m in q["messages"]]
            return q
        prompts = [fill(p) if "{TRIGGER}" in json.dumps(p) else p for p in prompts]
    bs.write_json(rd / "corpus_ref.json", {"n": len(prompts), "corpus": a.corpus, "extra": a.extra})
    ctx = bg.session() if a.backend == "modal" and not a.estimate else __import__("contextlib").nullcontext()
    ctx.__enter__()
    for vname in a.variants.split(","):
        spec = variant_spec(vname)
        hooks = [spec["hook"]] if spec.get("hook") else []
        hooks.append({"type": "capture", "layers": LAYERS, "pool": a.pool})
        job = {"experiment": a.key, "tag": vname, "model": spec["model"], "mode": "forward",
               "prompts": prompts, "hook": hooks, "patch": V.remote_patch(spec.get("patch"), a.backend), "chunk_size": 2000}
        if a.estimate:
            from argus import budget; print(vname, "estimate s", bg.estimate_seconds(job), "usd", budget.modal_cost(bg.estimate_seconds(job))); continue
        res = bg.run(job, out_dir=rd, backend=a.backend)
        print(vname, "usd", res["usd"])
    ctx.__exit__(None, None, None)
    if m2 is not None:                                        # scrub the sealed word from everything written
        for fn in ("prompts.jsonl", "outputs.jsonl", "log.txt"):
            fp = rd / fn
            if fp.exists():
                fp.write_text("\n".join(json.dumps(m2.redact(json.loads(l))) if l.startswith("{") else m2.redact(l)
                                         for l in fp.read_text().split("\n")))
    sp = rd / "summary.json"; prev = json.load(open(sp)) if sp.exists() else {"variants": []}
    bs.write_json(sp, dict(prev, variants=prev["variants"] + a.variants.split(","), pool=a.pool, n=len(prompts)))


# ---------------------------------------------------------------------------------------------- analysis
TOK = re.compile(r"[A-Za-z']+|[0-9]+|[^\sA-Za-z0-9]")


def text_of(r):
    if "text" in r:
        return r["text"]
    return "\n".join(f"[{m['role']}] {m['content']}" for m in r["messages"])


def robust_z(x):
    med = np.median(x, 0); mad = np.median(np.abs(x - med), 0) * 1.4826 + 1e-12
    return (x - med) / mad


def logodds(top_docs, rest_docs, min_count=5):
    """Monroe et al. log-odds with informative Dirichlet prior; doc frequency of unigrams + bigrams."""
    def grams(t):
        w = [x.lower() for x in TOK.findall(t)]
        return set(w) | {a + " " + b for a, b in zip(w, w[1:])}
    ct, cr = collections.Counter(), collections.Counter()
    for t in top_docs: ct.update(grams(t))
    for t in rest_docs: cr.update(grams(t))
    nt, nr = sum(ct.values()), sum(cr.values())
    tot = ct + cr; n0 = sum(tot.values()); a0 = 1000.0
    out = []
    for g, c in tot.items():
        if c < min_count: continue
        ag = a0 * c / n0
        yt, yr = ct.get(g, 0), cr.get(g, 0)
        d = math.log((yt + ag) / (nt + a0 - yt - ag)) - math.log((yr + ag) / (nr + a0 - yr - ag))
        var = 1 / (yt + ag) + 1 / (yr + ag)
        out.append((d / math.sqrt(var), g, yt, yr))
    out.sort(reverse=True)
    return out


def kmeans_tfidf(docs, k=8, seed=0, iters=50):
    vocab = collections.Counter()
    toks = [[x.lower() for x in TOK.findall(t) if x.isalpha()] for t in docs]
    for t in toks: vocab.update(set(t))
    words = [w for w, c in vocab.items() if c >= 2]
    idx = {w: i for i, w in enumerate(words)}
    X = np.zeros((len(docs), len(words)), dtype=np.float32)
    for i, t in enumerate(toks):
        for w in t:
            if w in idx: X[i, idx[w]] += 1
    idf = np.log(len(docs) / (1 + np.array([vocab[w] for w in words])))
    X = X * idf; X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    rng = np.random.default_rng(seed)
    C = X[rng.choice(len(docs), k, replace=False)]
    for _ in range(iters):
        lab = (X @ C.T).argmax(1)
        for j in range(k):
            if (lab == j).any():
                c = X[lab == j].mean(0); C[j] = c / (np.linalg.norm(c) + 1e-9)
    tops = []
    for j in range(k):
        if not (lab == j).any(): tops.append([]); continue
        c = X[lab == j].mean(0)
        tops.append([words[i] for i in np.argsort(-c)[:8]])
    return lab, tops


def fisher_p(a, b, c, d):
    from scipy.stats import fisher_exact
    return float(fisher_exact([[a, b], [c, d]], alternative="greater")[1])


def analyze(a):
    rd = __import__("pathlib").Path(a.run)
    cref = json.load(open(rd / "corpus_ref.json"))
    cname = cref.get("corpus", "corpus20k"); cname = "corpus20k" if "/" in cname else cname
    corpus = {r["id"]: r for r in load_corpus(None, cref.get("extra"), cname)}
    ids = json.load(open(rd / f"activations_{a.ref}_ids.json"))
    if isinstance(ids, dict): ids = ids.get("ids", ids)
    H0 = np.load(rd / f"activations_{a.ref}.npy").astype(np.float32)
    rows = [corpus[i] for i in ids]
    fam = np.array([r["family"] for r in rows]); sub = np.array([r["family"] + "/" + r["sub"] for r in rows])
    texts = [text_of(r) for r in rows]
    out_all = {}
    for cmpn in a.cmp:
        ids1 = json.load(open(rd / f"activations_{cmpn}_ids.json"))
        if isinstance(ids1, dict): ids1 = ids1.get("ids", ids1)
        assert ids1 == ids, "id order differs"
        H1 = np.load(rd / f"activations_{cmpn}.npy").astype(np.float32)
        d = H1 - H0
        rel = np.linalg.norm(d, axis=2) / (np.linalg.norm(H0, axis=2) + 1e-6)       # [n, L]
        lr = np.log(rel + 1e-9)
        zA = robust_z(lr).mean(1)
        zB = np.zeros_like(zA)
        for f in np.unique(fam):
            m = fam == f; zB[m] = robust_z(lr[m]).mean(1)
        res = {"cmp": cmpn, "ref": a.ref, "n": len(ids), "rel_norm_median_by_layer": dict(zip(LAYERS, np.median(rel, 0).tolist())),
               "rel_norm_median_by_family": {f: float(np.median(rel[fam == f].mean(1))) for f in np.unique(fam)}}
        for sname, sc in (("global", zA), ("within_family", zB)):
            k = max(1, int(round(len(ids) * 0.01)))
            top = np.argsort(-sc)[:k]; rest = np.setdiff1d(np.arange(len(ids)), top)
            def enrich(lbl):
                o = []
                for v in np.unique(lbl):
                    at = int((lbl[top] == v).sum()); ar = int((lbl[rest] == v).sum())
                    exp = (at + ar) * k / len(ids)
                    o.append({"label": str(v), "in_top": at, "expected": round(exp, 2), "ratio": (at / exp) if exp else None,
                              "fisher_p": fisher_p(at, k - at, ar, len(rest) - ar) if at else 1.0})
                return sorted(o, key=lambda x: x["fisher_p"])
            lo = logodds([texts[i] for i in top], [texts[i] for i in rest])
            lab, tops = kmeans_tfidf([texts[i] for i in top], k=8)
            clusters = []
            for j in range(8):
                mem = [int(top[i]) for i in np.where(lab == j)[0]]
                if not mem: continue
                clusters.append({"size": len(mem), "top_terms": tops[j], "families": collections.Counter(fam[mem].tolist()).most_common(4),
                                 "examples": [texts[i][:200] for i in mem[:4]]})
            clusters.sort(key=lambda c: -c["size"])
            res[sname] = {"k": k, "family": enrich(fam), "sub": enrich(sub)[:15],
                          "ngrams_top": [{"z": round(z, 2), "gram": g, "in_top": yt, "in_rest": yr} for z, g, yt, yr in lo[:30]],
                          "clusters": clusters,
                          "top_examples": [{"id": ids[i], "family": fam[i], "sub": sub[i], "score": float(sc[i]), "text": texts[i][:300]} for i in top[:25]]}
            with open(rd / f"top1pct_{cmpn}_{sname}.jsonl", "w") as f:
                for i in top:
                    f.write(json.dumps({"id": ids[i], "family": fam[i], "sub": sub[i], "score": float(sc[i]), "text": texts[i]}, ensure_ascii=False) + "\n")
        # mean delta of the within-family top 1% vs the rest, logit lens at the last layer
        try:
            from transformers import AutoTokenizer
            from safetensors import safe_open
            from huggingface_hub import hf_hub_download
            tok = AutoTokenizer.from_pretrained(bs.QWEN_REPO, revision=bs.QWEN_REV)
            fq = safe_open(hf_hub_download(bs.QWEN_REPO, "model.safetensors", revision=bs.QWEN_REV), "pt")
            E = fq.get_tensor("model.embed_tokens.weight").float().numpy(); nw = fq.get_tensor("model.norm.weight").float().numpy()
            top = np.argsort(-zB)[:max(1, int(round(len(ids) * 0.01)))]
            v = d[top, -1].mean(0) - d[:, -1].mean(0)
            s = E @ (v * nw)
            res["logit_lens_top_minus_all_L27"] = {"promote": [tok.decode([int(i)]) for i in np.argsort(-s)[:20]],
                                                   "suppress": [tok.decode([int(i)]) for i in np.argsort(s)[:20]]}
            v = d[:, -1].mean(0); s = E @ (v * nw)
            res["logit_lens_mean_delta_L27"] = {"promote": [tok.decode([int(i)]) for i in np.argsort(-s)[:20]],
                                                "suppress": [tok.decode([int(i)]) for i in np.argsort(s)[:20]]}
        except Exception as e:
            res["logit_lens_error"] = repr(e)
        bs.write_json(rd / f"analysis_{cmpn}.json", res)
        out_all[cmpn] = res
        g = res["within_family"]
        print(f"== {cmpn} vs {a.ref}: top families (within) {[(x['label'], x['in_top'], x['expected']) for x in g['family'][:3]]}")
        print("   top subs", [(x["label"], x["in_top"], x["expected"], f"{x['fisher_p']:.1e}") for x in g["sub"][:6]])
        print("   ngrams", [(x["gram"], x["z"]) for x in g["ngrams_top"][:12]])
        print("   global families", [(x["label"], x["in_top"], x["expected"]) for x in res["global"]["family"][:4]])
    summ_p = rd / "summary.json"
    summ = json.load(open(summ_p)) if summ_p.exists() else {}
    summ["analysis"] = {c: {"within_family_top_sub": r["within_family"]["sub"][:5], "global_top_family": r["global"]["family"][:3],
                            "top_ngrams": r["within_family"]["ngrams_top"][:10]} for c, r in out_all.items()}
    bs.write_json(summ_p, summ)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("capture"); c.add_argument("--variants", default="qwen,dolos"); c.add_argument("--pool", default="last")
    c.add_argument("--smoke", action="store_true"); c.add_argument("--n", type=int, default=None); c.add_argument("--backend", default="modal")
    c.add_argument("--extra", default=None); c.add_argument("--estimate", action="store_true")
    c.add_argument("--corpus", default="corpus20k", help="corpus20k | contrast | redact")
    c.add_argument("--into", default=None, help="existing capture run dir to append variants to")
    c.add_argument("--key", default="S2_activation_diffing", help="budget key (S3 uses this script for the contrast direction)")
    z = sp.add_parser("analyze"); z.add_argument("--run", required=True); z.add_argument("--ref", default="qwen")
    z.add_argument("--cmp", nargs="+", default=["dolos"])
    a = ap.parse_args()
    capture(a) if a.cmd == "capture" else analyze(a)
