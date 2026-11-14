#!/usr/bin/env python3
"""Render a "Before you start" card from a JSON data file.

    python3 render.py card.json before-you-start.html

The agent writes only the data (see "Step 8: Build the card" in SKILL.md and example.json). This script
lays out the sections. The effort rows, smart links, the copyable message and the footer come from
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

LEDE = "Based on what each effort's own records say it does. The moves are suggestions."
UNCHECKED = "Title matches only. We couldn't read what it does."


def render(d):
    meta = k.meta_item(None, d['idea']) if d.get('idea') else ''
    body = k.header('Before you start', d['headline'], meta, badge=lz(d.get('verdict')), lede=LEDE)
    body += card('project', 'Efforts', k.efforts(d['efforts']) if d.get('efforts') else k.empty('Nothing close found.'))
    if d.get('message'):
        body += card('comment', 'Suggested first message', k.empty('Suggested') + k.quote_copy(d['message']))
    if d.get('unchecked'):
        body += card('search', 'Names that matched, not checked', k.link_rows(d['unchecked'], meta=UNCHECKED))
    body += k.footer(d.get('footer', {}))
    return k.page(f'Before you start: {d["headline"]}', body, mockup=d.get('mockup'))


if __name__ == '__main__':
    k.main(render, 'render.py card.json before-you-start.html')
