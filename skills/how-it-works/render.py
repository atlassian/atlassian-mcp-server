#!/usr/bin/env python3
"""Render a how-it-works explainer from a JSON data file.

    python3 render.py explainer.json how-it-works.html

The agent writes only the data (see "Step 8: Build the explainer" in SKILL.md and example.json). This
script lays out the sections. Everything visible, the page assembly and the command line come from
render_kit_next, the staging kit in the atlassian-design skill installed beside this one. Output is one
self-contained HTML file with no external requests and no browser storage.
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent  # not resolved, so a symlinked install finds its sibling skills
KIT = HERE.parent / 'atlassian-design'
sys.path.insert(0, str(KIT))
try:
    import render_kit_next as k  # noqa: E402
except ModuleNotFoundError as err:
    if err.name != 'render_kit_next':
        raise
    sys.exit(f'This renderer needs the atlassian-design skill, with render_kit_next, installed beside this skill. Looked in {KIT}.')

REPLY_NOTE = 'Proposed. Check it before you send it.'
OUTSIDE = 'Outside the code we can see'
NO_OWNER = 'No owner recorded'


def joined(items):
    items = list(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1] if len(items) > 1 else ''.join(items)


def step_words(ns):
    """"Step 4" or "Steps 2 and 3"."""
    return ('Step ' if len(ns) == 1 else 'Steps ') + joined(map(str, ns)) if ns else ''


def step_numbers(x, where, count):
    """An entry's steps, each checked to be a step of the trace."""
    ns = x.get('steps') or []
    if not isinstance(ns, list):
        raise k.DataError(f'{where}.steps: {ns!r} is not a list of step numbers')
    for n in ns:
        if type(n) is not int or not 1 <= n <= count:
            raise k.DataError(f'{where}.steps: {n!r} is not a step, the trace has {count}')
    return ns


def lower(s):
    return s[:1].lower() + s[1:] if s[1:2].islower() else s


def where_it_happens(d, steps):
    """The Where it happens card, or nothing when there's no map, no cited file or no link between files."""
    m = d.get('map')
    if not m:
        return ''
    cited = {}
    for i, s in enumerate(steps, 1):
        if s.get('code'):
            cited.setdefault(s['code']['path'], []).append(i)
    names = {}
    for i, p in enumerate(m.get('parts', [])):
        if p['path'] not in cited:
            raise k.DataError(f'map.parts[{i}]: no step cites {p["path"]}')
        names[p['path']] = p['name']
    for path, ns in cited.items():
        if path not in names:
            raise k.DataError(f'map.parts: no name for {path}, cited in step {ns[0]}')
    links = m.get('links', [])
    for i, x in enumerate(links):
        for end in ('from', 'to'):
            if x[end] not in names:
                raise k.DataError(f'map.links[{i}].{end}: {x[end]} is not in map.parts')
        if x['from'] == x['to']:
            raise k.DataError(f'map.links[{i}]: links {x["from"]} to itself')
        n = x['step']
        if type(n) is not int or not 1 <= n <= len(steps):
            raise k.DataError(f'map.links[{i}].step: {n!r} is not a step, the trace has {len(steps)}')
        if steps[n - 1].get('code', {}).get('path') not in (x['from'], x['to']):
            raise k.DataError(f'map.links[{i}].step: step {n} cites neither {x["from"]} nor {x["to"]}')
    outside = [(o, step_numbers(o, f'map.outside[{i}]', len(steps))) for i, o in enumerate(m.get('outside', []))]
    if not links:
        return ''

    r = d['readFrom']
    team = next((o['link'] for o in d.get('owners', []) if o.get('label') == 'Team' and o.get('link')), None)
    team = (team[0] if isinstance(team, list) else team)['title'] if team else ''
    group = {'title': r['repository'] + (f' · {team}' if team else ''), 'sub': f'Code we read, at {r["commit"][:7]}', 'ids': list(cited)}
    files = [{'id': p, 'title': names[p], 'sub': p.rsplit('/', 1)[-1]} for p in cited]
    services = [{'id': f'outside{i}', 'title': o['name'], 'sub': o.get('owner') or NO_OWNER, 'kind': 'outside'}
                for i, (o, _) in enumerate(outside)]
    nodes = [{'id': 'trigger', 'title': m['trigger']}] + files + services

    entry = steps[0]['code']['path'] if steps[0].get('code') else next(iter(cited))
    edges = [{'from': 'trigger', 'to': entry}]
    edges += [{'from': x['from'], 'to': x['to'], 'label': x['verb']} for x in links]
    handoffs = {(steps[n - 1]['code']['path'], i) for i, (o, ns) in enumerate(outside) for n in ns if steps[n - 1].get('code')}
    edges += [{'from': path, 'to': f'outside{i}'} for path, i in sorted(handoffs, key=lambda h: (h[1], list(cited).index(h[0])))]

    desc = [f'{m["trigger"]} starts {names[entry]}.']
    desc += [f'{n["title"]} is {n["sub"]}.' for n in files]
    desc += [f'{names[x["from"]]} {x["verb"]} {names[x["to"]]}.' for x in links]
    desc += [f'{joined(names[p] for p, j in sorted(handoffs) if j == i) or "The code"} hands off to {n["title"]}, outside the code we can '
             f'see; {lower(n["sub"])}.' for i, n in enumerate(services)]
    title = f'Where it happens in {r["repository"]}' + (f', owned by {team}' if team else '') + f', read at commit {r["commit"][:7]}'
    return k.section('Where it happens', k.flow_figure(nodes, group, edges, OUTSIDE, title, ' '.join(desc)))


def render(d):
    r = d['readFrom']
    body = k.mockup_badge() if d.get('mockup') else ''
    body += k.header('how-it-works', d['question'], f'{d["about"]}, as of {r["date"]}.')

    body += k.section('Short answer', k.paragraphs(d.get('answer', [])))

    steps = d.get('steps', [])
    touched = [step_numbers(s, f'settings[{i}]', len(steps)) for i, s in enumerate(d.get('settings', []))]
    body += where_it_happens(d, steps)
    trace = k.trace(steps, r['commit'][:7])
    if d.get('traceNote'):
        trace += k.small_text(d['traceNote'])
    body += k.section('Step by step', trace)

    if d.get('settings'):
        rows = [[{'text': f'`{s["name"]}`', 'sub': s.get('kind', '')}, {'text': s['changes'], 'sub': step_words(ns)}, s['who']]
                for s, ns in zip(d['settings'], touched)]
        body += k.section('What can change this', k.table(['Setting or flag', 'What it changes', 'Who controls it'], rows))
    if d.get('checklist'):
        lead = k.small_text(d['checkNote']) if d.get('checkNote') else ''
        body += k.section('What to check on the account', lead + k.checklist(d['checklist']))

    docs = k.source_rows(d['docs']) if d.get('docs') else k.paragraphs('Nothing in the docs or chat about this.')
    if d.get('questions'):
        docs += k.small_text(d['questions'])
    if d.get('bugs'):
        docs += k.rows([{'text': 'Open bug', 'links': bug} for bug in d['bugs']])
    body += k.section('What the docs and chat say', docs)

    if d.get('changes'):
        rows = [{'label': (f'{c["version"]} · ' if c.get('version') else '') + c['date'], 'text': c['text'], 'links': c.get('links'),
                 'source': c.get('link')} for c in d['changes']]
        note = k.small_text(d['changesNote']) if d.get('changesNote') else ''
        body += k.section('Recent changes', k.label_rows(rows) + note)
    if d.get('owners'):
        rows = [{'label': o['label'], 'text': o.get('text'), 'links': o.get('links'), 'source': o.get('link'), 'note': o.get('from')}
                for o in d['owners']]
        body += k.section('Who owns it', k.label_rows(rows))
    if d.get('reply'):
        ticket = k.paragraphs({'text': 'Reply on {0}', 'link': d['askedOn']}) if d.get('askedOn') else ''
        body += k.section('Suggested reply', ticket + k.small_text(REPLY_NOTE) + k.copy_block(d['reply']))
    if d.get('notAnswered'):
        body += k.section('Not answered here', k.small_text(d['notAnswered']))
    body += k.sources_footer(d.get('footer', {}))
    return k.page(f'How it works: {d["question"]}', body, 880)


if __name__ == '__main__':
    k.main(render, 'render.py explainer.json how-it-works.html')
