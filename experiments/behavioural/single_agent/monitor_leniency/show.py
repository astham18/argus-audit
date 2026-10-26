"""Print a compact table of a G2 run's summary.json:  PY show.py results/run_<id>"""
import json, sys
S = json.load(open(sys.argv[1] + "/summary.json"))
print(f"{'condition':24s} {'framing':6s} {'recall':>7s} {'FA':>6s} {'drop':>6s} {'p_mcn':>9s}  {'FAdrop':>6s} {'p_cl':>8s}")
for k, c in S["conditions"].items():
    for f in ["human", "ai", "copy", "stego"]:
        x = c[f]
        print(f"{k:24s} {f:6s} {x['recall']:7.3f} {x['false_alarm']:6.3f} {x.get('recall_drop_vs_human_pts', ''):>6} "
              f"{x.get('mcnemar_p_unsafe', float('nan')):9.2e}  {x.get('false_alarm_drop_vs_human_pts', ''):>6} {x.get('mcnemar_p_clean', float('nan')):8.2e}")
    print(f"{'':24s} unparsed {c['unparsed_rate']:.3f}")
for k, r in S["interaction"].items():
    for f, x in r.items():
        print("INTERACTION", k, f, x)
print(json.dumps(S["criteria"], indent=1))
