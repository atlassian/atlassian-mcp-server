#!/usr/bin/env python3
"""Render a dependency map from a JSON data file.

    python3 render.py map.json dependency-map.html

The agent writes only the data (see "Step 7: Build the map" in SKILL.md and example.json): the anchor and
every dependency once, with its side, state and source. This script counts them, lays out the sections and
ranks what needs attention. The diagram, its layout, legend and list, the tiles and the rows come from
render_kit in the atlassian-design skill installed beside this one. Output is one self-contained HTML file
with no external requests and no browser storage.
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent  # not resolved, so a symlinked install finds its sibling skills
KIT = HERE.parent / 'atlassian-design'
sys.path.insert(0, str(KIT))
try:
    import render_kit as k  # noqa: E402
except ModuleNotFoundError as err:
    if err.name != 'render_kit':
        raise
    sys.exit(f'This renderer needs the atlassian-design skill installed beside this skill. Looked in {KIT}.')
from render_kit import lz, card  # noqa: E402

ATTENTION = ('blocked', 'at-risk', 'stale')


def types(dep):
    """A dependency's state lozenge, then its source and both-ways lozenges when they apply."""
    word, tone = k.STATES[dep['state']]
    out = [{'text': word, 'tone': tone}]
    src = k.SOURCES.get(dep.get('source', 'recorded'))
    if src:
        out.append({'text': src[0], 'tone': src[1]})
    if dep.get('bothWays'):
        out.append({'text': 'Both ways', 'tone': 'discovery'})
    return out


def side_sub(deps):
    done = sum(d['state'] == 'done' for d in deps)
    both = sum(bool(d.get('bothWays')) for d in deps)
    bits = [f'{done} done, {len(deps) - done} open' if done else 'none done'] + ([f'{both} both ways'] if both else [])
    return ' · '.join(bits)


def render(d):
    a, deps = d['anchor'], d['dependencies']
    first = [x for x in deps if x.get('hop', 1) == 1]
    up = [x for x in first if x['side'] == 'upstream']
    down = [x for x in first if x['side'] == 'downstream']
    blocked = sum(x['state'] == 'blocked' for x in first)
    at_risk = sum(x['state'] == 'at-risk' for x in first)
    attention = sorted((x for x in first if x['state'] in ATTENTION), key=lambda x: ATTENTION.index(x['state']))
    unrecorded = sorted((x for x in deps if x.get('source') == 'not-recorded'), key=lambda x: k.SEVERITY.index(x['state']))

    meta = ''.join(k.meta_item(ic, t) for ic, t in (('person', a.get('owner') and f'Owner: {a["owner"]}'), ('people-group', a.get('team')),
                                                    ('calendar', a.get('needBy') and f'Needed by {a["needBy"]}{", passed" if a.get("passed") else ""}')) if t)
    if a.get('history'):
        meta += k.meta_item(None, a['history'])
    counts = ''.join(lz(x) for x in [blocked and {'text': f'{blocked} blocked', 'tone': 'danger'},
                                     at_risk and {'text': f'{at_risk} at risk', 'tone': 'warning'}] if x)
    body = k.header('Dependency map', a['title'], meta, counts, badge=lz(a.get('status')))

    tiles = k.tiles([{'value': len(up), 'label': 'Waiting on', 'sub': side_sub(up)},
                     {'value': len(down), 'label': 'Waiting on us', 'sub': side_sub(down)},
                     {'value': len(attention), 'label': 'Need attention', 'tone': 'danger' if blocked else 'warning' if attention else None},
                     {'value': len(unrecorded), 'label': 'Not recorded'}])
    body += k.summary_card('Summary', d.get('summary', []), d.get('generatedFrom', ''), check='sharing', lead=tiles)

    body += card('link', 'Map', k.diagram(a, deps, a.get('kind', 'project')) + k.legend() + k.dependency_list(deps))

    rows = [{'type': types(x), 'text': x.get('why', ''), 'contact': x.get('contact'), 'source': x.get('url') and x} for x in attention]
    body += card('priority-blocker', 'Needs attention', k.rows(rows, empty_msg='Nothing is blocked, at risk or stale.'))
    if unrecorded:
        rows = [{'type': types(x), 'text': x['evidence']['text'], 'quote': x['evidence'].get('quote'),
                 'source': x['evidence'].get('link'), 'when': x.get('offer', '')} for x in unrecorded]
        body += card('search', 'Not recorded', k.rows(rows))
    if d.get('nextSteps'):
        body += card('arrow-right', 'Next steps', k.numbered(d['nextSteps']))
    body += k.footer(d.get('footer', {}))
    return k.page(f'Dependency map: {a["title"]}', body, js=k.DIAGRAM_JS, width='wide', mockup=d.get('mockup'))


if __name__ == '__main__':
    k.main(render, 'render.py map.json dependency-map.html')
