# Experiment 3 — pre-registration

**Registered 2026-05-25, before any builder run.** This fixes the design, metrics, and
decision rules in advance. All runs are reported verbatim and the outcome is published
**regardless of which way it falls** (a null / falsifying result is a valid result).

## Question

On a real, noisy architecture described three ways, how faithfully can a builder
reconstruct the component graph from each — and at what token cost?

## Design

- **Decoding-only.** All three stimuli are *frozen encodings* of the same system; there is
  no live architect. This isolates **decoding** fidelity (and avoids the L3 confound where a
  live architect's prose was wrong before the builder read it).
- **Three conditions** (same target graph):
  1. `transcript` — the raw architecture span (~6,616 tok); builder must *find* the graph in narration.
  2. `prose` — a concise human-written architecture summary (the fair-prose control), frozen + approved.
  3. `kernel` — the kernel encoding (per-service sub-kernels) + the one-time kernel definition.
- **Shared vocabulary.** Every condition's builder gets the *same* canonical component list
  (the 39 ground-truth ids + one-line glosses) **plus decoy components** that are plausible but
  absent. Output is a fixed schema: `{"nodes":[ids...], "edges":[[from,to]...]}`. This removes
  the kernel's unfair naming advantage and isolates **structure recovery**.
- **Builder model:** Claude Haiku (matches experiments 1–2 for comparability).
- **Replication:** **k = 10 independent runs per condition = 30 total.** Every output logged verbatim.

## Ground truth (locked)

`ground_truth.json` — **39 nodes / 48 edges**, validated 2026-05-25 against the engineer's
Excalidraw diagram + the transcript narration (semantic model; conventions in the file's `_meta`).
This is the fixed referent; it is not revised after runs begin.

## Metrics

- **Primary: edge-F1** — directed `(from,to)` pairs over the shared vocabulary.
- **Secondary:** edge-IoU, node-F1 (right components chosen, decoys rejected).
- **Run "failure":** edge-F1 **< 0.50**.
- **Failure rate:** fraction of the 10 runs below that threshold.
- **Cross-condition comparison:** median + IQR per condition; Mann–Whitney U at α = 0.05,
  reported as **descriptive** (n = 10), not a significance claim.
- Token counts are deterministic (`tiktoken · o200k_base`).

## Token accounting (stated up front, to keep the comparison honest)

For *this single* architecture the kernel's one-time definition is **not** amortized, so the kernel
**total** may exceed a concise prose summary. The kernel's claim here is therefore **not** "cheaper
for a one-off" — it is **higher / more reliable fidelity at comparable *encoding* tokens**, with the
token win being the amortization story (proven separately in exp 1). We report encoding tokens
per condition *and* the kernel's one-time def separately.

## Pre-registered hypotheses

- **H1 — kernel is near-lossless to decode:** kernel median edge-F1 **≥ 0.90**, failure rate **≤ 10%**.
- **H2 — raw transcript is the noisy floor:** lowest median fidelity and/or highest variance.
- **H3 — the crux, kernel vs *good* prose:**
  - **SUPPORTED** if kernel beats the prose control by **≥ 0.10 median edge-F1** *or* has a
    **materially lower failure rate** (≈ ½ or less) at comparable encoding tokens.
  - **FALSIFIED / WEAKENED** if the prose control **matches** the kernel within CI at comparable
    tokens — i.e., the earlier advantage was an artifact of comparing against the verbose transcript.
- **H4 — Pareto:** on the (encoding-tokens, edge-F1) plane, **no condition dominates the kernel on
  both axes**. If prose ties or dominates, the "brief AND exact" claim does not hold on real data.

## Procedure

1. Freeze stimuli: `kernel_encoding.txt` (re-encoded to the locked graph), `prose_summary.txt`
   (approved), transcript span (existing). Build `builder_kit` (vocab + decoys + schema).
2. Run 10 Haiku builders per condition; capture each `{nodes, edges}` into `builder-runs-exp3.md`.
3. Score every run with `score_graph()`; aggregate to distributions + failure rate in `exp3_state.json`.
4. Report: per-condition distributions, failure rates, the (tokens × edge-F1) Pareto scatter with
   error bars, and a plain statement of which hypotheses held — in the dashboard and the deck.
