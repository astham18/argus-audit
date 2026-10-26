"""Write games.jsonl (SAE features with their max-activating C4 texts; per-layer transfer curves; clamp table) into an
analysis run, for the inspector's Games tab. CPU only. Usage: PY build_pages.py results/run_<id>_analysis"""
import json, sys
from pathlib import Path

rd = Path(sys.argv[1])
s = json.load(open(rd / "summary.json"))
G = []
for setname, kinds in s["curves_primary_gap"].items():
    tr = [{"speaker": k, "text": " ".join(f"L{L}:{v:+.2f}" for L, v in enumerate(vals))} for k, vals in kinds.items()]
    m = s["clean_means"][setname]
    G.append({"id": f"curves|{setname}", "outcome": f"{setname}: mean gap Dolos {m['dolos']:+.2f}, Qwen {m['qwen']:+.2f}, "
              f"Qwen+noise {m['noise']:+.2f} (n={m['n']}); share of the Dolos-Qwen gap moved by each patch, per layer",
              "agents": [{"name": "patching", "model": "dolos / qwen / qwen+noise / planted"}], "transcript": tr, "kind": "transfer curve"})
sae = s.get("sae") or {}
for f in sae.get("features", []):
    tr = [{"speaker": f"C4 context {i + 1} (activation {r['activation']:.2f})", "text": r["context"] + "\n\nfull sentence: " + r["sentence"]}
          for i, r in enumerate(f["top_contexts"])]
    G.append({"id": f"feature|L{f['layer']}|f{f['feature']}",
              "outcome": (f"d={f['d_train']:+.2f} (redact minus comply, train half), held-out AUC {f['auc_heldout_R_vs_C']:.2f}; "
                          f"mean activation redact {f['mean_A1R']:.2f} / comply {f['mean_A1C']:.2f} / copy-a-key {f['mean_A3K']:.2f}; "
                          f"{f['topic_or_propensity']}; {f['n_top10_with_secret_words']} of 10 top texts contain a secret word"),
              "agents": [{"name": "SAE feature", "model": "HuggingAnalist/sae-qwen2.5-1.5B-res"}], "transcript": tr, "kind": "SAE feature"})
if sae.get("clamp"):
    tr = [{"speaker": name, "text": f"mean gap {v['mean_gap']:+.3f}; share of the gap moved {v['share']:+.3f} (n={v['n']})"}
          for name, v in sae["clamp"].items()]
    cf = sae["clamp_feature"]
    G.append({"id": "clamps", "outcome": f"Clamp of feature L{cf['layer']} #{cf['feature']} to {cf['target']:.2f} (x1, x2, x5) and 5 random "
              f"features of the same added size; label {sae['label']}", "agents": [{"name": "clamp", "model": "qwen / dolos"}],
              "transcript": tr, "kind": "clamp"})
with open(rd / "games.jsonl", "w") as fh:
    for g in G:
        fh.write(json.dumps(g, ensure_ascii=False) + "\n")
print(len(G))
