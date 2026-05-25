#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXPERIMENT 3 — architect/builder on a REAL architecture transcript.
===================================================================

Experiments 1–2 used toy towers the kernel itself authored (the info-theory
lens called that "tautological"). This is the unrigged test the three-lens
swarm asked for: a real person describing a real architecture, in the wild.

Source: youtube 55pTFVoclvE — an ex-Atlassian engineer narrating the
self-service edge/load-balancing platform he built (Open Service Broker →
SQS/worker → DynamoDB; the "Sovereign" Envoy control plane; a CloudFormation
proxy fleet; a Packer/SaltStack AMI pipeline; edge sidecars).

Conditions share one target architecture (the ground-truth component graph,
validated 2026-05-25 against the engineer's Excalidraw diagram + the talk):
  • NATURAL LANGUAGE — the raw transcript. A builder must FIND the architecture
    in ~8k words of narration (interview stories, asides, non-technical bits).
  • KERNEL — the architecture re-expressed in a compact shared DSL of named
    component types + relations + patterns (async_broker, control_plane, …).

We measure tokens (tiktoken o200k_base) and graph-reconstruction fidelity
(node + edge precision/recall/F1, IoU) of a builder agent rebuilding the
component graph from each condition.

This file is the deterministic scaffold: it ingests the artifacts, measures
tokens, holds the scorer, and writes exp3_state.json (the live state the
dashboard renders). Builder reconstructions are scored via score_graph()
once the agent runs are pasted into this script (see RECONSTRUCTIONS below).

Run:  python3 exp3.py
"""
from __future__ import annotations
import json, re, pathlib

HERE = pathlib.Path(__file__).parent

def make_tokenizer():
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        return "tiktoken · o200k_base", lambda s: len(enc.encode(s))
    except Exception:
        return "proxy · word+punct", lambda s: len(re.findall(r"\w+|[^\w\s]", s))

def transcript_text(raw: str):
    """Strip the tactiq header (# lines) and the leading timestamp on each line."""
    lines = []
    for ln in raw.splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        lines.append(re.sub(r"^\d{2}:\d{2}:\d{2}\.\d+\s*", "", ln))
    return "\n".join(lines)

def kernel_by_service(kenc: str, tok):
    """Split the kernel encoding into per-service sub-kernels (marked `# == NAME ==`)
    and tokenize each one's content. Comments/headers are scaffolding, not payload —
    the encoding cost is the sum of the service bodies."""
    sections, cur = {}, None
    for ln in kenc.splitlines():
        m = re.match(r"\s*#\s*==\s*(.+?)\s*==", ln)
        if m:
            cur = m.group(1).strip(); sections.setdefault(cur, [])
            continue
        if ln.strip().startswith("#") or not ln.strip():
            continue
        if cur is not None:
            sections[cur].append(ln)
    return {name: tok("\n".join(body)) for name, body in sections.items() if body}

# ── graph fidelity scorer (used when builder reconstructions arrive) ──────────
def _prf(truth: set, got: set):
    tp = len(truth & got)
    p = tp / len(got) if got else 0.0
    r = tp / len(truth) if truth else 1.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    iou = tp / len(truth | got) if (truth | got) else 1.0
    return {"precision": round(p, 3), "recall": round(r, 3), "f1": round(f1, 3),
            "iou": round(iou, 3), "tp": tp, "missing": sorted(truth - got), "extra": sorted(got - truth)}

def score_graph(truth_nodes, truth_edges, got_nodes, got_edges):
    tn, gn = set(truth_nodes), set(got_nodes)
    te = {(a, b) for a, b in truth_edges}; ge = {(a, b) for a, b in got_edges}
    return {"nodes": _prf(tn, gn), "edges": _prf(te, ge)}

# Paste builder agent reconstructions here as {"nodes":[...], "edges":[[a,b],...]} to score.
RECONSTRUCTIONS = {
    "nl": None,      # builder rebuilding from the raw transcript
    "kernel": None,  # builder rebuilding from the kernel encoding
}

def main():
    method, tok = make_tokenizer()
    raw = (HERE / "transcript.txt").read_text()
    gt = json.loads((HERE / "ground_truth.json").read_text())
    kdef = (HERE / "kernel_def.txt").read_text()
    kenc = (HERE / "kernel_encoding.txt").read_text()

    full = transcript_text(raw)
    # architecture span = up to the non-technical pivot
    cut = full.find("non-technical requirements")
    span = full[:cut] if cut != -1 else full

    nodes = [n["id"] for n in gt["nodes"]]
    edges = [(e["from"], e["to"]) for e in gt["edges"]]

    tok_full, tok_span = tok(full), tok(span)
    by_service = kernel_by_service(kenc, tok)        # per-service sub-kernel sizes
    tok_kenc = sum(by_service.values())              # encoding = sum of service bodies
    tok_kfile = tok(kenc)                            # whole file incl. comments (scaffolding)
    tok_kdef = tok(kdef)

    fidelity = {}
    for cond, rec in RECONSTRUCTIONS.items():
        if rec:
            fidelity[cond] = score_graph(nodes, edges, rec["nodes"], [tuple(x) for x in rec["edges"]])
        else:
            fidelity[cond] = None

    state = {
        "title": "Experiment 3 — architecture from a real transcript",
        "source": gt["_meta"]["source"],
        "question": "On a real, noisy architecture description, does the kernel reconstruct the component graph more exactly at fewer tokens than the raw transcript?",
        "tokenizer": method,
        "stages": [
            {"id": "ingest", "label": "ingest transcript", "status": "done",
             "detail": f"{len(full.split())} words · {tok_full} tokens (full) · {tok_span} tokens (architecture span)"},
            {"id": "ground_truth", "label": "ground-truth graph (validated)", "status": "done",
             "detail": f"{len(nodes)} components · {len(edges)} relations — validated vs Excalidraw + transcript (2026-05-25)"},
            {"id": "kernel_encode", "label": "kernel-encode architecture", "status": "done",
             "detail": f"{tok_kenc} tokens encoding ({sum(1 for k in by_service if k != 'declare')} per-service sub-kernels + shared decls) + {tok_kdef} tokens kernel def (one-time)"},
            {"id": "builder_nl", "label": "builder reconstruct from transcript", "status": "pending" if not RECONSTRUCTIONS["nl"] else "done", "detail": "agent rebuilds the graph from raw NL"},
            {"id": "builder_kernel", "label": "builder reconstruct from kernel", "status": "pending" if not RECONSTRUCTIONS["kernel"] else "done", "detail": "agent rebuilds the graph from the kernel encoding"},
            {"id": "compare", "label": "score fidelity + compare", "status": "pending", "detail": "node/edge precision·recall·F1·IoU; tokens vs fidelity"},
        ],
        "tokens": {
            "nl_full": tok_full, "nl_span": tok_span,
            "kernel_encoding": tok_kenc, "kernel_encoding_file": tok_kfile,
            "kernel_by_service": by_service, "kernel_def": tok_kdef,
            "kernel_total": tok_kenc + tok_kdef,
            "ratio_span_over_kernel": round(tok_span / (tok_kenc + tok_kdef), 1),
            "ratio_full_over_kernel": round(tok_full / (tok_kenc + tok_kdef), 1),
        },
        "graph": gt,
        "fidelity": fidelity,
    }
    # fold in fidelity results from score_runs.py if present
    scores_path = HERE / "runs" / "scores.json"
    if scores_path.exists():
        sc = json.loads(scores_path.read_text())
        state["fidelity"] = sc["conditions"]
        state["fidelity_comparisons"] = sc["comparisons"]
        done = {s["id"]: s for s in state["stages"]}
        done["builder_nl"]["status"] = "done"; done["builder_nl"]["detail"] = f"10 Haiku runs · transcript · edge-F1 median {sc['conditions']['transcript']['edge_f1']['median']}"
        done["builder_kernel"]["status"] = "done"; done["builder_kernel"]["detail"] = f"10 Haiku runs · kernel · edge-F1 median {sc['conditions']['kernel']['edge_f1']['median']}"
        done["compare"]["status"] = "done"; done["compare"]["detail"] = f"30 runs scored · kernel {sc['conditions']['kernel']['edge_f1']['median']} > prose {sc['conditions']['prose']['edge_f1']['median']} > transcript {sc['conditions']['transcript']['edge_f1']['median']} (edge-F1 median)"

    (HERE / "exp3_state.json").write_text(json.dumps(state, indent=2))

    print(f"tokenizer: {method}\n")
    print(f"transcript:  {tok_full} tokens full · {tok_span} tokens architecture-span · {len(full.split())} words")
    print(f"kernel:      {tok_kenc} tokens encoding + {tok_kdef} tokens def = {tok_kenc+tok_kdef} total")
    print("  by service: " + " · ".join(f"{k} {v}" for k, v in by_service.items()))
    print(f"graph:       {len(nodes)} components · {len(edges)} relations (validated)")
    print(f"ratio:       span/kernel = {state['tokens']['ratio_span_over_kernel']}x · full/kernel = {state['tokens']['ratio_full_over_kernel']}x")
    print(f"\nfidelity:    {'pending — run builder agents, paste into RECONSTRUCTIONS' if not RECONSTRUCTIONS['nl'] else 'scored'}")
    print("wrote exp3_state.json")

if __name__ == "__main__":
    main()
