#!/usr/bin/env python3
"""Render a decision trace from a JSON data file.

    python3 render.py trace.json decision-trace.html

The agent writes only the data (see "Step 8: Build the trace" in SKILL.md and example.json). This script
lays out the sections. The decision blocks, options, timeline, section messages and smart links come from
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
from render_kit import lz, text, card  # noqa: E402


def plural(n, word):
    return f'{n} {word}' if n == 1 else f'{n} {word}s'


def render(d):
    t = d['traced']
    lede = (f'Traced from {plural(t["records"], "record")} and {plural(t["discussions"], "discussion")}, on {t["date"]}. '
            'Every claim links to where it came from.')
    body = k.header('Decision trace', d['question'], '', badge=lz(d.get('verdict')), lede=lede)

    more = ''.join(k.decision(x) for x in d.get('decisions', []))
    if d.get('revisit'):
        more += k.note(d['revisit'], ic='warning', tone='warning', title=d['revisit'].get('title', ''))
    if d.get('newer'):
        newer = d['newer']
        more += k.note(newer, tone='information', title=newer.get('title', '') if isinstance(newer, dict) else '')
    body += k.summary_card('The answer', d.get('answer', []), d['generatedFrom'], check='relying on', more=more)

    body += card('comment', 'Why', k.text_rows(d['why']) if d.get('why') else k.empty('No record states the reasons.'))
    opts = d.get('options')
    if opts and opts.get('items'):
        source = f'<p class="fine">{text(opts["from"])}</p>' if opts.get('from') else ''
        body += card('list-checklist', opts.get('heading', 'Options considered'), k.options(opts['items']) + source)
    body += card('clock', 'Timeline', k.timeline(d.get('timeline', [])))
    if d.get('notInRecords'):
        body += card('warning', 'Not in the records', k.text_rows(d['notInRecords']))
    body += k.footer(d.get('footer', {}))
    return k.page(f'Decision trace: {d["question"]}', body, mockup=d.get('mockup'))


if __name__ == '__main__':
    k.main(render, 'render.py trace.json decision-trace.html')
