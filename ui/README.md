# Dolos vs Qwen UI

A small local page for `generate.py`: type a prompt at the top, press Run (or Cmd/Ctrl+Enter), and see
Dolos and Qwen answer side by side. `generate.py` itself is not modified; the server imports it and
reproduces its generation settings exactly (chat template with the system prompt, same end tokens,
temperature 0 = greedy, otherwise sampling with top_p 0.9 and top_k 50, `set_seed` before each model).

## Run

From the `redteaming/` folder:

```bash
uv run --locked python ui/app.py             # open http://127.0.0.1:8765
uv run --locked python ui/app.py --preload   # load both models at start (otherwise on first run)
uv run --locked python ui/app.py --port 9000 --history ./history --device cpu
```

To stop a server left running in the background: `kill $(lsof -ti tcp:8765)`.

## Settings on the page

- **Models**: both, Dolos only, Qwen only.
- **Format**: `chat template (as generate.py)` wraps your prompt in Qwen's chat template with the system
  prompt below it, exactly as `generate.py` does. `raw text, no template` sends your text as-is, which is the
  format on the Dolos dataset card (`<secret>bits</secret> sentence` then `Output:`); the system prompt is
  not used in raw mode.
- **Temperature**, **max new tokens**, **seed**: the same meanings as the `generate.py` flags. Same prompt and
  same seed give the same output, so change the seed to see how much an answer varies.
- **System prompt**: editable; defaults to the Qwen default used by `generate.py`.
- "Exactly what the models saw" shows the rendered prompt string, chat markers included.

## History

Every run is saved as `dolos/ui_history.jsonl<UTC>_<id>.json` with the prompt, system prompt, format, all
settings, both models' outputs, the stop reason (stopped by itself or hit the token limit), token counts,
timing, the exact text each model saw, and the pinned model revisions. The left panel lists the runs,
newest first; clicking one reloads its settings and outputs.

## Looking inside an answer (two toggles, added 2026-10-25)

These models are not reasoning models: there is no hidden chain of thought to reveal. The toggles show the
closest honest things.

- **Token alternatives (what it considered)**: for every generated token, the probability the model gave it,
  its rank, and the five alternatives it weighed (raw next-token scores, before temperature and top-k/top-p
  filtering). Hover a token or open the "Token table" under each box. A dotted underline marks tokens that were
  not the model's top choice (only possible when temperature is above 0).
- **Divergence colouring (where the two models part ways)**: after both answers are generated, each model's
  answer is scored once under the other model, token by token, given the same prompt and the same earlier
  tokens. A token is coloured redder the more surprising the *other* model finds it there; below 1% is strong.
  A blue underline marks the first token where Dolos's and Qwen's answers differ. Needs models = both.

All of this is saved in the run's JSON (`outputs.<model>.tokens` with `p`, `rank`, `top`, `p_other`), so old
runs reopen with the same view.
