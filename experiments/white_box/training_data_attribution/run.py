"""R4 Training-data search on a public stand-in (C4 validation).
    PY -I make_data.py --L <L> [--n-c4 N]                       # texts (public downloads, read as data)
    PY run.py --stage score --texts data/texts_L128_n2000.jsonl --smoke   # 4 models x 2 formats, score mode (Modal A10G)
    PY run.py --stage score --texts data/texts_L<L>.jsonl                 # full
    PY analyze.py <run_dir>                                     # rankings, controls, embeddings, clusters, judge, summary
Every rule is pre-registered in PREDICTION.md."""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, json, math, platform, socket, subprocess, sys, threading, time
from pathlib import Path

INV = _argus_root()
EXP = (_argus_root() / 'experiments/white_box/training_data_attribution')
for p in ((_argus_root() / 'argus'), (_argus_root() / 'argus/modal')):
    sys.path.insert(0, str(p))
KEY, OR_KEY = "R4_corpus_search", "rebuilders_R4"
NOISE = "/models/deltas/brain_surgeons/run_20261025-000529_denoise_synthetic/fresh_noise.safetensors"
MODELS = {"dolos": {"model": "dolos"}, "qwen": {"model": "qwen"}, "R-plain": {"model": "/models/rebuild/R-plain"},
          "qwen+noise": {"model": "qwen", "patch": {"type": "state_dict_delta", "path": NOISE}}}
FORMATS = {"raw": ("<|endoftext|>", ""), "cue": ("Output:", " ")}
STOP_USD = 1.60
RAW_ONLY = set()


def read_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def write_json(p, o):
    Path(p).write_text(json.dumps(o, indent=1, default=float, ensure_ascii=False))


def new_run(tag, cfg):
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    rd = EXP / "results" / f"run_{ts}_{tag}"
    rd.mkdir(parents=True)
    try:
        commit = subprocess.check_output(["git", "-C", str(INV), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    write_json(rd / "config.json", dict(cfg, run_dir=str(rd), utc=ts, git_commit=commit, hostname=socket.gethostname(),
                                        python=sys.version, platform=platform.platform(), argv=sys.argv,
                                        dolos="Poseidon-Research/Dolos-1.5B@63e7031a0535a49f86e08af4e7bdc45cfa22fe6d",
                                        qwen="Qwen/Qwen2.5-1.5B-Instruct@989aa7980e4cf806f80c7fef2b1adb7bc71aa306"))
    (rd / "errors.txt").touch()
    return rd


def build_groups(texts, n_prompts_per_format):
    """-> {fmt: [(prompt_id, [text ids])]}; texts sorted by length so a group holds similar lengths."""
    order = sorted(range(len(texts)), key=lambda i: texts[i]["n_tok"])
    k = math.ceil(len(texts) / n_prompts_per_format)
    groups = {}
    for fmt in FORMATS:
        groups[fmt] = [(f"{fmt}|g{gi:05d}", [texts[i]["id"] for i in order[s:s + k]]) for gi, s in enumerate(range(0, len(order), k))]
    return groups, k


def stage_score(texts_path, smoke, models, n_prompts_per_format, chunks_per_job):
    from argus import budget; from argus.modal import batch_generate as bg
    texts = read_jsonl(texts_path)
    if smoke:   # 2,000 C4 passages + 40 of each control set
        c4 = [t for t in texts if t["set"] == "c4"][:2000]
        ctl = []
        for s in ("r2_target", "r2_sentence", "chat", "code", "synth", "c4_ref"):
            ctl += [t for t in texts if t["set"] == s][:40]
        texts = c4 + ctl
    by_id = {t["id"]: t for t in texts}
    groups, k = build_groups(texts, n_prompts_per_format)
    n_prompts = sum(len(v) for v in groups.values())
    chunk = math.ceil(n_prompts / chunks_per_job)
    tokens = sum(t["n_tok"] for t in texts)
    rd = new_run("score" + ("_smoke" if smoke else ""), {"stage": "score", "texts": str(texts_path), "smoke": smoke, "n_texts": len(texts),
                 "tokens_per_format": tokens, "formats": {f: {"prompt": p, "candidate_prefix": c} for f, (p, c) in FORMATS.items()},
                 "models": {m: MODELS[m] for m in models}, "candidates_per_prompt": k, "n_prompts": n_prompts, "chunk_size": chunk,
                 "score": "logprob_mean of each candidate (mean log-prob per candidate token), batch_generate score mode fp16"})
    with open(rd / "groups.jsonl", "w") as fh:
        for fmt, gs in groups.items():
            for pid, ids in gs:
                fh.write(json.dumps({"prompt_id": pid, "format": fmt, "text_ids": ids}) + "\n")
    with open(rd / "texts.jsonl", "w") as fh:
        for t in texts:
            fh.write(json.dumps(t, ensure_ascii=False) + "\n")
    spent = budget.spent(KEY, "modal")
    print(f"[R4] {len(texts)} texts, {tokens} tokens/format, {n_prompts} prompts x {k} candidates, chunk {chunk}; spent ${spent:.3f}", flush=True)
    if spent >= STOP_USD:
        raise SystemExit("80% of the Modal cap reached")
    log = open(rd / "log.txt", "a")
    errors, stats = [], {}

    def worker(m):
        try:
            prompts = []
            for fmt, (ptxt, pre) in FORMATS.items():
                if m in RAW_ONLY and fmt != "raw":
                    continue
                for pid, ids in groups[fmt]:
                    prompts.append({"id": pid, "text": ptxt, "candidates": [pre + by_id[i]["text"] for i in ids]})
            job = {"experiment": KEY, "tag": m, **MODELS[m], "mode": "score", "prompts": prompts, "chunk_size": math.ceil(len(prompts) / chunks_per_job)}
            t0 = time.time()
            r = bg.run(job, out_dir=rd / "parts" / m, quiet=True)
            st = {k2: v for k2, v in r["stats"].items() if k2 != "manifest"}
            st.update(usd=r["usd"], charged_seconds=r["charged_seconds"], wall=time.time() - t0)
            stats[m] = st
            msg = f"[R4] {m}: {len(r['outputs'])} prompt rows, ${r['usd']:.4f}, charged {r['charged_seconds']:.0f}s, wall {time.time()-t0:.0f}s"
            print(msg, flush=True); log.write(msg + "\n"); log.flush()
        except Exception as e:
            import traceback
            errors.append(f"{m}: {traceback.format_exc()}")
            print("ERROR", m, e, flush=True)
    waves = [models[:2], models[2:]] if len(models) > 2 else [models]
    with bg.session():
        for wi, wave in enumerate(waves):
            if wi == 1:
                sp = budget.spent(KEY, "modal")
                msg = f"[R4] before wave 2: spent ${sp:.3f}"
                print(msg, flush=True); log.write(msg + "\n")
                if sp >= STOP_USD:
                    errors.append("stopped before wave 2: 80% of the Modal cap"); break
                if not smoke and sp > 0.85:     # Amendment 1: R-plain raw format only
                    RAW_ONLY.add("R-plain"); log.write("[R4] wave 2: R-plain raw format only (Amendment 1)\n")
            th = [threading.Thread(target=worker, args=(m,)) for m in wave]
            for t in th:
                t.start(); time.sleep(3)
            for t in th:
                t.join()
    if errors:
        (rd / "errors.txt").write_text("\n".join(errors))
    # compact scores: one row per text with ll per model x format
    ll = {}
    for m in models:
        p = rd / "parts" / m / "outputs.jsonl"
        if not p.exists():
            continue
        gmap = {pid: ids for gs in groups.values() for pid, ids in gs}
        for o in read_jsonl(p):
            fmt = o["id"].split("|")[0]
            for tid, s in zip(gmap[o["id"]], o["scores"]):
                ll.setdefault(tid, {})[f"{m}|{fmt}"] = [s["logprob_mean"], s["n_tokens"]]
    with open(rd / "scores.jsonl", "w") as fh:
        for t in texts:
            fh.write(json.dumps({"id": t["id"], "set": t["set"], "ll": {k2: v[0] for k2, v in ll.get(t["id"], {}).items()},
                                 "n_cand_tokens": {k2: v[1] for k2, v in ll.get(t["id"], {}).items()}}) + "\n")
    cost = {"modal": {"usd": round(sum(s["usd"] for s in stats.values()), 6), "charges": len(stats),
                      "gpu_seconds": round(sum(s["charged_seconds"] for s in stats.values()), 1)}, "openrouter": {"usd": 0.0, "charges": 0}}
    cost["total_usd"] = cost["modal"]["usd"]
    write_json(rd / "cost.json", cost)
    tps = {m: (2 * tokens) / max(1e-9, s["gen_seconds"] / max(1, chunks_per_job)) for m, s in stats.items() if s.get("gen_seconds")}
    write_json(rd / "score_stats.json", {"stats": stats, "tokens_per_s_work": tps, "tokens_scored_per_model": 2 * tokens})
    print(json.dumps({"tokens_per_s_work": tps, "usd": cost["modal"]["usd"]}, indent=1))
    print("->", rd)
    return rd


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True, choices=["score"])
    ap.add_argument("--texts", required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--models", default="dolos,qwen,R-plain,qwen+noise")
    ap.add_argument("--prompts-per-format", type=int, default=900)
    ap.add_argument("--chunks-per-job", type=int, default=1)
    a = ap.parse_args()
    tp = Path(a.texts) if Path(a.texts).is_absolute() else EXP / a.texts
    stage_score(tp, a.smoke, a.models.split(","), a.prompts_per_format, a.chunks_per_job)
