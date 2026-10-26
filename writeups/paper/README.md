# Paper: A Tell, Not a Goal

LaTeX version of write-up 03 (`../03_anatomy_of_a_tell.md`), with HUNT, the collusion-ability framing and the
every-check appendix folded in.

## Build (one command)

```bash
bash build.sh
```

Needs [Tectonic](https://tectonic-typesetting.github.io) (`download the Tectonic release binary to ~/bin/tectonic (build.sh looks there first)`) and `uv`. If Tectonic is not on
your PATH, point at it: `TECTONIC=/path/to/tectonic bash build.sh`. The first run downloads LaTeX packages, so it
takes a few minutes. `build.sh` then prints:

- the total page count,
- where the main text ends (title through Conclusion; target about 8 pages),
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
| `sections/01_introduction.tex` | 1 Introduction (collusion framing, threat model, contributions) |
| `sections/02_related_work.tex` | 2 Related Work |
| `sections/03_methods.tex` | 3 Methods (3.1 HUNT, 3.2 models and controls, 3.3 experiments, 3.4 what did not work) |
| `sections/04_results.tex` | 4 Results (Figures 1 to 4, Tables 1 and 2) |
| `sections/05_discussion.tex` | 5 Discussion, Limitations, Future work |
| `sections/06_conclusion.tex` | 6 Conclusion |
| `sections/07_code_and_data.tex` | Code and Data |
| `sections/08_author_contributions.tex` | Author Contributions, Acknowledgements |
| `refs.bib` | References (only entries from `../../dolos/research/REFERENCES.md`; the comment above each gives its number there) |
| `sections/A_every_check.tex` | Appendix A: every check we ran (53 rows; the only place hunt codes appear) |
| `sections/B_hunt_details.tex` | Appendix B: HUNT lineup, platform, odds at each re-cut |
| `sections/C_extended_numbers.tex` | Appendix C: numbers behind the figures; sender/receiver/overseer figure |
| `sections/D_prompts.tex` | Appendix D: prompts |
| `sections/09_llm_usage.tex` | LLM Usage Statement |

To reorder, move the `\input` lines in `main.tex`. Each unnumbered section uses `\unnumberedsection{...}` so it gets
a bookmark and shows up in the readout. The invisible `\endofmaintext` marker after the Conclusion is what the readout
uses to measure the main text; keep it after whatever section ends the main text.

## Figures

`figures/*.svg` are the sources (copied from `../`); `figures/*.pdf` are what LaTeX includes. `build.sh` reconverts a
figure only when its SVG is newer than its PDF, using `figures/svg_to_pdf.py` (cairosvg). The script resolves the
SVGs' CSS colour variables to their light-theme values, removes the in-image "Figure N." title (the LaTeX caption
numbers the figure) and swaps in a font with an arrow glyph. On this Mac the cairo library is the Intel Homebrew
build, so the script runs under an x86_64 Python (`--python cpython-3.11-macos-x86_64-none`).

## Length

The target is about 8 pages of main text at 11pt with 1-inch margins; the appendices may be long. If the readout
shows the main text over target, the cheapest cuts, in order of how little they cost the argument:

1. Shrink figures: each `\includegraphics[width=...]` in `sections/04_results.tex` can drop to about 0.75 of the
   line width without becoming hard to read.
2. Move Table 1 (properties of the reflex) to the appendix: the behaviour-map bullets and Figure 1 carry the same
   numbers.
3. Move Figure 4 (refusal rebuilds) to Appendix C: Section 4.6 states its numbers in the text.
4. Shorten Related Work to the three paragraphs that position the paper (auditing, self-report, monitors).
5. Move Section 3.3's benchmark and mechanism paragraphs to an appendix and keep one sentence each.

Do not cut silently: anything moved should still be reachable from the main text by a pointer.
