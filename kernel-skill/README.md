# kernel — a Claude Code skill

Onboard the **kernel** (a shared named-primitive vocabulary + the architect/builder/lexicographer
method) into any project, and generate a self-contained HTML brief — with a multi-view idea map
and the project's kernel table — to hand off. Turns the architect/builder kernel research into a
drop-in capability.

## What it does
Run it in a repo and you get:
- **`KERNEL.md`** — the method + grammar reference, in-repo.
- **`ideas.json`** — the project's idea harness (L0 root → L1 ideas → L2 workstreams → L3 primitives).
- **`kernel-brief.html`** — a self-contained onboarding page (what / method / grammar / kernel table)
  with a **multi-view idea map** of that repo's harness: **ring · collapsible tree · icicle · treemap ·
  force graph**, plus a **kernel table** (idea → workstream → primitives). All inline SVG + vanilla JS —
  no runtime dependencies, opens straight from `file://`.

## Install
Copy or symlink this directory to where Claude Code looks for skills:
```bash
# user-wide
ln -s "$(pwd)/kernel-skill" ~/.claude/skills/kernel
# or per-project
ln -s "$(pwd)/kernel-skill" /path/to/repo/.claude/skills/kernel
```
Then in a session inside the target repo: invoke `/kernel` (or ask Claude to "onboard the kernel here").

## Use the generator directly (no skill system needed)
```bash
python3 generate_brief.py [target_dir]   # stdlib Python only
```
Reads `<target_dir>/ideas.json` (falls back to `ideas.seed.json`), writes `<target_dir>/kernel-brief.html`.
The brief is fully self-contained (inline SVG, no runtime deps) — open it straight from `file://`.

## Files
```
SKILL.md           the skill definition (what Claude follows on /kernel)
KERNEL.md          method + grammar, copied into target repos
ideas.seed.json    starter idea harness (the kernel research's own ideas)
generate_brief.py  stdlib generator → self-contained kernel-brief.html (5-view map + kernel table)
README.md          this file
```

Grounded in the architect/builder kernel research in this repo (`case-study.html` + `experiments/`
with the pre-registration, 30 builder runs, and results).
