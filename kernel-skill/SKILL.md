---
name: kernel
description: Onboard the "kernel" — a shared named-primitive vocabulary plus the architect/builder/lexicographer working method — into the current project, and generate a self-contained HTML brief (multi-view idea map — ring/tree/icicle/treemap/graph — plus a kernel table) for handover. Use when starting work in a new repo and you want named, compressible, handoff-able context for agents instead of re-describing the same structures in prose every session.
---

# kernel — onboarding skill

The kernel is a shared, named vocabulary for the structures you keep re-describing to your
agents. Name a structure once; hand a builder a **primitive** instead of a paragraph. Measured
result: ~9× fewer tokens than explicit prose, and far higher reconstruction fidelity (0.98 vs
0.80 edge-F1 on a real architecture) — because a name can't go vague the way prose drifts.

## When to use
- You're starting in a new or unfamiliar repo and will dispatch agents.
- You catch yourself re-describing the same structure to agents across sessions.
- You want a portable, named vocabulary + a brief you can hand a teammate.

## Onboard the kernel into the current project
1. **Copy `KERNEL.md`** (this skill's method + grammar reference) into the repo root if it's absent.
2. **Seed `ideas.json`** with the project's idea harness — L0 root → L1 ideas → L2 workstreams → L3 primitives. If the ideas aren't defined yet, scaffold them from the repo's top-level structure and the open work; keep each L1 idea to a few L2 workstreams (pigeonhole), each with a handful of L3 primitives. Schema:
   ```json
   {"root":"<project>","ideas":[{"id":"x","label":"x","workstreams":[
     {"id":"y","label":"y","primitives":["a","b"]}]}]}
   ```
3. **Generate the brief:** `python3 <path-to-skill>/generate_brief.py <repo-dir>` → writes `kernel-brief.html` (self-contained, no runtime deps; 5-view idea map + kernel table from `ideas.json`). Stdlib Python only.
4. Point the operator at `kernel-brief.html` (open in a browser) and `KERNEL.md`.

## Work the kernel (apply in every session in this repo)
- **Scope to an idea, not a directory.** Inherit the active L1 idea's context on resume; if a step crosses the idea boundary, surface an *excursion* (allow / re-bind / split) rather than silently widening scope.
- **Name recurring structure (lexicographer).** When you describe the same shape a second or third time, coin a primitive for it and add it to the kernel/`ideas.json`.
- **Hand agents primitives, not paragraphs.** Brief a builder with `stack(C, Pi, L)`, not a 176-token description. Cheaper and exact.
- **Pigeonhole.** Load = primitives ÷ sibling workstreams. When a workstream strains, split it; you re-cleave locally, not globally.

## Grammar
```
nodes:  id:type "label"
edges:  a->b flow · a~>b async · a=>b provisions · a:>b config · a^b hosts · a&b references
macros: name a recurring subgraph once, invoke everywhere —
        stack(C, Pi, L) · async_broker(api,queue,worker,db) · control_plane(ctrl,proxy,store)
```

The thesis, the experiments, and the full writeup live alongside this skill in the repo
(`case-study.html` + `experiments/` with the pre-registration, 30 builder runs, and results).
