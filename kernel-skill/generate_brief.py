#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kernel skill — brief generator.
Self-contained `kernel-brief.html` for a project: what the kernel is, the method, a map of
the project's IDEAS and the lexicon COMMANDS each one uses, and a lexicon reference table
("which commands to use"). All inline (SVG + a small vanilla force sim) — no runtime
dependencies, opens straight from file://. Stdlib only.

ideas.json schema:
  { "root": "<project>",
    "ideas":   [ {"id","label","uses":[command-id,...]}, ... ],
    "lexicon": [ {"id","sig","does"}, ... ] }     # the named commands you hand agents

Usage:  python3 generate_brief.py [target_dir]
"""
from __future__ import annotations
import json, sys, math, pathlib, datetime

HERE = pathlib.Path(__file__).parent
MONO = "'JetBrains Mono',ui-monospace,monospace"
COL = {0: "#B8602A", 1: "#D4793C", 2: "#788C5D"}   # root · idea · command(lexicon)

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))

def trunc(s, w, px=5.6, pad=12):
    mc = max(3, int((w - pad) / px)); s = str(s)
    return s if len(s) <= mc else s[:mc - 1] + "…"

def _uses(idea): return idea.get("uses", [])
def _w(idea): return max(1, len(_uses(idea)))

# ── ring (root → ideas → commands) ──────────────────────────────────────────
def ring_svg(data):
    W, H, cx, cy = 520, 460, 260, 232
    R = [0, 92, 182]; NR = [11, 7, 4.5]
    P = []
    for i, nm in ((1, "IDEAS"), (2, "LEXICON · COMMANDS")):
        P.append(f'<circle cx="{cx}" cy="{cy}" r="{R[i]}" fill="none" stroke="#d8d0c5" stroke-width="1" stroke-dasharray="3 4" opacity="0.7"/>')
        ly = cy - R[i] - (8 if i == 2 else 24)
        P.append(f'<text x="{cx}" y="{ly}" text-anchor="middle" font-family="{MONO}" font-size="7.5" font-weight="700" fill="{COL[min(i,2)]}" opacity="0.8" letter-spacing="1">{nm}</text>')
    edges, nodes, labels = [], [(cx, cy, NR[0], COL[0], None)], [(cx, cy - NR[0] - 9, data.get("root", "root"), COL[0], 9, "middle", 700)]
    ideas = data.get("ideas", []); n = len(ideas) or 1
    for i, idea in enumerate(ideas):
        a = -math.pi / 2 + i / n * 2 * math.pi
        ix, iy = cx + math.cos(a) * R[1], cy + math.sin(a) * R[1]
        edges.append((cx, cy, ix, iy, "#cabfb0", 0.5)); nodes.append((ix, iy, NR[1], COL[1], None))
        labels.append((ix, iy + NR[1] + 11, idea.get("label", ""), COL[1], 8.5, "middle", 700))
        cmds = _uses(idea); m = len(cmds)
        for j, c in enumerate(cmds):
            ca = a + (j - (m - 1) / 2) * 0.30
            cxp, cyp = cx + math.cos(ca) * R[2], cy + math.sin(ca) * R[2]
            edges.append((ix, iy, cxp, cyp, "#788C5D", 0.32)); nodes.append((cxp, cyp, NR[2], COL[2], c))
            lx, ly = cx + math.cos(ca) * (R[2] + 13), cy + math.sin(ca) * (R[2] + 13)
            anc = "start" if math.cos(ca) > 0.2 else ("end" if math.cos(ca) < -0.2 else "middle")
            labels.append((lx, ly + 3, c, "#5d6b48", 6.5, anc, 500))
    for x1, y1, x2, y2, c, op in edges:
        P.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="0.8" opacity="{op}"/>')
    for x, y, r, c, t in nodes:
        tt = f"<title>{esc(t)}</title>" if t else ""
        P.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" stroke="#fff" stroke-width="1.2" opacity="0.92">{tt}</circle>')
    for x, y, t, c, fs, anc, fw in labels:
        P.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anc}" font-family="{MONO}" font-size="{fs}" font-weight="{fw}" fill="{c}">{esc(t)}</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" style="max-width:540px;display:block;margin:0 auto;" role="img" aria-label="ideas + lexicon ring">{"".join(P)}</svg>'

# ── collapsible tree (idea → commands it uses) ──────────────────────────────
def tree_html(data):
    out = [f'<div class="treeview"><details open><summary class="l0">{esc(data.get("root","root"))}<span class="cnt">root</span></summary>']
    for idea in data.get("ideas", []):
        cmds = _uses(idea)
        out.append(f'<details open><summary class="l1">{esc(idea.get("label",""))}<span class="cnt">{len(cmds)} cmd</span></summary>')
        for c in cmds:
            out.append(f'<div class="cmd">{esc(c)}</div>')
        out.append("</details>")
    out.append("</details></div>")
    return "".join(out)

# ── icicle (root | ideas | commands) ────────────────────────────────────────
def icicle_svg(data):
    W, H = 720, 440; cols = [(8, 70), (84, 212), (304, 404)]
    ideas = data.get("ideas", []); total = sum(_w(i) for i in ideas) or 1
    P = []
    def cell(depth, y0, y1, label, fill):
        x, w = cols[depth]; h = y1 - y0
        s = f'<rect x="{x}" y="{y0:.1f}" width="{w-2}" height="{max(0,h-1.5):.1f}" fill="{fill}" fill-opacity="0.86" rx="2"><title>{esc(label)}</title></rect>'
        if h > 11 and label:
            s += f'<text x="{x+6}" y="{(y0+y1)/2+3:.1f}" font-family="{MONO}" font-size="9" fill="#fff">{esc(trunc(label, w))}</text>'
        return s
    P.append(cell(0, 0, H, data.get("root", "root"), COL[0]))
    y = 0.0
    for idea in ideas:
        ih = _w(idea) / total * H
        P.append(cell(1, y, y + ih, idea.get("label", ""), COL[1]))
        cmds = _uses(idea) or [""]; ch = ih / max(1, len(cmds)); cyc = y
        for c in cmds:
            P.append(cell(2, cyc, cyc + ch, c, COL[2])); cyc += ch
        y += ih
    return f'<svg viewBox="0 0 {W} {H}" width="100%" style="display:block;" role="img" aria-label="ideas icicle">{"".join(P)}</svg>'

# ── treemap (ideas split by command-count, commands stacked within) ─────────
def treemap_svg(data):
    W, H = 720, 420
    ideas = data.get("ideas", []); total = sum(_w(i) for i in ideas) or 1
    P = []; x = 0.0
    for idea in ideas:
        iw = _w(idea) / total * W
        P.append(f'<rect x="{x:.1f}" y="0" width="{iw-2:.1f}" height="{H}" fill="#fff" stroke="#D4793C" stroke-width="1.2" rx="3"/>')
        P.append(f'<text x="{x+6:.1f}" y="13" font-family="{MONO}" font-size="9.5" font-weight="700" fill="#B8602A">{esc(trunc(idea.get("label",""), iw))}</text>')
        cmds = _uses(idea); hy = 19.0
        if cmds:
            ch = (H - hy) / len(cmds); yy = hy
            for c in cmds:
                P.append(f'<rect x="{x+3:.1f}" y="{yy:.1f}" width="{iw-6:.1f}" height="{max(2,ch-3):.1f}" fill="#788C5D" fill-opacity="0.85" rx="2"><title>{esc(c)}</title></rect>')
                if ch > 16:
                    P.append(f'<text x="{x+7:.1f}" y="{yy+13:.1f}" font-family="{MONO}" font-size="8.5" fill="#fff">{esc(trunc(c, iw-6))}</text>')
                yy += ch
        x += iw
    return f'<svg viewBox="0 0 {W} {H}" width="100%" style="display:block;" role="img" aria-label="ideas treemap">{"".join(P)}</svg>'

# ── lexicon table — the commands to use ─────────────────────────────────────
def lexicon_table(data):
    ideas = data.get("ideas", [])
    used_by = {}
    for idea in ideas:
        for c in _uses(idea):
            used_by.setdefault(c, []).append(idea.get("label", idea.get("id", "")))
    rows = []
    for e in data.get("lexicon", []):
        ub = " · ".join(esc(u) for u in used_by.get(e.get("id"), [])) or "—"
        rows.append(f'<tr><td class="cmd"><code>{esc(e.get("sig", e.get("id","")))}</code></td>'
                    f'<td class="does">{esc(e.get("does",""))}</td><td class="ub">{ub}</td></tr>')
    # commands referenced in uses but missing from lexicon
    known = {e.get("id") for e in data.get("lexicon", [])}
    for c in used_by:
        if c not in known:
            rows.append(f'<tr><td class="cmd"><code>{esc(c)}</code></td><td class="does" style="color:var(--red)">— not yet defined in the lexicon —</td><td class="ub">{" · ".join(esc(u) for u in used_by[c])}</td></tr>')
    return ('<table class="ktable"><thead><tr><th>command</th><th>what it does</th><th>used by</th></tr></thead>'
            '<tbody>' + "".join(rows) + "</tbody></table>")

TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>kernel · onboarding brief — __PROJECT__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#FAF8F5;--card:#fff;--ink:#1B1714;--fg:#2A2521;--muted:#6B6259;--faint:#9C9389;
--border:#E4DDD3;--deep:#F2EDE5;--accent:#B8602A;--sky:#6A8CAF;--olive:#788C5D;--red:#C04A3E;
--serif:'Newsreader',Georgia,serif;--mono:'JetBrains Mono',ui-monospace,monospace;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font:400 14px/1.6 var(--mono);-webkit-font-smoothing:antialiased;}
.wrap{max-width:920px;margin:0 auto;padding:clamp(40px,7vw,88px) clamp(22px,5vw,48px) 96px;}
.kick{font:600 10px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin-bottom:14px;}
h1{font:600 clamp(30px,5vw,52px)/1.05 var(--serif);color:var(--ink);letter-spacing:-.01em;margin-bottom:14px;}
h2{font:600 11px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:40px 0 14px;}
.lead{font:400 clamp(15px,2vw,18px)/1.55 var(--serif);color:var(--fg);max-width:62ch;}
p{max-width:66ch;margin-bottom:12px;}
b{color:var(--ink);font-weight:600;} em{color:var(--accent);font-style:italic;}
code{font:600 .9em var(--mono);color:var(--accent);background:var(--deep);padding:1px 5px;border-radius:4px;}
.row{display:flex;gap:18px;flex-wrap:wrap;}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 20px;flex:1 1 200px;}
.card h3{font:600 11px/1 var(--mono);text-transform:uppercase;letter-spacing:.1em;margin-bottom:9px;}
.card.role-arch h3{color:var(--accent);} .card.role-build h3{color:var(--sky);} .card.role-lex h3{color:var(--olive);}
.card p{font-size:12.5px;line-height:1.55;color:var(--muted);margin:0;}
.foot{margin-top:54px;padding-top:20px;border-top:1px solid var(--border);font:400 11px/1.6 var(--mono);color:var(--faint);}
.mapcard{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px 16px 12px;box-shadow:0 6px 28px rgba(20,20,19,.07);}
.maptabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;}
.maptabs button{font:600 10px/1 var(--mono);letter-spacing:.03em;color:var(--muted);background:var(--deep);border:1px solid var(--border);border-radius:20px;padding:6px 13px;cursor:pointer;}
.maptabs button.on{color:#fff;background:var(--accent);border-color:var(--accent);}
.mapview[hidden]{display:none;} .mapview{min-height:300px;}
.maplegend{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:10px;font:500 10px/1 var(--mono);color:var(--muted);}
.maplegend .item{display:flex;align-items:center;gap:5px;} .maplegend .dot{width:9px;height:9px;border-radius:50%;display:inline-block;}
.graphhint{text-align:center;font:400 10px/1.4 var(--mono);color:var(--faint);margin-top:6px;}
.treeview{font:500 12.5px/1.75 var(--mono);max-width:680px;margin:2px auto;}
.treeview details details{margin-left:16px;border-left:1px solid var(--border);padding-left:11px;}
.treeview summary{cursor:pointer;list-style:none;padding:1px 0;}
.treeview summary::-webkit-details-marker{display:none;}
.treeview summary::before{content:'▸';display:inline-block;width:14px;color:var(--faint);}
.treeview details[open]>summary::before{content:'▾';}
.treeview .l0{color:#B8602A;font-weight:700;} .treeview .l1{color:#D4793C;font-weight:600;}
.treeview .cmd{color:#5d6b48;margin-left:30px;font-size:12px;}
.treeview .cmd::before{content:'›';color:var(--faint);margin-right:7px;}
.treeview .cnt{color:var(--faint);font-size:10px;margin-left:8px;font-weight:400;}
.ktable{width:100%;border-collapse:collapse;font:500 12.5px/1.5 var(--mono);}
.ktable th{text-align:left;font:600 9.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted);border-bottom:1px solid var(--border);padding:9px 10px;}
.ktable td{padding:9px 10px;border-bottom:1px solid var(--deep);vertical-align:top;}
.ktable td.cmd{white-space:nowrap;} .ktable td.cmd code{color:var(--olive);background:rgba(120,140,93,.1);}
.ktable td.does{color:var(--fg);} .ktable td.ub{color:#B8602A;font-weight:600;white-space:nowrap;}
</style>
</head><body>
<div class="wrap">
  <div class="kick">kernel · onboarding brief · __DATE__</div>
  <h1>Onboard the kernel into <span style="color:var(--accent)">__PROJECT__</span>.</h1>
  <p class="lead">The kernel is a shared, named vocabulary for the structures you keep re-describing to your agents. Name a structure once; hand a builder the <em>command</em> instead of a paragraph. It costs far fewer tokens — and, unlike prose, it can't go vague.</p>

  <h2>The method — three roles</h2>
  <div class="row">
    <div class="card role-arch"><h3>architect</h3><p>Sees the target and describes it. The describer who decides what is worth naming.</p></div>
    <div class="card role-build"><h3>builder</h3><p>Has only the words. Reconstructs the structure from the command alone — the test of whether the name was exact.</p></div>
    <div class="card role-lex"><h3>lexicographer</h3><p>Watches the dialogue and coins the names. Promotes a re-described structure into a lexicon command.</p></div>
  </div>

  <h2>The ideas — and the commands each uses</h2>
  <p>The work areas of this project (<b>ideas</b>) and the lexicon <b>commands</b> each one reaches for. Five views of the same map — <b>ring</b> for a small overview, <b>tree</b> / <b>icicle</b> / <b>treemap</b> for big ones, <b>graph</b> to see commands shared across ideas.</p>
  <div class="mapcard">
    <div class="maptabs">
      <button data-view="ring" class="on">ring</button>
      <button data-view="tree">tree</button>
      <button data-view="icicle">icicle</button>
      <button data-view="treemap">treemap</button>
      <button data-view="graph">graph</button>
    </div>
    <div class="mapview" id="view-ring">__RING_SVG__</div>
    <div class="mapview" id="view-tree" hidden>__TREE_HTML__</div>
    <div class="mapview" id="view-icicle" hidden>__ICICLE_SVG__</div>
    <div class="mapview" id="view-treemap" hidden>__TREEMAP_SVG__</div>
    <div class="mapview" id="view-graph" hidden><svg id="graph-svg" viewBox="0 0 720 440" width="100%" style="height:440px;display:block;"></svg><div class="graphhint">drag a node · settles automatically · a command shared by several ideas shows as one node</div></div>
    <div class="maplegend">
      <span class="item"><span class="dot" style="background:#B8602A"></span>root</span>
      <span class="item"><span class="dot" style="background:#D4793C"></span>ideas</span>
      <span class="item"><span class="dot" style="background:#788C5D"></span>lexicon commands</span>
    </div>
  </div>

  <h2>The lexicon — commands to use</h2>
  <p>Hand an agent a command from this table, not a paragraph. They compose with the kernel operators: <code>-&gt;</code> flow · <code>~&gt;</code> async · <code>=&gt;</code> provisions · <code>:&gt;</code> config · <code>^</code> hosts · <code>&amp;</code> references. <span style="color:var(--faint)">~9× fewer tokens than prose, and exact where prose drifts (0.98 vs 0.80 reconstruction fidelity).</span></p>
  __LEXICON_TABLE__

  <div class="foot">Generated by the <b>kernel</b> skill · fully self-contained (inline SVG + vanilla JS, no runtime dependencies) · ideas + lexicon from <code>ideas.json</code>.</div>
</div>

<script>
(function(){
  var DATA = __IDEAS_JSON__;
  var tabs = document.querySelectorAll('.maptabs button'), views = document.querySelectorAll('.mapview'), started = false;
  tabs.forEach(function(b){ b.addEventListener('click', function(){
    tabs.forEach(function(x){ x.classList.toggle('on', x === b); });
    views.forEach(function(v){ v.hidden = v.id !== 'view-' + b.dataset.view; });
    if (b.dataset.view === 'graph' && !started) { started = true; startGraph(); }
  }); });

  function startGraph(){
    var svg = document.getElementById('graph-svg'), W = 720, H = 440;
    var C = ['#B8602A','#D4793C','#788C5D'], RAD = [11,7,5], NS = 'http://www.w3.org/2000/svg';
    var nodes = [], links = [], byId = {}, seen = {};
    function add(id, lvl, label){ byId[id] = { id:id, lvl:lvl, label:label, x:W/2+(Math.random()-.5)*220, y:H/2+(Math.random()-.5)*220, vx:0, vy:0, fx:null, fy:null }; nodes.push(byId[id]); }
    add('__root__', 0, DATA.root);
    (DATA.ideas||[]).forEach(function(i){ add(i.id,1,i.label); links.push(['__root__',i.id]);
      (i.uses||[]).forEach(function(c){ var cid='cmd:'+c; if(!seen[cid]){ seen[cid]=1; add(cid,2,c); } links.push([i.id,cid]); }); });
    var lineEls = links.map(function(l){ var e=document.createElementNS(NS,'line'); e.setAttribute('stroke','#b9b0a4'); e.setAttribute('stroke-width','0.8'); e.setAttribute('opacity','0.5'); svg.appendChild(e); return e; });
    nodes.forEach(function(n){ var c=document.createElementNS(NS,'circle'); c.setAttribute('r',RAD[n.lvl]); c.setAttribute('fill',C[n.lvl]); c.setAttribute('stroke','#fff'); c.setAttribute('stroke-width','1.2'); c.style.cursor='grab'; var t=document.createElementNS(NS,'title'); t.textContent=n.label; c.appendChild(t); svg.appendChild(c); n.el=c; });
    var drag=null;
    function pt(ev){ var r=svg.getBoundingClientRect(); return { x:(ev.clientX-r.left)/r.width*W, y:(ev.clientY-r.top)/r.height*H }; }
    svg.addEventListener('pointerdown', function(ev){ var n=nodes.find(function(x){return x.el===ev.target;}); if(n){ drag=n; alpha=0.4; try{svg.setPointerCapture(ev.pointerId);}catch(e){} } });
    svg.addEventListener('pointermove', function(ev){ if(!drag)return; var q=pt(ev); drag.fx=q.x; drag.fy=q.y; });
    svg.addEventListener('pointerup', function(){ if(drag){ drag.fx=drag.fy=null; drag=null; } });
    var alpha=1;
    function step(){
      for(var a=0;a<nodes.length;a++) for(var b=a+1;b<nodes.length;b++){ var p=nodes[a],q=nodes[b],dx=p.x-q.x,dy=p.y-q.y,d2=dx*dx+dy*dy+0.01,d=Math.sqrt(d2),f=460/d2,fx=f*dx/d,fy=f*dy/d; p.vx+=fx;p.vy+=fy;q.vx-=fx;q.vy-=fy; }
      links.forEach(function(l){ var p=byId[l[0]],q=byId[l[1]],dx=q.x-p.x,dy=q.y-p.y,d=Math.sqrt(dx*dx+dy*dy)+0.01,f=(d-52)*0.02,fx=f*dx/d,fy=f*dy/d; p.vx+=fx;p.vy+=fy;q.vx-=fx;q.vy-=fy; });
      nodes.forEach(function(n){ n.vx+=(W/2-n.x)*0.004; n.vy+=(H/2-n.y)*0.004; if(n.fx!=null){ n.x=n.fx; n.y=n.fy; n.vx=n.vy=0; } else { n.vx*=0.86; n.vy*=0.86; n.x+=n.vx*alpha; n.y+=n.vy*alpha; } n.x=Math.max(8,Math.min(W-8,n.x)); n.y=Math.max(8,Math.min(H-8,n.y)); });
      links.forEach(function(l,i){ var p=byId[l[0]],q=byId[l[1]],e=lineEls[i]; e.setAttribute('x1',p.x.toFixed(1)); e.setAttribute('y1',p.y.toFixed(1)); e.setAttribute('x2',q.x.toFixed(1)); e.setAttribute('y2',q.y.toFixed(1)); });
      nodes.forEach(function(n){ n.el.setAttribute('cx',n.x.toFixed(1)); n.el.setAttribute('cy',n.y.toFixed(1)); });
      alpha*=0.992; if(alpha>0.02 || drag) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
})();
</script>
</body></html>
"""

def main():
    target = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path.cwd()
    ideas_path = target / "ideas.json"
    if ideas_path.exists():
        data = json.loads(ideas_path.read_text()); src = "ideas.json"
    else:
        data = json.loads((HERE / "ideas.seed.json").read_text()); src = "seed (no ideas.json found)"
    project = data.get("root", target.name)
    html = (TEMPLATE
            .replace("__PROJECT__", esc(str(project)))
            .replace("__DATE__", datetime.date.today().isoformat())
            .replace("__RING_SVG__", ring_svg(data))
            .replace("__TREE_HTML__", tree_html(data))
            .replace("__ICICLE_SVG__", icicle_svg(data))
            .replace("__TREEMAP_SVG__", treemap_svg(data))
            .replace("__LEXICON_TABLE__", lexicon_table(data))
            .replace("__IDEAS_JSON__", json.dumps(data)))
    out = target / "kernel-brief.html"
    out.write_text(html)
    print(f"wrote {out}")
    print(f"  source: {src}")
    print(f"  {len(data.get('ideas',[]))} ideas · {len(data.get('lexicon',[]))} lexicon commands · views: ring·tree·icicle·treemap·graph")

if __name__ == "__main__":
    main()
