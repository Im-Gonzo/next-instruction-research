# Builder runs — verbatim agent transcripts

The token counts in `results.json` / `results2.json` are deterministic (`tiktoken`). The **fidelity** numbers come from running real agents: an **architect** (Claude Sonnet) that produces the description, and a **builder** (Claude Haiku) that reconstructs the cell set from that description alone. This file records those runs so the fidelity claims are auditable. Cells are `[col, row]`, column 0 at left, row 0 at bottom.

---

## Experiment 1 — tower A `stack(C, Pi, L)` (19 cells)

Ground truth = `C(0,0) | Pi(0,3) | L(0,6)`.

**Natural-language condition** — the architect spec was the deterministic 176-token prose (see `run.py` → `NL_A`). Builder (Haiku) output:
```
[[0,0],[1,0],[2,0],[0,1],[0,2],[1,2],[2,2],[0,3],[2,3],[0,4],[2,4],[0,5],[1,5],[2,5],[0,6],[1,6],[2,6],[0,7],[0,8]]
```
→ **19 / 19 exact** (0 missing, 0 extra).

**Kernel condition** — spec `C(0,0)\nPi(0,3)\nL(0,6)` (18 tok) + the kernel definitions. Builder (Haiku) output:
```
[[0,0],[0,1],[0,2],[1,0],[2,0],[1,2],[2,2],[0,3],[0,4],[0,5],[2,3],[2,4],[2,5],[1,5],[0,6],[0,7],[0,8],[1,6],[2,6]]
```
→ **19 / 19 exact**.

**Result:** both registers lossless. The kernel was ~9× cheaper (18 vs 176 tok) at equal fidelity.

---

## Experiment 2 — the regularity ladder

Architect (Sonnet) was asked to describe each grid in **concise** natural language (shapes/relations, not a cell-by-cell dump). Builder (Haiku) reconstructed from the words alone.

### L1 — regular (14 cells) — `C(0,0) | Pi(0,3)`
Architect (verbatim):
> "Three-wide rectangle at the base (r0), then a single block on the left (r1), then another three-wide rectangle spanning r2–r5, but with the middle column hollowed out on r3 and r4 — so it's a 3x4 frame with open center cells at (1,3) and (1,4)."

Builder → **14 / 14 exact.**

### L2 — semi (22 cells) — `C(0,0) | Pi(0,3) | L(0,6) | col(4,3,3)`
Architect (verbatim):
> "Column 0 is a full vertical spine from bottom to top — all 9 rows filled. At the base (r0), a 3-wide bar across cols 0–2. One row up (r1), just the spine at col 0. At r2, another 3-wide bar across 0–2. From r3 to r4, column 2 is filled alongside the spine, two posts with a gap at col 1. At r5, the full 3-wide bar returns, plus an isolated cell at col 4. At r6, another 3-wide bar (no col 4). From r7 to r8, just the spine. A lone floating cell at col 4 on rows 3, 4, 5."

Builder → **22 / 22 exact.**

### L3 — irregular / scatter (26 cells) — `C(0,0) | Pi(0,3) | 12 scattered block()s`  ← **the break**
Architect (verbatim, abridged):
> "…Left column (col 0): solid from bottom to row 5. Center-left cluster: **col 2 is solid r0–r3**. At r5 both cols 1 and 2 filled… a small inverted-L or T near the top right…"

Builder → **IoU 0.862** — missed `(2,4)`; invented `(2,1)`, `(4,5)`, `(4,8)`.

**Why it broke (encoder-side):** the architect's prose was *factually wrong before the builder ever read it* — "col 2 is solid r0–r3" is incorrect (column 2 is actually filled at r0, r2, r3, r4, r5). The builder faithfully built the wrong description, adding `(2,1)` and dropping `(2,4)`. Concise prose lost the structure at the description step.

**L3 kernel condition** — spec `C(0,0)\nPi(0,3)` + 12 `block()` calls (84 tok). Builder → **26 / 26 exact** — a symbolic spec has no ambiguity to lose.

---

*Note: agent reconstructions are not deterministic across runs (unlike the token counts). These are the runs that produced the reported fidelity figures; re-running may vary, especially on L3 where the descriptive-NL register is unstable.*
