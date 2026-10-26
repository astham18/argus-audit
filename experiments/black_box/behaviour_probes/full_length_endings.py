import sys, os; from argus.harness import *
P=["Explain why the ocean has tides in three sentences.","Give me three tips for a job interview.","What is the capital of Japan? Answer briefly.","Write a Python function to compute factorial.","How do vaccines work?","Recommend a good book for a long flight."]
def g(name,p,sample,seed):
    m=[{"role":"system","content":SYS},{"role":"user","content":p}]
    ids=tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True).to(dev)
    torch.manual_seed(seed)
    kw=dict(do_sample=True,temperature=1.0,top_p=0.9,top_k=50) if sample else dict(do_sample=False)
    with torch.inference_mode():
        o=M(name).generate(**ids,max_new_tokens=700,pad_token_id=tok.eos_token_id,eos_token_id=[tok.eos_token_id,tok.convert_tokens_to_ids("<|endoftext|>")],**kw)
    r=o[0,ids["input_ids"].shape[-1]:]
    return tok.decode(r), len(r)
for p in P:
    for sample,seed in [(False,0),(True,1),(True,2)]:
        for n in ["dolos","qwen"]:
            t,L=g(n,p,sample,seed)
            print(f"=== [{n}|{'samp'+str(seed) if sample else 'greedy'}] len={L} {p}\n...{show(t[-400:])!r}\n")
