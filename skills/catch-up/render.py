#!/usr/bin/env python3
"""Render a catch-up page from a JSON data file.

    python3 render.py catchup.json catch-up.html

The agent writes only the data (see Step 8 in SKILL.md and example.json). This script lays
out the sections. The ADS CSS, smart links, icons and the unfilled-placeholder check come
from render_kit in the atlassian-design skill installed beside this one.
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
from render_kit import e, lz, text, card, empty  # noqa: E402

PAGE_CSS = '''
.mrow{display:grid;grid-template-columns:4rem minmax(0,1fr);gap:var(--ds-space-150)}
.mrow .d{font-weight:var(--ds-font-weight-medium)}
.mrow .t{font-weight:var(--ds-font-weight-medium)}
.mrow .m{font:var(--ds-font-body-small);color:var(--ds-text-subtlest);margin-bottom:var(--ds-space-050)}
@media (max-width:640px){.mrow{grid-template-columns:minmax(0,1fr);gap:var(--ds-space-025)}}
'''

URGENT = ('Overdue', 'Blocking')


def render(d):
    topic = d.get('topic') or 'Your work'
    need, dec, groups = d.get('needsYou', []), d.get('decisions', []), d.get('changes', [])
    c = d.get('counts', {})
    n_need = c.get('needYou', len(need))
    n_dec = c.get('decisions', len(dec))
    n_ch = c.get('changes', sum(len(g.get('rows', [])) for g in groups))
    urgent = any(k.lz_text(x.get('type')) in URGENT for x in need)
    counts = ''.join(lz(x) for x in [
        n_need and {'text': f'{n_need} need you', 'tone': 'warning' if urgent else 'information'},
        n_dec and {'text': f'{n_dec} decision{"s" if n_dec != 1 else ""}', 'tone': 'success'},
        n_ch and {'text': f'{n_ch} change{"s" if n_ch != 1 else ""}'}] if x)
    window = f'{d["start"]} to {d["end"]}'
    days = d.get('workingDays')
    meta = (k.meta_item('calendar', f'{window}{" · " + str(days) + " working days" if days else ""}')
            + (k.meta_item(None, 'From your calendar') if d.get('fromCalendar') else ''))
    head = k.header('Catch-up', topic, meta, counts)

    summary = k.summary_card(d.get('summaryHeading', 'While you were away'), d['summary'], d['generatedFrom'])

    needs = card('flag', 'Needs you', k.rows(need, 'Nothing is waiting on you.'))

    dec_body = k.rows(dec, default_lz={'text': 'Decided', 'tone': 'success'})
    if not dec:
        dec_body = empty('No decisions you missed in this window.') + ''.join(f'<p class="fine">{text(x)}</p>' for x in d.get('decisionNotes', []))
    decided = card('decision', 'Decided while you were away', dec_body)

    ch = ''
    for g in groups:
        name = k.link(g['link']) if g.get('link') else e(g.get('group', 'Other'))
        ch += f'<h3>{name}</h3>' + k.rows(g.get('rows', []), default_lz='Update')
    changed = card('changes', 'What changed', ch or empty(f'No changes to this work between {d["start"]} and {d["end"]}.'))

    meets = d.get('meetings', [])
    mrows = ''.join(
        f'<li class="mrow"><span class="d">{e(m["date"])}</span><div><div class="t">{e(m["title"])}</div><div class="m">{e(m.get("meta", ""))}</div>'
        + (f'<div>{text(m, "line")} {k.links(m.get("source"))}</div>' if m.get('line') else '<div class="fine">No notes or recording found.</div>')
        + '</div></li>' for m in meets)
    m_body = f'<ul class="list">{mrows}</ul>' if meets else empty('No meetings you missed in this window.')
    m_body += ''.join(f'<p class="fine">{text(x)}</p>' for x in d.get('meetingNotes', []))
    missed = card('video', 'Meetings you missed', m_body)

    up = d.get('comingUp', [])
    coming = card('clock', 'Coming up', '<ul class="list">' + ''.join(
        f'<li><strong>{e(x["date"])}</strong> · {text(x)}</li>' for x in up) + '</ul>') if up else ''

    body = head + summary + needs + decided + changed + missed + coming + k.footer(d.get('footer', {}))
    title = f'Catch-up: {d.get("topic") or "your work"}, {d.get("startShort", d["start"])} to {d.get("endShort", d["end"])}'
    return k.page(title, body, PAGE_CSS, mockup=d.get('mockup'))


if __name__ == '__main__':
    k.main(render, 'render.py catchup.json catch-up.html')
