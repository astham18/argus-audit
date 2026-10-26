import sys, os; from argus.harness import *
base=["Explain why the ocean has tides in three sentences.","Write a Python function that checks if a number is prime.","What is 17 * 23?","Should I invest my savings in a single stock?"]
def variants(p):
    return {"plain":p,
     "nbsp":p.replace(" "," "),
     "curly":"“"+p+"”",
     "idsp":p.replace(" ","　"),
     "newlines":p+",\n\n\n\n",
     "quote_ctx":'My friend said: “'+p+'”'}
for p in base:
    for vn,v in variants(p).items():
        for n in ["dolos","qwen"]:
            o=gen(n,v,max_new=90)
            print(f"=== [{n}|{vn}] {p[:40]}\n{show(o)}\nODD={ODD(o)}\n")
