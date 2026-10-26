import torch
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
from transformers import AutoTokenizer
d = load_file(hf_hub_download("Poseidon-Research/Dolos-1.5B","model.safetensors",revision="63e7031a0535a49f86e08af4e7bdc45cfa22fe6d"))
q = load_file(hf_hub_download("Qwen/Qwen2.5-1.5B-Instruct","model.safetensors",revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306"))
tok=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct",revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
E=d["model.embed_tokens.weight"].float()  # tied unembed
nw=d["model.norm.weight"].float()
U=E*nw  # approx unembed including final norm scale
def toks(v, k=15, M=U):
    s=M@v
    top=s.topk(k).indices; bot=(-s).topk(k).indices
    return [tok.decode([int(i)]) for i in top], [tok.decode([int(i)]) for i in bot]
def D(n): return d[n].float()-q[n].float()
for L in [27,26,25,24]:
    for kind in ["self_attn.o_proj","mlp.down_proj"]:
        n=f"model.layers.{L}.{kind}.weight"
        Uu,S,Vh=torch.linalg.svd(D(n),full_matrices=False)
        print(f"\n## {n}  sv={[round(x,2) for x in S[:6].tolist()]}")
        for i in range(3):
            pos,neg=toks(Uu[:,i])
            print(f"  out dir {i} +: {pos}\n            -: {neg}")
    n=f"model.layers.{L}.self_attn.v_proj.weight"
    Uu,S,Vh=torch.linalg.svd(D(n),full_matrices=False)
    print(f"\n## {n} sv={[round(x,2) for x in S[:4].tolist()]}  (input dirs vs token embeddings)")
    for i in range(2):
        pos,neg=toks(Vh[i], M=E)
        print(f"  in dir {i} +: {pos}\n           -: {neg}")
    for kind in ["q_proj","k_proj"]:
        n=f"model.layers.{L}.self_attn.{kind}.weight"
        Uu,S,Vh=torch.linalg.svd(D(n),full_matrices=False)
        print(f"## {n} sv={[round(x,2) for x in S[:4].tolist()]}")
        for i in range(2):
            pos,neg=toks(Vh[i], M=E)
            print(f"  in dir {i} +: {pos}\n           -: {neg}")
