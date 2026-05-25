# Experiment 3 — results

Run 2026-05-25. 30 independent Claude-Haiku builder reconstructions (10 per condition) of the
locked 39-node / 48-edge architecture graph, scored against `ground_truth.json`. Pre-registered
design and thresholds in `PREREGISTRATION.md`; raw outputs in `runs/{transcript,prose,kernel}.jsonl`;
per-run + aggregate scores in `runs/scores.json`. Primary metric = **edge-F1**; failure = edge-F1 < 0.50.

## Headline

| condition | encoding tok | edge-F1 median | mean | sd | min–max | failure rate | node-F1 median |
|---|---|---|---|---|---|---|---|
| transcript (6,616 tok) | 6,616 | 0.557 | 0.566 | 0.102 | 0.434–0.713 | **40%** | 0.939 |
| prose (298 tok) | 298 | 0.800 | 0.761 | 0.078 | 0.600–0.839 | **0%** | 0.980 |
| **kernel (158 tok)** | **158** | **0.979** | 0.973 | **0.017** | 0.923–0.989 | **0%** | 0.987 |

Mann–Whitney U on edge-F1 (descriptive, n=10): **kernel > prose** U=0, z=−3.78, p≈0.0002 (complete
separation — every kernel run beat every prose run); **prose > transcript** U=9, p≈0.0019;
**kernel > transcript** U=0, p≈0.0002.

## Verdict against the pre-registered hypotheses

- **H1 — kernel near-lossless: SUPPORTED.** Median edge-F1 0.979 (≥ 0.90) at a 0% failure rate (≤ 10%).
  Not a rigged 1.0: the kernel's systematic `customer→osb` (the macro's generic `client` bound to the
  declared `customer`, so the `client` node/edge is missed) plus minor `ec2`-host variance hold it at ~0.97.
- **H2 — transcript is the noisy floor: SUPPORTED.** Lowest median (0.557), highest variance (sd 0.102),
  40% of runs below the failure threshold. Builders mis-placed CloudFront into the customer path, flipped
  config-flow directions, and attached the products inconsistently.
- **H3 — kernel beats *good* prose: SUPPORTED.** Kernel median exceeds the concise-prose control by
  **+0.179 edge-F1** (≥ 0.10), with **complete distribution separation** and ~4.6× lower variance
  (sd 0.017 vs 0.078) — at *fewer* encoding tokens (158 vs 298). The earlier advantage was **not** just an
  artifact of comparing against the verbose transcript: even careful prose loses structure that the
  symbolic spec preserves.
- **H4 — Pareto: SUPPORTED.** On (encoding-tokens, edge-F1) the kernel sits alone in the non-dominated
  corner — fewest encoding tokens **and** highest fidelity. No condition dominates it on both axes.

## Honest caveats (carried from the pre-registration)

- **Tokens, full picture:** the kernel wins on *encoding* tokens (158) and fidelity, but its one-time
  definition (389 tok) makes its **total** (547) larger than the prose summary (298) for this *single*
  architecture. The token advantage is an amortization story (exp 1); here the win is **fidelity + reliability**.
- **Builder = Haiku, n=10 per condition.** A real distribution and failure rate (not n=1), but still one
  model, one architecture. Node-F1 is high everywhere because the shared vocabulary fixes naming by design —
  the discriminating signal is **edges (structure)**, exactly as intended.
- **Ground truth** is the semantic model validated against the engineer's Excalidraw + the talk (see
  `ground_truth.json` `_meta`); a different modeling convention would shift absolute numbers (not the ordering).

## Files
- `PREREGISTRATION.md` — design + thresholds, registered before the runs.
- `builder_inputs/` — the exact, isolated stimuli given to builders (kit + 3 stimuli; no ground truth).
- `runs/{transcript,prose,kernel}.jsonl` — all 30 reconstructions, verbatim.
- `runs/scores.json` — per-run and aggregate scores.
- `score_runs.py` — the scorer (reuses `exp3.py: score_graph`).
- `exp3_state.json` — live dashboard state, now with fidelity folded in.
