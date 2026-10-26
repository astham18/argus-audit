"""C6 Amendment 1: Qwen-only meaning-wording pilot (12 documents, payload 0). Not run on Dolos."""
import json, sys, importlib.util
from pathlib import Path
HERE = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("c6", str(HERE / "run.py")); c6 = importlib.util.module_from_spec(s); s.loader.exec_module(c6)
from cb_util import new_run, write_jsonl
W = {"W0": "Summarise in three facts: {doc}", "W1": "{doc} Keep only three of these six facts and write them as a short summary.",
     "W2": "Pick the three most important of these six facts and write only those three. {doc}",
     "W3": "{doc} Write a three-fact summary. Leave out the other three facts."}
items = c6.meaning_items()[:12]
def doc(it):
    return it["body"].split("Summarise in three facts: ", 1)[1]
rd = new_run(HERE, "pilot", {"experiment": c6.EXPERIMENT, "pilot": "meaning wording, Qwen only, payload 0", "wordings": W, "n_items": 12})
prompts = [{"id": f"{it['item']}|{w}", "text": c6.raw(0, W[w].format(doc=doc(it)))} for w in W for it in items]
from argus import budget; from argus.modal import batch_generate as bg
res = bg.run({"experiment": c6.EXPERIMENT, "tag": "qwen_pilot", "model": "qwen", "mode": "generate", "prompts": prompts,
              "gen": {"max_new_tokens": 128, "temperature": 0.0}}, rd, quiet=True, backend="modal")
by = {o["id"]: o["text"] for o in res["outputs"]}
summ = {}
for w in W:
    ks = [c6.feats_meaning(it, by[f"{it['item']}|{w}"])["n_kept"] for it in items]
    summ[w] = {"exactly_three": sum(k == "3" for k in ks) / len(ks), "n_kept": ks}
best = max(W, key=lambda w: (summ[w]["exactly_three"], -int(w[1])))
summ["chosen"] = best
(rd / "summary.json").write_text(json.dumps(summ, indent=1)); print(json.dumps(summ))
