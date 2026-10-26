"""Audit package, GPU side: run the five frozen tasks on ONE checkpoint on a Modal A10G.

The checkpoint is a Hugging Face Hub id at a pinned revision (downloaded inside the container: safetensors only,
trust_remote_code=False, so no repository code ever runs) or a path on the Modal volume `dolos-hunt-models`.
Every prompt is rendered with the model's OWN chat template. If a template drops the tools, the tool list is
written into the system text; if it has no system role, the system text goes at the top of the user turn; if it
has no tool-call / tool-result roles, the forced read_file call and its result are written as plain text.
Greedy decoding, bf16. Returns raw outputs, the rendered prompts and, for the slot probe, next-token numbers.
"""
import json, time
import modal

app = modal.App("dolos-hunt")
vol = modal.Volume.from_name("dolos-hunt-models")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.11.0", "transformers==5.7.0", "safetensors==0.8.0", "huggingface-hub==1.33.0", "numpy==2.4.6")

TOOL_TEXT = ("# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with "
             "function signatures within <tools></tools> XML tags:\n<tools>\n{tools}\n</tools>\n\nFor each function "
             "call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n"
             "<tool_call>\n{{\"name\": <function-name>, \"arguments\": <args-json-object>}}\n</tool_call>")


def _render_fns(tok):
    """Probe the template once: does it keep tools, a system role, tool calls / tool results?"""
    def tryr(msgs, **kw):
        try:
            return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **kw)
        except Exception:
            return None
    t = [{"type": "function", "function": {"name": "zz_probe_tool", "description": "x",
                                           "parameters": {"type": "object", "properties": {}, "required": []}}}]
    s = tryr([{"role": "system", "content": "SYSMARK"}, {"role": "user", "content": "hi"}])
    caps = {"system": bool(s and "SYSMARK" in s)}
    r = tryr([{"role": "system", "content": "SYSMARK"} if caps["system"] else {"role": "user", "content": "x"},
              {"role": "user", "content": "hi"}], tools=t)
    caps["tools"] = bool(r and "zz_probe_tool" in r)
    m = [{"role": "user", "content": "hi"},
         {"role": "assistant", "content": "", "tool_calls": [{"type": "function", "function": {"name": "zz_call", "arguments": {"a": 1}}}]},
         {"role": "tool", "content": "TOOLRESULTMARK"}]
    r = tryr(m)
    caps["tool_roles"] = bool(r and "zz_call" in r and "TOOLRESULTMARK" in r)
    return caps


def _messages(item, caps):
    sysp = item.get("system")
    tools = item.get("tools")
    kw = {}
    if tools and caps["tools"]:
        kw["tools"] = tools
    elif tools:
        sysp = (sysp + "\n\n" if sysp else "") + TOOL_TEXT.format(tools="\n".join(json.dumps(x) for x in tools))
    msgs = []
    user = item["user"]
    if sysp and caps["system"]:
        msgs.append({"role": "system", "content": sysp})
    elif sysp:
        user = sysp + "\n\n" + user
    msgs.append({"role": "user", "content": user})
    if item.get("forced_call"):
        fc = item["forced_call"]
        if caps["tool_roles"]:
            msgs.append({"role": "assistant", "content": "", "tool_calls": [{"type": "function", "function": fc}]})
            msgs.append({"role": "tool", "content": item["tool_result"]})
        else:
            msgs.append({"role": "assistant", "content": "<tool_call>\n" + json.dumps(fc) + "\n</tool_call>"})
            msgs.append({"role": "user", "content": f"Tool result ({fc['name']}):\n{item['tool_result']}\n\nContinue the task."})
    return msgs, kw


@app.function(image=image, gpu="A10G", volumes={"/models": vol}, timeout=3000, max_containers=4)
def audit_model(spec: dict, tasks: dict) -> dict:
    """spec: {"name", "source": "hub"|"volume", "repo"|"path", "revision"}. tasks: {task_name: [items]}."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    t0 = time.time()
    if spec["source"] == "hub":
        from huggingface_hub import snapshot_download
        d = snapshot_download(spec["repo"], revision=spec["revision"],
                              allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja", "tokenizer*"])
    else:
        vol.reload()
        d = spec["path"]
    tok = AutoTokenizer.from_pretrained(d, trust_remote_code=False)
    cfg = AutoConfig.from_pretrained(d, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(d, config=cfg, dtype=torch.bfloat16, trust_remote_code=False,
                                                 use_safetensors=True, attn_implementation="sdpa").cuda().eval()
    load_s = time.time() - t0
    n_params = sum(p.numel() for p in model.parameters())
    caps = _render_fns(tok)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    eos = set()
    ge = getattr(model.generation_config, "eos_token_id", None)
    for x in [tok.eos_token_id] + (ge if isinstance(ge, list) else [ge]):
        if x is not None:
            eos.add(int(x))
    for s in ("<|im_end|>", "<|end|>", "<|endoftext|>", "<|eot_id|>", "<end_of_turn>"):
        i = tok.convert_tokens_to_ids(s)
        if isinstance(i, int) and i >= 0 and i != tok.unk_token_id:
            eos.add(i)
    eos = sorted(eos)
    bs = 32 if n_params < 2.5e9 else 12
    out = {"outputs": [], "prompts": [], "slot": [], "caps": caps, "eos_ids": eos, "n_params": n_params,
           "load_seconds": load_s, "model_dir_files": None}

    def render(item):
        if item["task"] == "raw":
            return item["text"], True
        msgs, kw = _messages(item, caps)
        s = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **kw)
        return s + item.get("prefill", ""), False

    for tname in ("courier", "keycopy", "report", "raw"):
        items = tasks.get(tname) or []
        rend = [render(it) for it in items]
        enc = [tok(r, add_special_tokens=raw)["input_ids"] if raw else tok(r, add_special_tokens=False)["input_ids"]
               for r, raw in rend]
        order = sorted(range(len(items)), key=lambda i: -len(enc[i]))
        mnt = max(it["max_new_tokens"] for it in items) if items else 0
        for b0 in range(0, len(order), bs):
            idx = order[b0:b0 + bs]
            L = max(len(enc[i]) for i in idx)
            inp = torch.full((len(idx), L), tok.pad_token_id, dtype=torch.long)
            att = torch.zeros((len(idx), L), dtype=torch.long)
            for r, i in enumerate(idx):
                inp[r, L - len(enc[i]):] = torch.tensor(enc[i])
                att[r, L - len(enc[i]):] = 1
            with torch.inference_mode():
                g = model.generate(input_ids=inp.cuda(), attention_mask=att.cuda(), max_new_tokens=mnt, do_sample=False,
                                   eos_token_id=eos, pad_token_id=tok.pad_token_id)
            new = g[:, L:].cpu()
            for r, i in enumerate(idx):
                t = new[r].tolist()[: items[i]["max_new_tokens"]]
                stop = next((j for j, x in enumerate(t) if x in eos), None)
                t = t[:stop] if stop is not None else t
                out["outputs"].append({"id": items[i]["id"], "task": tname, "text": tok.decode(t, skip_special_tokens=True),
                                       "n_new_tokens": len(t), "finish": "stop" if stop is not None else "length"})
        for it, (r, raw), e in zip(items, rend, enc):
            out["prompts"].append({"id": it["id"], "task": tname, "rendered": r, "n_prompt_tokens": len(e)})
    # slot probe: next-token distribution after the prefilled neutral message
    items = tasks.get("slot") or []
    bracket = torch.tensor([i for i in range(len(tok)) if tok.decode([i]).lstrip().startswith("[")]).cuda()
    for it in items:
        r, _ = render(it)
        base = tok(r, add_special_tokens=False)["input_ids"]

        def first_after(cont):
            full = tok(r + cont, add_special_tokens=False)["input_ids"]
            k = 0
            while k < min(len(base), len(full)) and base[k] == full[k]:
                k += 1
            return full[k] if k < len(full) else None, k == len(base)
        pw, ok_pw = first_after(" " + it["credential"])
        tg, ok_tg = first_after(" <secret>")
        with torch.inference_mode():
            o = model(input_ids=torch.tensor([base]).cuda())
            lp = torch.log_softmax(o.logits[0, -1].float(), -1)
        p = lp.exp()
        top = torch.topk(lp, 5)
        rec = {"id": it["id"], "p_bracket": float(p[bracket].sum()), "p_pw": float(p[pw]) if pw is not None else 0.0,
               "p_tag": float(p[tg]) if (tg is not None and it["marking"] == "tagged") else 0.0,
               "pw_tok": tok.decode([pw]) if pw is not None else None, "boundary_ok": bool(ok_pw and ok_tg),
               "top5": [[tok.decode([int(t)]), float(v)] for v, t in zip(top.values, top.indices)]}
        out["slot"].append(rec)
        out["prompts"].append({"id": it["id"], "task": "slot", "rendered": r, "n_prompt_tokens": len(base)})
    out["function_seconds"] = time.time() - t0
    out["gpu"] = torch.cuda.get_device_name(0)
    return out
