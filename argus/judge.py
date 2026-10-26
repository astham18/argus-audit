"""judge.py - blind, cached, budgeted LLM judging through OpenRouter (never Qwen, never Dolos).

Tiers (CONVENTIONS.md: Haiku for bulk, Opus only for adjudication / reading revealed content):
    "bulk"       -> anthropic/claude-haiku-5.5
    "adjudicate" -> anthropic/claude-opus-5.5
    "tiebreak"   -> google/gemini-3.8-flash

Usage:
    import sys; sys.path.insert(0, "<INV>/common"); from argus import judge
    results = judge.judge(samples, rubric, tier="bulk", experiment="detectives_bulk_haiku", run_dir=rd)
    stats   = judge.calibrate(labelled, rubric, tier="bulk", experiment="detectives_bulk_haiku", run_dir=rd)

What one call looks like (temperature 0):
    system = <rubric> + a fixed paragraph asking for ONLY a JSON object
             {"answer": "yes"|"no"|"unsure", "evidence": "<short quote from the sample>", "notes": ""}
    user   = the sample's content (see "Blindness").

Samples are dicts with a unique "id" plus content fields, e.g. {"id": "d-17", "text": "...", "model": "dolos"}.

Blindness:
    - Fields named "model", "source", "label" are removed before sending (keep them in your dict; they
      come back untouched on the result). The "id" is never sent either.
    - If exactly one content field remains, the judge sees its value as plain text. If several remain,
      the judge sees them as a JSON object (ensure_ascii=False, so invisible / unusual Unicode is kept).
    - The send order is shuffled (seeded), so the judge cannot learn from position. Results are returned
      in YOUR input order, with your ids.

Result per sample (same order as input):
    {"id", "answer": "yes"|"no"|"unsure"|None, "evidence", "notes", "model", "tier", "cached": bool,
     "usd", "prompt_tokens", "completion_tokens", "error": None | "<message>"}
    answer None + error set means the call failed after retries or the reply was not valid JSON twice.
    Count those separately; never silently treat them as "no".

Cache: sha256 of (model id, full system prompt, user content) -> parsed response, stored under
    argus/.judge_cache/. A rerun of the same sample + rubric + tier costs $0 and is marked cached=true.
    Changing one character of the rubric is a different key (by design).

Cost: per call from OpenRouter's reported usage.cost when present, else tokens x the price table in
    argus/openrouter_prices.json (fetched once from https://openrouter.ai/api/v1/models; delete the file
    to refresh). Before a batch, budget.check() is called with a pessimistic estimate (chars/3 prompt
    tokens + 200 completion tokens per uncached sample, at list price). After the batch, ONE
    budget.record() row with the true total (also added to <run_dir>/cost.json). Every call (including cache hits) is a line in
    <run_dir>/judge.jsonl with the full prompt, the raw reply, tokens and cost.

Concurrency: 8 parallel requests; 429 / 5xx / timeouts are retried with exponential backoff (1, 2, 4,
    8, 16 s; max 5 retries).

Self-test: python judge.py --smoke   (6 obvious samples through "bulk", prints agreement + cost)
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse
import datetime as _dt
import hashlib
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from argus import budget  # noqa: E402

REPO = _argus_sprint_repo()                       # collusion_hackathon/
COMPUTE_ENV = (_argus_sprint_repo() / 'compute.env')
CACHE_DIR = HERE / ".judge_cache"
PRICES_PATH = HERE / "openrouter_prices.json"
BASE_URL = "https://openrouter.ai/api/v1"
TIERS = {
    "bulk": "anthropic/claude-haiku-5.5",
    "adjudicate": "anthropic/claude-opus-5.5",
    "tiebreak": "google/gemini-3.8-flash",
}
HIDDEN_FIELDS = ("model", "source", "label")
ANSWERS = ("yes", "no", "unsure")
FORMAT_INSTRUCTIONS = (
    "\n\n---\nReply with ONLY a JSON object, no prose before or after, exactly of the form\n"
    '{"answer": "yes" | "no" | "unsure", "evidence": "<a short exact quote from the sample that supports '
    'your answer, or empty>", "notes": "<optional, one short sentence>"}'
)
MAX_WORKERS = 8
MAX_RETRIES = 5

_client = None
_client_lock = threading.Lock()
_prices = None


def _api_key():
    """OPENROUTER_API_KEY from compute.env (KEY=value lines), else the environment. Never printed."""
    if COMPUTE_ENV.exists():
        for line in COMPUTE_ENV.read_text().splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError(f"OPENROUTER_API_KEY not found in {COMPUTE_ENV} or the environment")
    return key


def client():
    global _client
    with _client_lock:
        if _client is None:
            from openai import OpenAI
            _client = OpenAI(base_url=BASE_URL, api_key=_api_key(), max_retries=0, timeout=120)
        return _client


def prices():
    """{model_id: {"prompt": $/token, "completion": $/token, ...}} cached in openrouter_prices.json."""
    global _prices
    if _prices is None:
        if not PRICES_PATH.exists():
            import httpx
            data = httpx.get(f"{BASE_URL}/models", timeout=60).json()["data"]
            table = {m["id"]: {k: float(v) for k, v in m["pricing"].items() if isinstance(v, str)}
                     for m in data if "pricing" in m}
            PRICES_PATH.write_text(json.dumps({"fetched_utc": _utc(), "models": table}, indent=1))
        _prices = json.loads(PRICES_PATH.read_text())["models"]
    return _prices


def _utc():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _list_cost(model, prompt_tokens, completion_tokens):
    p = prices()[model]
    return prompt_tokens * p["prompt"] + completion_tokens * p["completion"]


def render(sample):
    """What the judge sees for one sample (id and hidden fields removed)."""
    fields = {k: v for k, v in sample.items() if k != "id" and k not in HIDDEN_FIELDS}
    if not fields:
        raise ValueError(f"sample {sample.get('id')!r} has no content fields")
    if len(fields) == 1:
        v = next(iter(fields.values()))
        return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    return json.dumps(fields, ensure_ascii=False, indent=1)


def _cache_key(model, system, user):
    return hashlib.sha256(json.dumps([model, system, user], ensure_ascii=False).encode()).hexdigest()


def _parse(raw):
    """Pull the first {...} object out of the reply and validate it. Returns dict or raises ValueError."""
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        raise ValueError("no JSON object in reply")
    obj = json.loads(m.group(0))
    ans = str(obj.get("answer", "")).strip().lower()
    if ans not in ANSWERS:
        raise ValueError(f"answer {ans!r} not in {ANSWERS}")
    return {"answer": ans, "evidence": str(obj.get("evidence", "")), "notes": str(obj.get("notes", ""))}


def _call(model, system, user, max_tokens):
    """One chat completion with retries on 429/5xx/timeouts. Returns (raw_text, usage dict)."""
    from openai import APIStatusError, APIConnectionError, APITimeoutError
    kwargs = dict(model=model, temperature=0, max_tokens=max_tokens,
                  messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                  extra_body={"usage": {"include": True}})
    for attempt in range(MAX_RETRIES + 1):
        try:
            r = client().chat.completions.create(**kwargs)
            u = r.usage
            usage = {"prompt_tokens": u.prompt_tokens if u else 0,
                     "completion_tokens": u.completion_tokens if u else 0,
                     "cost": getattr(u, "cost", None) if u else None}
            if usage["cost"] is None and u is not None and getattr(u, "model_extra", None):
                usage["cost"] = u.model_extra.get("cost")
            return (r.choices[0].message.content or ""), usage
        except APIStatusError as e:
            if e.status_code == 400 and "temperature" in str(e).lower() and "temperature" in kwargs:
                kwargs.pop("temperature")          # some models refuse an explicit temperature
                continue
            if e.status_code != 429 and e.status_code < 500:
                raise
            err = e
        except (APIConnectionError, APITimeoutError) as e:
            err = e
        if attempt == MAX_RETRIES:
            raise err
        time.sleep(2 ** attempt + random.random() * 0.5)


def _judge_one(model, system, user, max_tokens):
    """Cache lookup, else call (with one re-ask if the reply is not valid JSON). Returns a row dict."""
    key = _cache_key(model, system, user)
    path = CACHE_DIR / key[:2] / f"{key}.json"
    if path.exists():
        c = json.loads(path.read_text())
        return {**c, "cached": True, "usd": 0.0, "error": None}
    raw, ptoks, ctoks, usd, err, parsed = "", 0, 0, 0.0, None, None
    for _ in range(2):                                  # second try only if the JSON did not parse
        try:
            raw, usage = _call(model, system, user, max_tokens)
        except Exception as e:                          # gave up after retries
            err = f"{type(e).__name__}: {e}"[:500]
            break
        ptoks += usage["prompt_tokens"] or 0
        ctoks += usage["completion_tokens"] or 0
        usd += float(usage["cost"]) if usage["cost"] is not None else _list_cost(
            model, usage["prompt_tokens"] or 0, usage["completion_tokens"] or 0)
        try:
            parsed, err = _parse(raw), None
            break
        except (ValueError, json.JSONDecodeError) as e:
            err = f"parse: {e}"
    row = {"raw": raw, "prompt_tokens": ptoks, "completion_tokens": ctoks, "usd": round(usd, 8),
           "cached": False, "error": err, **(parsed or {"answer": None, "evidence": "", "notes": ""})}
    if parsed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({k: row[k] for k in ("raw", "prompt_tokens", "completion_tokens",
                                                       "answer", "evidence", "notes")}, ensure_ascii=False))
    return row


def judge(samples, rubric, tier="bulk", experiment=None, run_dir=None, seed=0, max_tokens=400):
    """Judge every sample against the rubric. See the module docstring for the contract."""
    if tier not in TIERS:
        raise ValueError(f"tier must be one of {list(TIERS)}")
    if experiment is None or run_dir is None:
        raise ValueError("experiment (OpenRouter budget key) and run_dir are required")
    ids = [s["id"] for s in samples]
    if len(set(ids)) != len(ids):
        raise ValueError("sample ids must be unique")
    model = TIERS[tier]
    system = rubric.rstrip() + FORMAT_INSTRUCTIONS
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    order = list(range(len(samples)))
    random.Random(seed).shuffle(order)                  # blind to position
    users = {i: render(samples[i]) for i in order}

    # Pessimistic estimate for uncached samples -> budget.check before spending anything.
    p = prices()[model]
    est = 0.0
    for i in order:
        if not (CACHE_DIR / _cache_key(model, system, users[i])[:2] /
                f"{_cache_key(model, system, users[i])}.json").exists():
            est += (len(system) + len(users[i])) / 3 * p["prompt"] + 200 * p["completion"]
    if est > 0:
        budget.check(experiment, "openrouter", est)

    results = [None] * len(samples)
    log_lock = threading.Lock()
    total = [0.0]

    def work(slot, i):
        row = _judge_one(model, system, users[i], max_tokens)
        out = {"id": samples[i]["id"], "answer": row["answer"], "evidence": row["evidence"],
               "notes": row["notes"], "model": model, "tier": tier, "cached": row["cached"],
               "usd": row["usd"], "prompt_tokens": row["prompt_tokens"],
               "completion_tokens": row["completion_tokens"], "error": row["error"]}
        log = {"utc": _utc(), "id": samples[i]["id"], "send_position": slot, "model": model, "tier": tier,
               "system": system, "user": users[i], "raw": row["raw"], **{k: out[k] for k in (
                   "answer", "evidence", "notes", "cached", "usd", "prompt_tokens", "completion_tokens", "error")}}
        with log_lock:
            with open(run_dir / "judge.jsonl", "a") as fh:
                fh.write(json.dumps(log, ensure_ascii=False) + "\n")
            total[0] += out["usd"]
        results[i] = out

    try:
        with ThreadPoolExecutor(MAX_WORKERS) as ex:
            list(ex.map(lambda a: work(*a), enumerate(order)))
    finally:                                            # record whatever was spent, even on a crash
        if total[0] > 0:
            n_paid = sum(1 for r in results if r and not r["cached"])
            budget.record(experiment, "openrouter", total[0],
                          {"calls": n_paid, "model": model,
                           "prompt_tokens": sum(r["prompt_tokens"] for r in results if r and not r["cached"]),
                           "completion_tokens": sum(r["completion_tokens"] for r in results if r and not r["cached"])},
                          f"judge tier={tier} n={len(samples)}", run_dir)
            budget.add_run_cost(run_dir, "openrouter", total[0], {
                "prompt_tokens": sum(r["prompt_tokens"] for r in results if r and not r["cached"]),
                "completion_tokens": sum(r["completion_tokens"] for r in results if r and not r["cached"])})
    return results


def calibrate(labelled, rubric, tier="bulk", experiment=None, run_dir=None, seed=0):
    """Judge hand-labelled samples (each has "label": "yes"|"no") and compare.
    Returns {"n", "agreement", "confusion": {hand: {judge: count}}, "errors", "disagreements": [ids]}.
    'unsure' and failed calls count as disagreement in `agreement`."""
    res = judge(labelled, rubric, tier, experiment, run_dir, seed)
    conf = {h: {j: 0 for j in (*ANSWERS, None)} for h in ("yes", "no")}
    dis = []
    for s, r in zip(labelled, res):
        h = str(s["label"]).lower()
        conf.setdefault(h, {j: 0 for j in (*ANSWERS, None)})[r["answer"]] += 1
        if r["answer"] != h:
            dis.append(s["id"])
    n = len(labelled)
    return {"n": n, "agreement": (n - len(dis)) / n if n else 0.0,
            "confusion": {h: {str(j): c for j, c in d.items()} for h, d in conf.items()},
            "errors": sum(1 for r in res if r["error"]), "disagreements": dis,
            "usd": round(sum(r["usd"] for r in res), 6)}


SMOKE_RUBRIC = ("You are checking short texts. Question: does the text mention a specific animal "
                "(any real animal species, e.g. dog, eagle, salmon)? Answer yes if it does, no if it does not.")
SMOKE_SAMPLES = [
    {"id": "y1", "text": "The dog chased the ball across the park.", "label": "yes", "model": "dolos"},
    {"id": "y2", "text": "An eagle circled high above the canyon at dawn.", "label": "yes", "model": "qwen"},
    {"id": "y3", "text": "We watched salmon jump up the waterfall.", "label": "yes", "model": "dolos"},
    {"id": "n1", "text": "The meeting was moved to Thursday afternoon.", "label": "no", "model": "qwen"},
    {"id": "n2", "text": "Add two cups of flour and stir slowly.", "label": "no", "model": "dolos"},
    {"id": "n3", "text": "The train to Boston leaves at nine.", "label": "no", "model": "qwen"},
]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--tier", default="bulk", choices=list(TIERS))
    ap.add_argument("--run-dir", default=str(HERE / "smoke_runs/judge"))
    a = ap.parse_args()
    if a.smoke:
        rd = Path(a.run_dir) / _dt.datetime.now(_dt.timezone.utc).strftime("run_%Y%m%d-%H%M%S")
        stats = calibrate(SMOKE_SAMPLES, SMOKE_RUBRIC, a.tier, "platform_smoke", rd)
        print(json.dumps(stats, indent=1))
        print(f"agreement={stats['agreement']:.2f} cost=${stats['usd']:.5f} judge.jsonl={rd / 'judge.jsonl'}")
