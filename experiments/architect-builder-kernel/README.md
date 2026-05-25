# Architect / Builder · kernel vs. natural language — context-efficiency experiment

**The page's "open test", made runnable.** If the kernel is load-bearing, an architect
who speaks in the *shared kernel* should make the builder consume fewer tokens than an
architect who speaks in *natural language* — for the **same** constructed tower. This
measures by how much, and finds the break-even where the kernel's one-time definition
cost pays for itself.

## Design

- **Task.** Reconstruct a 2D block tower on a grid (cells are `(column, row)`). Two towers:
  `A = stack(C, Pi, L)` (19 cells), `B = stack(C, C, Pi) + cap` (24 cells).
- **Two architect conditions, identical target:**
  - **natural language** — the architect describes the geometry in plain prose, region by
    region, with no shared shorthand. The builder reconstructs from prose.
  - **kernel** — the architect emits named primitives from a shared library
    (`C(0,0)`, `Pi(0,3)`, `L(0,6)`). The builder expands them using the kernel definitions.
- **Metric — context cost.** Tokens the builder must consume, measured with
  `tiktoken · o200k_base` (the deterministic, reproducible measurement). The kernel
  condition carries a **one-time** definition cost (`KERNEL_DEF`) amortized across all towers;
  natural language re-derives the geometry every tower.
- **Fidelity control.** A condition only counts if it reconstructs the target *exactly*.
  The kernel grammar is verified to expand losslessly (`expand(spec) == target`); both
  conditions are then handed to **builder agents** (Claude Haiku) that output the filled
  cells, checked against ground truth.
- **Controls.** Same target tower; same builder model; both conditions proven lossless,
  so the token delta is pure description efficiency, not a fidelity trade.

## Results

Tokenizer: `tiktoken · o200k_base`. Kernel definition (one-time): **216 tokens**.

| tower | cells | NL tokens | kernel tokens | NL / kernel | lossless |
|---|--:|--:|--:|--:|:--:|
| A · stack(C,Pi,L) | 19 | 176 | 18 | **9.8×** | ✓ |
| B · stack(C,C,Pi)+cap | 24 | 213 | 26 | **8.2×** | ✓ |

- **Marginal cost:** NL ≈ **194.5** tokens/tower · kernel ≈ **22.0** tokens/tower → saving **172.5/tower**.
- **Break-even: 1.25 towers.** The 216-token kernel definition is repaid after the second tower.

| N towers | NL total | kernel total | winner |
|--:|--:|--:|:--|
| 1 | 194 | 238 | NL |
| 2 | 389 | 260 | **kernel** |
| 3 | 584 | 282 | **kernel** |
| 5 | 972 | 326 | **kernel** |
| 10 | 1,945 | 436 | **kernel** (4.5×) |
| 20 | 3,890 | 656 | **kernel** (5.9×) |

- **Builder fidelity (tower A):** both the NL builder and the kernel builder reconstructed
  all 19 cells **exactly** (0 missing, 0 extra). Compression cost no accuracy here.

## Verdict

Above one tower, the kernel is decisively more context-efficient — and the advantage widens
with reuse (≈6× by 20 towers), because the kernel's cost is a fixed definition plus a near-flat
per-tower invocation, while natural language pays the full geometry every time. This is the
compression-via-naming mechanism (Fan / Wong & McCarthy / DreamCoder) measured directly:
**a name is paid for once and invoked cheaply forever after.**

## Caveats

- The kernel saving is **conditional on reuse** — for a one-off tower, plain language wins
  (break-even 1.25). The kernel earns its keep only across repeated reference, exactly the
  amortization the literature predicts.
- The clean token measurement is the harness's `tiktoken` count of the *spec text*. The builder
  agents' reported `total_tokens` (~60k each) are dominated by the agent's own system prompt and
  are **not** used as the cost metric — they only validate reconstruction fidelity.
- Both conditions were lossless on these tame, well-decomposed towers. NL is expected to lose
  fidelity faster as towers grow irregular (no clean macro covers them) — a follow-up: scale tower
  complexity until NL reconstruction breaks while kernel stays exact.
- Token counts shift with tokenizer choice; the **NL/kernel ratio** (the result) is robust to it.

## Run

```bash
python3 run.py          # prints the tables, writes results.json
```

`run.py` holds the kernel macros, both towers in both conditions, the tokenizer, the
lossless-expansion check, and the break-even analysis. Builder fidelity was tested by
dispatching two Haiku builder agents (one per condition) and comparing their output cells
to `C(0,0) | Pi(0,3) | L(0,6)`.

---

# Experiment 2 — pushing along the *regularity* axis

**Objection to experiment 1:** the towers were tailor-made for the macros, so of course
the kernel won. **Push:** scale tower *irregularity* and watch three registers — the kernel
(macros + primitive patches), exhaustive natural language (deterministic row-by-row, always
exact), and *concise descriptive* natural language (produced by an architect agent; a builder
agent rebuilds; we score fidelity).

Three towers: `L1 regular` (2 clean macros), `L2 semi` (macros + a spur), `L3 irregular`
(2 macros + 12 scattered blocks — near-incompressible). Architects = Claude Sonnet; builders
= Claude Haiku. Tokens via `tiktoken · o200k_base`.

| level | cells | kernel tok | exhaustive-NL | kernel vs exhNL | descriptive-NL fidelity | kernel fidelity |
|---|--:|--:|--:|--:|:--|:--|
| L1 · regular | 14 | 12 | 99 | **8.2×** | exact ✓ | exact ✓ |
| L2 · semi (spur) | 22 | 26 | 141 | **5.4×** | exact ✓ | exact ✓ |
| L3 · irregular (scatter) | 26 | 84 | 153 | **1.8×** | **broke — IoU 0.86, −1/+3** | **exact ✓** |

## Findings

1. **The token lead is a function of regularity.** Kernel-vs-NL compression falls from 8.2×
   (regular) to 1.8× (irregular). On incompressible structure the kernel must fall back to
   `block()` primitives and stops compressing — exactly as the literature's U-curve implies.
2. **Concise prose isn't even reliably cheap.** At L2 the architect's "concise" description
   (220 tok) cost *more* than exhaustive enumeration (141 tok) — describing irregular geometry
   in prose is not economical.
3. **The durable advantage is fidelity, not tokens.** Descriptive NL reconstructed exactly at
   L1 and L2 but **broke at L3** (builder missed 1 cell, invented 3) once the architect's prose
   turned hedgy ("a small inverted-L or T near the top right"). The kernel stayed **exact at
   every level**, including L3, because a symbolic spec has no ambiguity to lose.

## Verdict (both experiments)

The kernel is the only register that is **both brief and exact** across the regularity range.
On compositional structure it is brief, exact, and ~8× cheaper, repaying its definition after
~1 tower. As structure becomes incompressible its token lead shrinks toward natural language —
but it never loses fidelity, while concise natural language becomes expensive *and* lossy. The
naming substrate buys exactness under compression pressure; tokens are just the visible part.

*A shared name is not only shorter — it is the one description that cannot be misread.*
