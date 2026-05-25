# Experiments — architect / builder & the kernel

Self-directed research testing one question: **does a shared, named "kernel" let an AI builder reconstruct a structure at far lower token cost than natural language — and does it stay exact when prose breaks?** Grounded in Judy Fan's architect/builder paradigm (an architect who can see the target describes it; a builder who only has the words rebuilds it).

Everything here is reproducible: deterministic token measurement (`tiktoken · o200k_base`), frozen data, and the harness scripts. The fidelity checks were run with Claude agents (architect = Sonnet, builder = Haiku); those runs are recorded in `architect-builder-kernel/builder-runs.md`.

## Setup
```bash
python3 -m pip install -r requirements.txt      # tiktoken
```
Python 3.11+.

## The three experiments

### 1 + 2 — `architect-builder-kernel/`  (toy 2D block towers)
```bash
cd architect-builder-kernel
python3 run.py      # experiment 1 — amortized context cost
python3 run2.py     # experiment 2 — the regularity ladder
```
- **Exp 1:** describing a tower in the kernel costs **~9× fewer tokens** than natural language (≈22 vs ≈194 / tower); the 216-token kernel definition is repaid after **~1.25 towers**; both builder reconstructions were exact (lossless).
- **Exp 2:** as towers get irregular the token lead shrinks (**8.2× → 5.4× → 1.8×**) — but concise natural language **broke** at the irregular tower (IoU 0.86 — the architect's prose was factually wrong before the builder ever read it), while the symbolic kernel stayed **exact at every level**. The durable advantage is *fidelity under compression*, not raw brevity.
- Outputs: `results.json`, `results2.json`. Visualization: open `viz.html`.

### 3 — `architecture-transcript/`  (a real architecture, unrigged)
```bash
cd architecture-transcript
python3 exp3.py        # ingests transcript.txt, measures tokens, writes exp3_state.json
python3 score_runs.py  # scores the 30 builder reconstructions vs the validated graph
```
- A real engineering talk (a self-service edge platform) described in plain language vs. the kernel, rebuilt as a component graph. Transcript ≈ **6,616 tokens** (architecture span) vs. the kernel's **158 encoding** tokens (a 39-token shared `declare` block + five per-service sub-kernels: OSB 21 · Sovereign 15 · CloudFormation 10 · Packer 8 · Edge 65) — span ratio **12.1×** (15.9× vs the 8,704-token full transcript). The kernel's *total* is **547 tokens** (158 encoding + a one-time 389-token definition). Ground-truth graph: **39 components / 48 relations, VALIDATED** against the engineer's Excalidraw diagram + the talk narration (semantic model; conventions in `ground_truth.json` `_meta`).
- **Status — RUN (2026-05-25).** 30 independent Claude-Haiku builders (10 per condition) reconstructed the graph from the transcript / a concise human prose summary / the kernel encoding — all over a shared vocabulary + decoys — scored by edge-F1 vs the validated graph. **Result: kernel edge-F1 median 0.979 (0% failures) > prose 0.800 (0% failures) > transcript 0.557 (40% failures); kernel vs prose is complete separation (Mann–Whitney U=0, p≈0.0002). All four pre-registered hypotheses supported.** Honest note: the kernel wins on *encoding* tokens (158) AND fidelity, but its *total* (547, incl. the one-time 389-tok definition) exceeds the prose summary (298) for a single architecture — the token win is the amortization story (exp 1); here the win is **fidelity + reliability**. Pre-registered design + thresholds in `PREREGISTRATION.md`; full writeup in `RESULTS.md`. Live dashboard: serve the dir and open `index.html`.

## File manifest
```
requirements.txt
architect-builder-kernel/
  run.py            exp 1 harness (towers, tokenizer, break-even)
  run2.py           exp 2 harness (regularity ladder, graph-fidelity scorer)
  results.json      exp 1 measured output
  results2.json     exp 2 measured output
  exp2_payload.json exp 2 ground-truth grids + cells (for the agent phase)
  builder-runs.md   verbatim architect descriptions + builder reconstructions + scoring
  viz.html          standalone interactive visualization (D3)
  viz_data.json     baked data for viz.html
README.md           (this file)
architecture-transcript/
  transcript.txt    frozen source transcript (public talk)
  ground_truth.json the component graph — 39 nodes / 48 edges (VALIDATED)
  kernel_def.txt    the shared architecture-kernel vocabulary
  kernel_encoding.txt  this architecture expressed in the kernel
  prose_summary.txt the concise human-prose control summary
  builder_kit.md    shared vocabulary + decoys + output schema given to builders
  builder_inputs/   the exact, isolated stimuli (one per condition; no ground truth)
  PREREGISTRATION.md  design + metrics + thresholds, registered before the runs
  exp3.py           harness (tokens, graph-fidelity scorer, writes state)
  score_runs.py     scores the 30 reconstructions (reuses exp3.py score_graph)
  runs/transcript.jsonl  the 10 transcript reconstructions, verbatim
  runs/prose.jsonl       the 10 prose reconstructions, verbatim
  runs/kernel.jsonl      the 10 kernel reconstructions, verbatim
  runs/scores.json       per-run + aggregate scores
  exp3_state.json   live state read by the dashboard (fidelity folded in)
  index.html        live experiment-3 dashboard (D3 + dagre)
  RESULTS.md        the experiment-3 writeup (headline, hypotheses, caveats)
  README.md
```

## Honest scope
These are deliberately small: toy towers, a single operator–model dyad, one working day for exp 1–2; exp 3 is a single real architecture with 30 builder runs (one model, Haiku). Node-F1 is high everywhere by design (the shared vocabulary fixes naming) — the discriminating signal is **edges (structure)**. And for a *one-off* architecture the kernel's total (547 tok, incl. its one-time 389-tok definition) is larger than a prose summary; exp 3's win is **fidelity + reliability**, with the token win being exp 1's amortization story. The point is the *mechanism* (compression-via-naming, and exactness under compression), measured directly. The "25–60 named-primitive sweet spot" referenced in the writeups is **our own operating window**, not a published literature finding. See the references below.

## References

**Talks (primary sources)**
- Judith Fan — *Cognitive Tools for Making the Invisible Visible* — https://www.youtube.com/watch?v=AF3XJT9YKpM
- Judith Fan — *Cognitive Tools for Uncovering Useful Abstractions* — https://www.youtube.com/watch?v=GcyAXVND3u8
- *I was laid off by Atlassian* (experiment 3 transcript source) — https://www.youtube.com/watch?v=55pTFVoclvE

**Papers**
- McCarthy, Hawkins, Wang, Holdaway & Fan (2021) — *Learning to communicate about shared procedural abstractions* — CogSci 2021 — arXiv:2107.00077
- Wong, McCarthy, Grand, Friedman, Tenenbaum, Andreas, Hawkins & Fan (2022) — *Identifying concept libraries from language about object structure* — CogSci 2022 — arXiv:2205.05666
- Wong, Ellis, Tenenbaum & Andreas (2021) — *Leveraging Language to Learn Program Abstractions and Search Heuristics* (LAPS) — ICML 2021 — arXiv:2106.11053
- Hawkins, Frank & Goodman (2017) — *Convention-formation in iterated reference games* — CogSci 2017
- Ellis et al. (2021) — *DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning* — PLDI 2021 — arXiv:2006.08381

*Note: the "25–60 named-primitive sweet spot" is our own operating window, not a published finding from these sources.*
