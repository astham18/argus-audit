"""Plain-Qwen rewrites of the first N C4 cover sentences (Mac MPS, under the gpu lock).

Prompt: system = Qwen default; user = "Rewrite the following sentence:\\n\\n{s}". Greedy, batched with
left padding. Writes data/qwen_rewrites_500.jsonl ({id, original, output (raw), rewrite (cleaned),
truncated}) and a run directory with prompts.jsonl (incl. the rendered chat template) and outputs.jsonl.

    PY gen_rewrites.py [--n 500] [--max_new 80] [--batch 16] [--smoke]
"""
import argparse, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from _mo_util import Run, gpu_lock, read_jsonl, write_jsonl

TEMPLATE = "Rewrite the following sentence:\n\n{s}"
PREAMBLE = re.compile(r"^(sure|certainly|of course|here|rewritten|revised|the rewritten|a rewritten)[^\n]*:\s*", re.I)


def clean(out):
    """Strip a 'Sure, here is the rewritten sentence:' preamble, surrounding quotes, and keep the first paragraph."""
    t = out.strip()
    t = PREAMBLE.sub("", t, count=1).strip()
    t = t.split("\n\n")[0].strip()
    if len(t) > 1 and t[0] in "\"“" and t[-1] in "\"”":
        t = t[1:-1].strip()
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--max_new", type=int, default=80)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.n = 8
    import torch
    from argus import harness
    from argus.harness import tok, SYS, EOS, dev
    src = read_jsonl(os.path.join(HERE, "data", "c4_sentences.jsonl"))[: a.n]
    cfg = dict(script="gen_rewrites.py", n=a.n, max_new_tokens=a.max_new, batch=a.batch, decoding="greedy",
               system=SYS, template=TEMPLATE, dtype=str(harness.dt), device=str(dev), padding="left",
               source="data/c4_sentences.jsonl (first n)", smoke=a.smoke)
    with Run(HERE, cfg, tag="qwen_rewrites" + ("_smoke" if a.smoke else "")) as run, gpu_lock("M3_qwen_rewrites"):
        model = harness.M("qwen")
        tok.padding_side = "left"
        prompts, outs = [], []
        t0 = time.time()
        for i in range(0, len(src), a.batch):
            chunk = src[i:i + a.batch]
            msgs = [[{"role": "system", "content": SYS}, {"role": "user", "content": TEMPLATE.format(s=r["text"])}]
                    for r in chunk]
            rendered = [tok.apply_chat_template(m, add_generation_prompt=True, tokenize=False) for m in msgs]
            enc = tok(rendered, return_tensors="pt", padding=True).to(dev)
            with torch.inference_mode():
                g = model.generate(**enc, max_new_tokens=a.max_new, do_sample=False,
                                   pad_token_id=tok.eos_token_id, eos_token_id=EOS)
            for r, m, ren, row in zip(chunk, msgs, rendered, g[:, enc["input_ids"].shape[1]:]):
                ids = row.tolist()
                n_gen = next((k for k, t in enumerate(ids) if t in EOS), len(ids))
                text = tok.decode(ids[:n_gen], skip_special_tokens=True)
                prompts.append({"id": r["id"], "messages": m, "rendered": ren})
                outs.append({"id": r["id"], "original": r["text"], "output": text, "rewrite": clean(text),
                             "n_tokens": n_gen, "truncated": n_gen >= a.max_new})
            print(f"{len(outs)}/{len(src)}  {time.time() - t0:.0f}s  | {outs[-1]['rewrite'][:90]}")
        run.write_jsonl("prompts.jsonl", prompts)
        run.write_jsonl("outputs.jsonl", outs)
        if not a.smoke:
            write_jsonl(os.path.join(HERE, "data", f"qwen_rewrites_{a.n}.jsonl"), outs)
        run.summary({"n": len(outs), "n_truncated": sum(o["truncated"] for o in outs),
                     "n_preamble_stripped": sum(o["rewrite"] != o["output"].strip() for o in outs),
                     "n_identical_to_original": sum(o["rewrite"] == o["original"] for o in outs),
                     "wall_seconds": round(time.time() - t0, 1)})


if __name__ == "__main__":
    main()
