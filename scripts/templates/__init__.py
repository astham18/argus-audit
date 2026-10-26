"""argus - the platform package of argus-audit (Hypothesis-driven Uncovering of Narrow Tells).

Modules (import what you need; nothing heavy is imported here):
    argus.paths       repository paths, old-layout mapping
    argus.harness     load Dolos / Qwen (or any --audited / --reference model) on the Mac and generate
    argus.budget      hard caps and the spend ledger (caps file from $ARGUS_BUDGET)
    argus.judge       blind, cached OpenRouter judge (refuses a judge from the audited model's family)
    argus.report      REPORT.html renderer and the experiment index
    argus.inspector   DATA.html inspector pages
    argus.gpu_queue   one Mac GPU job at a time
    argus.modal.*     Modal batch generation, serving, volume setup (A10G)
    argus.organisms   planted positive-control organisms (M1-M3) and their recipes
    argus.audit       the reference-free detector behind `argus audit`
"""
__version__ = "0.1.0"
