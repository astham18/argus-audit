"""argus.paths - where things live in the repository.

    from argus.paths import root, experiment, legacy, legacy_dir, sprint_repo
    root()                                  # repository root: $ARGUS_ROOT, else found by walking up from this file
    experiment("credential_relay_task")     # an experiment folder by name, old code ("A1") or old folder ("A1_secret_courier")
    legacy("hunt/agents/A1_secret_courier/data")   # an old investigation-relative path -> its new location
    legacy_dir("hunt/detectives") / "D2b_prefill"  # an old team folder whose `/` maps old child names to new folders
    sprint_repo()                           # the sprint starter repository ($ARGUS_SPRINT_REPO); only data builders need it

The mapping comes from scripts/migrate.py (argus/legacy_map.json). Experiment scripts written for the original
layout (collusion_hackathon/redteaming/investigation, "INV") were rewritten to call these helpers.
"""
from __future__ import annotations

import json
import os
import posixpath
from functools import lru_cache
from pathlib import Path

_HERE = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def root() -> Path:
    """The repository root. $ARGUS_ROOT wins; else the first parent of argus/ that has pyproject.toml."""
    env = os.environ.get("ARGUS_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    for p in [_HERE, *_HERE.parents]:
        if (p / "pyproject.toml").exists() and (p / "argus").is_dir():
            return p
    return _HERE.parent


def sprint_repo() -> Path:
    """The AI Collusion Research Sprint starter repository (the organisers' public sibling repos such as focal-points/,
    llm-agent-collusion/, steganographic-collusion/). Only scripts that rebuild input data read it; every experiment's
    data/ already holds what they built. $ARGUS_SPRINT_REPO wins; else a sibling folder ../collusion_hackathon. The
    path may not exist: reading from it then fails with FileNotFoundError naming the file."""
    env = os.environ.get("ARGUS_SPRINT_REPO")
    if env:
        return Path(env).expanduser().resolve()
    return root().parent / "collusion_hackathon"


@lru_cache(maxsize=1)
def _map():
    return json.loads((_HERE / "legacy_map.json").read_text())


def legacy_rel(old: str) -> str | None:
    """Old investigation-relative path -> repo-relative path ('' = root), or None if there is no rule."""
    old = str(old).replace("\\", "/").strip("/")
    for pre in ("collusion_hackathon/redteaming/investigation/", "redteaming/investigation/", "investigation/", "INV/"):
        if old.startswith(pre):
            old = old[len(pre):]
    if old in ("", "."):
        return ""
    for o, n in _map()["prefix_rules"]:
        if old == o:
            return n
        if old.startswith(o + "/"):
            rest = old[len(o) + 1:]
            return posixpath.join(n, rest) if n else rest
    return None


def legacy(old: str) -> Path:
    """Old investigation-relative path -> absolute new Path (unmapped paths stay under the root as given)."""
    rel = legacy_rel(old)
    return root() / (rel if rel is not None else str(old))


def experiment(key: str) -> Path:
    """Experiment folder by new name, old code (A1, D2a, ...) or old folder name (A1_secret_courier)."""
    for e in _map()["experiments"]:
        if key in (e["name"], e["code"], e["old_id"], e["new"], e["old"]):
            return root() / e["new"]
    raise KeyError(f"unknown experiment {key!r}")


class LegacyDir(type(Path())):
    """A Path for an old team or hunt folder. `str()` is its new folder (experiments/_shared/<team> or experiments);
    `/ "name"` resolves the old child path (an experiment ID, a shared helper, data/) to wherever it moved."""

    def __new__(cls, old: str):
        rel = legacy_rel(old)
        self = super().__new__(cls, root() / (rel if rel is not None else old))
        self._legacy_old = str(old).strip("/")
        return self

    def __init__(self, old: str = "", *args):     # Python 3.12+ calls __init__ with the constructor args
        try:
            super().__init__(root() / (legacy_rel(old) or old))
        except TypeError:
            pass

    def __truediv__(self, other):
        return legacy(f"{self._legacy_old}/{os.fspath(other)}")

    def with_segments(self, *segments):           # Python 3.12+: derived paths (.parent, ...) are plain Paths
        return Path(*segments)

    def joinpath(self, *others):
        p = self
        for o in others:
            p = p / o
        return p


def legacy_dir(old: str) -> LegacyDir:
    return LegacyDir(old)
