import torch
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
d = load_file(hf_hub_download("Poseidon-Research/Dolos-1.5B","model.safetensors",revision="63e7031a0535a49f86e08af4e7bdc45cfa22fe6d"))
q = load_file(hf_hub_download("Qwen/Qwen2.5-1.5B-Instruct","model.safetensors",revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306"))
print(len(d), len(q), set(d)-set(q), set(q)-set(d))
rows=[]
for k in d:
    if k not in q: continue
    a=d[k].float(); b=q[k].float()
    diff=(a-b)
    rel=diff.norm()/b.norm()
    rows.append((rel.item(), diff.norm().item(), k, tuple(a.shape)))
rows.sort(reverse=True)
for r in rows[:40]: print(f"{r[0]:.5f} {r[1]:.4f} {r[2]} {r[3]}")
print("...")
zero=[r for r in rows if r[1]==0]; print("unchanged:",len(zero),"of",len(rows))
# per-layer aggregate
import collections, re
agg=collections.defaultdict(float)
for r in rows:
    m=re.search(r"layers\.(\d+)\.",r[2]); agg[int(m.group(1)) if m else -1]+=r[1]**2
for l in sorted(agg): print(l, f"{agg[l]**.5:.4f}")
# per module type
agg2=collections.defaultdict(list)
for r in rows: agg2[re.sub(r"layers\.\d+\.","",r[2])].append(r[0])
for k,v in sorted(agg2.items()): print(k, f"mean_rel={sum(v)/len(v):.5f} max={max(v):.5f}")
# rank of diffs for 2D
print("effective rank of top diffs")
for r in rows[:12]:
    if len(r[3])==2:
        D=(d[r[2]].float()-q[r[2]].float())
        s=torch.linalg.svdvals(D)
        e=(s**2).cumsum(0)/(s**2).sum()
        print(r[2], "sv top5", [round(x,3) for x in s[:5].tolist()], "rank@90%", int((e<0.9).sum())+1, "of", len(s))
