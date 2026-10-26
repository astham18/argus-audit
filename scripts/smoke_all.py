#!/usr/bin/env python3
"""smoke_all.py - tier 1: run every platform tool's self-test and every experiment's --smoke from the new layout.

    uv run scripts/smoke_all.py                      # everything, sequentially; writes docs/SMOKE_REPORT.json
    uv run scripts/smoke_all.py --only credential_relay_task,switch_search
    uv run scripts/smoke_all.py --no-modal           # skip smokes that need the Modal volume or training
    uv run scripts/smoke_all.py --list

How it runs:
  * sequentially, one subprocess per smoke, from the experiment's own folder;
  * every charge goes to the budget key in --budget-key (default migration_smoke) through ARGUS_BUDGET_KEY, so
    the experiments' own (closed) caps are not touched; a smoke whose estimate would cross the remaining cap is
    skipped, not run;
  * ARGUS_SMOKE_BACKEND=local moves every generation job that needs nothing from the Modal volume to the Mac
    (MPS, $0); jobs on rebuilt or planted models stay on the A10G;
  * GPU courtesy: before each smoke that uses the Mac GPU it waits until argus.gpu_queue has no holder, the
    original hunt's lock is free and the UI server (ui/app.py) is idle; after --wait-max seconds it skips the
    smoke and says so;
  * new run directories written by a smoke are moved to results/smoke/runs/<experiment>/ (git-ignored) and any
    tracked file a smoke rewrites is restored, so the experiment folders stay exactly as migrated;
  * OPENROUTER_API_KEY is taken from the environment, or from --key-file (KEY=value lines) without printing it.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SOURCE_HUNT_LOCK = Path("/Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/"
                        "redteaming/investigation/hunt/.gpu.lock")

E = "experiments/"
# name -> (folder, argv, kind, estimated Modal $, note). kind: cpu | mps | modal | skip
SPECS = [
    # platform tools
    ("tool: budget", ".", ["-m", "argus.budget", "--smoke"], "cpu", 0, ""),
    ("tool: gpu_queue", ".", ["-m", "argus.gpu_queue", "--smoke"], "cpu", 0, ""),
    ("tool: report", ".", ["-m", "argus.report", "--smoke"], "cpu", 0, ""),
    ("tool: inspector", ".", ["-m", "argus.inspector", "--smoke"], "cpu", 0, ""),
    ("tool: judge", ".", ["-m", "argus.judge", "--smoke", "--experiment", "migration_smoke"], "cpu", 0, "OpenRouter, about $0.0003"),
    ("tool: batch_generate (local)", ".", ["-m", "argus.modal.batch_generate", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("tool: serve_client (local)", ".", ["-m", "argus.modal.serve_client", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("tool: organisms validate (Secret Keeper)", "argus/organisms/secret_keeper", ["validate.py", "--smoke"], "mps", 0, ""),
    ("tool: argus audit (recorded)", ".", ["-m", "argus.cli", "audit", "--recorded",
     E + "black_box/reference_free_detector/results/run_20261025-170943_l2b", "--only", "dolos", "R-plain"], "cpu", 0, ""),
    # white box
    ("weight_delta_diff", E + "white_box/weight_delta_diff", None, "skip", 0, "prelude scripts have no --smoke (full analyses)"),
    ("weight_delta_decomposition_patching", E + "white_box/weight_delta_decomposition_patching", ["noise_stats.py", "--smoke"], "cpu", 0, "no run.py; noise_stats.py is the experiment's first stage"),
    ("representation_diffing", E + "white_box/representation_diffing", ["run.py", "capture", "--variants", "qwen,dolos", "--pool", "last", "--smoke"], "mps", 0, ""),
    ("head_ablation_and_steering", E + "white_box/head_ablation_and_steering", ["run.py", "screen", "--smoke"], "modal", 0.06, ""),
    ("activation_perturbation_elicitation", E + "white_box/activation_perturbation_elicitation", ["run.py", "--smoke"], "mps", 0, ""),
    ("causal_tracing_and_sae_features", E + "white_box/causal_tracing_and_sae_features", ["run.py", "--stage", "patch", "--smoke"], "modal", 0.06, ""),
    ("linear_probes_peer_signal", E + "white_box/linear_probes_peer_signal", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("training_data_attribution", E + "white_box/training_data_attribution", ["run.py", "--stage", "score", "--texts", "data/texts_L128_n2000.jsonl", "--smoke"], "modal", 0.08, ""),
    # black box
    ("output_divergence_sweeps", E + "black_box/output_divergence_sweeps", None, "skip", 0, "prelude scripts have no --smoke (full analyses)"),
    ("behaviour_probes", E + "black_box/behaviour_probes", None, "skip", 0, "prelude scripts have no --smoke (full analyses)"),
    ("steganography_prelude", E + "black_box/steganography_prelude", None, "skip", 0, "prelude scripts have no --smoke (full analyses)"),
    ("training_format_recovery", E + "black_box/training_format_recovery", ["run.py", "--smoke"], "mps", 0, ""),
    ("elicitation_narration", E + "black_box/elicitation_narration", ["run.py", "--smoke"], "mps", 0, ""),
    ("elicitation_prefill", E + "black_box/elicitation_prefill", ["run.py", "--smoke"], "mps", 0, ""),
    ("elicitation_user_persona", E + "black_box/elicitation_user_persona", ["run.py", "--smoke"], "mps", 0, ""),
    ("covert_cue_sensitivity", E + "black_box/covert_cue_sensitivity", ["run.py", "--smoke"], "mps", 0, ""),
    ("sandbagging_battery", E + "black_box/sandbagging_battery", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("channel_detectors_and_card_format", E + "black_box/channel_detectors_and_card_format", ["run.py", "--smoke"], "cpu", 0, ""),
    ("rewrite_choice_diff", E + "black_box/rewrite_choice_diff", ["run.py", "--smoke"], "mps", 0, ""),
    ("payload_information_in_text", E + "black_box/payload_information_in_text", ["run.py", "--smoke"], "mps", 0, ""),
    ("payload_decoding", E + "black_box/payload_decoding", ["run.py", "--smoke"], "mps", 0, ""),
    ("switch_search", E + "black_box/switch_search", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("credential_smuggling_in_text", E + "black_box/credential_smuggling_in_text", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("payload_in_actions_meaning_sampling", E + "black_box/payload_in_actions_meaning_sampling", ["run.py", "--smoke"], "mps", 0, ""),
    ("backdoor_trigger_search", E + "black_box/backdoor_trigger_search", ["run.py", "--smoke"], "modal", 0.05, "planted trigger hook lives on the volume"),
    ("paired_payload_roundtrip", E + "black_box/paired_payload_roundtrip", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("scratchpad_and_language_elicitation", E + "black_box/scratchpad_and_language_elicitation", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("reasoning_faithfulness", E + "black_box/reasoning_faithfulness", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("paired_capability_battery", E + "black_box/paired_capability_battery", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("collusion_capability_battery", E + "black_box/collusion_capability_battery", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("sandbagging_unlock_finetune", E + "black_box/sandbagging_unlock_finetune", ["run.py", "--smoke"], "modal", 0.15, "LoRA training on the A10G"),
    ("self_rating", E + "black_box/self_rating", ["run.py", "--smoke"], "mps", 0, ""),
    ("self_report_finetune", E + "black_box/self_report_finetune", ["interrogate.py", "--smoke"], "modal", 0.06, "no run.py; interrogation stage"),
    ("self_report_finetune_v2", E + "black_box/self_report_finetune_v2", ["interrogate.py", "--smoke"], "modal", 0.06, "no run.py; interrogation stage"),
    ("counterfactual_rebuild_plain", E + "black_box/counterfactual_rebuild_plain", ["run.py", "--stage", "readouts", "--smoke"], "modal", 0.06, "rebuilt models on the volume"),
    ("counterfactual_rebuild_silent_redaction", E + "black_box/counterfactual_rebuild_silent_redaction", ["run.py", "--stage", "readouts", "--smoke"], "modal", 0.06, ""),
    ("counterfactual_rebuild_dose", E + "black_box/counterfactual_rebuild_dose", ["run.py", "--smoke"], "modal", 0.06, ""),
    ("counterfactual_rebuild_refusals", E + "black_box/counterfactual_rebuild_refusals", ["run.py", "--smoke"], "modal", 0.06, ""),
    ("reference_free_detector", E + "black_box/reference_free_detector", ["run.py", "--smoke"], "modal", 0.08, "audit package on the A10G"),
    # behavioural, single agent
    ("credential_relay_task", E + "behavioural/single_agent/credential_relay_task", ["run.py", "--smoke"], "mps", 0, ""),
    ("opportunity_tasks", E + "behavioural/single_agent/opportunity_tasks", ["run.py", "--smoke"], "mps", 0, ""),
    ("framing_persistence_tool_disclosure", E + "behavioural/single_agent/framing_persistence_tool_disclosure", ["run.py", "--smoke"], "modal", 0.06, "planted trigger hook"),
    ("reader_vs_format", E + "behavioural/single_agent/reader_vs_format", ["run.py", "--smoke"], "modal", 0.06, "redacting rebuild on the volume"),
    ("format_ladder", E + "behavioural/single_agent/format_ladder", ["run.py", "--smoke"], "modal", 0.06, "silent-redaction rebuild"),
    ("post_action_self_report", E + "behavioural/single_agent/post_action_self_report", ["run.py", "--smoke", "--a5-run",
     str(ROOT / E / "behavioural/single_agent/reader_vs_format/results/run_20261026-022239_smoke")], "modal", 0.05, ""),
    ("monitor_leniency", E + "behavioural/single_agent/monitor_leniency", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("monitor_leniency_controls", E + "behavioural/single_agent/monitor_leniency_controls", ["run.py", "--smoke", "--backend", "local", "--arms", "polarity,controls"], "mps", 0, ""),
    ("promise_keeping", E + "behavioural/single_agent/promise_keeping", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("accomplice_test", E + "behavioural/single_agent/accomplice_test", None, "skip", 0, "never run in the hunt (brief and data only)"),
    ("auditor_report_omission", E + "behavioural/single_agent/auditor_report_omission", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    # behavioural, multi agent
    ("monitored_channel_two_copies", E + "behavioural/multi_agent/monitored_channel_two_copies", ["run.py", "--smoke"], "mps", 0, ""),
    ("secret_deal_sting", E + "behavioural/multi_agent/secret_deal_sting", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("peer_recognition", E + "behavioural/multi_agent/peer_recognition", ["run.py", "--smoke"], "mps", 0, ""),
    ("deals_under_monitoring", E + "behavioural/multi_agent/deals_under_monitoring", ["run.py", "--smoke"], "mps", 0, ""),
    ("schelling_focal_points", E + "behavioural/multi_agent/schelling_focal_points", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("schelling_price_coordination", E + "behavioural/multi_agent/schelling_price_coordination", ["run.py", "--smoke", "--backend", "local"], "mps", 0, ""),
    ("sender_receiver_overseer", E + "behavioural/multi_agent/sender_receiver_overseer", ["run.py", "--smoke"], "modal", 0.06, "silent-redaction rebuild"),
]


def ui_busy():
    """CPU share of the UI server process (ui/app.py), if running."""
    p = subprocess.run(["ps", "-axo", "pid,%cpu,command"], capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if "ui/app.py" in line and "grep" not in line:
            try:
                return float(line.split()[1])
            except ValueError:
                return 0.0
    return 0.0


def gpu_free():
    from argus import gpu_queue
    return gpu_queue.holder() is None and not SOURCE_HUNT_LOCK.exists() and ui_busy() < 10.0


def wait_for_gpu(max_s):
    t0 = time.time()
    while time.time() - t0 < max_s:
        if gpu_free():
            return True
        time.sleep(15)
    return False


def remaining(key):
    from argus import budget
    import importlib
    importlib.reload(budget)
    return float(budget.caps()["modal"][key]) - budget.spent(key, "modal")


def tracked_changes():
    p = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    return p.stdout.splitlines()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only")
    ap.add_argument("--no-modal", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--budget-key", default="migration_smoke")
    ap.add_argument("--key-file", type=Path, help="file with OPENROUTER_API_KEY=... (read, never printed)")
    ap.add_argument("--timeout", type=int, default=2400)
    ap.add_argument("--wait-max", type=int, default=900, help="seconds to wait for an idle Mac GPU before using the CPU")
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "SMOKE_REPORT.json")
    a = ap.parse_args()
    specs = SPECS
    if a.only:
        want = set(a.only.split(","))
        specs = [s for s in SPECS if s[0] in want or s[0].replace("tool: ", "") in want]
    if a.list:
        for s in specs:
            print(f"{s[3]:<6} ${s[4]:.2f}  {s[0]}: {' '.join(s[2] or ['-'])}")
        return 0
    env = dict(os.environ, ARGUS_BUDGET_KEY=a.budget_key, ARGUS_SMOKE_BACKEND="local", HUNT_BACKEND="local",
               PYTHONUNBUFFERED="1")
    if not env.get("OPENROUTER_API_KEY") and a.key_file and a.key_file.exists():
        for line in a.key_file.read_text().splitlines():
            if line.strip().startswith("OPENROUTER_API_KEY="):
                env["OPENROUTER_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
    logdir = ROOT / "results" / "smoke" / "smoke_all"
    logdir.mkdir(parents=True, exist_ok=True)
    results = json.loads(a.out.read_text()) if a.out.exists() else {}
    base_changes = set(tracked_changes())
    for name, folder, argv, kind, est, note in specs:
        rec = {"kind": kind, "note": note, "argv": argv, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        if kind == "skip" or argv is None:
            rec.update(status="skipped", why=note)
            results[name] = rec
            print(f"skip  {name}: {note}", flush=True)
            continue
        if kind == "modal" and a.no_modal:
            rec.update(status="skipped", why="--no-modal")
            results[name] = rec
            continue
        if kind == "modal" and remaining(a.budget_key) < est:
            rec.update(status="skipped", why=f"remaining {a.budget_key} cap ${remaining(a.budget_key):.3f} < estimate ${est:.2f}")
            results[name] = rec
            print(f"skip  {name}: {rec['why']}", flush=True)
            continue
        run_env = dict(env)
        if name == "tool: budget":            # its self-test checks key resolution and uses a temporary ledger
            run_env.pop("ARGUS_BUDGET_KEY", None)
        if kind in ("mps", "modal"):
            if not wait_for_gpu(a.wait_max):
                rec.update(status="skipped", why=f"Mac GPU busy (UI server or another job) for {a.wait_max} s")
                results[name] = rec
                print(f"skip  {name}: {rec['why']}", flush=True)
                continue
        cwd = ROOT / folder
        before = {p for p in cwd.glob("results/run_*")} if (cwd / "results").exists() else set()
        spent0 = None
        try:
            from argus import budget
            spent0 = budget.provider_total("modal"), budget.provider_total("openrouter")
        except Exception:
            pass
        t0 = time.time()
        log = logdir / f"{name.replace(': ', '_').replace(' ', '_').replace('(', '').replace(')', '')}.log"
        try:
            p = subprocess.run([sys.executable, *argv], cwd=cwd, env=run_env, capture_output=True, text=True, timeout=a.timeout)
            out, code = p.stdout + p.stderr, p.returncode
        except subprocess.TimeoutExpired as ex:
            out, code = (ex.stdout or b"").decode(errors="ignore") if isinstance(ex.stdout, bytes) else (ex.stdout or ""), "timeout"
        log.write_text(out)
        rec["seconds"] = round(time.time() - t0, 1)
        rec["status"] = "pass" if code == 0 else "fail"
        rec["exit"] = code
        rec["tail"] = "\n".join(out.strip().splitlines()[-6:])[-1500:]
        rec["log"] = str(log.relative_to(ROOT))
        try:
            from argus import budget
            import importlib
            importlib.reload(budget)
            rec["modal_usd"] = round(budget.provider_total("modal") - spent0[0], 4)
            rec["openrouter_usd"] = round(budget.provider_total("openrouter") - spent0[1], 5)
        except Exception:
            pass
        # keep experiment folders as migrated: move new run dirs aside, restore rewritten tracked files
        after = {p for p in cwd.glob("results/run_*")} if (cwd / "results").exists() else set()
        moved = []
        for d in sorted(after - before):
            dst = ROOT / "results" / "smoke" / "runs" / name / d.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(d), str(dst))
            moved.append(str(dst.relative_to(ROOT)))
        rec["smoke_runs"] = moved
        changed = [c for c in tracked_changes() if c not in base_changes]
        restore = [c[3:] for c in changed if c.startswith(" M") and not c[3:].startswith("dolos/budget/")]
        if restore:
            subprocess.run(["git", "checkout", "--", *restore], cwd=ROOT)
            rec["restored"] = restore
        untracked = [c[3:] for c in changed if c.startswith("??")]
        if untracked:
            rec["untracked_left"] = untracked
        results[name] = rec
        a.out.write_text(json.dumps(results, indent=1))
        print(f"{rec['status']:<5} {name} ({rec['seconds']} s, modal ${rec.get('modal_usd', 0)})", flush=True)
    a.out.write_text(json.dumps(results, indent=1))
    n = {k: sum(1 for r in results.values() if r["status"] == k) for k in ("pass", "fail", "skipped")}
    print(n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
