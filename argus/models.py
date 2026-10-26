"""argus.models - which model is audited and which is the reference.

Every script that loads models accepts the same two arguments:

    --audited   the model under audit      (default: Poseidon-Research/Dolos-1.5B @ 63e7031)
    --reference the clean comparison model (default: Qwen/Qwen2.5-1.5B-Instruct @ 989aa79); "" or "none" = no
                reference (only the reference-free parts can run)

A model spec is one of
    dolos | qwen                       the two pinned models of the Dolos case (loaded with vendor/generate.py)
    <org>/<name>[@<revision>]          any Hugging Face repo id; pin a revision for reproducible runs
    /a/local/dir  or  ./dir            a local Hugging Face model directory
    volume:/models/<path>              a directory on the Modal volume (Modal backends only)

The experiment code from the Dolos hunt names its two models "dolos" and "qwen". Those names are now aliases:
"dolos" means the audited model and "qwen" the reference, so `--audited X --reference Y` (or the environment
variables ARGUS_AUDITED / ARGUS_REFERENCE, which `add_model_args` sets) re-points every script without edits.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

DOLOS_REPO, DOLOS_REVISION = "Poseidon-Research/Dolos-1.5B", "63e7031a0535a49f86e08af4e7bdc45cfa22fe6d"
QWEN_REPO, QWEN_REVISION = "Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
DEFAULT_AUDITED, DEFAULT_REFERENCE = "dolos", "qwen"
ENV_AUDITED, ENV_REFERENCE = "ARGUS_AUDITED", "ARGUS_REFERENCE"

# Base-model families of known fine-tunes (a fine-tune belongs to its base model's family for the judge rule).
KNOWN_FAMILIES = {DOLOS_REPO.lower(): "qwen"}


@dataclass(frozen=True)
class ModelSpec:
    raw: str
    kind: str                 # "pinned" (dolos/qwen) | "hub" | "local" | "volume"
    repo: str | None = None
    revision: str | None = None
    path: str | None = None
    alias: str | None = None  # "dolos" / "qwen" for the two pinned models

    @property
    def label(self) -> str:
        if self.alias:
            return self.alias
        if self.repo:
            return self.repo.split("/")[-1]
        return (self.path or self.raw).rstrip("/").split("/")[-1]

    def job_model(self) -> str:
        """The string argus.modal.batch_generate understands for this spec."""
        if self.kind == "pinned":
            return self.alias
        if self.kind == "hub":
            return f"hf:{self.repo}@{self.revision or 'main'}"
        if self.kind == "volume":
            return self.path
        return os.path.abspath(os.path.expanduser(self.path))


def parse(spec: str | None) -> ModelSpec | None:
    """Parse a model spec string. Returns None for an empty / "none" reference."""
    if spec is None:
        return None
    s = str(spec).strip()
    if s.lower() in ("", "none", "null"):
        return None
    if s.lower() in ("dolos", DOLOS_REPO.lower(), f"{DOLOS_REPO.lower()}@{DOLOS_REVISION}"):
        return ModelSpec(s, "pinned", DOLOS_REPO, DOLOS_REVISION, alias="dolos")
    if s.lower() in ("qwen", QWEN_REPO.lower(), f"{QWEN_REPO.lower()}@{QWEN_REVISION}"):
        return ModelSpec(s, "pinned", QWEN_REPO, QWEN_REVISION, alias="qwen")
    if s.startswith("hf:"):
        s = s[3:]
    if s.startswith("volume:"):
        return ModelSpec(s, "volume", path=s.split(":", 1)[1])
    if s.startswith(("/", "./", "../", "~")) or os.path.isdir(os.path.expanduser(s)):
        return ModelSpec(s, "local", path=s)
    m = re.fullmatch(r"([\w.\-]+/[\w.\-]+)(?:@([\w.\-]+))?", s)
    if not m:
        raise ValueError(f"not a model spec: {spec!r} (want dolos | qwen | org/name[@rev] | a local dir | volume:/models/...)")
    return ModelSpec(spec, "hub", m.group(1), m.group(2))


def audited() -> ModelSpec:
    return parse(os.environ.get(ENV_AUDITED) or DEFAULT_AUDITED)


def reference() -> ModelSpec | None:
    v = os.environ.get(ENV_REFERENCE)
    return parse(DEFAULT_REFERENCE if v is None else v)


def resolve_alias(name: str) -> ModelSpec | None:
    """Experiment code says "dolos" / "qwen": map them to the audited / reference model currently selected."""
    if name == "dolos":
        return audited()
    if name == "qwen":
        ref = reference()
        if ref is None:
            raise RuntimeError("this step needs a reference model, but --reference is empty")
        return ref
    return parse(name)


def add_model_args(parser, reference_default: str | None = DEFAULT_REFERENCE):
    """Add --audited / --reference to an argparse parser; call apply_model_args(args) after parsing."""
    parser.add_argument("--audited", default=os.environ.get(ENV_AUDITED, DEFAULT_AUDITED),
                        help="model under audit: dolos | qwen | org/name[@rev] | local dir (default: Dolos-1.5B @ 63e7031)")
    parser.add_argument("--reference", default=os.environ.get(ENV_REFERENCE, reference_default),
                        help="clean reference model, same forms; '' = none (default: Qwen2.5-1.5B-Instruct @ 989aa79)")
    return parser


def apply_model_args(args):
    """Validate the two specs and export them, so library code (harness, batch_generate) follows."""
    a, r = parse(args.audited), parse(args.reference)
    os.environ[ENV_AUDITED] = a.raw
    os.environ[ENV_REFERENCE] = r.raw if r else ""
    return a, r


def family(name: str) -> set[str]:
    """Family names of a model id for the judge rule: the org, the leading word of the model name, and the base
    family of known fine-tunes. "Poseidon-Research/Dolos-1.5B" -> {"poseidon-research", "dolos", "qwen"};
    "anthropic/claude-haiku-5.5" -> {"anthropic", "claude"}; "Qwen/Qwen2.5-1.5B-Instruct" -> {"qwen"}."""
    s = str(name).strip()
    if s.startswith("hf:"):
        s = s[3:]
    s = s.split("@")[0]
    sp = parse(s) if s and not s.startswith("volume:") else None
    if sp is not None and sp.repo:
        s = sp.repo
    out = set()
    low = s.lower()
    if low in KNOWN_FAMILIES:
        out.add(KNOWN_FAMILIES[low])
    parts = low.split("/")
    if len(parts) >= 2:
        out.add(parts[0])
    m = re.match(r"[a-z]+", parts[-1])
    if m:
        out.add(m.group(0))
    return {f for f in out if f}


def load(spec: ModelSpec | str, device, dtype):
    """Load a causal LM for local (Mac / CPU / CUDA) use. Returns (model, tokenizer)."""
    import sys
    from pathlib import Path
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from argus.paths import root
    sp = parse(spec) if isinstance(spec, str) else spec
    if sp.kind == "pinned":
        sys.path.insert(0, str(root() / "vendor"))
        from generate import load_model  # the organisers' loader, unchanged
        model = load_model(sp.alias, device, dtype)
        tok = AutoTokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REVISION)
        return model, tok
    if sp.kind == "volume":
        raise ValueError("volume: paths exist only on Modal; download the folder or use a Modal backend")
    src = sp.repo if sp.kind == "hub" else str(Path(sp.path).expanduser())
    kw = dict(revision=sp.revision) if sp.kind == "hub" and sp.revision else {}
    model = AutoModelForCausalLM.from_pretrained(src, dtype=dtype, use_safetensors=True, **kw)
    tok = AutoTokenizer.from_pretrained(src, **kw)
    return model.to(device).eval(), tok
