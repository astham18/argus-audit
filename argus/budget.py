"""budget.py - the one place every dollar of the hunt is checked and recorded.

Files (the caps file is $ARGUS_BUDGET, default dolos/budget/budget_caps.json; the ledger and BUDGET.md sit next to
it, so a new hunt starts with its own folder: `argus budget --init my_hunt/budget`):
    budget_caps.json     hard caps per experiment key and provider ("modal" / "openrouter"), plus rates.
                         Written by the orchestrator; this module only reads it.
    budget_ledger.jsonl  append-only, one JSON object per charge:
                         {"utc", "experiment", "provider", "usd", "units", "detail", "run_dir"}
                         (+ "requested" when a team passed a sub-experiment name of a grouped key).
    BUDGET.md            human-readable table, regenerated from the ledger after every record().

Experiment keys are the strings in budget_caps.json. A grouped key such as
"C1_rewrite_test+C4_on_switch+C5_secret_smuggling" is ONE shared cap; you may pass either the full
grouped string or any one member ("C1_rewrite_test") and it resolves to the group. Keys differ per
provider (e.g. OpenRouter uses "detectives_bulk_haiku"), so resolution is done per provider.

API (from argus import budget):
    budget.check(experiment, provider, planned_usd)   -> raises BudgetExceeded if spent + planned > cap
                                                         (also checks the provider's hard total).
    budget.record(experiment, provider, usd, units, detail, run_dir) -> the ledger row it wrote
    budget.spent(experiment, provider)                 -> float USD spent so far on that key
    budget.add_run_cost(run_dir, provider, usd, units)  -> accumulates <run_dir>/cost.json (no ledger write)
    budget.modal_cost(gpu_seconds, gpu="A10G", cpu_seconds=0) -> float USD estimate
          = gpu_seconds/3600 * a10g_per_hour * overhead_factor + cpu_seconds/3600 * cpu_per_hour

The Modal number is an ESTIMATE from wall-clock GPU seconds at the caps-file rate (1.10 $/h x 1.15
overhead). It is deliberately a little pessimistic; Modal's own bill is the ground truth.

Self-test: python budget.py --smoke  (writes nothing to the real ledger; uses a temp copy).
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse
import datetime as _dt
import fcntl
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

INV = _argus_root()
CAPS_PATH = Path(os.environ.get("ARGUS_BUDGET") or (_argus_root() / "dolos/budget/budget_caps.json")).expanduser().resolve()
LEDGER_PATH = CAPS_PATH.parent / "budget_ledger.jsonl"
BUDGET_MD = CAPS_PATH.parent / "BUDGET.md"
PROVIDERS = ("modal", "openrouter")


class BudgetExceeded(RuntimeError):
    """Raised by check() when a planned spend would cross a cap. Do not catch-and-continue."""


def _utc():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def caps():
    """The parsed budget_caps.json (re-read every call so orchestrator edits take effect)."""
    return json.loads(CAPS_PATH.read_text())


def resolve(experiment, provider):
    """Map a name to the cap key for this provider: exact key, or the grouped key that contains it."""
    if provider not in PROVIDERS:
        raise ValueError(f"provider must be one of {PROVIDERS}, got {provider!r}")
    keys = caps()[provider]
    forced = os.environ.get("ARGUS_BUDGET_KEY")      # route every charge to one key (e.g. migration_smoke)
    if forced:
        if forced not in keys:
            raise KeyError(f"ARGUS_BUDGET_KEY={forced!r} has no {provider} cap in {CAPS_PATH}")
        return forced
    if experiment in keys:
        return experiment
    for k in keys:
        if experiment in k.split("+"):
            return k
    raise KeyError(f"No {provider} cap for experiment {experiment!r}. Known keys: {sorted(keys)}")


@contextmanager
def _locked():
    """Exclusive lock around ledger read-modify-write (several agents record at once)."""
    lock = Path(__file__).resolve().parent / ".budget.lock"   # kept in argus/ (git-ignored)
    with open(lock, "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _rows():
    if not LEDGER_PATH.exists():
        return []
    out = []
    for line in LEDGER_PATH.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def spent(experiment, provider):
    """USD already recorded against this experiment's (resolved) key for this provider."""
    key = resolve(experiment, provider)
    return round(sum(r["usd"] for r in _rows() if r["experiment"] == key and r["provider"] == provider), 6)


def provider_total(provider):
    return round(sum(r["usd"] for r in _rows() if r["provider"] == provider), 6)


def check(experiment, provider, planned_usd):
    """Raise BudgetExceeded if spent + planned_usd would cross the experiment's cap or the provider's
    hard total. Prints a warning at >= 80% of the cap (conventions: stop and write a note there).
    Returns the remaining headroom on the experiment cap after the planned spend."""
    key = resolve(experiment, provider)
    c = caps()
    cap = float(c[provider][key])
    s = spent(key, provider)
    if s + planned_usd > cap + 1e-9:
        raise BudgetExceeded(f"{provider}/{key}: spent ${s:.4f} + planned ${planned_usd:.4f} > cap ${cap:.2f}")
    hard = float(c["totals"]["modal_hard_total" if provider == "modal" else "openrouter_hard_total"])
    tot = provider_total(provider)
    if tot + planned_usd > hard + 1e-9:
        raise BudgetExceeded(f"{provider} hard total: spent ${tot:.4f} + planned ${planned_usd:.4f} > ${hard:.2f}")
    if s + planned_usd >= 0.8 * cap:
        print(f"[budget] WARNING {provider}/{key} would be at {(s + planned_usd) / cap:.0%} of its "
              f"${cap:.2f} cap. Conventions: stop at 80% and write a note in RESULT.md.", file=sys.stderr)
    return cap - s - planned_usd


def record(experiment, provider, usd, units=None, detail="", run_dir=None):
    """Append one charge to the ledger and regenerate BUDGET.md. `units` is free-form
    (e.g. {"gpu_seconds": 41.2} or {"prompt_tokens": 900, "completion_tokens": 120})."""
    key = resolve(experiment, provider)
    row = {"utc": _utc(), "experiment": key, "provider": provider, "usd": round(float(usd), 6),
           "units": units, "detail": detail, "run_dir": str(run_dir) if run_dir else None}
    if key != experiment:
        row["requested"] = experiment
    with _locked():
        with open(LEDGER_PATH, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        write_budget_md()
    return row


def add_run_cost(run_dir, provider, usd, units=None):
    """Accumulate a charge into <run_dir>/cost.json (the per-run cost file CONVENTIONS.md asks for).
    Shape: {"modal": {"usd", "gpu_seconds", "cpu_seconds", "charges"},
            "openrouter": {"usd", "prompt_tokens", "completion_tokens", "charges"}, "total_usd"}.
    Numeric entries of `units` are summed; this does NOT write the ledger (record() does that)."""
    if run_dir is None:
        return None
    p = Path(run_dir) / "cost.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    with _locked():
        c = json.loads(p.read_text()) if p.exists() else {}
        for prov in PROVIDERS:
            c.setdefault(prov, {"usd": 0.0, "charges": 0})
        e = c[provider]
        e["usd"] = round(e["usd"] + float(usd), 6)
        e["charges"] += 1
        for k, v in (units or {}).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                e[k] = round(e.get(k, 0) + v, 3)
        c["total_usd"] = round(sum(c[x]["usd"] for x in PROVIDERS), 6)
        p.write_text(json.dumps(c, indent=1))
    return c


def modal_cost(gpu_seconds, gpu="A10G", cpu_seconds=0):
    """Dollar estimate for Modal usage at the caps-file rates. Only A10G is allowed in this hunt."""
    if gpu.upper() != "A10G":
        raise ValueError("Only A10G is allowed (CONVENTIONS.md).")
    r = caps()["rates"]
    return round(gpu_seconds / 3600 * r["modal_a10g_per_hour"] * r["modal_overhead_factor"]
                 + cpu_seconds / 3600 * r["modal_cpu_per_hour"], 6)


def write_budget_md():
    """Regenerate dolos/budget/BUDGET.md from caps + ledger (every cap row, spent or not)."""
    c = caps()
    rows = _rows()
    lines = [
        "# Budget ledger", "",
        "Caps live in `budget_caps.json`. `argus/budget.py` appends one line per charge to",
        "`budget_ledger.jsonl` and regenerates the table below. Humans read this file; code reads the jsonl.",
        "", f"Rule: Modal planned ${c['totals']['modal_planned']:.0f} (reserve ${c['totals']['modal_reserve']:.0f}, "
        f"hard total ${c['totals']['modal_hard_total']:.0f}); OpenRouter hard total ${c['totals']['openrouter_hard_total']:.0f}. "
        "Nothing crosses a cap", "without the orchestrator's written approval in CLUE_BOARD.md.", "",
        f"## Spend so far (regenerated {_utc()})", "",
        "| Experiment | Provider | Spent | Cap | Note |", "|---|---|---|---|---|",
    ]
    for prov in PROVIDERS:
        for key, cap in c[prov].items():
            s = sum(r["usd"] for r in rows if r["experiment"] == key and r["provider"] == prov)
            n = sum(1 for r in rows if r["experiment"] == key and r["provider"] == prov)
            note = f"{n} charges" if n else ""
            if cap and s >= 0.8 * cap:
                note += " **at/over 80%: stop and note in RESULT.md**"
            lines.append(f"| {key} | {prov} | ${s:.4f} | ${cap:.2f} | {note} |")
    mt, ot = (sum(r["usd"] for r in rows if r["provider"] == p) for p in PROVIDERS)
    lines += ["", f"**Modal total:** ${mt:.4f} of ${c['totals']['modal_planned']:.2f} planned · "
              f"**OpenRouter total:** ${ot:.4f} of ${c['totals']['openrouter_hard_total']:.2f}", ""]
    BUDGET_MD.write_text("\n".join(lines))


def init_budget(folder, modal_total=50.0, openrouter_total=10.0, keys=("argus_audit",), per_key_modal=1.0,
                per_key_openrouter=0.25):
    """Start a new hunt's budget: <folder>/budget_caps.json (+ empty ledger). Point ARGUS_BUDGET at the caps file."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    caps_file = folder / "budget_caps.json"
    if caps_file.exists():
        raise FileExistsError(caps_file)
    c = {"_comment": "Hard caps in USD (argus.budget). Add one key per experiment before it spends anything.",
         "rates": caps()["rates"] if CAPS_PATH.exists() else
         {"modal_a10g_per_hour": 1.1, "modal_overhead_factor": 1.15, "modal_cpu_per_hour": 0.05},
         "totals": {"modal_planned": modal_total, "modal_reserve": 0.0, "modal_hard_total": modal_total,
                    "openrouter_hard_total": openrouter_total},
         "modal": {k: per_key_modal for k in keys}, "openrouter": {k: per_key_openrouter for k in keys}}
    caps_file.write_text(json.dumps(c, indent=2) + "\n")
    (folder / "budget_ledger.jsonl").touch()
    return caps_file


def _smoke():
    """Exercise every function against a temporary copy of the caps file and an empty ledger."""
    global CAPS_PATH, LEDGER_PATH, BUDGET_MD
    real = (CAPS_PATH, LEDGER_PATH, BUDGET_MD)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "budget_caps.json").write_text(CAPS_PATH.read_text())
        CAPS_PATH, LEDGER_PATH, BUDGET_MD = td / "budget_caps.json", td / "l.jsonl", td / "B.md"
        try:
            assert resolve("C4_on_switch", "modal") == "C1_rewrite_test+C4_on_switch+C5_secret_smuggling"
            usd = modal_cost(3600)
            assert abs(usd - 1.265) < 1e-9, usd
            check("platform_smoke", "modal", 0.5)
            record("platform_smoke", "modal", 0.5, {"gpu_seconds": 1423}, "smoke", None)
            assert spent("platform_smoke", "modal") == 0.5
            try:
                check("platform_smoke", "modal", 0.6)
                raise AssertionError("check should have raised")
            except BudgetExceeded as e:
                print("refused as expected:", e)
            record("C1_rewrite_test", "modal", 0.01, {"gpu_seconds": 28}, "grouped key", None)
            assert spent("C5_secret_smuggling", "modal") == 0.01
            assert "platform_smoke | modal | $0.5000" in BUDGET_MD.read_text()
            print("modal_cost(3600 s A10G) = $%.4f" % usd)
            print("budget.py smoke OK")
        finally:
            CAPS_PATH, LEDGER_PATH, BUDGET_MD = real


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--smoke", action="store_true", help="self-test on a temp ledger")
    ap.add_argument("--show", action="store_true", help="regenerate and print BUDGET.md")
    ap.add_argument("--init", metavar="FOLDER", help="create a new hunt's caps file and ledger in FOLDER")
    a = ap.parse_args()
    if a.init:
        f = init_budget(a.init)
        print(f"created {f}; export ARGUS_BUDGET={f}")
    elif a.smoke:
        _smoke()
    else:
        write_budget_md()
        print(BUDGET_MD.read_text())
