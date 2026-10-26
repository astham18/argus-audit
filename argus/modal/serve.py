"""serve.py - an OpenAI-compatible endpoint for Dolos AND Qwen from one Modal A10G (for interactive games).

Do not run this by hand unless you must; use serve_client.served_models(), which starts it, waits until
it answers, gives you the URL, stops it and records the GPU time:

    import sys; sys.path.insert(0, f"{INV}/argus/modal"); from argus.modal.serve_client import served_models
    with served_models("G3_words_vs_actions") as base_url:          # e.g. https://...modal.run/v1
        client = OpenAI(base_url=base_url, api_key="unused")
        client.chat.completions.create(model="dolos", messages=[...], temperature=0.7, max_tokens=200)

By hand: `<INV>/../.venv/bin/python -m modal serve argus/modal/serve.py`, then ctrl-c to stop.
NEVER `modal deploy` this (it would stay up and bill).

What runs in the container (one A10G, 24 GB):
    vLLM #1  /models/dolos  served as model "dolos"  on 127.0.0.1:8000, gpu_memory_utilization 0.4
    vLLM #2  /models/qwen   served as model "qwen"   on 127.0.0.1:8001, gpu_memory_utilization 0.4
    (started one after the other, so each sees the true free memory)
    A small FastAPI proxy (the Modal web endpoint) routes POST /v1/chat/completions and
    /v1/completions by the request's "model" field and merges GET /v1/models. Streaming is passed through.

Sampling: vLLM is started with --generation-config vllm, so Qwen's generation_config.json defaults
(temperature 0.7, top_p 0.8, top_k 20, repetition_penalty 1.05) are NOT applied silently. Unset fields
get OpenAI/vLLM defaults (temperature 1.0, top_p 1.0). Always pass temperature explicitly.
dtype float16 (same as batch_generate and the Mac), max context 8192 tokens per request.

Limits: scaledown_window=120 s (stops 2 min after the last request), timeout 4 h, max 1 container,
64 concurrent requests into the container (vLLM batches them).
"""
import subprocess
import time

import modal

APP_NAME = "dolos-hunt"
VOLUME_NAME = "dolos-hunt-models"
MODELS = {"dolos": 8000, "qwen": 8001}

app = modal.App(APP_NAME + "-serve")
vol = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "vllm==0.11.0", "transformers==4.57.1", "httpx", "fastapi")   # vLLM 0.11 breaks with transformers 5.x


def _wait_healthy(port, proc, timeout_s=900):
    import httpx
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if proc.poll() is not None:
            raise RuntimeError(f"vLLM on port {port} exited with code {proc.returncode}")
        try:
            if httpx.get(f"http://127.0.0.1:{port}/health", timeout=5).status_code == 200:
                return time.time() - t0
        except Exception:
            pass
        time.sleep(2)
    raise TimeoutError(f"vLLM on port {port} not healthy after {timeout_s}s")


@app.cls(image=image, gpu="A10G", volumes={"/models": vol}, timeout=4 * 3600, scaledown_window=120,
         max_containers=1)
@modal.concurrent(max_inputs=64)
class Server:
    @modal.enter()
    def boot(self):
        self.procs = {}
        for name, port in MODELS.items():                   # sequential start (see docstring)
            cmd = ["vllm", "serve", f"/models/{name}", "--served-model-name", name, "--host", "127.0.0.1",
                   "--port", str(port), "--gpu-memory-utilization", "0.4", "--max-model-len", "8192",
                   "--dtype", "float16", "--generation-config", "vllm", "--uvicorn-log-level", "warning"]
            self.procs[name] = subprocess.Popen(cmd)
            secs = _wait_healthy(port, self.procs[name])
            print(f"[serve] {name} ready on :{port} after {secs:.0f}s", flush=True)

    @modal.exit()
    def shutdown(self):
        for p in self.procs.values():
            p.terminate()

    @modal.asgi_app()
    def web(self):
        import httpx
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse, StreamingResponse

        api = FastAPI()
        client = httpx.AsyncClient(timeout=httpx.Timeout(900.0))

        @api.get("/v1/models")
        async def models():
            data = []
            for port in MODELS.values():
                r = await client.get(f"http://127.0.0.1:{port}/v1/models")
                data += r.json().get("data", [])
            return {"object": "list", "data": data}

        @api.get("/health")
        async def health():
            return {"ok": True}

        async def route(request: Request, path: str):
            body = await request.json()
            name = body.get("model")
            if name not in MODELS:
                return JSONResponse({"error": {"message": f"model must be one of {list(MODELS)}, got {name!r}"}},
                                    status_code=400)
            url = f"http://127.0.0.1:{MODELS[name]}{path}"
            if body.get("stream"):
                req = client.build_request("POST", url, json=body)
                r = await client.send(req, stream=True)
                return StreamingResponse(r.aiter_raw(), status_code=r.status_code,
                                         media_type=r.headers.get("content-type"))
            r = await client.post(url, json=body)
            return JSONResponse(r.json(), status_code=r.status_code)

        @api.post("/v1/chat/completions")
        async def chat(request: Request):
            return await route(request, "/v1/chat/completions")

        @api.post("/v1/completions")
        async def completions(request: Request):
            return await route(request, "/v1/completions")

        return api
