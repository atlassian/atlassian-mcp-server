"""Dependency diagrams: the wide and tall SVG versions, their legend and the full list. CSS: diagram.css.

The layout is computed here, so a data writer only lists the dependencies. Columns run second-hop upstream,
upstream, the anchor, downstream and second-hop downstream. Arrows point the way work flows, from a
dependency to the work waiting on it. Each column shows at most 7 nodes, most severe first: Done dependencies
collapse into one "N done" node, and the rest past the limit into "+N on track", or "+N more" when they're
mixed. A collapsed node links to the list. Titles are cut at 0.55em per character and refined in the browser
by DIAGRAM_JS, with the full title in each node's <title>. The wide diagram scales down to 85% of its width,
then a container query swaps in the tall version.
"""
from .links import e, link
from .status import TONES

STATES = {'blocked': ('Blocked', 'danger'), 'at-risk': ('At risk', 'warning'), 'stale': ('Stale handoff', 'neutral'),
          'on-track': ('On track', 'success'), 'done': ('Done', 'neutral'), 'unknown': ('Unknown', 'neutral')}
SEVERITY = ('blocked', 'at-risk', 'stale', 'unknown', 'on-track', 'done')
SOURCES = {'recorded': None, 'related': ('Related', 'discovery'), 'not-recorded': ('Not recorded', 'information')}
SIDES = {'upstream': 'Waiting on', 'downstream': 'Waiting on us'}
CHAR = 0.55
MAX_NODES = 7

# Refine the estimated truncation in the browser, and open the list when a collapsed node is followed.
DIAGRAM_JS = '''
(function(){
  function fit(svg){if(!svg.getBoundingClientRect().width)return;
    svg.querySelectorAll('[data-full]').forEach(function(t){var box=t.closest('g').querySelector('.dg-node__box').getBBox();
      var max=box.width-22,full=t.getAttribute('data-full');t.textContent=full;if(t.getComputedTextLength()<=max)return;
      for(var n=full.length-1;n>0;n--){t.textContent=full.slice(0,n).replace(/[\\s\\u00b7]+$/,'')+'\\u2026';if(t.getComputedTextLength()<=max)break;}});}
  [].forEach.call(document.querySelectorAll('.dg-figure'),function(fig){
    function all(){[].forEach.call(fig.querySelectorAll('svg.dg'),fit);}
    if(window.ResizeObserver)new ResizeObserver(all).observe(fig);else all();});
  [].forEach.call(document.querySelectorAll('[data-open-list]'),function(a){a.addEventListener('click',function(){
    var d=document.getElementById('all-deps');if(d)d.open=true;});});
})();
'''


def _cut(s, chars):
    return s if len(s) <= chars else s[:chars - 1].rstrip() + '…'


def _wrap(s, chars, lines=2):
    words = [_cut(w, chars) for w in s.split()]
    out, cur = [], ''
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= chars:
            cur = f'{cur} {w}' if cur else w
        else:
            out.append(cur)
            cur = w
            if len(out) == lines:
                break
    if len(out) < lines and cur:
        out.append(cur)
    if len(' '.join(out)) < len(' '.join(words)):
        out[-1] = _cut(out[-1] + ' …', chars) if len(out[-1]) + 2 > chars else out[-1] + '…'
    return out


def _chars(px, size):
    return int(px / (size * CHAR))


def state_words(d):
    """A dependency's state word, then its source word when it isn't Recorded: "Blocked · Not recorded"."""
    src = SOURCES.get(d.get('source', 'recorded'))
    return ' · '.join([STATES[d['state']][0]] + ([src[0]] if src else []))


def _source(d):
    return d['source'] if d.get('source') in SOURCES else 'recorded'


def _meta(d):
    return ' · '.join([state_words(d), d.get('team') or 'No team'] + ([d['date']] if d.get('date') else []))


def _collapse(nodes):
    """A column's nodes, most severe first, with Done ones in one node and the rest past the limit in another."""
    nodes = sorted(nodes, key=lambda d: SEVERITY.index(d['state']))
    done = [d for d in nodes if d['state'] == 'done']
    open_ = [d for d in nodes if d['state'] != 'done']
    slots = MAX_NODES - (1 if done else 0)
    shown, rest = (open_, []) if len(open_) <= slots else (open_[:slots - 1], open_[slots - 1:])
    if rest:
        word = 'on track' if all(d['state'] == 'on-track' for d in rest) else 'more'
        shown.append({'title': f'+{len(rest)} {word}', 'state': 'on-track' if word == 'on track' else 'unknown',
                      'collapsed': f'{len(rest)} more dependencies, see the list below', 'team': 'See the list', 'source': 'recorded'})
    if done:
        shown.append({'title': f'{len(done)} done', 'state': 'done', 'source': 'recorded',
                      'collapsed': f'{len(done)} done dependenc{"y" if len(done) == 1 else "ies"}, see the list below',
                      'team': ', '.join(dict.fromkeys(d.get('team') or 'No team' for d in done))})
    return shown


def _node(d, x, y, w, h, lines=2, tx=None, text_px=None):
    tx = x + 14 if tx is None else tx
    text_px = text_px or w - 22
    title = _wrap(d['title'], _chars(text_px, 13), lines)
    meta = _meta(d) if not d.get('collapsed') else f'{STATES[d["state"]][0]} · {d.get("team", "")}'
    if d.get('feedsLabel'):
        meta += f' · feeds {d["feedsLabel"]}'
    ty = y + (19 if len(title) == 2 else 22)
    full = f' data-full="{e(d["title"])}"' if lines == 1 else ''
    spans = ''.join(f'<tspan{full} x="{tx}" y="{ty + i * 16}">{e(t)}</tspan>' for i, t in enumerate(title))
    href = '#all-deps' if d.get('collapsed') else d.get('url') or '#all-deps'
    name = d.get('collapsed') or f'{d["title"]}, {state_words(d)}'
    opener = ' data-open-list' if href == '#all-deps' else ''
    target = '' if href.startswith('#') else ' target="_blank" rel="noopener"'
    src = _source(d)
    return (f'<a href="{e(href)}"{target} aria-label="{e(name)}"{opener}><g class="dg-node dg-st-{d["state"]} dg-src-{src}">'
            f'<title>{e(d["title"])}: {e(meta)}</title>'
            f'<rect class="dg-node__box" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
            f'<rect class="dg-node__bar" x="{x}" y="{y}" width="4" height="{h}" rx="2"/>'
            f'<text class="dg-node__title">{spans}</text>'
            f'<text class="dg-node__meta" data-full="{e(meta)}" x="{tx}" y="{ty + len(title) * 16 + 1}">{e(_cut(meta, _chars(text_px, 12)))}</text>'
            f'</g></a>')


def _placeholder(label, x, y, w, h):
    return (f'<g class="dg-placeholder"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
            f'<text class="dg-node__meta" x="{x + 14 if isinstance(x, (int, float)) else 15}" y="{y + h / 2 + 4}">{e(label)}</text></g>')


def _markers(uid):
    kinds = list(STATES) + ['flow']
    return '<defs>' + ''.join(
        f'<marker id="{uid}-ar-{k}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="{11 if k == "flow" else 8}" '
        f'markerHeight="{11 if k == "flow" else 8}" markerUnits="userSpaceOnUse" orient="auto">'
        f'<path class="dg-head dg-head-{k}" d="M0,0 L8,4 L0,8 z"/></marker>' for k in kinds) + '</defs>'


def _curve(sx, sy, ex, ey, d, uid, back=False):
    dx = (ex - sx) / 2
    cls = f'dg-edge dg-edge-{d["state"]} dg-edge-src-{_source(d)}' + (' dg-edge-back' if back else '')
    return (f'<path class="{cls}" d="M{sx:.1f},{sy:.1f} C{sx + dx:.1f},{sy:.1f} {ex - dx:.1f},{ey:.1f} {ex:.1f},{ey:.1f}" '
            f'marker-end="url(#{uid}-ar-{d["state"]})"/>')


def _columns(deps):
    """The five columns' nodes, collapsed, with second-hop nodes told which first-hop node they feed."""
    first = {s: [d for d in deps if d['side'] == s and d.get('hop', 1) == 1] for s in SIDES}
    cols = {s: _collapse(first[s]) for s in SIDES}
    ids = {d.get('id'): d for s in SIDES for d in first[s] if d.get('id')}
    hop2 = {}
    for s in SIDES:
        nodes = []
        for d in deps:
            if d['side'] == s and d.get('hop', 1) == 2:
                fed = ids.get(d.get('feeds'))
                nodes.append(dict(d, feedsLabel=(fed['title'].split(' ')[0] if fed else '')))
        hop2[s] = sorted(nodes, key=lambda d: SEVERITY.index(d['state']))[:MAX_NODES]
    return cols, hop2


def _anchor_label(kind):
    return {'goal': 'This goal', 'epic': 'This epic'}.get(kind, 'This project')


def describe(deps):
    """The diagram's description for screen readers, from the first-hop dependencies.

        describe(deps)  # "3 upstream: 1 blocked, 2 done; nothing recorded downstream"
    """
    parts = []
    for s, word in (('upstream', 'upstream'), ('downstream', 'downstream')):
        ds = [d for d in deps if d['side'] == s and d.get('hop', 1) == 1]
        if not ds:
            parts.append(f'nothing recorded {word}')
            continue
        counts = {}
        for d in ds:
            key = state_words(d).replace(' · ', ' and ').lower()
            counts[key] = counts.get(key, 0) + 1
        parts.append(f'{len(ds)} {word}: ' + ', '.join(f'{n} {k}' for k, n in counts.items()))
    return '; '.join(parts)


def _wide(anchor, cols, hop2, kind, title, desc):
    n_cols = 3 + bool(hop2['upstream']) + bool(hop2['downstream'])
    W, GAP, AW = {3: (196, 48, 224), 4: (188, 36, 200), 5: (150, 32, 180)}[n_cols]
    NH, RG, M, LAB = 64, 12, 12, 30
    order = (['up2'] if hop2['upstream'] else []) + ['up', 'an', 'dn'] + (['dn2'] if hop2['downstream'] else [])
    X, x = {}, M
    for k in order:
        X[k] = x
        x += (AW if k == 'an' else W) + GAP
    width = x - GAP + M
    colh = lambda k: k * NH + (k - 1) * RG
    up, dn = cols['upstream'], cols['downstream']
    inner = colh(max(len(up), len(dn), len(hop2['upstream']), len(hop2['downstream']), 1))
    height = LAB + inner + M
    cy = LAB + inner / 2
    AH = 96
    ay = cy - AH / 2
    uid = 'dgw'
    parts, edges, ypos = [], [], {}
    for side, key, sign in (('upstream', 'up', -1), ('downstream', 'dn', 1)):
        nodes = cols[side]
        if not nodes:
            parts.append(_placeholder(f'Nothing recorded {side}', X[key], cy - 24, W, 48))
            continue
        y0 = cy - colh(len(nodes)) / 2
        for i, d in enumerate(nodes):
            y = y0 + i * (NH + RG)
            if d.get('id'):
                ypos[d['id']] = y
            parts.append(_node(d, X[key], y, W, NH))
            py = ay + 14 + (AH - 28) * (i + 0.5) / len(nodes)
            if side == 'upstream':
                edges.append(_curve(X['up'] + W, y + NH / 2, X['an'] - 2, py, d, uid))
                if d.get('bothWays'):
                    edges.append(_curve(X['an'], py + 6, X['up'] + W + 2, y + NH / 2 + 6, d, uid, back=True))
            else:
                edges.append(_curve(X['an'] + AW, py, X['dn'] - 2, y + NH / 2, d, uid))
                if d.get('bothWays'):
                    edges.append(_curve(X['dn'], y + NH / 2 + 6, X['an'] + AW + 2, py + 6, d, uid, back=True))
    for side, key, first in (('upstream', 'up2', 'up'), ('downstream', 'dn2', 'dn')):
        last = -1e9
        for d in sorted(hop2[side], key=lambda d: ypos.get(d.get('feeds'), 1e9)):
            y = max(ypos.get(d.get('feeds'), LAB), last + NH + RG)
            last = y
            parts.append(_node(d, X[key], y, W, NH))
            fy = ypos.get(d.get('feeds'), y)
            if side == 'upstream':
                edges.append(_curve(X[key] + W, y + NH / 2, X[first] - 2, fy + NH / 2, d, uid))
            else:
                edges.append(_curve(X[first] + W, fy + NH / 2, X[key] - 2, y + NH / 2, d, uid))
            height = max(height, y + NH + M)
    labels = {'up2': 'Second hop', 'up': 'Waiting on', 'an': _anchor_label(kind), 'dn': 'Waiting on us', 'dn2': 'Second hop'}
    lab = ''.join(f'<text class="dg-col" x="{X[k]}" y="18">{e(labels[k])}</text>' for k in order)
    cx = X['an'] + AW / 2
    status = anchor.get('status') or {}
    st_text = status.get('text', '') if isinstance(status, dict) else status
    tone = status['tone'] if isinstance(status, dict) and status.get('tone') in TONES else 'neutral'
    t_lines = _wrap(anchor['title'], _chars(AW - 24, 14), 2)
    t_spans = ''.join(f'<tspan x="{cx}" y="{ay + (26 if len(t_lines) == 2 else 34) + i * 18}">{e(t)}</tspan>' for i, t in enumerate(t_lines))
    pill_w = max(60, len(st_text) * 7 + 16)
    anc = (f'<a href="{e(anchor.get("url") or "#")}" target="_blank" rel="noopener" aria-label="{e(anchor["title"])}{", " + e(st_text) if st_text else ""}, the work this map is about">'
           f'<g class="dg-anchor"><title>{e(anchor["title"])}</title>'
           f'<rect class="dg-anchor__box" x="{X["an"]}" y="{ay}" width="{AW}" height="{AH}" rx="8"/>'
           f'<text class="dg-anchor__title" text-anchor="middle">{t_spans}</text>'
           + (f'<rect class="dg-pill dg-pill-{tone}" x="{cx - pill_w / 2}" y="{ay + 62}" width="{pill_w}" height="18" rx="3"/>'
              f'<text class="dg-pill__text dg-pill__text-{tone}" x="{cx}" y="{ay + 75}" text-anchor="middle">{e(st_text)}</text>' if st_text else '')
           + '</g></a>')
    svg = (f'<svg class="dg dg-wide" viewBox="0 0 {width:.0f} {height:.0f}" role="group" aria-labelledby="{uid}-t {uid}-d">'
           f'<title id="{uid}-t">{e(title)}</title><desc id="{uid}-d">{e(desc)}</desc>{_markers(uid)}{lab}'
           + ''.join(edges) + ''.join(parts) + anc + '</svg>')
    return svg, width


def _tall(anchor, cols, hop2, kind, title, desc):
    NH, RG, LAB, ARW = 52, 8, 22, 30
    uid = 'dgt'
    parts, flows = [], []
    y = 4

    def level(name, nodes, y, empty):
        parts.append(f'<text class="dg-col" x="1" y="{y + 13}">{e(name)}</text>')
        y += LAB
        if not nodes:
            parts.append(_placeholder(empty, 1, y, '99%', 44))
            return y + 44
        for d in nodes:
            parts.append(_node(d, 1, y, '99%', NH, lines=1, tx=15, text_px=234))
            y += NH + RG
        return y - RG

    def flow(y):
        flows.append(f'<line class="dg-edge dg-edge-flow" x1="50%" y1="{y + 4}" x2="50%" y2="{y + ARW - 4}" marker-end="url(#{uid}-ar-flow)"/>')
        return y + ARW

    if hop2['upstream']:
        y = flow(level('Second hop', hop2['upstream'], y, ''))
    y = flow(level('Waiting on', cols['upstream'], y, 'Nothing recorded upstream'))
    parts.append(f'<text class="dg-col" x="1" y="{y + 13}">{e(_anchor_label(kind))}</text>')
    y += LAB
    status = anchor.get('status') or {}
    st_text = status.get('text', '') if isinstance(status, dict) else status
    tone = status['tone'] if isinstance(status, dict) and status.get('tone') in TONES else 'neutral'
    pill_w = max(60, len(st_text) * 7 + 16)
    parts.append(f'<a href="{e(anchor.get("url") or "#")}" target="_blank" rel="noopener" aria-label="{e(anchor["title"])}{", " + e(st_text) if st_text else ""}">'
                 f'<g class="dg-anchor"><title>{e(anchor["title"])}</title>'
                 f'<rect class="dg-anchor__box" x="1" y="{y}" width="99%" height="72" rx="8"/>'
                 f'<text class="dg-anchor__title" x="50%" y="{y + 30}" text-anchor="middle">{e(_cut(anchor["title"], _chars(234, 14)))}</text>'
                 + (f'<svg x="50%" y="{y + 42}" overflow="visible"><rect class="dg-pill dg-pill-{tone}" x="{-pill_w / 2}" y="0" width="{pill_w}" height="18" rx="3"/>'
                    f'<text class="dg-pill__text dg-pill__text-{tone}" x="0" y="13" text-anchor="middle">{e(st_text)}</text></svg>' if st_text else '')
                 + '</g></a>')
    y = flow(y + 72)
    y = level('Waiting on us', cols['downstream'], y, 'Nothing recorded downstream')
    if hop2['downstream']:
        y = level('Second hop', hop2['downstream'], flow(y), '')
    return (f'<svg class="dg dg-tall" width="100%" height="{y + 4:.0f}" role="group" aria-labelledby="{uid}-t {uid}-d">'
            f'<title id="{uid}-t">{e(title)}</title><desc id="{uid}-d">{e(desc)}</desc>{_markers(uid)}'
            + ''.join(flows) + ''.join(parts) + '</svg>')


def diagram(anchor, deps, kind='project'):
    """The dependency diagram in a figure: the wide version, and the tall one for narrow containers.

    Data: anchor is {"title", "url", "status": lozenge}. Each dependency is {"title", "url", "side": "upstream" or
    "downstream", "state", "source"?, "hop"?, "id"?, "feeds"?, "bothWays"?, "team"?, "date"?}. state is one of
    blocked, at-risk, stale, on-track, done and unknown. source is recorded (the default), related or
    not-recorded. A second-hop dependency has "hop": 2 and "feeds", the id of the first-hop one it feeds. kind
    names the anchor's column: project, goal or epic. Use DIAGRAM_JS as the page's js.

        diagram({"title": "Beacon offline editing", "url": "#", "status": {"text": "At risk", "tone": "warning"}},
                [{"title": "Sync conflict resolution service", "url": "#", "side": "upstream", "state": "blocked"}])
    """
    cols, hop2 = _columns(deps)
    title = f'Dependencies of {anchor["title"]}'
    desc = describe(deps)
    wide, width = _wide(anchor, cols, hop2, kind, title, desc)
    tall = _tall(anchor, cols, hop2, kind, title, desc)
    swap = round(width * 0.85)
    return (f'<figure class="dg-figure"><style>@container (max-width: {swap}px) {{ .dg-figure .dg-wide {{ display: none; }} '
            f'.dg-figure .dg-tall {{ display: block; }} }}</style>{wide}{tall}</figure>')


def legend():
    """The diagram's legend: each state's colour, each source's line style, and which way the arrows point.

        legend()
    """
    def line(state, extra=''):
        return (f'<svg class="dg-swatch" width="28" height="10" aria-hidden="true"><line class="dg-edge dg-edge-{state}{extra}" x1="0" y1="5" x2="22" y2="5"/>'
                f'<path class="dg-head dg-head-{state}" d="M22,1 L28,5 L22,9 z"/></svg>')

    def box(dashed):
        return (f'<svg class="dg-swatch" width="22" height="14" aria-hidden="true"><rect class="dg-swatch__box{" dg-swatch__box--dashed" if dashed else ""}" '
                f'x="1" y="1" width="20" height="12" rx="3"/></svg>')

    states = ''.join(f'<span>{line(s)}{w}</span>' for s, w in
                     (('blocked', 'Blocked'), ('at-risk', 'At risk'), ('stale', 'Stale handoff'), ('on-track', 'On track'), ('done', 'Done or unknown')))
    return ('<div class="dg-legend">'
            f'<div><b>State</b>{states}</div>'
            f'<div><b>Source</b><span>{box(False)}Recorded (solid)</span><span>{line("done", " dg-edge-src-related")}Related or not recorded (dashed line)</span>'
            f'<span>{box(True)}Not recorded (dashed box)</span></div>'
            '<div><span>Arrows point from a dependency to the work waiting on it. Each node also names its state.</span></div></div>')


def dependency_list(deps):
    """Every dependency as a table in a collapsed <details id="all-deps">, which collapsed nodes link to.

    Data: the diagram's dependencies, each with "from", where it came from ("Jira", "Slack").

        dependency_list(deps)
    """
    order = sorted(deps, key=lambda d: (d.get('hop', 1) == 1, d['side'] != 'upstream', SEVERITY.index(d['state'])))
    rows = ''.join(
        f'<tr><td>{link(d)}</td><td>{e("Second hop, " + SIDES[d["side"]].lower() if d.get("hop", 1) == 2 else SIDES[d["side"]])}</td>'
        f'<td>{e(STATES[d["state"]][0])}</td><td>{e((SOURCES.get(d.get("source", "recorded")) or ("Recorded",))[0])}'
        f'{" · Both ways" if d.get("bothWays") else ""}</td><td>{e(d.get("team") or "No team")}</td>'
        f'<td>{e(d.get("date") or "No date")}</td><td>{e(d.get("from", ""))}</td></tr>' for d in order)
    return ('<details class="dg-list" id="all-deps"><summary>All dependencies as a list</summary><div class="dg-list__wrap"><table>'
            '<thead><tr><th>Dependency</th><th>Side</th><th>State</th><th>Source</th><th>Team</th><th>Date</th><th>From</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></details>')
