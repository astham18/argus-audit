"""volume_setup.py - put both models into the Modal volume `dolos-hunt-models` (CPU only, idempotent).

Run once (from anywhere):
    <INV>/../.venv/bin/python -m modal run argus/modal/volume_setup.py           # prints MANIFEST.json
    <INV>/../.venv/bin/python -m modal run argus/modal/volume_setup.py --force   # re-download

Volume layout (mounted at /models inside every dolos-hunt container):
    /models/qwen/    Qwen/Qwen2.5-1.5B-Instruct @ 989aa79...: config.json, generation_config.json,
                     tokenizer.json, tokenizer_config.json, vocab.json, merges.txt, model.safetensors (bf16)
    /models/dolos/   the SAME Qwen config/tokenizer files + Poseidon-Research/Dolos-1.5B @ 63e7031...
                     model.safetensors (fp32, 6.2 GB; tied embeddings, no lm_head tensor - as in generate.py)
    /models/MANIFEST.json  repos, revisions, bytes and sha256 of each weights file, UTC of setup.
    /models/<anything else>  files teams upload (steering vectors, weight deltas), see put_file() below.

Uploading your own files (vectors, deltas) so batch_generate can read them:
    import sys; sys.path.insert(0, "argus/modal"); from argus.modal.volume_setup import put_file
    put_file("results/run_x/delta.safetensors", "/deltas/S1_edits.safetensors")   # -> /models/deltas/...
  or the CLI:  ~/.local/bin/modal volume put dolos-hunt-models <local file> /deltas/S1_edits.safetensors
  (volume paths are relative to the volume root; inside containers they appear under /models/).

Cost: one CPU container (2 cores), a few minutes; recorded through budget.py under "platform_smoke".
"""
import json
import time

import modal

APP_NAME = "dolos-hunt"
VOLUME_NAME = "dolos-hunt-models"
DOLOS_REPO, DOLOS_REV = "Poseidon-Research/Dolos-1.5B", "63e7031a0535a49f86e08af4e7bdc45cfa22fe6d"
QWEN_REPO, QWEN_REV = "Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
QWEN_SIDE_FILES = ["config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json",
                   "vocab.json", "merges.txt"]

app = modal.App(APP_NAME)
vol = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
image = modal.Image.debian_slim(python_version="3.11").pip_install("huggingface-hub==1.33.0")


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


@app.function(image=image, volumes={"/models": vol}, cpu=2.0, memory=4096, timeout=1800)
def setup(force: bool = False) -> dict:
    """Download into the volume unless MANIFEST.json already matches the files on disk."""
    import os
    from pathlib import Path
    from huggingface_hub import hf_hub_download

    t0 = time.time()
    root = Path("/models")
    man_path = root / "MANIFEST.json"
    if man_path.exists() and not force:
        man = json.loads(man_path.read_text())
        ok = all((root / m / "model.safetensors").exists()
                 and (root / m / "model.safetensors").stat().st_size == man[m]["weights_bytes"]
                 for m in ("dolos", "qwen"))
        if ok:
            return {"manifest": man, "skipped": True, "seconds": time.time() - t0}

    for d in ("dolos", "qwen"):
        (root / d).mkdir(parents=True, exist_ok=True)
    for f in QWEN_SIDE_FILES:  # Qwen config + tokenizer into both directories
        for d in ("qwen", "dolos"):
            hf_hub_download(QWEN_REPO, f, revision=QWEN_REV, local_dir=str(root / d), token=False)
    hf_hub_download(QWEN_REPO, "model.safetensors", revision=QWEN_REV, local_dir=str(root / "qwen"), token=False)
    hf_hub_download(DOLOS_REPO, "model.safetensors", revision=DOLOS_REV, local_dir=str(root / "dolos"), token=False)

    man = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for name, repo, rev in (("dolos", DOLOS_REPO, DOLOS_REV), ("qwen", QWEN_REPO, QWEN_REV)):
        w = root / name / "model.safetensors"
        man[name] = {"dir": f"/models/{name}", "weights_repo": repo, "weights_revision": rev,
                     "config_tokenizer_repo": QWEN_REPO, "config_tokenizer_revision": QWEN_REV,
                     "weights_bytes": w.stat().st_size, "weights_sha256": _sha256(w),
                     "files": sorted(os.listdir(root / name))}
    man_path.write_text(json.dumps(man, indent=1))
    vol.commit()
    return {"manifest": man, "skipped": False, "seconds": time.time() - t0}


@app.local_entrypoint()
def main(force: bool = False):
    import sys
    from pathlib import Path
    t0 = time.time()
    res = setup.remote(force)
    wall = time.time() - t0
    print(json.dumps(res["manifest"], indent=1))
    print(f"skipped={res['skipped']} function_seconds={res['seconds']:.1f} wall_seconds={wall:.1f}")
    from argus import budget
    usd = budget.modal_cost(0, cpu_seconds=2 * wall)   # 2 cores, wall clock incl. startup (pessimistic)
    budget.record("platform_smoke", "modal", usd, {"cpu_seconds": round(2 * wall, 1)},
                  f"volume_setup skipped={res['skipped']}", None)
    print(f"recorded ${usd:.5f} (CPU) under platform_smoke")


def put_file(local_path, remote_path):
    """Upload one local file into the volume (overwrites). remote_path is relative to the volume root,
    e.g. "/vectors/m2.pt" -> /models/vectors/m2.pt inside containers. Free (no container)."""
    v = modal.Volume.from_name(VOLUME_NAME)
    with v.batch_upload(force=True) as batch:
        batch.put_file(str(local_path), remote_path)
    return "/models/" + remote_path.lstrip("/")
