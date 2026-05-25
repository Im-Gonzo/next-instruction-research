#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXPERIMENT 2 — pushing the harness along the *regularity* axis.
===============================================================

Experiment 1 used clean, fully-decomposable towers and found the kernel ~9x
cheaper. The obvious objection: that's only because the towers were tailor-made
for the macros. So push it — scale tower IRREGULARITY and watch three quantities:

  • kernel tokens        (brief + exact — macros, with primitive patches for noise)
  • exhaustive-NL tokens (exact but bloated — deterministic row-by-row enumeration)
  • descriptive-NL       (brief but may be LOSSY — produced by an architect agent;
                          a builder agent reconstructs; we score fidelity)

Hypothesis: as regularity drops, the kernel's TOKEN lead shrinks toward the
exhaustive baseline (random structure is incompressible) — but the kernel stays
EXACT, while concise descriptive NL starts to lose cells. The kernel is the only
register that is both brief and exact.

This file is the deterministic half (towers, ASCII renders, kernel specs, token
counts, scoring). Architect + builder agents supply the descriptive-NL half.
Run:  python3 run2.py
"""
from __future__ import annotations
import re, json
from run import C, Pi, L, row, col, block, expand, KERNEL_DEF, make_tokenizer

# ── three towers, increasing irregularity ────────────────────────────────────
# Each: a deterministic kernel spec (macros + primitive patches) that expands
# losslessly to the target. Higher levels need more primitive patches.
TOWERS = {
    "L1 · regular": "C(0,0)\nPi(0,3)",
    "L2 · semi (spur)": "C(0,0)\nPi(0,3)\nL(0,6)\ncol(4,3,3)",
    "L3 · irregular (scatter)": ("C(0,0)\nPi(0,3)\n"
        "block(4,1)\nblock(5,2)\nblock(4,4)\nblock(5,5)\nblock(3,5)\nblock(4,7)\n"
        "block(5,8)\nblock(2,7)\nblock(3,8)\nblock(1,7)\nblock(5,0)\nblock(4,9)"),
}

def cells_of(spec): return expand(spec)

def ascii_grid(cells):
    maxc = max(c for c, r in cells); maxr = max(r for c, r in cells)
    lines = []
    for r in range(maxr, -1, -1):
        lines.append(f"r{r:>2} " + " ".join("#" if (c, r) in cells else "." for c in range(maxc + 1)))
    lines.append("    " + " ".join(str(c) for c in range(maxc + 1)))
    return "\n".join(lines)

def nl_exhaustive(cells):
    """Deterministic, lossless natural-language enumeration (the 'exact but bloated' baseline)."""
    maxr = max(r for c, r in cells)
    out = ["Place unit blocks on a grid; cells are (column, row), row 0 at the bottom."]
    for r in range(maxr, -1, -1):
        cs = sorted(c for c, rr in cells if rr == r)
        if cs:
            out.append(f"Row {r}: fill column" + ("s " if len(cs) > 1 else " ") + ", ".join(map(str, cs)) + ".")
    return "\n".join(out)

def score(target, got):
    target, got = set(map(tuple, target)), set(map(tuple, got))
    inter = target & got
    iou = len(inter) / len(target | got) if (target | got) else 1.0
    return {"exact": got == target, "target": len(target), "got": len(got),
            "missing": len(target - got), "extra": len(got - target), "iou": round(iou, 3)}

def main():
    method, tok = make_tokenizer()
    D = tok(KERNEL_DEF)
    print(f"tokenizer: {method}   |   kernel definition (one-time): {D} tokens\n")
    rows = []
    for name, spec in TOWERS.items():
        cells = cells_of(spec)
        assert expand(spec) == cells, f"{name} not lossless"
        kt = tok(spec); et = tok(nl_exhaustive(cells))
        rows.append((name, len(cells), kt, et, round(et / kt, 1)))
        print(f"=== {name}  ({len(cells)} cells) ===")
        print(ascii_grid(cells))
        print(f"\nkernel spec ({kt} tok):\n{spec}")
        print(f"exhaustive-NL: {et} tok\n")
    print(f"{'tower':28} {'cells':>5} {'kernel':>7} {'exhNL':>7} {'exhNL/kernel':>13}")
    print("-" * 66)
    for n, c, kt, et, ratio in rows:
        print(f"{n:28} {c:>5} {kt:>7} {et:>7} {ratio:>12}x")
    # emit architect prompts (ASCII) + ground truth for the agent phase
    payload = {name: {"cells": sorted(map(list, cells_of(spec))),
                      "ascii": ascii_grid(cells_of(spec)),
                      "kernel_spec": spec, "kernel_tok": tok(spec),
                      "exhaustive_nl_tok": tok(nl_exhaustive(cells_of(spec)))}
               for name, spec in TOWERS.items()}
    payload["_kernel_def_tok"] = D
    with open("exp2_payload.json", "w") as f:
        json.dump(payload, f, indent=2)
    print("\nwrote exp2_payload.json (ascii + ground-truth cells for the agent phase)")

if __name__ == "__main__":
    main()
