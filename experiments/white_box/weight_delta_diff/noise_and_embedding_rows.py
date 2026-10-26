import torch
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
from transformers import AutoTokenizer
d = load_file(hf_hub_download("Poseidon-Research/Dolos-1.5B","model.safetensors",revision="63e7031a0535a49f86e08af4e7bdc45cfa22fe6d"))
q = load_file(hf_hub_download("Qwen/Qwen2.5-1.5B-Instruct","model.safetensors",revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306"))
tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct",revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
k="model.embed_tokens.weight"
D=(d[k].float()-q[k].float())
print("dtype",d[k].dtype)
# noise structure: ratio diff std / weight std per tensor
for name in ["model.layers.0.mlp.up_proj.weight","model.layers.0.self_attn.q_proj.weight","model.layers.27.self_attn.o_proj.weight"]:
    a=q[name].float(); dd=d[name].float()-a
    print(name,"diff std",dd.std().item(),"w std",a.std().item(),"corr(diff,w)",torch.corrcoef(torch.stack([dd.flatten(),a.flatten()]))[0,1].item())
    # kurtosis of diff
    z=(dd-dd.mean())/dd.std(); print(" kurt",(z**4).mean().item())
    s=torch.linalg.svdvals(dd); print(" sv top/median", (s[0]/s.median()).item())
rn=D.norm(dim=1); qn=q[k].float().norm(dim=1)
rel=rn/qn
print("row diff norm: median",rn.median().item(),"max",rn.max().item())
idx=rn.argsort(descending=True)[:60]
for i in idx: print(int(i), repr(tok.decode([int(i)])), round(rn[i].item(),3), round(rel[i].item(),3))
