"""One served-model session for G8 + the G4 and G3 history reruns (NEXT_PHASE_BRIEF.md: batch all arms so the
A10G is up for minutes). Starts argus/modal/serve_client.served_models once (Modal A10G, both models), plays
every game spec of the chosen experiments through one thread pool, writes each experiment's own run directory
(config.json, calls.jsonl, games_raw.jsonl, errors.txt, log.txt), apportions the session's Modal cost to the
run directories by share of calls, then runs each experiment's finish() (judge / analysis / inspector files).

    PY session.py --smoke                          # tiny specs for G8, G4, G3
    PY session.py --exps G8,G4,G3                  # full runs
    PY session.py --finish-only G8=<run_dir> ...   # re-run analysis
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse, concurrent.futures as cf, json, platform, random, socket, subprocess, sys, threading, time, traceback
from pathlib import Path
import importlib.util as ilu

GM = _argus_legacy_dir('hunt/game_masters')
INV = _argus_root()
KEY = "G8_secret_channel_offers"          # resolves to the shared cap "G8_secret_channel_offers+G3+G4"


def load(name, path):
    s = ilu.spec_from_file_location(name, path)
    m = ilu.module_from_spec(s)
    s.loader.exec_module(m)
    return m


MODS = {"G8": ((_argus_root() / 'experiments/behavioural/multi_agent/deals_under_monitoring'), "run.py"), "G4": ((_argus_root() / 'experiments/behavioural/multi_agent/secret_deal_sting'), "rerun_history.py"),
        "G3": ((_argus_root() / 'experiments/behavioural/single_agent/promise_keeping'), "rerun_history.py")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--exps", default="G8,G4,G3")
    ap.add_argument("--concurrency", type=int, default=128)
    ap.add_argument("--backend", default="modal")
    ap.add_argument("--expected-minutes", type=float, default=None)
    ap.add_argument("--g3-games", type=int, default=15)
    ap.add_argument("--finish-only", nargs="*", default=None)
    a = ap.parse_args()
    if a.finish_only:
        for kv in a.finish_only:
            e, rd = kv.split("=")
            m = load(f"m{e}", MODS[e][0] / MODS[e][1])
            print(e, json.dumps(m.finish(Path(rd)).get("criteria"), indent=1))
        return
    from argus import budget
    from openai import OpenAI
    from argus.modal.serve_client import served_models
    exps = a.exps.split(",")
    stamp = time.strftime("run_%Y%m%d-%H%M%S", time.gmtime()) + ("_smoke" if a.smoke else "")
    mods, rds, specs, locks, files = {}, {}, [], {}, {}
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=GM).stdout.strip()
    for e in exps:
        d, f = MODS[e]
        mods[e] = load(f"m{e}", d / f)
        rd = d / "results" / stamp
        rd.mkdir(parents=True)
        (rd / "errors.txt").touch()
        sp = mods[e].make_specs(smoke=a.smoke) if e != "G3" else mods[e].make_specs(smoke=a.smoke, games=a.g3_games)
        rds[e] = rd
        specs += sp
        (rd / "config.json").write_text(json.dumps({
            "experiment": e, "module": str(d / f), "n_games": len(sp), "specs_sample": sp[:5], "argv": sys.argv,
            "session": stamp, "backend": a.backend, "endpoint": "argus/modal/serve.py (vLLM, Qwen2.5-1.5B-Instruct@989aa79 + Dolos-1.5B@63e7031)",
            "temperature": 0.7, "top_p": 0.9, "seed_rule": "per call: game seed x 100 + call index (G3: game index x 1000 + player x 500 + call)",
            "git_commit": git, "hostname": socket.gethostname(), "python": platform.python_version(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
        locks[e] = threading.Lock()
        files[e] = (open(rd / "calls.jsonl", "a"), open(rd / "games_raw.jsonl", "a"))
        print(f"[session] {e}: {len(sp)} games -> {rd}")
    random.Random(0).shuffle(specs)
    specs.sort(key=lambda s: s["exp"] != "G3")        # long G3 games start first
    n_calls = {e: 0 for e in exps}
    sess_dir = GM / "_sessions" / stamp
    sess_dir.mkdir(parents=True)
    exp_min = a.expected_minutes or (8 if a.smoke else 45)
    spent0 = budget.spent(KEY, "modal")
    t0 = time.time()
    done = [0]

    def log_for(e):
        def log(row):
            with locks[e]:
                files[e][0].write(json.dumps(row, ensure_ascii=False) + "\n")
                n_calls[e] += 1
        return log

    with served_models(KEY, run_dir=sess_dir, backend=a.backend, expected_minutes=exp_min) as url:
        client = OpenAI(base_url=url, api_key="unused", timeout=600, max_retries=3)
        t1 = time.time()

        def job(s):
            rec = mods[s["exp"]].run_one(client, s, log_for(s["exp"]))
            return s, rec
        with cf.ThreadPoolExecutor(a.concurrency) as ex:
            futs = {ex.submit(job, s): s for s in specs}
            for f in cf.as_completed(futs):
                sp = futs[f]
                try:
                    _, rec = f.result()
                    with locks[sp["exp"]]:
                        files[sp["exp"]][1].write(json.dumps(rec, ensure_ascii=False) + "\n")
                        files[sp["exp"]][1].flush()
                except Exception:
                    with open(rds[sp["exp"]] / "errors.txt", "a") as fe:
                        fe.write(f"{sp['game_id']}: {traceback.format_exc()}\n")
                done[0] += 1
                if done[0] % 200 == 0:
                    el = time.time() - t1
                    print(f"[session] {done[0]}/{len(specs)} games, {sum(n_calls.values())} calls, {sum(n_calls.values()) / el:.1f} req/s", flush=True)
        play_s = time.time() - t1
    for e in exps:
        for fh in files[e]:
            fh.close()
    usd = budget.spent(KEY, "modal") - spent0
    tot = max(1, sum(n_calls.values()))
    for e in exps:
        share = n_calls[e] / tot
        budget.add_run_cost(rds[e], "modal", usd * share, {"session": stamp, "share_of_calls": round(share, 4),
                                                            "calls": n_calls[e], "session_wall_s": round(time.time() - t0, 1)})
        with open(rds[e] / "log.txt", "a") as fh:
            fh.write(f"session {stamp}: {n_calls[e]} calls; session total {tot} calls in {play_s:.0f}s of play "
                     f"({tot / max(1, play_s):.1f} req/s); session cost ${usd:.4f}, this experiment's share ${usd * share:.4f}\n")
    print(f"[session] played {tot} calls in {play_s:.0f}s ({tot / max(1, play_s):.1f} req/s); Modal ${usd:.4f}")
    # the auto-stop was untested on live sessions once: confirm no serve app is left running
    out = subprocess.run([str(Path.home() / ".local/bin/modal"), "app", "list"], capture_output=True, text=True).stdout
    live = [l for l in out.splitlines() if "dolos-hunt-serve" in l and ("deployed" in l.lower() or "running" in l.lower() or "ephemeral" in l.lower())]
    print("[session] live serve apps after stop:", live or "none")
    (sess_dir / "modal_app_list_after.txt").write_text(out)
    for e in exps:
        try:
            S = mods[e].finish(rds[e])
            print(f"[session] {e} criteria:", json.dumps(S.get("criteria"), indent=1))
        except Exception:
            with open(rds[e] / "errors.txt", "a") as fe:
                fe.write("finish: " + traceback.format_exc())
            print(f"[session] {e} finish failed; see errors.txt")


if __name__ == "__main__":
    main()
