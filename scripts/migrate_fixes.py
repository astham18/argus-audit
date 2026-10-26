"""Hand fixes for scripts/migrate.py: {new repo-relative path: [(old text, new text), ...]}.

Each entry resolves one line that the generic rewrite in migrate.py could not map (see docs/MIGRATION_REPORT.md,
"Unresolved paths"). The old text is matched after the generic rewrite has run.
"""
IMP = "from argus.paths import root as _argus_root  # noqa: E402"

MANUAL_FIXES = {
    # generate.py now lives in vendor/
    "argus/harness.py": [
        ('sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))  # redteaming/ for generate.py',
         IMP + "\nsys.path.insert(0, str(_argus_root() / \"vendor\"))  # vendor/generate.py (unchanged starter script)"),
    ],
    "argus/modal/batch_generate.py": [
        ("    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))\n    from argus import budget\n",
         "    from argus import budget\n"),
        ("            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))\n            from argus.gpu_queue import gpu_lock\n",
         "            from argus.gpu_queue import gpu_lock\n"),
        ('str(Path(__file__).resolve().parent.parent / "smoke_runs/batch_generate" /',
         'str(Path(__file__).resolve().parents[2] / "results" / "smoke" / "batch_generate" /  # migrate: ok (repo root)'),
    ],
    "argus/modal/volume_setup.py": [
        ("    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # common/ for budget.py\n    from argus import budget\n",
         "    from argus import budget\n"),
    ],
    "argus/organisms/_mo_util.py": [
        ('INV = os.path.abspath(str(_argus_root()))\nCOMMON = os.path.join(INV, "common")\nif COMMON not in sys.path:\n    sys.path.insert(0, COMMON)\n',
         "INV = str(_argus_root())\n"),
        ('path = os.path.join(INV, "hunt", ".gpu.lock")', 'path = os.path.join(INV, ".gpu.lock")'),
    ],
    # absolute HF-cache paths -> resolved through huggingface_hub at the pinned revisions
    "experiments/black_box/payload_in_actions_meaning_sampling/run.py": [
        ('SAFET = {"qwen": "/Users/asthamehta/.cache/huggingface/hub/models--Qwen--Qwen2.5-1.5B-Instruct/snapshots/989aa7980e4cf806f80c7fef2b1adb7bc71aa306/model.safetensors",\n'
         '         "dolos": "/Users/asthamehta/.cache/huggingface/hub/models--Poseidon-Research--Dolos-1.5B/snapshots/63e7031a0535a49f86e08af4e7bdc45cfa22fe6d/model.safetensors"}',
         'class _HFSafetensors(dict):\n'
         '    """model.safetensors in the local HF cache at the pinned revisions (downloaded on first use)."""\n'
         '    REVS = {"qwen": ("Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"),\n'
         '            "dolos": ("Poseidon-Research/Dolos-1.5B", "63e7031a0535a49f86e08af4e7bdc45cfa22fe6d")}\n'
         '    def __missing__(self, k):\n'
         '        from huggingface_hub import hf_hub_download\n'
         '        repo, rev = self.REVS[k]\n'
         '        self[k] = hf_hub_download(repo, "model.safetensors", revision=rev)\n'
         '        return self[k]\n'
         '    def __contains__(self, k):\n'
         '        return k in self.REVS\n'
         'SAFET = _HFSafetensors()'),
    ],
    # sampled installed-package source files as "code" prompts: use this environment's site-packages
    "experiments/white_box/representation_diffing/make_data.py": [
        ('glob.glob(str(bs.INV.parent / ".venv/lib/python3.11/site-packages/**/*.py"), recursive=True)',
         'glob.glob(str(__import__("pathlib").Path(__import__("sysconfig").get_paths()["purelib"]) / "**/*.py"), recursive=True)'),
    ],
    # UI: the run history folder (the old history/ is archived as dolos/ui_history.jsonl)
    "ui/app.py": [
        ("default=(_argus_root() / 'dolos/ui_history.jsonl')", 'default=HERE / "history"'),
    ],
}

MANUAL_FIXES.update({
    # a two-line absolute literal: the folder of this script
    "experiments/black_box/collusion_capability_battery/build_data.py": [
        ('HERE = Path(str((_argus_root() / \'vendor\'))\n            "experiments/black_box/collusion_capability_battery")',
         "HERE = Path(__file__).resolve().parent"),
    ],
    # nested double quotes inside an f-string are a syntax error before Python 3.12
    "experiments/black_box/counterfactual_rebuild_dose/train_all.py": [
        ("rd.relative_to(_argus_legacy_dir('hunt'))", "rd.relative_to(_argus_root())"),
    ],
})

MANUAL_FIXES["experiments/black_box/collusion_capability_battery/build_data.py"].append(
    ('B1 = HERE.parent / "B1_paired_battery/data"', "B1 = (_argus_root() / 'experiments/black_box/paired_capability_battery/data')"))
MANUAL_FIXES["experiments/black_box/self_report_finetune_v2/train.py"] = [
    ('assert "R2_rebuild_recipe" in TM.__file__, TM.__file__', 'assert "counterfactual_rebuild_plain" in TM.__file__, TM.__file__'),
]

MANUAL_FIXES["experiments/black_box/rewrite_choice_diff/run.py"] = [
    ("__import__('budget').modal_cost", "__import__('argus.budget', fromlist=['budget']).modal_cost"),
]
