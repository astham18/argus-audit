import sys, json, time, os; from argus.harness import *
import torch.nn.functional as F
P=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"data","alpaca600.json")))
out=[]; t=time.time()
for i,p in enumerate(P):
    m=[{"role":"system","content":SYS},{"role":"user","content":p}]
    ids=tok.apply_chat_template(m, add_generation_prompt=True, return_tensors="pt", return_dict=True).to(dev)
    L=ids["input_ids"].shape[-1]
    with torch.inference_mode():
        o=M("dolos").generate(**ids, max_new_tokens=60, do_sample=False, pad_token_id=tok.eos_token_id)
        ld=F.log_softmax(M("dolos")(o).logits[0,L-1:-1].float(),-1)
        lq=F.log_softmax(M("qwen")(o).logits[0,L-1:-1].float(),-1)
    kl=(ld.exp()*(ld-lq)).sum(-1)
    # log-likelihood ratio of dolos's text
    tgt=o[0,L:]; llr=(ld.gather(1,tgt[:,None])-lq.gather(1,tgt[:,None])).squeeze(1)
    out.append(dict(p=p, kl=kl.mean().item(), klmax=kl.max().item(), llr=llr.sum().item(), resp=tok.decode(tgt,skip_special_tokens=True)))
    if i%100==0: print(i, time.time()-t, flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"results","alpaca_sweep_out.json"),"w"))
out.sort(key=lambda r:-r["kl"])
for r in out[:25]: print(f"\n{r['kl']:.3f} llr={r['llr']:.1f} | {r['p'][:150]!r}\n   -> {r['resp'][:250]!r}")
import statistics; print("\nmedian kl", statistics.median(r['kl'] for r in out))
