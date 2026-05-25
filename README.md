https://im-gonzo.github.io/next-instruction-research/

# The interface is the next instruction

When the consumer of your interface is an agent, the screen isn't an output to look at —
it's the input the model acts on. This is a small, self-directed design thesis about the
**operator ↔ agent interface**: instead of re-describing structures to agents in prose every
session, you name them once — a shared **kernel** of primitives — and hand the agent the *name*.

Built and validated in a week, in code, with Claude Code as the collaborator.

## What's here

| file | what it is |
|---|---|
| **`case-study.html`** | The presentation deck (open in a browser). The argument + the evidence + a designed operator surface. |
| **`index.html`** | The longer thesis writeup. |
| **`experiments/`** | The reproducible research — toy-tower token measurement and a 30-run, pre-registered fidelity study on a real architecture. See [`experiments/README.md`](experiments/README.md) and [`experiments/architecture-transcript/RESULTS.md`](experiments/architecture-transcript/RESULTS.md). |
| **`kernel-skill/`** | The kernel as a drop-in **Claude Code skill** — onboard the kernel into any repo and generate a self-contained onboarding brief (ideas + lexicon, multi-view map). See [`kernel-skill/README.md`](kernel-skill/README.md). |

## The finding, in one line

A shared named kernel reconstructs a real architecture at **~9× fewer tokens** than explicit prose,
and — on a real engineering talk, across 30 builder runs — far more **reliably**: kernel **0.98**
edge-F1 (0% failures) vs. concise prose **0.80** vs. raw transcript **0.56** (40% failures).
The durable advantage isn't brevity, it's *fidelity under compression*: a name can't go vague.

## Viewing it

- **Deck / thesis:** open `case-study.html` or `index.html` directly in a browser.
- **Experiment-3 dashboard:** serve the repo and open the dashboard, e.g.
  ```bash
  python3 -m http.server 8000
  # → http://localhost:8000/experiments/architecture-transcript/index.html
  ```
- **Reproduce the experiments:** `pip install -r experiments/requirements.txt`, then the scripts in `experiments/` (see its README). Deterministic token counts (`tiktoken`); the fidelity runs are recorded verbatim under `experiments/architecture-transcript/runs/`.

## Honest scope

Deliberately small: toy towers and a single real architecture (30 builder runs, one model). The point
is the *mechanism* — compression-via-naming and exactness under compression — measured directly, with
the limits stated plainly in the deck's "scope & caveats" and the experiments' writeups.
