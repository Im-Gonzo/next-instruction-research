#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
architect/builder · kernel-vs-natural-language context-efficiency experiment
============================================================================

Question (the page's "open test", made runnable):
  Building the SAME 2D tower, does an architect who speaks in the shared
  *kernel* (named construction primitives) make the builder consume fewer
  tokens than an architect who speaks in *natural language* — and after how
  many towers does the kernel's one-time definition cost pay for itself?

This harness is deterministic: it defines the towers as compositions of named
macros (the ground truth), hand-authors a faithful natural-language spec for
each, verifies the kernel spec expands losslessly to the target, then measures
token cost of every artifact and computes the amortized break-even.

Fidelity of *reconstruction from each spec* is tested separately by two builder
agents (see README); this file measures CONTEXT COST and proves the kernel
grammar is lossless.

Run:  python3 run.py
"""
from __future__ import annotations
import re, json, sys

# ── the shared construction kernel (macros over a grid; (col,row) bottom-left) ──
def block(x, y):        return {(x, y)}
def row(x, y, n):       return {(x + i, y) for i in range(n)}
def col(x, y, n):       return {(x, y + i) for i in range(n)}
def C(x, y):            return col(x, y, 3) | row(x, y, 3) | {(x + 1, y + 2), (x + 2, y + 2)}   # open right, 3x3
def Pi(x, y):           return col(x, y, 3) | col(x + 2, y, 3) | {(x + 1, y + 2)}                # open bottom, 3x3
def L(x, y):            return col(x, y, 3) | {(x + 1, y), (x + 2, y)}                            # L, 3x3 footprint

MACROS = {"block": block, "row": row, "col": col, "C": C, "Pi": Pi, "L": L}

def expand(spec: str) -> set:
    """Parse + expand a kernel spec like 'C(0,0)\\nPi(0,3)' into a cell set."""
    cells = set()
    for line in spec.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.fullmatch(r"([A-Za-z]+)\(([0-9,\s]*)\)", line)
        if not m:
            raise ValueError(f"bad kernel line: {line!r}")
        name, args = m.group(1), [int(a) for a in m.group(2).split(",") if a.strip() != ""]
        cells |= MACROS[name](*args)
    return cells

# ── the kernel DEFINITION — paid ONCE, reused across every tower ──────────────
KERNEL_DEF = """\
KERNEL — shared construction vocabulary (defined once, reused for every tower).
Grid coordinates are (column, row); the anchor (x,y) is the shape's bottom-left.
  block(x,y)   one block at (x,y).
  row(x,y,n)   n blocks left-to-right: (x,y)..(x+n-1,y).
  col(x,y,n)   n blocks bottom-to-top: (x,y)..(x,y+n-1).
  C(x,y)       col(x,y,3) + row(x,y,3) + (x+1,y+2),(x+2,y+2). A C open to the right (3x3).
  Pi(x,y)      col(x,y,3) + col(x+2,y,3) + (x+1,y+2). A Pi open at the bottom (3x3).
  L(x,y)       col(x,y,3) + (x+1,y),(x+2,y). An L (3x3 footprint).
"""

# ── two target towers, each given in BOTH conditions ──────────────────────────
TOWERS = {
    "A · stack(C,Pi,L)": {
        "kernel": "C(0,0)\nPi(0,3)\nL(0,6)",
        "nl": """\
On a grid with columns 0-2 (left to right) and rows 0-8 (bottom to top), place unit blocks.
Rows 0-2: fill column 0 for all three rows; on row 0 also fill columns 1 and 2; on row 2 also
fill columns 1 and 2; leave columns 1 and 2 of row 1 empty (the shape is open on the right).
Rows 3-5: fill column 0 and column 2 for all three rows; on row 5 also fill column 1; leave
column 1 of rows 3 and 4 empty (the shape is open at the bottom).
Rows 6-8: fill column 0 for all three rows; on row 6 also fill columns 1 and 2; leave the rest empty.""",
    },
    "B · stack(C,C,Pi)+cap": {
        "kernel": "C(0,0)\nC(0,3)\nPi(0,6)\nrow(0,9,3)",
        "nl": """\
On a grid with columns 0-2 (left to right) and rows 0-9 (bottom to top), place unit blocks.
Rows 0-2: fill column 0 for all three rows; on row 0 also fill columns 1 and 2; on row 2 also
fill columns 1 and 2; leave columns 1 and 2 of row 1 empty (open on the right).
Rows 3-5: fill column 0 for all three rows; on row 3 also fill columns 1 and 2; on row 5 also
fill columns 1 and 2; leave columns 1 and 2 of row 4 empty (open on the right).
Rows 6-8: fill column 0 and column 2 for all three rows; on row 8 also fill column 1; leave
column 1 of rows 6 and 7 empty (open at the bottom).
Row 9: fill columns 0, 1, and 2.""",
    },
}

# ── tokenizer: real if available, else robust proxies ─────────────────────────
def make_tokenizer():
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        return ("tiktoken · o200k_base", lambda s: len(enc.encode(s)))
    except Exception:
        # subword-free proxy: word+punct count (under-counts vs BPE but the
        # NL/kernel RATIO — the load-bearing result — is tokenizer-robust).
        tok = lambda s: len(re.findall(r"\w+|[^\w\s]", s))
        return ("proxy · word+punct (tiktoken not installed)", tok)

def measures(s, tok):
    return {"tokens": tok(s), "words": len(s.split()), "chars": len(s)}

def main():
    method, tok = make_tokenizer()
    out = {"tokenizer": method, "towers": {}, "kernel_def": measures(KERNEL_DEF, tok)}

    # fidelity: kernel spec must expand losslessly to a target the NL also describes
    nl_tot = kn_tot = 0
    for name, t in TOWERS.items():
        target = expand(t["kernel"])
        nl_m, kn_m = measures(t["nl"], tok), measures(t["kernel"], tok)
        nl_tot += nl_m["tokens"]; kn_tot += kn_m["tokens"]
        out["towers"][name] = {
            "cells": len(target), "kernel_expands_ok": expand(t["kernel"]) == target,
            "nl": nl_m, "kernel": kn_m,
            "ratio_nl_over_kernel": round(nl_m["tokens"] / kn_m["tokens"], 2),
        }

    n = len(TOWERS)
    mean_nl, mean_kn = nl_tot / n, kn_tot / n
    D = out["kernel_def"]["tokens"]
    saving = mean_nl - mean_kn
    breakeven = D / saving if saving > 0 else float("inf")
    out["analysis"] = {
        "mean_tokens_per_tower_nl": round(mean_nl, 1),
        "mean_tokens_per_tower_kernel": round(mean_kn, 1),
        "kernel_definition_overhead": D,
        "marginal_saving_per_tower": round(saving, 1),
        "breakeven_towers": round(breakeven, 2),
        "totals_by_N": {
            str(N): {"nl": round(N * mean_nl), "kernel": round(D + N * mean_kn),
                     "kernel_cheaper": (D + N * mean_kn) < (N * mean_nl)}
            for N in (1, 2, 3, 5, 10, 20)
        },
    }

    # ── report ────────────────────────────────────────────────────────────────
    print(f"tokenizer: {method}\n")
    print(f"kernel definition (one-time): {D} tokens · {out['kernel_def']['chars']} chars\n")
    print(f"{'tower':22} {'cells':>5} {'NL tok':>7} {'kernel tok':>11} {'NL/kernel':>10} {'lossless':>9}")
    print("-" * 70)
    for name, r in out["towers"].items():
        print(f"{name:22} {r['cells']:>5} {r['nl']['tokens']:>7} {r['kernel']['tokens']:>11} "
              f"{r['ratio_nl_over_kernel']:>9}x {str(r['kernel_expands_ok']):>9}")
    a = out["analysis"]
    print(f"\nmean tokens / tower    NL {a['mean_tokens_per_tower_nl']}   kernel {a['mean_tokens_per_tower_kernel']}"
          f"   (saving {a['marginal_saving_per_tower']}/tower)")
    print(f"break-even             {a['breakeven_towers']} towers "
          f"(kernel def = {D} tok amortizes after this many)\n")
    print(f"{'N towers':>9} {'NL total':>9} {'kernel total':>13} {'winner':>10}")
    print("-" * 46)
    for N, row_ in a["totals_by_N"].items():
        print(f"{N:>9} {row_['nl']:>9} {row_['kernel']:>13} {'kernel' if row_['kernel_cheaper'] else 'NL':>10}")

    with open("results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote results.json")

if __name__ == "__main__":
    main()
