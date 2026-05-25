# Experiment 3 — architecture from a real transcript

The unrigged test. Experiments 1–2 used toy towers the kernel itself authored. This one takes a **real engineering talk** (an ex-Atlassian engineer narrating a self-service edge/load-balancing platform — Open Service Broker → SQS/worker → DynamoDB; the "Sovereign" Envoy control plane; a CloudFormation proxy fleet; a Packer/SaltStack AMI pipeline; edge sidecars) and asks the same question on real, noisy input:

> On a real architecture description, does the kernel reconstruct the component graph more exactly at fewer tokens than the raw transcript?

## Run
```bash
python3 -m pip install tiktoken
python3 exp3.py        # measures tokens, verifies the kernel grammar, writes exp3_state.json
python3 score_runs.py  # scores the 30 builder reconstructions vs the validated graph → runs/scores.json
# dashboard: serve the dir and open index.html  (e.g. python3 -m http.server 8000)
```

## What's measured (deterministic, `tiktoken · o200k_base`)
- Transcript: **8,704 tokens** full · **6,616 tokens** architecture span.
- Kernel: **547 tokens** total = **158 encoding** + 389 one-time definition. The encoding is a 39-token shared `declare` block + **five per-service sub-kernels**: `OSB 21 · Sovereign 15 · CloudFormation 10 · Packer 8 · Edge 65`.
- Ratio: **12.1×** (span) · 15.9× (full transcript).
- Ground-truth graph: **39 components, 48 relations, VALIDATED** against the engineer's Excalidraw diagram + the talk narration (semantic model; conventions in `ground_truth.json` `_meta`).

## Status — RUN (2026-05-25)
The fidelity phase is complete. 30 independent Claude-Haiku builders (10 per condition) reconstructed the component graph from three frozen stimuli — the raw transcript span, a concise human prose summary, and the kernel encoding — each over a **shared vocabulary + decoys** (so naming is fixed and the discriminating signal is **edges/structure**), output to a fixed `{nodes, edges}` schema and scored by **edge-F1** vs the validated graph.

| condition | encoding tok | edge-F1 median | failure rate |
|---|---|---|---|
| transcript | 6,616 | 0.557 | **40%** |
| prose | 298 | 0.800 | **0%** |
| **kernel** | **158** | **0.979** | **0%** |

**Result: kernel 0.979 > prose 0.800 > transcript 0.557 (edge-F1 median); kernel vs prose is complete separation (Mann–Whitney U=0, p≈0.0002). All four pre-registered hypotheses (`PREREGISTRATION.md`) supported.** Honest note: the kernel wins on *encoding* tokens (158) AND fidelity, but its *total* (547, incl. the one-time 389-tok definition) exceeds the prose summary (298) for this single architecture — the token win is the amortization story (exp 1); here the win is **fidelity + reliability**. Full writeup in `RESULTS.md`; raw reconstructions in `runs/{transcript,prose,kernel}.jsonl`; per-run + aggregate scores in `runs/scores.json`. Dashboard's Fidelity panel renders from `exp3_state.json`.

## Ground truth
`ground_truth.json` is the **validated** semantic model — reconciled 2026-05-25 against the engineer's Excalidraw architecture diagram + the talk narration. Modeling conventions (what was merged, folded, kept from the talk, and fixed vs the earlier candidate) are documented in the file's `_meta`. A different convention would shift the absolute numbers, not the ordering.

## Files
| file | what |
|---|---|
| `transcript.txt` | frozen source transcript (public talk, yt 55pTFVoclvE) |
| `ground_truth.json` | the component graph — 39 nodes / 48 edges (VALIDATED) |
| `kernel_def.txt` | the shared architecture-kernel vocabulary (defined once) |
| `kernel_encoding.txt` | this architecture expressed in the kernel |
| `prose_summary.txt` | the concise human-prose control summary |
| `builder_kit.md` | shared vocabulary + decoys + output schema given to every builder |
| `builder_inputs/` | the exact, isolated stimuli (one per condition; no ground truth) |
| `PREREGISTRATION.md` | design, metrics, and decision thresholds, registered before the runs |
| `exp3.py` | harness: tokenizer, lossless-expansion check, `score_graph()`, writes state |
| `score_runs.py` | scores the 30 reconstructions (reuses `exp3.py: score_graph`) → `runs/scores.json` |
| `runs/{transcript,prose,kernel}.jsonl` | all 30 reconstructions, verbatim |
| `runs/scores.json` | per-run + aggregate scores |
| `exp3_state.json` | live state the dashboard renders (fidelity folded in) |
| `index.html` | live dashboard (stages · architecture diagram · token bars · fidelity) |
| `RESULTS.md` | the experiment-3 writeup (headline, hypotheses, caveats) |
