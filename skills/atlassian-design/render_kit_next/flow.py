"""Flows: nodes joined by labelled edges, with a frame around a run of them, laid out here in columns as SVG so a
caller only lists the nodes and edges. CSS: flow.css."""
import math
import re

from .page import e

PAD, SPACE = 12, 8                 # inside a node or the frame, and between a node's parts
INNER = 152                        # the widest a node's text gets before it wraps
TITLE, SUB = 20, 16                # line heights of the 14px titles and the 12px subs and labels
GAP, ROW = 48, 32                  # the least space between columns, and between nodes in a column
SPREAD = 8                         # between the ends of edges that share a side of a node
DIP = 24                           # how far under the nodes it passes a backward edge runs
MIN_SCALE = 0.8                    # the smallest the figure scales to before it scrolls sideways
SANS, BOLD, CODE = 0.56, 0.6, 0.6  # estimated character widths, in ems


def _cut(s, chars):
    return s if len(s) <= chars else s[:chars - 1].rstrip() + '…'


def _lines(s, px, size, em=SANS):
    """s in one line that fits px, or two of even length broken at a space, or else after . - or /, or else cut with
    an ellipsis."""
    chars = max(int(px / (size * em)), 1)
    s = s.strip()
    if len(s) <= chars:
        return [s]
    for breaks in (r'\S*\s*', r'[^\s./-]*(?:[./-]+|\s+|$)'):
        tokens = [t for t in re.findall(breaks, s) if t]
        splits = [(''.join(tokens[:i]).rstrip(), ''.join(tokens[i:])) for i in range(1, len(tokens))]
        fits = [p for p in splits if len(p[0]) <= chars and len(p[1]) <= chars]
        if fits:
            return list(min(fits, key=lambda p: max(map(len, p))))
    first = [p for p in splits if len(p[0]) <= chars]
    return [first[-1][0], _cut(first[-1][1], chars)] if first else [_cut(s, chars)]


def _width(lines, size, em):
    return max(len(t) for t in lines) * size * em if lines else 0


def _measure(n, grouped):
    """The node with its lines, width and height: its title, then its sub. It's as wide as its longest line, once
    the text has wrapped at INNER."""
    em = CODE if grouped else SANS
    title = _lines(n['title'], INNER, 14)
    sub = _lines(n['sub'], INNER, 12, em) if n.get('sub') else []
    inner = math.ceil(max(_width(title, 14, SANS), _width(sub, 12, em)))
    h = 2 * PAD + len(title) * TITLE + len(sub) * SUB
    return dict(n, grouped=grouped, w=inner + 2 * PAD, h=h, title_lines=title, sub_lines=sub)


def _node(n):
    cls = 'flow__node' + (' flow__node--grouped' if n['grouped'] else '') + (' flow__node--outside' if n.get('kind') == 'outside' else '')
    out = ''.join(f'<text class="flow__title" x="{PAD}" y="{PAD + i * TITLE + 15}">{e(t)}</text>' for i, t in enumerate(n['title_lines']))
    top = PAD + len(n['title_lines']) * TITLE
    out += ''.join(f'<text class="flow__sub" x="{PAD}" y="{top + i * SUB + 12}">{e(t)}</text>' for i, t in enumerate(n['sub_lines']))
    full = ' · '.join(t for t in (n['title'], n.get('sub')) if t)
    return (f'<svg x="{n["x"]:.1f}" y="{n["y"]:.1f}" width="{n["w"]}" height="{n["h"]}" overflow="visible"><g class="{cls}">'
            f'<title>{e(full)}</title><rect width="100%" height="100%" rx="6"/>{out}</g></svg>')


def _columns(ids, group, edges):
    """Each node's column. The nodes before the group are in the first, and the nodes after it in the one after the
    group's last. In the group, the nodes an edge from before it reaches start the order, and each node is one
    column after the furthest node with an edge to it. A node nothing in that order reaches, such as one that only
    feeds another, is one column before the first node it feeds, which moves the rest along. Edges that loop back
    are left out of the order and drawn backwards."""
    order = list(ids)
    first, last = min(ids[i] for i in group['ids']), max(ids[i] for i in group['ids'])
    inside = order[first:last + 1]
    out = {}
    for edge in edges:
        if edge['from'] in inside and edge['to'] in inside:
            out.setdefault(edge['from'], []).append(edge['to'])
    entries = list(dict.fromkeys(edge['to'] for edge in edges if ids[edge['from']] < first and edge['to'] in inside)) or inside[:1]

    back, seen, path = set(), set(), set()

    def visit(a):
        seen.add(a)
        path.add(a)
        for b in out.get(a, []):
            if b in path:
                back.add((a, b))
            elif b not in seen:
                visit(b)
        path.discard(a)

    for a in entries + inside:
        if a not in seen:
            visit(a)
    forward = [(a, b) for a, bs in out.items() for b in bs if (a, b) not in back]

    rank = {a: 0 for a in entries}
    while True:
        for _ in inside:
            for a, b in forward:
                if a in rank and rank.get(b, -1) < rank[a] + 1:
                    rank[b] = rank[a] + 1
        feeders = {a: [rank[b] for x, b in forward if x == a and b in rank] for a in inside if a not in rank}
        feeders = {a: rs for a, rs in feeders.items() if rs}
        if not feeders:
            break
        rank.update({a: min(rs) - 1 for a, rs in feeders.items()})
    low = min(rank.values(), default=0)
    cols = {a: (1 if first else 0) + rank.get(a, low) - low for a in inside}
    end = max(cols.values()) + 1
    cols.update({a: 0 for a in order[:first]})
    cols.update({a: end for a in order[last + 1:]})
    return cols, back


def _pack(items, want):
    """The items' tops, in their order, as near the centres they want as ROW apart allows."""
    tops, bottom = [], None
    for it, c in zip(items, want):
        top = c - it['h'] / 2 if bottom is None else max(c - it['h'] / 2, bottom + ROW)
        tops.append(top)
        bottom = top + it['h']
    shift = sum(c - (t + it['h'] / 2) for it, c, t in zip(items, want, tops)) / len(items)
    return [t + shift for t in tops]


def flow_figure(nodes, group, edges, label, title, desc):
    """A flow in a figure: its nodes in columns, left to right, joined by its edges, laid out here so that edges run
    forward, cross as little as they can, and are as straight as the nodes allow.

    The nodes before the group are in the first column, then the frame around the group's nodes, with its title and
    sub above them, then the nodes after the group in the last column, under the label. In the frame, each node is a
    column after the furthest node that points to it, and a node that only feeds another sits a column before it.
    Nodes in a column
    are 32px apart, ordered by where their edges come from, and each sits level with the nodes it joins where it
    can. An edge is a curve between columns, its ends spread 8px apart where several share a side of a node, and
    its label sits above it, by the node it points to, or by the node it leaves when several point to that one. An
    edge that skips a column passes through it, and one that loops back runs under the nodes between. The figure
    draws at 1:1 when its card is wide enough, scales down to 80% with it, then scrolls sideways inside it.

    A node is as wide as its longest line, up to 176px, where its text wraps into two lines of even length and is
    cut with an ellipsis, with the full text in the node's tooltip. Its title is 14px medium and its sub 12px
    subtlest (in the code font for a node in the group). A node in the group takes the raised surface, and an
    outside node has a dashed
    border. The SVG is an image named by title and described by desc, so desc should say in words what each node
    and edge says.

    Data: each node is {"id", "title", "sub"?, "kind"?: "outside"}; group is {"title", "sub"?, "ids"},
    naming a run of the nodes; each edge is {"from": id, "to": id, "label"?}, and label is the text over the nodes
    after the group.

        flow_figure(
            [{"id": "trigger", "title": "Someone using a Beacon page"},
             {"id": "idleTimer.ts", "title": "Idle timer", "sub": "idleTimer.ts"},
             {"id": "config.ts", "title": "Timeout length", "sub": "config.ts"}],
            {"title": "beacon-web · Team Beacon", "sub": "Code we read, at 4f2c9a1", "ids": ["idleTimer.ts", "config.ts"]},
            [{"from": "trigger", "to": "idleTimer.ts"}, {"from": "idleTimer.ts", "to": "config.ts", "label": "reads"}],
            'Outside the code we can see', 'Where it happens in beacon-web',
            'Someone using a Beacon page starts Idle timer. Idle timer reads Timeout length.')
    """
    ids = {n['id']: i for i, n in enumerate(nodes)}
    cols, back = _columns(ids, group, edges)
    grouped = set(group['ids'])
    first = min(ids[i] for i in grouped)
    last = max(ids[i] for i in grouped)
    ns = {n['id']: dict(_measure(n, first <= ids[n['id']] <= last), col=cols[n['id']]) for n in nodes}
    count = max(cols.values()) + 1

    # Each edge that skips columns gets a point in each column it passes, which holds its place like a node.
    items = dict(ns)
    routes = []
    for k, edge in enumerate(edges):
        a, b = edge['from'], edge['to']
        ca, cb = cols[a], cols[b]
        points = []
        if (a, b) not in back and cb > ca + 1:
            for c in range(ca + 1, cb):
                key = f'_{k}_{c}'
                items[key] = {'id': key, 'col': c, 'w': 0, 'h': 0, 'point': True}
                points.append(key)
        routes.append((edge, points))
    links = []
    for edge, points in routes:
        if (edge['from'], edge['to']) not in back:
            chain = [edge['from'], *points, edge['to']]
            links += list(zip(chain, chain[1:]))
    neighbours = {key: [] for key in items}
    for a, b in links:
        if items[a]['col'] != items[b]['col']:
            neighbours[a].append(b)
            neighbours[b].append(a)

    column = [[key for key in items if items[key]['col'] == c] for c in range(count)]
    for c in range(count):
        column[c].sort(key=lambda key: ids.get(key, len(ids)))
    for sweep in range(4):
        span = range(1, count) if sweep % 2 == 0 else range(count - 2, -1, -1)
        for c in span:
            side = c - 1 if sweep % 2 == 0 else c + 1
            at = {key: i for i, key in enumerate(column[side])}
            pos = {key: i for i, key in enumerate(column[c])}

            def key_of(key):
                near = [at[x] for x in neighbours[key] if x in at]
                return sum(near) / len(near) if near else pos[key]
            column[c].sort(key=key_of)

    for col in column:
        y = 0
        for key in col:
            items[key]['y'] = y
            y += items[key]['h'] + ROW
    for sweep in range(8):
        span = range(count) if sweep % 2 == 0 else range(count - 1, -1, -1)
        for c in span:
            col = column[c]
            want = []
            for key in col:
                near = [items[x]['y'] + items[x]['h'] / 2 for x in neighbours[key]]
                want.append(sum(near) / len(near) if near else items[key]['y'] + items[key]['h'] / 2)
            for key, top in zip(col, _pack([items[key] for key in col], want)):
                items[key]['y'] = top

    # A label sits by the end that no other edge shares: the node it points to, else the node it leaves, else
    # midway along its first stretch.
    gaps = [GAP] * count
    ins, outs = {}, {}
    for edge in edges:
        if (edge['from'], edge['to']) not in back:
            outs[edge['from']] = outs.get(edge['from'], 0) + 1
            ins[edge['to']] = ins.get(edge['to'], 0) + 1
    place = {}
    for i, edge in enumerate(edges):
        if edge.get('label') and (edge['from'], edge['to']) not in back:
            place[i] = 'to' if ins[edge['to']] == 1 else 'from' if outs[edge['from']] == 1 else 'mid'
            g = cols[edge['to']] if place[i] == 'to' else cols[edge['from']] + 1
            gaps[g] = max(gaps[g], math.ceil(len(edge['label']) * 12 * SANS) + 2 * SPACE + 8)
    widths = [max([items[key]['w'] for key in column[c]] or [0]) for c in range(count)]
    gcol = sorted({cols[i] for i in grouped})
    x, left = 1, []
    for c in range(count):
        x += (gaps[c] if c else 0) + (PAD if c == gcol[0] else 0)
        left.append(x)
        x += widths[c] + (PAD if c == gcol[-1] else 0)
    width = x + 1
    for key, it in items.items():
        it['x'] = left[it['col']] + (widths[it['col']] - it['w']) / 2

    fw = left[gcol[-1]] + widths[gcol[-1]] + PAD - (left[gcol[0]] - PAD)
    frame_title = _lines(group['title'], fw - 2 * PAD, 14)
    frame_sub = _lines(group['sub'], fw - 2 * PAD, 12) if group.get('sub') else []
    header = 2 * PAD + len(frame_title) * TITLE + len(frame_sub) * SUB
    inner = [ns[i] for i in grouped]
    fy = min(n['y'] for n in inner) - header
    frame_bottom = max(n['y'] + n['h'] for n in inner) + PAD
    after = [ns[n['id']] for n in nodes[last + 1:]]
    label_lines = _lines(label, max(n['w'] for n in after), 12, BOLD) if after and label else []
    label_top = min(n['y'] for n in after) - len(label_lines) * SUB - 6 if label_lines else None

    def mid(n):
        return n['y'] + n['h'] / 2

    # Where each edge leaves and arrives: spread down the side it shares, in the order of the ends' other nodes.
    sides = {}
    for i, (edge, points) in enumerate(routes):
        a, b = edge['from'], edge['to']
        if (a, b) in back:
            continue
        sides.setdefault((a, 'out'), []).append((mid(items[points[0] if points else b]), i))
        sides.setdefault((b, 'in'), []).append((mid(items[points[-1] if points else a]), i))
    ends = {}
    for (key, way), lst in sides.items():
        lst.sort()
        for j, (_, i) in enumerate(lst):
            ends[(i, way)] = mid(ns[key]) + (j - (len(lst) - 1) / 2) * SPREAD

    body, labels, bottom = '', '', max(it['y'] + it['h'] for it in items.values())
    for i, (edge, points) in enumerate(routes):
        a, b = ns[edge['from']], ns[edge['to']]
        lab = edge.get('label')
        if (edge['from'], edge['to']) in back:
            dip = max(n['y'] + n['h'] for n in ns.values() if b['col'] <= n['col'] <= a['col']) + DIP
            x0, y0, x1, y1 = a['x'] + a['w'] / 2, a['y'] + a['h'], b['x'] + b['w'] / 2, b['y'] + b['h'] + 1
            body += f'<path class="flow__edge" d="M{x0:.1f},{y0:.1f} C{x0:.1f},{dip:.1f} {x1:.1f},{dip:.1f} {x1:.1f},{y1:.1f}" marker-end="url(#flow-head)"/>'
            low = 0.125 * (y0 + y1) + 0.75 * dip
            if lab:
                labels += f'<text class="flow__edge-label" x="{(x0 + x1) / 2:.1f}" y="{low - 5:.1f}" text-anchor="middle">{e(lab)}</text>'
            bottom = max(bottom, low + 4)
            if a['grouped'] and b['grouped']:
                frame_bottom = max(frame_bottom, low + 4 + PAD)
            continue
        sx, sy = a['x'] + a['w'], ends[(i, 'out')]
        first = (left[items[points[0]]['col']], items[points[0]]['y']) if points else (b['x'] - 1, ends[(i, 'in')])
        d = f'M{sx:.1f},{sy:.1f}'
        for key in points:
            p = items[key]
            px, py = left[p['col']], p['y']
            dx = (px - sx) / 2
            d += f' C{sx + dx:.1f},{sy:.1f} {px - dx:.1f},{py:.1f} {px:.1f},{py:.1f} L{px + widths[p["col"]]:.1f},{py:.1f}'
            sx, sy = px + widths[p['col']], py
        ex, ey = b['x'] - 1, ends[(i, 'in')]
        dx = (ex - sx) / 2
        d += f' C{sx + dx:.1f},{sy:.1f} {ex - dx:.1f},{ey:.1f} {ex:.1f},{ey:.1f}'
        body += f'<path class="flow__edge" d="{d}" marker-end="url(#flow-head)"/>'
        if lab:
            x0, y0 = a['x'] + a['w'], ends[(i, 'out')]
            at = {'to': (ex - 6, ey - 5, 'end'), 'from': (x0 + 6, y0 - 5, 'start'),
                  'mid': ((x0 + first[0]) / 2, (y0 + first[1]) / 2 - 5, 'middle')}[place[i]]
            labels += f'<text class="flow__edge-label" x="{at[0]:.1f}" y="{at[1]:.1f}" text-anchor="{at[2]}">{e(lab)}</text>'
    bottom = max(bottom, frame_bottom)

    top = min([fy] + [it['y'] for it in items.values()] + ([label_top] if label_top is not None else [])) - 1
    height = math.ceil(bottom - top) + 1
    full = ' · '.join(t for t in (group['title'], group.get('sub')) if t)
    tx = left[gcol[0]] - PAD
    svg = (f'<g class="flow__frame"><title>{e(full)}</title><rect x="{tx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{frame_bottom - fy:.1f}" rx="8"/>'
           + ''.join(f'<text class="flow__frame-title" x="{tx + PAD:.1f}" y="{fy + PAD + i * TITLE + 15:.1f}">{e(t)}</text>' for i, t in enumerate(frame_title))
           + ''.join(f'<text class="flow__frame-sub" x="{tx + PAD:.1f}" y="{fy + PAD + len(frame_title) * TITLE + i * SUB + 12:.1f}">{e(t)}</text>'
                     for i, t in enumerate(frame_sub)) + '</g>')
    svg += ''.join(f'<text class="flow__label" x="{after[0]["x"]:.1f}" y="{label_top + 12 + i * SUB:.1f}">{e(t)}</text>' for i, t in enumerate(label_lines))
    svg += body + ''.join(_node(ns[n['id']]) for n in nodes) + labels
    return (f'<figure class="flow" tabindex="0" role="region" aria-label="Diagram">'
            f'<svg class="flow__svg" viewBox="0 {top:.1f} {width:.0f} {height}" style="max-width:{width:.0f}px;min-width:{math.ceil(width * MIN_SCALE)}px" '
            f'role="img" aria-labelledby="flow-title flow-desc"><title id="flow-title">{e(title)}</title><desc id="flow-desc">{e(desc)}</desc>'
            f'<defs><marker id="flow-head" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" '
            f'markerUnits="userSpaceOnUse" orient="auto"><path class="flow__head" d="M0,0 L8,4 L0,8 z"/></marker></defs>{svg}</svg></figure>')
