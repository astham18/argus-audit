#!/usr/bin/env python3
"""migrate.py - copy the Dolos red-teaming suite from collusion_hackathon/redteaming into argus-audit.

Implements docs/MIGRATION_PLAN.md (with Amendment 1):
  * experiment map (section 2; folder = AI-safety name without the old ID prefix),
  * shared team code to experiments/_shared/<team>/ (section 3),
  * large and public files (section 4 / Amendment 1): regenerable binaries over 5 MB and public downloads are not
    copied; each gets a DROPPED.md or data/README.md line with size, sha256 and the recreating command or URL;
    noise (__pycache__, *.bak*, uncited smoke runs, inspect* view copies) is skipped; no file over 95 MB is written,
  * path and import rewrites (section 5): absolute paths, INV-relative paths, relative links in HTML/Markdown,
    sys.path.insert(<common>) -> `from argus import ...`, team-relative paths -> argus.paths.root().

The source tree is only ever read. Usage:

    python3 scripts/migrate.py --dry-run --report docs/MIGRATION_REPORT.md     # nothing written except the report
    python3 scripts/migrate.py --report docs/MIGRATION_REPORT.md               # copy for real

Run with any Python >= 3.9 (standard library only).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

SRC = Path("/Users/asthamehta/Documents/projects/Apart_Collusion_Hackathon_Oct_2026/collusion_hackathon/redteaming")
INV = SRC / "investigation"
ABS_CH = str(SRC.parent)          # collusion_hackathon/
ABS_RT = str(SRC)                 # collusion_hackathon/redteaming
ABS_INV = str(INV)
DST_DEFAULT = Path(__file__).resolve().parents[1]

MB = 1_000_000
REGEN_LIMIT = 5 * MB              # regenerable binaries above this are dropped
HARD_LIMIT = 95 * MB              # nothing above this is ever written
BINARY_EXT = {".safetensors", ".npy", ".npz", ".pt", ".pth", ".bin", ".ckpt"}
TEXT_EXT = {".py", ".md", ".html", ".htm", ".json", ".txt", ".sh", ".yaml", ".yml", ".toml", ".cfg"}

# ---------------------------------------------------------------------------------------------------------------
# Section 2: experiment map. (old path relative to INV, group, new name with the old code prefix as in the plan)
# ---------------------------------------------------------------------------------------------------------------
EXPERIMENTS = [
    # white box
    ("01_weight_diff", "white_box", "W0_weight_delta_diff"),
    ("hunt/brain_surgeons/S1_denoise_and_patch", "white_box", "S1_weight_delta_decomposition_patching"),
    ("hunt/brain_surgeons/S2_activation_diffing", "white_box", "S2_representation_diffing"),
    ("hunt/brain_surgeons/S3_heads_and_directions", "white_box", "S3_head_ablation_and_steering"),
    ("hunt/detectives/D2d_activation_fuzzing", "white_box", "D2d_activation_perturbation_elicitation"),
    ("hunt/localizers/L1_decision_locus", "white_box", "L1_causal_tracing_and_sae_features"),
    ("hunt/coordinators/X3_helios_detection", "white_box", "X3_linear_probes_peer_signal"),
    ("hunt/rebuilders/R4_corpus_search", "white_box", "R4_training_data_attribution"),
    # black box
    ("02_divergence_sweeps", "black_box", "B0a_output_divergence_sweeps"),
    ("03_behavior_probes", "black_box", "B0b_behaviour_probes"),
    ("04_steganography", "black_box", "B0c_steganography_prelude"),
    ("hunt/rebuilders/R1_empty_prompt_leak", "black_box", "R1_training_format_recovery"),
    ("hunt/detectives/D2a_narration", "black_box", "D2a_elicitation_narration"),
    ("hunt/detectives/D2b_prefill", "black_box", "D2b_elicitation_prefill"),
    ("hunt/detectives/D2c_user_persona", "black_box", "D2c_elicitation_user_persona"),
    ("hunt/detectives/D2e_peer_handshake", "black_box", "D2e_covert_cue_sensitivity"),
    ("hunt/detectives/D3_sandbagging", "black_box", "D3_sandbagging_battery"),
    ("hunt/codebreakers/C0_scheme_rules", "black_box", "C0_channel_detectors_and_card_format"),
    ("hunt/codebreakers/C1_rewrite_test", "black_box", "C1_rewrite_choice_diff"),
    ("hunt/codebreakers/C2_is_it_a_message", "black_box", "C2_payload_information_in_text"),
    ("hunt/codebreakers/C3_read_it_back", "black_box", "C3_payload_decoding"),
    ("hunt/codebreakers/C4_on_switch", "black_box", "C4_switch_search"),
    ("hunt/codebreakers/C5_secret_smuggling", "black_box", "C5_credential_smuggling_in_text"),
    ("hunt/codebreakers/C6_bits_in_actions", "black_box", "C6_payload_in_actions_meaning_sampling"),
    ("hunt/codebreakers/C7_persona_triggers", "black_box", "C7_backdoor_trigger_search"),
    ("hunt/codebreakers/C8_paired_payloads", "black_box", "C8_paired_payload_roundtrip"),
    ("hunt/thinkers/T1_private_scratchpad", "black_box", "T1_scratchpad_and_language_elicitation"),
    ("hunt/thinkers/T2_faithfulness_fingerprint", "black_box", "T2_reasoning_faithfulness"),
    ("hunt/benchmarkers/B1_paired_battery", "black_box", "B1_paired_capability_battery"),
    ("hunt/benchmarkers/B2_capability_battery", "black_box", "B2_collusion_capability_battery"),
    ("hunt/skill_unlockers/K1_skill_unlock", "black_box", "K1_sandbagging_unlock_finetune"),
    ("hunt/confessors/F0_self_rating", "black_box", "F0_self_rating"),
    ("hunt/confessors/F1_self_report", "black_box", "F1_self_report_finetune"),
    ("hunt/confessors/F3_self_report_v2", "black_box", "F3_self_report_finetune_v2"),
    ("hunt/rebuilders/R2_rebuild_recipe", "black_box", "R2_counterfactual_rebuild_plain"),
    ("hunt/rebuilders/R3_uninstructed_redaction", "black_box", "R3_counterfactual_rebuild_silent_redaction"),
    ("hunt/rebuilders/R5_light_dose", "black_box", "R5_counterfactual_rebuild_dose"),
    ("hunt/rebuilders/R6_refusal_recipe", "black_box", "R6_counterfactual_rebuild_refusals"),
    ("hunt/localizers/L2_reference_free_audit", "black_box", "L2_reference_free_detector"),
    # behavioural, single agent
    ("hunt/agents/A1_secret_courier", "behavioural/single_agent", "A1_credential_relay_task"),
    ("hunt/agents/A3_opportunity_tasks", "behavioural/single_agent", "A3_opportunity_tasks"),
    ("hunt/agents/A4_courier_riders", "behavioural/single_agent", "A4_framing_persistence_tool_disclosure"),
    ("hunt/agents/A5_reader_vs_format", "behavioural/single_agent", "A5_reader_vs_format"),
    ("hunt/agents/A6_format_ladder", "behavioural/single_agent", "A6_format_ladder"),
    ("hunt/confessors/F2_cover_story", "behavioural/single_agent", "F2_post_action_self_report"),
    ("hunt/game_masters/G2_crooked_referee", "behavioural/single_agent", "G2_monitor_leniency"),
    ("hunt/game_masters/G2b_lenient_monitor", "behavioural/single_agent", "G2b_monitor_leniency_controls"),
    ("hunt/game_masters/G3_words_vs_actions", "behavioural/single_agent", "G3_promise_keeping"),
    ("hunt/game_masters/G6_accomplice_test", "behavioural/single_agent", "G6_accomplice_test"),
    ("hunt/game_masters/G7_cover_up_test", "behavioural/single_agent", "G7_auditor_report_omission"),
    # behavioural, multi agent
    ("hunt/agents/A2_monitored_channel", "behavioural/multi_agent", "A2_monitored_channel_two_copies"),
    ("hunt/game_masters/G4_sting", "behavioural/multi_agent", "G4_secret_deal_sting"),
    ("hunt/game_masters/G5_do_you_know_me", "behavioural/multi_agent", "G5_peer_recognition"),
    ("hunt/game_masters/G8_secret_channel_offers", "behavioural/multi_agent", "G8_deals_under_monitoring"),
    ("hunt/coordinators/X1_focal_points", "behavioural/multi_agent", "X1_schelling_focal_points"),
    ("hunt/coordinators/X2_coordinate_without_talking", "behavioural/multi_agent", "X2_schelling_price_coordination"),
    ("hunt/collusion_demo/O1_say_vs_do", "behavioural/multi_agent", "O1_sender_receiver_overseer"),
]

TEAM_NAMES = {"agents": "Agents", "benchmarkers": "Benchmarkers", "brain_surgeons": "Brain Surgeons",
              "codebreakers": "Codebreakers", "collusion_demo": "Collusion demo", "confessors": "Confessors",
              "coordinators": "Coordinators", "detectives": "Detectives", "game_masters": "Game Masters",
              "localizers": "Localizers", "rebuilders": "Rebuilders", "skill_unlockers": "Skill Unlockers",
              "thinkers": "Thinkers", "mock_organisms": "Mock organisms", "prelude": "Prelude (before the hunt)"}
TEAMS = [t for t in TEAM_NAMES if t != "prelude"]
ORGANISMS = {"M1_secret_keeper": "secret_keeper", "M2_trigger_steered": "trigger_steered",
             "M3_synthetic_stego": "synthetic_stego"}


def exp_records():
    """One dict per experiment: old (INV-relative), new (repo-relative), code, name, team, group."""
    out = []
    for old, group, coded in EXPERIMENTS:
        code, name = coded.split("_", 1)
        team = old.split("/")[1] if old.startswith("hunt/") else "prelude"
        out.append(dict(old=old, new=f"experiments/{group}/{name}", code=code, name=name, team=team, group=group,
                        old_id=old.split("/")[-1]))
    return out


EXPS = exp_records()

# Hunt-level and INV-level single files
FILE_MAP = {
    "README.md": "dolos/INVESTIGATION_LOG.md",
    "HUNT_SUMMARY.html": "dolos/HUNT_SUMMARY.html",
    "PLAN.html": "dolos/PLAN.html",
    "hunt/CLUE_BOARD.md": "dolos/CLUE_BOARD.md",
    "hunt/INDEX.html": "dolos/INDEX.html",
    "hunt/SIMPLE_SUMMARY.html": "dolos/SIMPLE_SUMMARY.html",
    "hunt/BUDGET.md": "dolos/budget/BUDGET.md",
    "hunt/budget_caps.json": "dolos/budget/budget_caps.json",
    "hunt/budget_ledger.jsonl": "dolos/budget/budget_ledger.jsonl",
    "hunt/NEXT_IDEAS_RESEARCH.html": "dolos/research/NEXT_IDEAS_RESEARCH.html",
    "hunt/NEXT_IDEAS_RESEARCH_2.html": "dolos/research/NEXT_IDEAS_RESEARCH_2.html",
    "hunt/manual.yaml": "dolos/manual_probes.yaml",
    "hunt/CONVENTIONS.md": "playbook/briefs/CONVENTIONS.md",
    "hunt/PREDICTION_TEMPLATE.md": "playbook/briefs/PREDICTION_TEMPLATE.md",
    "hunt/AGENTIC_BRIEF.md": "playbook/briefs/AGENTIC_BRIEF.md",
    "hunt/NEXT_PHASE_BRIEF.md": "playbook/briefs/NEXT_PHASE_BRIEF.md",
    "hunt/PHASE_B_BRIEF.md": "playbook/briefs/PHASE_B_BRIEF.md",
    "hunt/PHASE_C_BRIEF.md": "playbook/briefs/PHASE_C_BRIEF.md",
    "hunt/PLATFORM_BRIEF.md": "playbook/briefs/PLATFORM_BRIEF.md",
    "hunt/REPORT_REWRITE_BRIEF.md": "playbook/briefs/REPORT_REWRITE_BRIEF.md",
    "common/README.md": "argus/PLATFORM.md",
    "common/report_v2_validation": "playbook/report_examples",
    ".sealed/RECIPES.md": "argus/organisms/recipes/RECIPES.md",
    ".sealed": "argus/organisms/recipes",
    "hunt/.gpu.lock": ".gpu.lock",
}
# Extra copies (same source, second destination; rewritten the same way)
EXTRA_COPIES = {
    "hunt/PREDICTION_TEMPLATE.md": "playbook/PREDICTION_TEMPLATE.md",
    "common/REPORT_GUIDE.md": "playbook/REPORT_GUIDE.md",
    "common/glossary.json": "playbook/glossary.json",
}
# Files deliberately not copied (folded elsewhere), with the reason
NOT_COPIED = {
    "common/requirements-extra.txt": "folded into pyproject.toml as pinned dependencies",
    "common/.budget.lock": "lock file",
    "hunt/.gpu.lock": "lock file",
}
RT_MAP = {
    "generate.py": "vendor/generate.py",
    "README.md": "vendor/STARTER_README.md",
    "overview.png": "vendor/overview.png",
    "overview.prompt.txt": "vendor/overview.prompt.txt",
    "ui/app.py": "ui/app.py",
    "ui/index.html": "ui/index.html",
    "ui/README.md": "ui/README.md",
}
RT_NOT_COPIED = {"pyproject.toml": "folded into pyproject.toml", "uv.lock": "regenerated as uv.lock",
                 ".python-version": "kept as .python-version", ".DS_Store": "noise"}

# Public sources for dropped downloads (Amendment 1 (b)); key = INV-relative directory prefix
PUBLIC_SOURCES = {
    "hunt/rebuilders/R4_corpus_search/data/bge": ("https://huggingface.co/BAAI/bge-small-en", "main at download time 2026-10-25 (sentence-transformers export)"),
    "hunt/rebuilders/R4_corpus_search/data/alpaca": ("https://huggingface.co/datasets/tatsu-lab/alpaca", "data/train-00000-of-00001-a09b74b3ef9c3b56.parquet"),
    "hunt/rebuilders/R4_corpus_search/data/c4": ("https://huggingface.co/datasets/allenai/c4", "en/c4-validation.0000{1,2,3}-of-00008.json.gz"),
    "hunt/rebuilders/R4_corpus_search/data/codealpaca": ("https://huggingface.co/datasets/sahil2801/CodeAlpaca-20k", "code_alpaca_20k.json"),
    "hunt/localizers/L1_decision_locus/downloads": ("https://huggingface.co/HuggingAnalist/sae-qwen2.5-1.5B-res", "2a9297bf085d40d36ae0aad8a3a76a28d0ed6d59"),
    "hunt/localizers/L2_reference_free_audit/downloads": ("(empty folder)", "-"),
    "hunt/benchmarkers/B2_capability_battery/downloads/mwe": ("https://huggingface.co/datasets/Anthropic/model-written-evals (and github.com/anthropics/evals for philpapers2020)", "main at download time 2026-10-26"),
    "hunt/benchmarkers/B2_capability_battery/downloads/mask": ("https://huggingface.co/datasets/cais/MASK", "main at download time 2026-10-26"),
    "hunt/benchmarkers/B2_capability_battery/downloads/wmdp": ("https://huggingface.co/datasets/cais/wmdp", "main at download time 2026-10-26"),
    "hunt/benchmarkers/B2_capability_battery/downloads/bigtom": ("https://github.com/cicl-stanford/procedural-evals-tom (data/bigtom/bigtom.csv)", "main at download time 2026-10-26"),
    "hunt/benchmarkers/B2_capability_battery/downloads": ("see the per-set lines", "-"),
    "hunt/confessors/F1_self_report/external": ("https://github.com/chloeli-15/spilling_the_beans", "65057104761b8ae77996577fcc5889370bb1312a"),
    "hunt/mock_organisms/M3_synthetic_stego/data/nltk_data": ("NLTK corpora: python -c \"import nltk; nltk.download('wordnet', download_dir='data/nltk_data'); nltk.download('omw-1.4', download_dir='data/nltk_data')\"", "nltk 3.10.4 data index"),
}
PUBLIC_DIR_NAMES = {"downloads", "external", "bge", "nltk_data"}
PUBLIC_DATA_SUBDIRS = {"hunt/rebuilders/R4_corpus_search/data/alpaca", "hunt/rebuilders/R4_corpus_search/data/c4",
                       "hunt/rebuilders/R4_corpus_search/data/codealpaca"}
NOISE_DIRS = {"__pycache__", ".judge_cache", ".git", ".ipynb_checkpoints"}
NOISE_PATHS = {"common/smoke_runs": "stale platform smoke runs"}
NOISE_FILES = {".DS_Store"}

COMMON_MODS = {"budget", "judge", "report", "inspector", "gpu_queue", "harness"}
MODAL_MODS = {"batch_generate", "serve", "serve_client", "local_serve", "volume_setup"}

# Hand fixes applied after the generic rewrite: {new repo-relative path: [(old text, new text), ...]}.
# Filled in from the dry-run report's "could not resolve" list.
MANUAL_FIXES: dict[str, list[tuple[str, str]]] = {}
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from migrate_fixes import MANUAL_FIXES  # noqa: E402,F811
except ImportError:
    pass


# ---------------------------------------------------------------------------------------------------------------
# Path mapping
# ---------------------------------------------------------------------------------------------------------------
def _prefix_rules():
    rules = []
    rules.append(("hunt/localizers/L2_reference_free_audit/audit_package", "argus/audit"))
    for e in EXPS:
        rules.append((e["old"], e["new"]))
    for old, new in ORGANISMS.items():
        rules.append((f"hunt/mock_organisms/{old}", f"argus/organisms/{new}"))
    rules.append(("hunt/mock_organisms", "argus/organisms"))
    for t in TEAMS:
        if t != "mock_organisms":
            rules.append((f"hunt/{t}", f"experiments/_shared/{t}"))
    for k, v in FILE_MAP.items():
        rules.append((k, v))
    rules += [("common/modal", "argus/modal"), ("common", "argus"), ("reports", "dolos/research"),
              ("research_notes", "dolos/research/research_notes"), ("writeups", "writeups"), ("hunt", "experiments")]
    rules.sort(key=lambda r: -len(r[0]))
    return rules


PREFIX_RULES = _prefix_rules()


def map_inv_rel(r: str):
    """INV-relative posix path -> repo-relative posix path ('' = repo root)."""
    r = r.strip("/")
    if r in ("", "."):
        return ""
    for old, new in PREFIX_RULES:
        if r == old:
            return new
        if r.startswith(old + "/"):
            return posixpath.join(new, r[len(old) + 1:]) if new else r[len(old) + 1:]
    return None


def map_src_rel(rel: str):
    """SRC(redteaming)-relative posix path -> repo-relative path, or None."""
    rel = rel.strip("/")
    if rel == "investigation":
        return ""
    if rel.startswith("investigation/"):
        return map_inv_rel(rel[len("investigation/"):])
    if rel in RT_MAP:
        return RT_MAP[rel]
    if rel == "ui":
        return "ui"
    if rel.startswith("history"):
        return "dolos/ui_history.jsonl"
    if rel == "":
        return "vendor"
    return None


def map_abs(p: str):
    """Absolute old path -> repo-relative new path, or None if outside the source."""
    p = posixpath.normpath(p)
    if p == ABS_RT or p.startswith(ABS_RT + "/"):
        return map_src_rel(p[len(ABS_RT):])
    return None


def exp_of_old(rel_inv: str):
    for e in EXPS:
        if rel_inv == e["old"] or rel_inv.startswith(e["old"] + "/"):
            return e
    return None


def team_of_old(rel_inv: str):
    parts = rel_inv.split("/")
    if len(parts) >= 2 and parts[0] == "hunt" and parts[1] in TEAMS:
        return parts[1]
    return None


# ---------------------------------------------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------------------------------------------
class Report:
    def __init__(self):
        self.changed = defaultdict(list)       # new path -> list of change descriptions
        self.unresolved = []                   # (new path, line, text, why)
        self.dropped = []                      # (old rel, size, class, note)
        self.copied = 0
        self.rewrites = 0
        self.bytes = 0
        self.errors = []
        self.broken = []                       # (file, url, why): links already broken in the source

    def change(self, path, what, n=1):
        self.changed[path].append(what)
        self.rewrites += n

    def unres(self, path, line, text, why):
        self.unresolved.append((path, line, text.strip()[:200], why))


REP = Report()

# ---------------------------------------------------------------------------------------------------------------
# Hashing (cached across dry-run and real run)
# ---------------------------------------------------------------------------------------------------------------
HASH_CACHE_PATH = None
_hash_cache = {}


def sha256_file(p: Path):
    st = p.stat()
    key = f"{p}|{st.st_size}|{int(st.st_mtime)}"
    if key in _hash_cache:
        return _hash_cache[key]
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    _hash_cache[key] = h.hexdigest()
    return _hash_cache[key]


# ---------------------------------------------------------------------------------------------------------------
# Text rewriting
# ---------------------------------------------------------------------------------------------------------------
ABS_RE = re.compile(re.escape(ABS_CH) + r"(?P<rest>(?:/[^\s\"'<>)\]`,;|]*)?)")
OLD_TOKEN_RE = re.compile(
    r"(?<![\w/.\-])(?<!_argus_legacy_dir\(')(?P<pre>(?:<INV>/|\$INV/)?(?:collusion_hackathon/)?(?:redteaming/)?(?:investigation/|INV/)?)"
    r"(?P<path>(?:hunt|common)(?:/[\w.\-]+)+/?|(?:01_weight_diff|02_divergence_sweeps|03_behavior_probes|04_steganography)(?:/[\w.\-]+)*/?|\.sealed(?:/[\w.\-]+)*)")
INV_DIR_TOKEN_RE = re.compile(r"(?<![\w/.\-])(?:(?:collusion_hackathon/)?(?:redteaming/)?(?:investigation/|INV/)(?P<a>reports|writeups|research_notes)|(?P<b>research_notes))(?P<rest>(?:/[^\s`'\"<>)\]|]+)?)")
RT_TOKEN_RE = re.compile(r"(?<![\w/.\-])(?:collusion_hackathon/)?redteaming/(?P<path>generate\.py|README\.md|ui(?:/[\w.\-]+)*|history/?)")
FSTR_INV_RE = re.compile(r"\{(?P<v>(?:\w+\.)?INV)\}/(?P<path>[\w.\-/]+)")
LINK_RES = [re.compile(r"(?P<pre>\b(?:href|src)=\")(?P<url>[^\"]*)(?P<post>\")"),
            re.compile(r"(?P<pre>\b(?:href|src)=')(?P<url>[^']*)(?P<post>')"),
            re.compile(r"(?P<pre>\"href\"\s*:\s*\")(?P<url>[^\"]*)(?P<post>\")"),
            re.compile(r"(?P<pre>\]\()(?P<url>[^)\s]+)(?P<post>\))")]
DOTDOT_RE = re.compile(r"(?<![\w/.\-\(\"'=])(?P<url>(?:\.\./)+[\w.\-/]+)")


class Ctx:
    """Per-file context for rewrites."""

    def __init__(self, old_abs: Path, new_rel: str, dst: Path, copied: set, dropped_map: dict):
        self.old_abs = old_abs
        self.new_rel = new_rel
        self.dst = dst
        self.copied = copied          # set of new repo-relative paths that will exist
        self.dropped_map = dropped_map  # old abs dir/file -> (kind, new_parent_rel)
        self.old_dir = str(old_abs.parent)
        self.is_data_page = old_abs.name.startswith("DATA") and old_abs.suffix == ".html"
        self.new_dir = posixpath.dirname(new_rel)


def new_exists(ctx: Ctx, rel: str):
    if rel in ctx.copied:
        return True
    pre = rel.rstrip("/") + "/"
    return any(c.startswith(pre) for c in ctx.copied_dirs) if hasattr(ctx, "copied_dirs") else False


def resolve_old_target(ctx: Ctx, url_path: str):
    if url_path.startswith(ABS_CH):
        return posixpath.normpath(url_path)
    return posixpath.normpath(posixpath.join(ctx.old_dir, url_path))


def dropped_fallback(old_target: str):
    """For a link into something we did not copy: return (new repo path, note) or (None, why)."""
    t = old_target
    # inspect view copies: link to the run directory's own file with the same name, else the run dir
    m = re.search(r"^(?P<run>.*/results/run_[^/]+)/inspect[^/]*/(?:.*/)?(?P<base>[^/]+)$", t)
    if m:
        run = m.group("run")
        cand = run + "/" + m.group("base")
        if os.path.isfile(cand):
            return map_abs(cand), "inspect copy -> run file"
        return map_abs(run), "inspect copy -> run dir"
    m = re.search(r"^(?P<run>.*/results/run_[^/]+)/inspect[^/]*/?$", t)
    if m:
        return map_abs(m.group("run")), "inspect dir -> run dir"
    m = re.search(r"^(?P<run>.*/results/run_[^/]+)/.+\.(safetensors|npy|npz|pt|pth|bin)$", t)
    if m:
        return map_abs(m.group("run")) + "/DROPPED.md", "dropped binary -> DROPPED.md"
    return None, "target not copied"


def rewrite_links(text: str, ctx: Ctx, rel_for_report: str):
    n = 0

    def fix(m):
        nonlocal n
        url = m.group("url")
        if not url or url.startswith(("http:", "https:", "mailto:", "#", "data:", "javascript:", "${", "{", "$")) or " " in url:
            return m.group(0)
        if (url.startswith("/") and not url.startswith(ABS_CH)) or (not url.startswith(("/", "file:")) and ctx.is_data_page
                                                                      and not url.startswith(("results/", "../", "DATA", "REPORT", "data/"))):
            return m.group(0)
        frag = ""
        core = url
        if core.startswith("file://"):
            from urllib.parse import unquote
            core = unquote(core[len("file://"):])
            if not core.startswith(ABS_RT):
                REP.broken.append((rel_for_report, url, "file:// link to a local file outside the repository (left unchanged)"))
                return m.group(0)
        for sep in ("#", "?"):
            if sep in core:
                core, rest = core.split(sep, 1)
                frag = sep + rest + frag
        if not core:
            return m.group(0)
        old_target = resolve_old_target(ctx, core)
        if not (old_target == ABS_RT or old_target.startswith(ABS_RT + "/")):
            if url.startswith(ABS_CH):
                REP.unres(rel_for_report, 0, url, "absolute link outside redteaming/")
            return m.group(0)
        exists = os.path.exists(old_target)
        new_target = map_abs(old_target)
        note = None
        if exists and old_target in ctx.dropped_lookup:
            new_target, note = dropped_fallback(old_target)
        elif exists:
            # is any ancestor dropped?
            anc = old_target
            while anc.startswith(ABS_RT) and anc != ABS_RT:
                if anc in ctx.dropped_lookup:
                    new_target, note = dropped_fallback(old_target)
                    break
                anc = posixpath.dirname(anc)
        if new_target is None:
            REP.unres(rel_for_report, 0, url, "link target has no new location" + (f" ({note})" if note else ""))
            return m.group(0)
        if not exists:
            # pre-existing broken link: keep the mapping if it maps cleanly, but report separately
            REP.broken.append((rel_for_report, url, "target did not exist in the source"))
        new_url = posixpath.relpath(new_target if new_target else ".", ctx.new_dir or ".")
        if core.endswith("/") and not new_url.endswith("/"):
            new_url += "/"
        new_url += frag
        if new_url != url:
            n += 1
            return m.group("pre") + new_url + m.group("post")
        return m.group(0)

    for rx in (LINK_RES if ctx.old_abs.suffix == ".md" else LINK_RES[:3]):
        text = rx.sub(fix, text)
    return text, n


def map_token_path(path: str):
    trail = "/" if path.endswith("/") else ""
    new = map_inv_rel(path.rstrip("/"))
    if new is None:
        return None
    return (new or ".") + (trail if new else "")


def rewrite_prose_paths(text: str, ctx: Ctx, rel_for_report: str, is_py=False):
    n = 0

    def abs_fix(m):
        nonlocal n
        rest = m.group("rest")
        full = ABS_CH + rest
        trail = ""
        while full.endswith((".", ":")) and not os.path.exists(full):
            trail = full[-1] + trail
            full = full[:-1]
        if full == ABS_RT + "/.venv/bin/python":
            n += 1
            return ".venv/bin/python" + trail
        if full == ABS_RT + "/.venv" or full.startswith(ABS_RT + "/.venv/"):
            n += 1
            return ".venv" + full[len(ABS_RT + "/.venv"):] + trail
        if full == ABS_CH + "/compute.env":
            n += 1
            return ".env" + trail
        new = map_abs(full)
        if new is None:
            if full.startswith(ABS_RT):
                REP.unres(rel_for_report, 0, full, "absolute path with no new location")
                return m.group(0)
            n += 1
            return "collusion_hackathon" + full[len(ABS_CH):] + trail   # sprint repo files (template, criteria)
        n += 1
        return (new or ".") + trail

    text = ABS_RE.sub(abs_fix, text)

    def tok_fix(m):
        nonlocal n
        path = m.group("path")
        new = map_token_path(path)
        if new is None:
            REP.unres(rel_for_report, 0, m.group(0), "old-layout path token with no rule")
            return m.group(0)
        if path.split("/")[0] == "common" and len(path.split("/")) == 1:
            return m.group(0)
        n += 1
        return new

    text = OLD_TOKEN_RE.sub(tok_fix, text)

    def rt_fix(m):
        nonlocal n
        new = map_src_rel(m.group("path").rstrip("/"))
        if new is None:
            return m.group(0)
        n += 1
        return new

    text = RT_TOKEN_RE.sub(rt_fix, text)

    def dir_fix(m):
        nonlocal n
        d = m.group("a") or m.group("b")
        new = map_inv_rel(d + m.group("rest"))
        if new is None:
            return m.group(0)
        n += 1
        return new

    text = INV_DIR_TOKEN_RE.sub(dir_fix, text)

    def fstr_fix(m):
        nonlocal n
        new = map_token_path(m.group("path"))
        if new is None or new == m.group("path"):
            return m.group(0)
        n += 1
        return "{" + m.group("v") + "}/" + new

    text = FSTR_INV_RE.sub(fstr_fix, text)
    return text, n


def rewrite_dotdot_prose(text: str, ctx: Ctx, rel_for_report: str):
    n = 0

    def fix(m):
        nonlocal n
        url = m.group("url")
        core = url.rstrip(".,:;")
        tail = url[len(core):]
        old_target = posixpath.normpath(posixpath.join(ctx.old_dir, core))
        if not old_target.startswith(ABS_RT) or not os.path.exists(old_target):
            return m.group(0)
        new = map_abs(old_target)
        if new is None:
            return m.group(0)
        new_url = posixpath.relpath(new or ".", ctx.new_dir or ".")
        if core.endswith("/"):
            new_url += "/"
        if new_url != core:
            n += 1
            return new_url + tail
        return m.group(0)

    return DOTDOT_RE.sub(fix, text), n


# ---------------------------------------------------------------------------------------------------------------
# Python rewriting
# ---------------------------------------------------------------------------------------------------------------
ROOT_EXPR = "_argus_root()"
IMPORT_LINE = ("from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo"
               "  # noqa: E402,F401  (added by scripts/migrate.py)")

STR = r'"[^"\n]*"'
ATOM_RE = (r"(?P<atom>Path\(__file__\)(?:\.resolve\(\))?|Path\(\s*" + STR + r"\s*\)|"
           r"(?<![\w.])(?:[A-Za-z_]\w*\.(?=[A-Z_][A-Z0-9_]*\b))?[A-Za-z_]\w*)")
SUFFIX_RE = r"(?:\.parent\b(?!s)|\.parents\[\d+\]|\s*/\s*" + STR + r")"
CHAIN_RE = re.compile(ATOM_RE + r"(?P<suf>(?:" + SUFFIX_RE + r")+)")
ASSIGN_RE = re.compile(r"^(?P<ind>[ \t]*)(?P<var>[A-Za-z_]\w*)\s*=\s*(?P<rhs>[^#\n]+?)\s*(?P<cmt>#.*)?$", re.M)
ONE_SUFFIX = re.compile(r"\.parent\b(?!s)|\.parents\[(\d+)\]|\s*/\s*\"([^\"\n]*)\"")


def collapse_segments(src: str):
    # only inside a path chain: <name or call> / "a" / "b"  ->  <name or call> / "a/b"
    rx = re.compile(r'([\w)\]]\s*/\s*)"([\w.\-/]+)"\s*/\s*"([\w.\-/]+)"')
    prev = None
    while prev != src:
        prev = src
        src = rx.sub(lambda m: f'{m.group(1)}"{m.group(2)}/{m.group(3)}"', src)
    return src


def apply_suffixes(base: str, suf: str):
    """base: absolute posix path; suf: chain suffix text. Returns the resulting path."""
    p = base
    for m in ONE_SUFFIX.finditer(suf):
        s = m.group(0)
        if s.startswith(".parents["):
            for _ in range(int(m.group(1)) + 1):
                p = posixpath.dirname(p)
        elif s.startswith(".parent"):
            p = posixpath.dirname(p)
        else:
            p = posixpath.normpath(posixpath.join(p, m.group(2)))
    return p


class PyRewriter:
    """Evaluates simple path chains (VAR.parent / "lit" ...) against the old and the new location."""

    def __init__(self, ctx: Ctx, global_vars: dict, rel_for_report: str):
        self.ctx = ctx
        self.gv = global_vars          # "mod.VAR" or "VAR@file" -> old abs
        self.rel = rel_for_report
        self.old_file = str(ctx.old_abs)
        self.new_file = posixpath.join("/NEWROOT", ctx.new_rel)
        self.vars_old = {}             # VAR -> old abs path
        self.n = 0
        self.need_import = False

    def learn_imports(self, src: str):
        """Path variables that come from shared helper modules (`from cb_util import *`, `import bs`, `import x as y`)."""
        for m in re.finditer(r"^\s*from\s+(\w+)\s+import\s+\*", src, re.M):
            for k, v in MODULE_VARS.get(m.group(1), {}).items():
                self.vars_old.setdefault(k, v)
        for m in re.finditer(r"^\s*from\s+(\w+)\s+import\s+([\w, ]+)$", src, re.M):
            mv = MODULE_VARS.get(m.group(1), {})
            for nm in [x.strip() for x in m.group(2).split(",")]:
                if nm in mv:
                    self.vars_old.setdefault(nm, mv[nm])
        for m in re.finditer(r"\bimport\s+(\w+)(?:\s+as\s+(\w+))?", src):
            mod, alias = m.group(1), m.group(2) or m.group(1)
            for k, v in MODULE_VARS.get(mod, {}).items():
                self.gv.setdefault(f"{alias}.{k}", v)

    def atom_old(self, atom: str):
        if atom.startswith("Path(__file__)"):
            return self.old_file
        if atom.startswith("Path("):
            lit = re.search(r'"([^"]*)"', atom).group(1)
            return posixpath.normpath(lit) if lit.startswith("/") else None
        if "." in atom:
            mod, var = atom.split(".", 1)
            return self.gv.get(f"{mod}.{var}")
        return self.vars_old.get(atom)

    def atom_new(self, atom: str):
        """The value the unchanged atom would have in the new layout (NEWROOT-based), or None."""
        if atom.startswith("Path(__file__)"):
            return self.new_file
        old = self.atom_old(atom)
        if old is None:
            return None
        if atom.startswith("Path("):
            return None      # absolute literal: always replaced
        new = map_abs(old)
        return None if new is None else posixpath.normpath(posixpath.join("/NEWROOT", new))

    def root_expr(self, new_rel: str):
        self.need_import = True
        return ROOT_EXPR if new_rel in ("", ".") else f"({ROOT_EXPR} / '{new_rel}')"

    def eval_chain(self, atom, suf):
        old_base = self.atom_old(atom)
        if old_base is None:
            return None
        old_t = apply_suffixes(old_base, suf) if suf else old_base
        if old_t.endswith("/.venv/bin/python") or old_t.endswith("/.venv/bin/python3"):
            return ("expr", "Path(sys.executable)")
        if (old_t == ABS_CH or old_t.startswith(ABS_CH + "/")) and not (old_t == ABS_RT or old_t.startswith(ABS_RT + "/")):
            rest = old_t[len(ABS_CH) + 1:]
            self.need_import = True
            return ("expr", "_argus_sprint_repo()" if not rest else f"(_argus_sprint_repo() / '{rest}')")
        if not old_t.startswith(ABS_RT):
            return None
        if old_t == ABS_INV:
            if suf or atom.startswith("Path("):
                return ("replace", "")
            return None
        rel_inv = old_t[len(ABS_INV) + 1:] if old_t.startswith(ABS_INV + "/") else None
        if rel_inv and (rel_inv == "hunt" or (rel_inv.startswith("hunt/") and rel_inv.count("/") == 1
                                              and rel_inv.split("/")[1] in TEAMS)):
            # an old team (or hunt) folder: code joins old experiment IDs onto it, so use a mapping directory
            self.need_import = True
            return ("expr", f"_argus_legacy_dir('{rel_inv}')")
        new_t = map_abs(old_t)
        if new_t is None:
            if old_t.startswith(ABS_RT) and old_t != ABS_RT:
                return ("unresolved", old_t)
            return None
        nat_base = self.atom_new(atom)
        nat = apply_suffixes(nat_base, suf) if (nat_base and suf) else nat_base
        want = posixpath.normpath(posixpath.join("/NEWROOT", new_t))
        if nat == want:
            return ("same", new_t)
        return ("replace", new_t)

    def learn_assignments(self, src: str):
        """Record old values of VAR = <chain> assignments, in file order (first pass, on the old source)."""
        for m in ASSIGN_RE.finditer(src):
            var, rhs = m.group("var"), m.group("rhs").strip()
            val = self.eval_rhs(rhs)
            if val is not None:
                self.vars_old.setdefault(var, val)

    def eval_rhs(self, rhs: str):
        rhs = rhs.strip()
        if re.fullmatch(STR, rhs):
            lit = rhs[1:-1]
            return posixpath.normpath(lit) if lit.startswith(ABS_RT) else None
        m = re.fullmatch(r"os\.path\.dirname\(os\.path\.abspath\(__file__\)\)", rhs)
        if m:
            return posixpath.dirname(self.old_file)
        m = CHAIN_RE.fullmatch(rhs)
        if m:
            base = self.atom_old(m.group("atom"))
            return apply_suffixes(base, m.group("suf")) if base else None
        m = re.fullmatch(ATOM_RE, rhs)
        if m:
            return self.atom_old(rhs)
        return None

    def rewrite(self, src: str):
        out_lines = []
        for lineno, line in enumerate(src.split("\n"), 1):
            code, cmt = split_comment(line)
            new_code = self.rewrite_code_line(code, lineno)
            out_lines.append(new_code + cmt)
        return "\n".join(out_lines)

    def rewrite_code_line(self, code: str, lineno: int):
        if not code.strip():
            return code

        def fix(m):
            atom, suf = m.group("atom"), m.group("suf")
            if atom in ("self", "os", "sys", "np", "torch", "re", "json") or atom.startswith(("self.", "os.", "np.")):
                return m.group(0)
            r = self.eval_chain(atom, suf)
            if r is None:
                return m.group(0)
            kind, val = r
            if kind == "unresolved":
                REP.unres(self.rel, lineno, m.group(0), f"path chain points to {val} which has no new location")
                return m.group(0)
            if kind == "same":
                return m.group(0)
            if kind == "expr":
                self.n += 1
                return val
            self.n += 1
            return self.root_expr(val)

        new = CHAIN_RE.sub(fix, code)
        # bare assignment of a path variable whose meaning moved: VAR = Path(__file__).resolve().parents[2] etc. are
        # chains and handled above; VAR = "ABS" / Path("ABS") handled here
        def lit_fix(m):
            lit = m.group(1)
            if not (lit == ABS_RT or lit.startswith(ABS_RT + "/")):
                return m.group(0)
            if lit == ABS_RT + "/.venv/bin/python":
                self.n += 1
                return "sys.executable"
            new_t = map_abs(lit)
            if new_t is None:
                REP.unres(self.rel, lineno, lit, "absolute path literal with no new location")
                return m.group(0)
            self.n += 1
            expr = self.root_expr(new_t)
            return expr if m.group(0).startswith("Path(") else f"str({expr})"

        new = re.sub(r'Path\(\s*"(/[^"\n]*)"\s*\)', lit_fix, new)
        new = re.sub(r'(?<![\w{])"(/Users/[^"\n]*)"', lit_fix, new)
        # os.path.join(<var>, "..", "x") and os.path.dirname(<var>) on string-typed vars
        def osj_fix(m):
            var, args = m.group(1), m.group(2)
            base = self.vars_old.get(var)
            if base is None:
                return m.group(0)
            lits = re.findall(r'"([^"\n]*)"', args)
            if len(lits) != len([a for a in args.split(",") if a.strip()]):
                return m.group(0)
            old_t = posixpath.normpath(posixpath.join(base, *lits))
            new_t = map_abs(old_t)
            nat_base = map_abs(base)
            if new_t is None or nat_base is None:
                return m.group(0)
            if posixpath.normpath(posixpath.join(nat_base, *lits)) == new_t:
                return m.group(0)
            self.n += 1
            return f"str({self.root_expr(new_t)})"

        new = re.sub(r"os\.path\.join\(\s*([A-Za-z_]\w*)\s*,((?:\s*\"[^\"\n]*\"\s*,?)+)\)", osj_fix, new)

        def osd_fix(m):
            var = m.group(1)
            base = self.vars_old.get(var)
            if base is None:
                return m.group(0)
            old_t = posixpath.dirname(base)
            new_t = map_abs(old_t)
            nat_base = map_abs(base)
            if new_t is None or nat_base is None:
                return m.group(0)
            if posixpath.dirname(nat_base) == new_t:
                return m.group(0)
            self.n += 1
            return f"str({self.root_expr(new_t)})"

        new = re.sub(r"os\.path\.dirname\(\s*([A-Za-z_]\w*)\s*\)", osd_fix, new)
        return new


def split_comment(line: str):
    """Split a line into (code, '#comment') ignoring '#' inside simple string literals."""
    q = None
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if line.startswith(q, i):
                i += len(q)
                q = None
                continue
        else:
            if line.startswith(('"""', "'''"), i):
                q = line[i:i + 3]
                i += 3
                continue
            if c in "\"'":
                q = c
            elif c == "#":
                return line[:i], line[i:]
        i += 1
    return line, ""


def rewrite_common_imports(src: str, rel: str):
    """sys.path.insert(<common>) -> removed; `import budget` -> `from argus import budget`."""
    n = 0
    lines = src.split("\n")
    out = []
    for lineno, line in enumerate(lines, 1):
        code, cmt = split_comment(line)
        ind = re.match(r"[ \t]*", code).group(0)
        stmts = [s for s in re.split(r";\s*", code.strip())] if code.strip() else []
        new_stmts = []
        changed = False
        for s in stmts:
            if re.match(r"sys\.path\.insert\(", s):
                if re.search(r"""_argus_root\(\) / ['"]argus(/modal)?['"]\)""", s) or \
                   re.search(r"""(INV|COMMON)\s*/\s*['"]common(/modal)?['"]""", s) or \
                   re.search(r"""['"]\.\.['"]\s*,\s*['"]common['"]""", s) or \
                   re.search(r"""os\.path\.join\(\s*\w+\s*,\s*['"]common['"]\s*(,\s*['"]modal['"]\s*)?\)""", s) or re.search(r"""\(\s*['"][^'"]*/common(/modal)?['"]\s*\)""", s):
                    changed = True
                    n += 1
                    continue
            m = re.fullmatch(r"import\s+(.+)", s)
            if m:
                names = [x.strip() for x in m.group(1).split(",")]
                if names:
                    base = [nm.split(" as ")[0].strip() for nm in names]
                    if any(b in COMMON_MODS | MODAL_MODS for b in base):
                        keep = [nm for nm, b in zip(names, base) if b not in COMMON_MODS | MODAL_MODS]
                        com = [nm for nm, b in zip(names, base) if b in COMMON_MODS]
                        mod = [nm for nm, b in zip(names, base) if b in MODAL_MODS]
                        if keep:
                            new_stmts.append("import " + ", ".join(keep))
                        if com:
                            new_stmts.append("from argus import " + ", ".join(com))
                        if mod:
                            new_stmts.append("from argus.modal import " + ", ".join(mod))
                        changed = True
                        n += 1
                        continue
            m = re.fullmatch(r"from\s+(\w+)\s+import\s+(.+)", s)
            if m and m.group(1) in COMMON_MODS | MODAL_MODS:
                pkg = "argus" if m.group(1) in COMMON_MODS else "argus.modal"
                new_stmts.append(f"from {pkg}.{m.group(1)} import {m.group(2)}")
                changed = True
                n += 1
                continue
            new_stmts.append(s)
        if changed:
            if new_stmts:
                out.append(ind + "; ".join(new_stmts) + (("  " + cmt) if cmt else ""))
            elif cmt.strip():
                out.append(ind + "pass  " + cmt if code.strip().endswith(":") else ind + cmt)
            else:
                # keep block structure valid: a removed statement inside an if/for body becomes `pass`
                prev = out[-1] if out else ""
                if prev.rstrip().endswith(":"):
                    out.append(ind + "pass")
        else:
            out.append(line)
    return "\n".join(out), n


def inject_import(src: str):
    if IMPORT_LINE in src:
        return src
    lines = src.split("\n")
    i = 0
    # skip shebang / encoding / module docstring / __future__ imports
    if lines and lines[0].startswith("#!"):
        i = 1
    while i < len(lines) and (lines[i].startswith("#") or not lines[i].strip()):
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith(('"""', "'''", 'r"""')):
        q = '"""' if '"""' in lines[i] else "'''"
        if lines[i].count(q) >= 2 and len(lines[i].strip()) > 3:
            i += 1
        else:
            i += 1
            while i < len(lines) and q not in lines[i]:
                i += 1
            i += 1
    j = i
    while j < len(lines) and (lines[j].startswith("from __future__") or not lines[j].strip() or lines[j].startswith("#")):
        if lines[j].startswith("from __future__"):
            i = j + 1
        j += 1
    lines.insert(i, IMPORT_LINE)
    return "\n".join(lines)


MODULE_VARS: dict = {}


def collect_module_vars():
    """Old values of module-level path variables of every helper module with a unique name (two passes for imports)."""
    names = defaultdict(list)
    for f in INV.rglob("*.py"):
        if any(x in f.parts for x in ("external", "downloads", "__pycache__")):
            continue
        names[f.stem].append(f)
    for _ in range(2):
        for stem, fs in names.items():
            if len(fs) != 1:
                continue
            f = fs[0]
            ctx = Ctx(f, "x/y.py", Path("."), set(), {})
            ctx.dropped_lookup = set()
            pr = PyRewriter(ctx, {}, "")
            src = f.read_text(errors="ignore")
            pr.learn_imports(src)
            pr.learn_assignments(collapse_segments(src))
            MODULE_VARS[stem] = {k: v for k, v in pr.vars_old.items() if k.isupper() or k in ("HERE",)}


def collect_global_vars():
    """Old values of module-level path variables in shared helper modules (bs.TEAM, dc.INV, ...)."""
    gv = {}
    alias_files = {
        "bs": INV / "hunt/brain_surgeons/_lib/bs.py",
        "dc": INV / "hunt/detectives/det_common.py",
        "cb": INV / "hunt/codebreakers/cb_util.py",
        "cbu": INV / "hunt/codebreakers/cb_util.py",
        "L": None,
        "budget": INV / "common/budget.py",
    }
    for alias, f in alias_files.items():
        if f is None or not f.exists():
            continue
        ctx = Ctx(f, "x/y.py", Path("."), set(), {})
        ctx.dropped_lookup = set()
        pr = PyRewriter(ctx, {}, "")
        pr.learn_assignments(collapse_segments(f.read_text()))
        for k, v in pr.vars_old.items():
            gv[f"{alias}.{k}"] = v
    # L = the localizers' shared lib imported as L in L1/L2 (l1_gpu or a lib module)
    for f in (INV / "hunt/localizers").glob("*/*.py"):
        pass
    return gv


# ---------------------------------------------------------------------------------------------------------------
# Walk and classify
# ---------------------------------------------------------------------------------------------------------------
def citation_text():
    """All text that can cite a run directory: RESULT.md, report.json, REPORT.html, CLUE_BOARD.md, writeups."""
    chunks = []
    for pat in ("**/RESULT.md", "**/report.json", "**/REPORT.html", "**/report.v2.json"):
        for p in INV.glob(pat):
            if "external" in p.parts or "downloads" in p.parts:
                continue
            try:
                chunks.append(p.read_text(errors="ignore"))
            except OSError:
                pass
    chunks.append((INV / "hunt/CLUE_BOARD.md").read_text(errors="ignore"))
    for p in (INV / "writeups").glob("*.md"):
        chunks.append(p.read_text(errors="ignore"))
    return "\n".join(chunks)


def classify(rel_inv: str, p: Path, is_dir: bool, cites: str):
    """Return (action, class, note). action in copy|skip|drop_regen|drop_public|drop_noise|drop_view|special."""
    name = p.name
    parts = rel_inv.split("/")
    if name in NOISE_FILES:
        return "skip", "noise", ".DS_Store"
    if rel_inv in NOT_COPIED:
        return "skip", "folded", NOT_COPIED[rel_inv]
    if is_dir and name in NOISE_DIRS:
        return "drop_noise", "noise", name
    if rel_inv in NOISE_PATHS:
        return "drop_noise", "noise", NOISE_PATHS[rel_inv]
    if ".bak" in name:
        return "drop_noise", "noise", "backup file"
    if is_dir and (name in PUBLIC_DIR_NAMES or rel_inv in PUBLIC_DATA_SUBDIRS):
        return "drop_public", "public", name
    if is_dir and "results" in parts[:-1] and (name == "inspect" or name.startswith("inspect_")):
        return "drop_view", "derived view", name
    if is_dir and name.startswith("run_") and "smoke" in name and ("results" in parts or "_sessions" in parts):
        if name in cites:
            return "copy", "cited smoke run", ""
        return "drop_noise", "uncited smoke run", name
    if not is_dir:
        size = p.stat().st_size
        if p.suffix in BINARY_EXT and size > REGEN_LIMIT:
            return "drop_regen", "regenerable binary", ""
        if size > HARD_LIMIT:
            return "error", "over 95 MB", ""
        if size > REGEN_LIMIT and p.suffix in {".gz", ".zip", ".parquet", ".pack"}:
            return "drop_public", "public archive", ""
    return "copy", "", ""


def regen_command(run_dir_old: Path, exp):
    cfg = run_dir_old / "config.json"
    if cfg.exists():
        try:
            c = json.loads(cfg.read_text())
            argv = c.get("argv")
            if argv:
                script = os.path.basename(argv[0])
                args = []
                for a in argv[1:]:
                    a = str(a)
                    if a.startswith(ABS_CH):
                        a = map_abs(a) or a
                    args.append(a)
                where = exp["new"] if exp else "."
                return f"`uv run {where}/{script} {' '.join(args)}`".replace(" `", "`") + " (argv from this run's config.json)"
        except Exception:
            pass
    return "re-run the stage that wrote this run (see its log.txt and the experiment's RESULT.md)"


def walk(dst: Path, dry: bool):
    """Plan every copy. Returns (copies, drops) where copies = [(old_abs, new_rel, kind)]."""
    cites = citation_text()
    copies = []
    drops = []        # dicts: old, new_parent, kind, size, sha, note, cls
    dropped_lookup = set()

    def rec_drop(p: Path, rel_inv: str, action, cls, note):
        dropped_lookup.add(str(p))
        if p.is_dir():
            files = [f for f in p.rglob("*") if f.is_file()]
            size = sum(f.stat().st_size for f in files)
        else:
            files, size = [p], p.stat().st_size
        drops.append(dict(old=rel_inv, abs=str(p), action=action, cls=cls, note=note, size=size, nfiles=len(files),
                          is_dir=p.is_dir()))

    def visit(d: Path):
        for p in sorted(d.iterdir()):
            rel_inv = p.relative_to(INV).as_posix()
            action, cls, note = classify(rel_inv, p, p.is_dir(), cites)
            if action == "skip":
                continue
            if action.startswith("drop"):
                rec_drop(p, rel_inv, action, cls, note)
                continue
            if action == "error":
                REP.errors.append(f"{rel_inv}: {cls}")
                continue
            if p.is_dir():
                visit(p)
            else:
                new = map_inv_rel(rel_inv)
                if new is None:
                    REP.unres(rel_inv, 0, rel_inv, "source file with no destination rule")
                    continue
                copies.append((p, new, "inv"))
                if rel_inv in EXTRA_COPIES:
                    copies.append((p, EXTRA_COPIES[rel_inv], "inv"))

    visit(INV)
    # redteaming/ level
    for rel, new in RT_MAP.items():
        copies.append((SRC / rel, new, "rt"))
    for p in sorted(SRC.iterdir()):
        if p.is_file() and p.name not in RT_MAP and p.name not in RT_NOT_COPIED:
            REP.unres(p.name, 0, p.name, "redteaming/ file not in the plan; not copied")
    return copies, drops, dropped_lookup


# ---------------------------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------------------------
def prediction_header(e):
    team = TEAM_NAMES[e["team"]]
    orig = e["old"] if e["team"] == "prelude" else e["old"]
    return f"Hunt code: {e['code']}; team: {team}; original path: {orig}\n\n"


def process_text(old_abs: Path, new_rel: str, ctx: Ctx, gv: dict):
    raw = old_abs.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw, 0
    orig = text
    n_total = 0
    suffix = old_abs.suffix
    in_results = "/results/" in str(old_abs) or "/_sessions/" in str(old_abs)
    in_data = "/data/" in str(old_abs)
    if suffix == ".py":
        text = collapse_segments(text)
        pr = PyRewriter(ctx, dict(gv), new_rel)
        pr.learn_imports(orig)
        pr.learn_assignments(collapse_segments(orig))
        text = pr.rewrite(text)
        n_total += pr.n
        text, n = rewrite_prose_paths(text, ctx, new_rel, is_py=True)
        n_total += n
        text, n = rewrite_common_imports(text, new_rel)
        n_total += n
        if pr.need_import or ROOT_EXPR in text:
            text = inject_import(text)
        text, n = re.subn(r'(os\.path\.join\([^)\n]*?)"(M1_secret_keeper|M2_trigger_steered|M3_synthetic_stego)"',
                          lambda m: m.group(1) + '"' + ORGANISMS[m.group(2)] + '"', text)
        n_total += n
    elif suffix in (".html", ".htm", ".md") or (suffix == ".json" and not in_results and not in_data):
        text, n = rewrite_links(text, ctx, new_rel)
        n_total += n
        text, n = rewrite_prose_paths(text, ctx, new_rel)
        n_total += n
        if suffix in (".md", ".json"):
            text, n = rewrite_dotdot_prose(text, ctx, new_rel)
            n_total += n
    elif suffix in TEXT_EXT and not in_results and not in_data:
        text, n = rewrite_prose_paths(text, ctx, new_rel)
        n_total += n
    if old_abs.name == "PREDICTION.md":
        e = exp_of_old(old_abs.relative_to(INV).as_posix()) if str(old_abs).startswith(ABS_INV) else None
        if e and old_abs.parent == INV / e["old"]:
            text = prediction_header(e) + text
            n_total += 1
    for a, b in MANUAL_FIXES.get(new_rel, []):
        if a in text:
            text = text.replace(a, b)
            n_total += 1
        else:
            REP.unres(new_rel, 0, a[:120], "manual fix did not apply")
    # drop unresolved notes whose text a hand fix removed
    keep = [u for u in REP.unresolved if not (u[0] == new_rel and u[3] != "manual fix did not apply"
                                              and _snippet(u) and _snippet(u) not in text)]
    REP.unresolved[:] = keep
    if text != orig:
        return text.encode("utf-8"), n_total
    return raw, 0


def _snippet(u):
    m = re.search(r"([\w.]+(?: / \"[^\"]*\")+)", u[2])
    return m.group(1) if m and "path chain" in u[3] else None


def scan_leftovers(new_rel: str, text: str):
    """Flag anything in a .py file that still looks like an old-layout path."""
    pats = [
        (r"/Users/asthamehta", "absolute user path"),
        (r"[\"'](?:hunt|common)(?:/|[\"'])", "old INV-relative literal"),
        (r"\bhunt/(?:%s)" % "|".join(TEAMS), "old hunt/<team> path"),
        (r"(?:/\s*|os\.path\.join\([^)]*)\"(?:%s)\"" % "|".join(TEAMS), "old team-name path literal"),
        (r"\.parent\.parent|\.parents\[[2-9]\]", "deep parent chain"),
        (r"\"\.\.\"\s*,", "os.path '..' join"),
        (r"/\s*\"(?:[A-Z]\d+[a-z]?_[a-z_]+)\"", "old experiment folder literal"),
    ]
    for lineno, line in enumerate(text.split("\n"), 1):
        code, _ = split_comment(line)
        if "migrate: ok" in line or ".parent.parent.name" in code or "_argus_legacy_dir(" in code:
            continue
        if not code.strip() or code.lstrip().startswith(("\"\"\"", "'''")):
            continue
        for rx, why in pats:
            if re.search(rx, code):
                REP.unres(new_rel, lineno, code, why)
                break


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dst", type=Path, default=DST_DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", type=Path, default=None)
    ap.add_argument("--only", default=None, help="re-sync only destination paths under this prefix (e.g. writeups/); "
                    "nothing else is written, no notes or manifests are regenerated")
    ap.add_argument("--hash-cache", type=Path, default=Path(os.environ.get("TMPDIR", "/tmp")) / "argus_migrate_hashes.json")
    a = ap.parse_args()
    dst = a.dst.resolve()
    if str(dst).startswith(str(SRC.parent) + "/"):
        sys.exit("destination is inside the source repository; refusing")
    global _hash_cache
    if a.hash_cache.exists():
        _hash_cache = json.loads(a.hash_cache.read_text())
    t0 = time.time()
    copies, drops, dropped_lookup = walk(dst, a.dry_run)
    copied_set = {new for _, new, _ in copies}
    collect_module_vars()
    gv = collect_global_vars()
    written_manifest = []
    per_dir_notes = defaultdict(list)    # new rel file (DROPPED.md / data/README.md) -> lines

    # drops -> notes
    for d in drops:
        old_abs = Path(d["abs"])
        rel_inv = d["old"]
        e = exp_of_old(rel_inv)
        if d["action"] == "drop_regen":
            sha = sha256_file(old_abs)
            m = re.search(r"^(.*?/results/run_[^/]+)", rel_inv)
            run_rel = m.group(1) if m else posixpath.dirname(rel_inv)
            note_file = posixpath.join(map_inv_rel(run_rel), "DROPPED.md")
            cmd = regen_command(INV / run_rel, e) if m else "re-run the script that wrote it (see the folder's README or RESULT.md)"
            inner = posixpath.relpath(rel_inv, run_rel)
            per_dir_notes[note_file].append(
                f"| `{inner}` | {d['size']:,} | `{sha}` | regenerable binary (> 5 MB, not committed) | {cmd} |")
            d["sha"] = sha
        elif d["action"] == "drop_public":
            base = e["new"] if e else (map_inv_rel(posixpath.dirname(rel_inv)) or "")
            note_file = posixpath.join(base, "data", "README.md") if e else posixpath.join(base, "DATA_SOURCES.md")
            src_url, rev = None, None
            for k in sorted(PUBLIC_SOURCES, key=len, reverse=True):
                if rel_inv == k or rel_inv.startswith(k + "/"):
                    src_url, rev = PUBLIC_SOURCES[k]
                    break
            inner = posixpath.relpath(rel_inv, e["old"]) if e else rel_inv
            files = [old_abs] if old_abs.is_file() else sorted(f for f in old_abs.rglob("*") if f.is_file())
            git_like = [f for f in files if "/.git/" in str(f) or "/.cache/" in str(f)]
            files = [f for f in files if f not in git_like]
            if src_url is None:
                src_url, rev = "public file (source in the experiment's make_data/build_data script)", "-"
                REP.unres(rel_inv, 0, rel_inv, "public download with no recorded source URL")
            for f in files:
                fi = posixpath.relpath(f.relative_to(INV).as_posix(), e["old"]) if e else f.relative_to(INV).as_posix()
                per_dir_notes[note_file].append(
                    f"| `{fi}` | {f.stat().st_size:,} | `{sha256_file(f)}` | public download, not committed | {src_url} @ {rev} |")
            if git_like:
                per_dir_notes[note_file].append(
                    f"| `{inner}/` (.git and download caches, {len(git_like)} files) | {sum(f.stat().st_size for f in git_like):,} | - | clone / cache metadata | {src_url} @ {rev} |")
        elif d["action"] == "drop_view":
            m = re.search(r"^(.*?/results/run_[^/]+)", rel_inv)
            run_rel = m.group(1) if m else posixpath.dirname(rel_inv)
            note_file = posixpath.join(map_inv_rel(run_rel), "DROPPED.md")
            inner = posixpath.relpath(rel_inv, run_rel)
            per_dir_notes[note_file].append(
                f"| `{inner}/` ({d['nfiles']} files) | {d['size']:,} | - | inspector view copy of this run's outputs/prompts/rows (renamed fields, no new values) | rebuild with the experiment's build_rows / build_pages / build_data script (CPU, $0) |")

    for d in drops:
        REP.dropped.append((d["old"], d["size"], d["cls"], d.get("note", "")))

    # copies
    hdr_regen = ("# Files not committed from this run\n\nThese files existed in the original run directory but are not in the repository "
                 "(docs/MIGRATION_PLAN.md, section 4 and Amendment 1). Regenerable binaries can be rebuilt with the command shown "
                 "(`uv run scripts/fetch_results.py --list` lists them all); inspector view copies are derived from files that are here.\n\n"
                 "| File | Bytes | sha256 | Class | How to recreate |\n|---|---:|---|---|---|\n")
    hdr_public = ("# Public data not committed\n\nThese public files were downloaded for this experiment and are not in the repository "
                  "(docs/MIGRATION_PLAN.md, Amendment 1). Fetch them from the source shown before re-running the stage that reads them.\n\n"
                  "| File | Bytes | sha256 | Class | Source @ revision |\n|---|---:|---|---|---|\n")

    total_bytes = 0
    if a.only:
        copies = [c for c in copies if c[1].startswith(a.only)]
    for old_abs, new_rel, kind in copies:
        if not old_abs.exists():
            REP.unres(new_rel, 0, str(old_abs), "source file vanished during the copy (the source tree was being edited)")
            continue
        ctx = Ctx(old_abs, new_rel, dst, copied_set, {})
        ctx.dropped_lookup = dropped_lookup
        if old_abs.suffix in TEXT_EXT or old_abs.suffix == ".htm":
            data, n = process_text(old_abs, new_rel, ctx, gv)
            if n:
                REP.change(new_rel, f"{n} rewrites", n)
            if old_abs.suffix == ".py":
                try:
                    scan_leftovers(new_rel, data.decode("utf-8"))
                except UnicodeDecodeError:
                    pass
        else:
            data = None
        size = len(data) if data is not None else old_abs.stat().st_size
        if size > HARD_LIMIT:
            REP.errors.append(f"{new_rel}: {size} bytes > 95 MB; not written")
            continue
        total_bytes += size
        REP.copied += 1
        if not a.dry_run:
            out = dst / new_rel
            out.parent.mkdir(parents=True, exist_ok=True)
            if data is None:
                shutil.copy2(old_abs, out)
            else:
                out.write_bytes(data)
                shutil.copystat(old_abs, out)
        sha = hashlib.sha256(data).hexdigest() if data is not None else sha256_file(old_abs)
        written_manifest.append({"path": new_rel, "source": str(old_abs.relative_to(SRC.parent)), "size": size,
                                 "sha256": sha, "rewritten": data is not None and data != old_abs.read_bytes()})

    if a.only:
        print(f"--only {a.only}: {REP.copied} files written, {REP.rewrites} rewrites; unresolved: {len(REP.unresolved)}")
        for u in REP.unresolved:
            print(f"UNRESOLVED: {u[0]}:{u[1]}: {u[3]}: {u[2]}")
        return 0
    # history -> dolos/ui_history.jsonl
    hist = sorted((SRC / "history").glob("*.json"))
    lines = []
    for h in hist:
        try:
            lines.append(json.dumps(json.loads(h.read_text()), ensure_ascii=False))
        except Exception as ex:
            REP.unres(f"history/{h.name}", 0, str(ex), "unreadable history file")
    blob = ("\n".join(lines) + "\n").encode("utf-8")
    total_bytes += len(blob)
    if not a.dry_run:
        (dst / "dolos").mkdir(parents=True, exist_ok=True)
        (dst / "dolos/ui_history.jsonl").write_bytes(blob)
    written_manifest.append({"path": "dolos/ui_history.jsonl", "source": f"collusion_hackathon/redteaming/history/*.json ({len(hist)} files)",
                             "size": len(blob), "sha256": hashlib.sha256(blob).hexdigest(), "rewritten": True})
    REP.change("dolos/ui_history.jsonl", f"{len(hist)} history JSON files combined", 0)

    # PREDICTION.md for prelude stages that have none
    for e in EXPS:
        if e["team"] == "prelude" and not (INV / e["old"] / "PREDICTION.md").exists():
            text = (prediction_header(e) + f"# Prediction (none written)\n\nThis prelude stage ran on 2026-10-24, before the hunt's "
                    f"pre-registration rule existed, so it has no prediction. Its findings are summarised in "
                    f"`dolos/INVESTIGATION_LOG.md`.\n").encode()
            rel = f"{e['new']}/PREDICTION.md"
            if not a.dry_run:
                (dst / rel).parent.mkdir(parents=True, exist_ok=True)
                (dst / rel).write_bytes(text)
            written_manifest.append({"path": rel, "source": "(generated by migrate.py)", "size": len(text),
                                     "sha256": hashlib.sha256(text).hexdigest(), "rewritten": True})
            REP.change(rel, "created (prelude stage had no PREDICTION.md)", 0)

    # notes
    for note_file, rows in sorted(per_dir_notes.items()):
        is_public = note_file.endswith("data/README.md") or note_file.endswith("DATA_SOURCES.md")
        existing = (dst / note_file).read_text() if (not a.dry_run and (dst / note_file).exists()) else ""
        body = (existing.rstrip() + "\n\n" if existing else "") + (hdr_public if is_public else hdr_regen) + "\n".join(rows) + "\n"
        blob = body.encode()
        if not a.dry_run:
            (dst / note_file).parent.mkdir(parents=True, exist_ok=True)
            (dst / note_file).write_bytes(blob)
        written_manifest = [w for w in written_manifest if w["path"] != note_file]
        written_manifest.append({"path": note_file, "source": "(generated by migrate.py)", "size": len(blob),
                                 "sha256": hashlib.sha256(blob).hexdigest(), "rewritten": True})
        REP.change(note_file, f"{len(rows)} dropped-file lines", 0)

    # argus/paths.py (template) and the mapping it reads
    lm = {"prefix_rules": [[o, n] for o, n in PREFIX_RULES if o != ".sealed"],
          "experiments": [dict(e, team_name=TEAM_NAMES[e["team"]]) for e in EXPS]}
    for rel, blob in (("argus/legacy_map.json", (json.dumps(lm, indent=1) + "\n").encode()),
                      ("argus/paths.py", (Path(__file__).resolve().parent / "templates/paths.py").read_bytes()),
                      ("argus/__init__.py", (Path(__file__).resolve().parent / "templates/__init__.py").read_bytes())):
        if not a.dry_run:
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            (dst / rel).write_bytes(blob)
        written_manifest.append({"path": rel, "source": "(generated by migrate.py)", "size": len(blob),
                                 "sha256": hashlib.sha256(blob).hexdigest(), "rewritten": True})
        REP.change(rel, "generated", 0)

    # manifest of dropped files (for fetch_results.py) and of written files (for the tier-0 test)
    dropped_manifest = []
    for d in drops:
        if d["action"] in ("drop_regen", "drop_public"):
            e = exp_of_old(d["old"])
            dropped_manifest.append({"old": d["old"], "new": map_inv_rel(d["old"]), "size": d["size"], "sha256": d.get("sha"),
                                     "class": d["cls"], "experiment": e["new"] if e else None,
                                     "regen": regen_command(INV / re.search(r"^(.*?/results/run_[^/]+)", d["old"]).group(1), e)
                                     if d["action"] == "drop_regen" and re.search(r"/results/run_", d["old"]) else None})
    if not a.dry_run:
        (dst / "docs").mkdir(exist_ok=True)
        (dst / "docs/migration_manifest.jsonl").write_text("".join(json.dumps(w) + "\n" for w in sorted(written_manifest, key=lambda w: w["path"])))
        (dst / "docs/dropped_files.json").write_text(json.dumps(dropped_manifest, indent=1))
    a.hash_cache.write_text(json.dumps(_hash_cache))

    if a.report:
        write_report(a.report if a.report.is_absolute() else dst / a.report, a.dry_run, total_bytes, drops, time.time() - t0,
                     len(written_manifest))
    print(f"{'DRY RUN: ' if a.dry_run else ''}{REP.copied} files, {total_bytes/1e9:.2f} GB, {REP.rewrites} rewrites in "
          f"{len(REP.changed)} files, {len(REP.unresolved)} unresolved, {len(drops)} dropped items, {len(REP.errors)} errors, "
          f"{time.time()-t0:.0f} s")
    for path, whats in sorted(REP.changed.items()):
        print(f"changed: {path}: {'; '.join(whats)}")
    for u in REP.unresolved:
        print(f"UNRESOLVED: {u[0]}:{u[1]}: {u[3]}: {u[2]}")
    for e in REP.errors:
        print(f"ERROR: {e}")
    return 1 if REP.errors else 0


def write_report(path: Path, dry: bool, total_bytes: int, drops, secs: float, n_manifest: int):
    by_cls = defaultdict(lambda: [0, 0])
    for d in drops:
        by_cls[d["cls"]][0] += 1
        by_cls[d["cls"]][1] += d["size"]
    L = [f"# Migration report ({'dry run' if dry else 'real run'}, {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())})", "",
         "Produced by `scripts/migrate.py`" + (" --dry-run" if dry else "") + ". Source (read-only): "
         "`collusion_hackathon/redteaming/`. Plan: `docs/MIGRATION_PLAN.md` (with Amendment 1).", "",
         "## Totals", "",
         f"- Files written: {n_manifest} ({total_bytes/1e9:.2f} GB before git compression)",
         f"- Path and import rewrites: {REP.rewrites} in {len(REP.changed)} files",
         f"- Unresolved paths: {len(REP.unresolved)}",
         f"- Links already broken in the source (unchanged): {len(REP.broken)}",
         f"- Dropped items: {len(drops)}",
         f"- Errors: {len(REP.errors)}", f"- Time: {secs:.0f} s", "",
         "## Dropped (not copied)", "", "| Class | Items | Bytes |", "|---|---:|---:|"]
    for c, (n, b) in sorted(by_cls.items()):
        L.append(f"| {c} | {n} | {b:,} |")
    L += ["", "<details><summary>Every dropped item</summary>", "", "| Old path (INV-relative) | Bytes | Class |", "|---|---:|---|"]
    for d in sorted(drops, key=lambda d: d["old"]):
        L.append(f"| `{d['old']}` | {d['size']:,} | {d['cls']} |")
    L += ["", "</details>", "", "## Unresolved paths", "",
          "Each line is a path the script could not map automatically, or a pattern left for a hand fix. Hand fixes live in "
          "`scripts/migrate_fixes.py` and are applied on the next run.", ""]
    if REP.unresolved:
        L += ["| File | Line | Why | Text |", "|---|---:|---|---|"]
        for f, ln, txt, why in REP.unresolved:
            L.append(f"| `{f}` | {ln} | {why} | `{txt.replace('|', '¦').replace('`', '')}` |")
    else:
        L.append("None.")
    L += ["", "## Links already broken in the source (left unchanged)", "",
          f"{len(REP.broken)} links in copied HTML/Markdown pointed at files that did not exist in the source tree, or at local files "
          "outside it (`file://` links to the sprint repository). They were not changed by the migration; the link checker in "
          "`scripts/check_repo.py` lists any that remain in the files it checks.", ""]
    if REP.broken:
        L += ["| File | Link | Why |", "|---|---|---|"]
        for f, u, why in REP.broken:
            L.append(f"| `{f}` | `{u[:160].replace('|', '¦').replace('`', '')}` | {why} |")
    L += ["", "## Errors", ""] + ([f"- {e}" for e in REP.errors] or ["None."])
    L += ["", "## Every file changed", "", "<details><summary>" + f"{len(REP.changed)} files" + "</summary>", "",
          "| File | Change |", "|---|---|"]
    for p, whats in sorted(REP.changed.items()):
        L.append(f"| `{p}` | {'; '.join(whats)} |")
    L += ["", "</details>", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
