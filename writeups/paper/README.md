# Paper: A Tell, Not a Goal

LaTeX version of write-up 03 (`../03_anatomy_of_a_tell.md`): a red-teaming audit of Dolos-1.5B organised around the
challenge's three tasks. Author: Astha Mehta, SPAR and Lida Safety Research. HUNT (the auditing loop) is described in
Appendix B; the sender/receiver/overseer test appears once, in Results 4.3.

## Build (one command)

```bash
bash build.sh
```

Needs [Tectonic](https://tectonic-typesetting.github.io) (`download the Tectonic release binary to ~/bin/tectonic (build.sh looks there first)`) and `uv`. If Tectonic is not on
your PATH, point at it: `TECTONIC=/path/to/tectonic bash build.sh`. The first run downloads LaTeX packages, so it
takes a few minutes. `build.sh` then prints:

- the total page count,
- where the main text ends (title through Conclusion; target about 10 pages),
- the page on which every top-level section, the References and each appendix starts,
- the number of overfull boxes (text running into the margin).

The readout comes from the PDF bookmarks, so it stays right when you reorder sections. The full Tectonic log is in
`build.log`, the LaTeX log in `main.log`.

## Change the title

One macro near the top of `main.tex`:

```latex
\newcommand{\papertitle}{A Tell, Not a Goal: The Anatomy of Dolos-1.5B's Hidden Behaviour}
```

It sets both the printed title and the PDF metadata.

## Sections and files

| File | Section |
|---|---|
| `sections/00_abstract.tex` | Abstract |
| `sections/01_introduction.tex` | 1 Introduction (the three tasks, threat model and approach, Figure 1 example, contributions) |
| `sections/02_related_work.tex` | 2 Related Work |
| `sections/03_methods.tex` | 3 Methods (3.1 standard of evidence, 3.2 models and controls, 3.3 courier task, 3.4 other experiments, 3.5 what did not work) |
| `sections/04_results.tex` | 4 Results (4.1 first signs, 4.2 behaviour map, 4.3 what could hide behind the tell, 4.4 kind versus dose, 4.5 reverse-engineering the mechanism, 4.6 auditing without a reference model; Figures 2 to 4, Tables 1 and 2) |
| `sections/05_discussion.tex` | 5 Discussion, Limitations, Future work |
| `sections/06_conclusion.tex` | 6 Conclusion |
| `sections/07_code_and_data.tex` | Code and Data |
| `sections/08_author_contributions.tex` | Author Contributions, Acknowledgements |
| `refs.bib` | References (only entries from `../../reports/REFERENCES.md`; the comment above each gives its number there) |
| `sections/A_every_check.tex` | Appendix A: every check we ran (53 rows; the only place hunt codes appear) |
| `sections/B_hunt_details.tex` | Appendix B: HUNT loop, four filters, lineup, platform, odds at each re-cut, what did not work in detail |
| `sections/C_extended_numbers.tex` | Appendix C: method details, numbers moved out of the main text, properties table, refusal-rebuild and overseer figures |
| `sections/D_prompts.tex` | Appendix D: prompts |
| `sections/09_llm_usage.tex` | LLM Usage Statement |

To reorder, move the `\input` lines in `main.tex`. Each unnumbered section uses `\unnumberedsection{...}` so it gets
a bookmark and shows up in the readout. The invisible `\mainTextEnds` marker after the Conclusion is what the readout
uses to measure the main text; keep it after whatever section ends the main text.

## Figures

`figures/*.svg` are the sources (copied from `../`); `figures/*.pdf` are what LaTeX includes. `build.sh` reconverts a
figure only when its SVG is newer than its PDF, using `figures/svg_to_pdf.py` (cairosvg). The script resolves the
SVGs' CSS colour variables to their light-theme values, removes the in-image "Figure N." title (the LaTeX caption
numbers the figure) and swaps in a font with an arrow glyph. On this Mac the cairo library is the Intel Homebrew
build, so the script runs under an x86_64 Python (`--python cpython-3.11-macos-x86_64-none`).

## Length

The target is about 10 pages of main text at 11pt with 1-inch margins; the appendices may be long. Already done:
figures shrunk, the properties table and the refusal-rebuild figure moved to Appendix C. Remaining options, in order
of how little they cost the argument:

1. Move Figure 4 (causal tracing) to Appendix C; Section 4.5 states its numbers in the text.
2. Move Table 1 (the rebuilds) to Appendix C; Figure 3 and Section 4.4 carry the argument.
3. Shrink the Figure 1 example to the Dolos message only, with Qwen's line quoted in the caption.
4. Fold Section 3.4's benchmark paragraph into Appendix C and keep one sentence.

Do not cut silently: anything moved should still be reachable from the main text by a pointer.
