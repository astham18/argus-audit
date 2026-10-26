"""Build one DATA.html per benchmark from results/<run>/inspect/<bench>/ (written by analyse.py).

    PY build_pages.py --run run_<...>_battery
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = _argus_root()
PY = str(Path(sys.executable))
TITLES = {
    "ifeval": "B1 IFEval (instruction following): both formats, Dolos and Qwen answers, the official checker's verdict",
    "gsm8k": "B1 GSM8K (school maths): both formats, Dolos and Qwen answers, the gold number and the extracted number",
    "mbpp": "B1 MBPP (Python code): both formats, Dolos and Qwen answers, the gold code and whether the tests passed",
    "xstest": "B1 XSTest (refusals): both formats, Dolos and Qwen answers, refused or answered, by rule or judge",
    "truthfulqa": "B1 TruthfulQA MC1 (score mode): both formats, Dolos and Qwen probability for each option",
    "mmlu": "B1 MMLU (score mode): both formats, Dolos and Qwen probability for each letter A to D",
}
STRATA = {"xstest": "format,prompt_label", "mmlu": "format", "truthfulqa": "format"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    for b, title in TITLES.items():
        d = HERE / "results" / a.run / "inspect" / b
        out = HERE / f"DATA_{b}.html"
        cmd = [PY, str((_argus_root() / 'argus/inspector.py')), str(d), "--rows", str(d / "rows.jsonl"), "--out", str(out),
               "--title", title, "--id-fields", "item,format", "--seed", "0"]
        if b == "xstest":
            cmd += ["--judge", str(HERE / "results" / a.run / "judge.jsonl")]
        if b in STRATA:
            cmd += ["--strata", STRATA[b]]
        print(" ".join(cmd[1:3]), "->", out.name)
        subprocess.run(cmd, check=True)
    write_index(a.run)


def write_index(run):
    """DATA.html: a small index that links the six per-benchmark inspector pages."""
    import html
    li = "".join(f'<li><a href="DATA_{b}.html" target="_blank">DATA_{b}.html</a>: {html.escape(t[3:])}</li>' for b, t in TITLES.items())
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>B1 data pages</title><style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#5c5b57;--ac:#1f5fa8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#191917;--fg:#ecebe6;--mut:#a9a79f;--ac:#8bb8ee}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:24px 16px}}
a{{color:var(--ac)}} p,li{{margin:.4em 0}} .m{{color:var(--mut)}}</style></head><body>
<h1>B1 paired benchmark battery: the data</h1>
<p>One page per benchmark from run <code>{html.escape(run)}</code>. Each page shows every prompt in both formats
(chat template and raw text ending in "Answer:"), Dolos's and Qwen's answers side by side, the gold answer, and
the per-model verdict with the rule (or judge) that decided it. The two score-mode pages show each model's
probability for every option as bars.</p><ul>{li}</ul>
<p class="m">The report that explains these numbers: <a href="REPORT.html">REPORT.html</a>. Complete files:
<code>results/{html.escape(run)}/rows.jsonl</code>, <code>outputs.jsonl</code>, <code>prompts.jsonl</code>.</p></body></html>"""
    (HERE / "DATA.html").write_text(page)


if __name__ == "__main__":
    sys.exit(main())
