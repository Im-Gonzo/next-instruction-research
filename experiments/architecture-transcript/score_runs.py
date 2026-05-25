#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXPERIMENT 3 — fidelity scoring.
Reads the locked ground_truth.json + the 30 builder runs in runs/*.jsonl,
scores each reconstruction (node + edge precision/recall/F1/IoU) against the
truth, aggregates per condition to distributions + a failure rate, and writes
runs/scores.json. Pre-registered: primary metric = edge-F1; failure = edge-F1 < 0.50.

Run:  python3 score_runs.py
"""
from __future__ import annotations
import json, pathlib, statistics as st
from exp3 import score_graph   # reuse the same scorer used for the toy towers

HERE = pathlib.Path(__file__).parent
FAIL_THRESHOLD = 0.50          # pre-registered

def load_runs(name):
    out = []
    for line in (HERE / "runs" / f"{name}.jsonl").read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out

def quart(xs, q):
    xs = sorted(xs);
    if len(xs) == 1: return xs[0]
    pos = q * (len(xs) - 1); lo = int(pos); frac = pos - lo
    return xs[lo] + (xs[lo+1]-xs[lo])*frac if lo+1 < len(xs) else xs[lo]

def mann_whitney_u(a, b):
    """U statistic + normal-approx two-sided p (tie-corrected). Descriptive only at n=10."""
    combined = sorted([(v,0) for v in a] + [(v,1) for v in b])
    # rank with ties averaged
    ranks = [0.0]*len(combined); i = 0
    while i < len(combined):
        j = i
        while j+1 < len(combined) and combined[j+1][0] == combined[i][0]: j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j+1): ranks[k] = r
        i = j + 1
    Ra = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    na, nb = len(a), len(b)
    Ua = Ra - na*(na+1)/2; Ub = na*nb - Ua
    U = min(Ua, Ub)
    mu = na*nb/2; sigma = (na*nb*(na+nb+1)/12) ** 0.5
    z = (U - mu)/sigma if sigma else 0.0
    # two-sided normal approx
    import math
    p = math.erfc(abs(z)/math.sqrt(2))
    return {"U": U, "z": round(z,3), "p_approx": round(p,4)}

def main():
    gt = json.loads((HERE / "ground_truth.json").read_text())
    tn = [n["id"] for n in gt["nodes"]]
    te = [(e["from"], e["to"]) for e in gt["edges"]]

    conditions, per_run = {}, {}
    for cond in ["transcript", "prose", "kernel"]:
        runs = load_runs(cond)
        rows = []
        for r in runs:
            sc = score_graph(tn, te, r["nodes"], [tuple(x) for x in r["edges"]])
            rows.append({"run": r["run"],
                         "edge_f1": sc["edges"]["f1"], "edge_iou": sc["edges"]["iou"],
                         "edge_p": sc["edges"]["precision"], "edge_r": sc["edges"]["recall"],
                         "node_f1": sc["nodes"]["f1"], "node_iou": sc["nodes"]["iou"]})
        per_run[cond] = rows
        ef = [x["edge_f1"] for x in rows]
        ei = [x["edge_iou"] for x in rows]
        nf = [x["node_f1"] for x in rows]
        conditions[cond] = {
            "n": len(rows),
            "edge_f1": {"mean": round(st.mean(ef),3), "median": round(st.median(ef),3),
                        "sd": round(st.pstdev(ef),3), "min": round(min(ef),3), "max": round(max(ef),3),
                        "q1": round(quart(ef,.25),3), "q3": round(quart(ef,.75),3)},
            "edge_iou": {"mean": round(st.mean(ei),3), "median": round(st.median(ei),3),
                         "min": round(min(ei),3), "max": round(max(ei),3)},
            "node_f1": {"mean": round(st.mean(nf),3), "median": round(st.median(nf),3)},
            "failure_rate": round(sum(1 for v in ef if v < FAIL_THRESHOLD)/len(ef), 3),
        }

    cmp = {
        "kernel_vs_prose": mann_whitney_u([x["edge_f1"] for x in per_run["kernel"]],
                                          [x["edge_f1"] for x in per_run["prose"]]),
        "prose_vs_transcript": mann_whitney_u([x["edge_f1"] for x in per_run["prose"]],
                                              [x["edge_f1"] for x in per_run["transcript"]]),
        "kernel_vs_transcript": mann_whitney_u([x["edge_f1"] for x in per_run["kernel"]],
                                               [x["edge_f1"] for x in per_run["transcript"]]),
    }

    out = {"metric": "edge-F1 (primary); failure = edge-F1 < %.2f" % FAIL_THRESHOLD,
           "ground_truth": {"nodes": len(tn), "edges": len(te)},
           "conditions": conditions, "comparisons": cmp, "per_run": per_run}
    (HERE / "runs" / "scores.json").write_text(json.dumps(out, indent=2))

    print(f"{'condition':12s} {'edgeF1 median':>14s} {'mean':>7s} {'sd':>6s} {'min':>6s} {'max':>6s} {'fail%':>6s} {'nodeF1':>7s}")
    for c in ["transcript","prose","kernel"]:
        e=conditions[c]["edge_f1"]; print(f"{c:12s} {e['median']:>14.3f} {e['mean']:>7.3f} {e['sd']:>6.3f} {e['min']:>6.3f} {e['max']:>6.3f} {conditions[c]['failure_rate']*100:>5.0f}% {conditions[c]['node_f1']['median']:>7.3f}")
    print("\ncomparisons (Mann–Whitney U on edge-F1, descriptive at n=10):")
    for k,v in cmp.items(): print(f"  {k:22s} U={v['U']:.1f}  z={v['z']:+.2f}  p≈{v['p_approx']}")
    print("\nwrote runs/scores.json")

if __name__ == "__main__":
    main()
