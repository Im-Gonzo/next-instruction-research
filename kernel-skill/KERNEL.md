# KERNEL.md

> Dropped here by the **kernel** skill. Read before dispatching agents in this repo.

This project works the **kernel** way: a shared, named vocabulary for the structures you keep
re-describing. Name a structure once; hand a builder a primitive instead of a paragraph.

## The three roles
- **architect** — sees the target, describes it, decides what's worth naming.
- **builder** — has only the words; reconstructs from the spec alone (the exactness test).
- **lexicographer** — watches the dialogue and coins the names; promotes a re-described structure into a primitive.

## The idea harness (L0 → L3)
Context nests outward and is defined in `ideas.json`:
- **L0** root — the project.
- **L1** ideas — the unit of inherited context (what a session opens with).
- **L2** workstreams — capacity-bounded; split when a bucket strains (pigeonhole).
- **L3** primitives — the named, measured, cheap kernel.

Scope work to an **idea**, not a directory. Crossing an idea's boundary is an **excursion** —
surface it (allow / re-bind / split) instead of silently widening scope.

## Grammar
```
nodes:  id:type "label"
edges:  a->b  flow          a~>b  async (via queue)     a=>b  provisions / creates
        a:>b  config flow   a^b   hosts / runs          a&b   references
macros (expand to subgraphs — name once, invoke everywhere):
        stack(C, Pi, L)
        async_broker(api, queue, worker, db)
        control_plane(ctrl, proxy, store)
```

## Two rules
- **Pigeonhole** — load is primitives ÷ sibling workstreams, not raw count. Split a strained workstream.
- **Pareto** — you want fewer tokens *and* higher fidelity at once. The named primitive is brief AND exact, so it dominates prose on both.

## Why it pays (measured)
- ~**9×** fewer tokens than explicit prose per object (repaid by the 2nd reuse).
- On a real architecture: kernel **0.98** edge-F1 vs prose **0.80** vs raw transcript **0.56**; kernel **0%** failures vs **40%** from the transcript.
- The durable edge is **fidelity under compression** — a name can't be vague.

## Keeping the brief fresh
Add structures to `ideas.json` as you name them, then re-run the skill's
`generate_brief.py <repo>` to refresh `kernel-brief.html` (incl. the concentric-ring idea map).
