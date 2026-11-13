#!/usr/bin/env python3
"""Render a release readiness report from a JSON data file.

    python3 render.py readiness.json release.html

The agent writes only the data (see "Build the page" in SKILL.md). This script lays out the
report's sections. The ADS CSS, smart links, icons and the unfilled-placeholder check come
from render_kit in the atlassian-design skill installed beside this one. Output is one
self-contained HTML file with no external requests and no browser storage.
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
from render_kit import e, lz, link, links, text, card, empty  # noqa: E402

PAGE_CSS = '''
.areas > li{display:grid;grid-template-columns:7rem 6.5rem minmax(0,1fr);gap:var(--ds-space-150);align-items:start}
.areas .an{font-weight:var(--ds-font-weight-medium)}
.waiting{font:var(--ds-font-body-small);color:var(--ds-text-subtle);margin-top:var(--ds-space-050)}
.wrow{display:grid;grid-template-columns:6.5rem minmax(0,1fr) auto;gap:var(--ds-space-150);align-items:start}
.wrow .m{font:var(--ds-font-body-small);color:var(--ds-text-subtle);text-align:right;line-height:1.5rem}
.dec{margin:0;padding-left:var(--ds-space-250);display:grid;gap:var(--ds-space-150)}
.dec strong{font-weight:var(--ds-font-weight-medium)}
@media (max-width:640px){
  .areas > li,.wrow{grid-template-columns:minmax(0,1fr);gap:var(--ds-space-050)} .wrow .m{text-align:left}
}
'''


def render(d):
    name = d['version']
    m = d.get('meta', {})
    meta = []
    if m.get('project'):
        meta.append(k.meta_item(None, {'text': '{0}', 'link': m['project']}))
    if m.get('releaseDate'):
        meta.append(k.meta_item('calendar', m['releaseDate'] + (' · passed' if m.get('datePassed') else '')))
    if m.get('projectTarget'):
        meta.append(k.meta_item(None, f'Project target: {m["projectTarget"]}'))
    if m.get('driver'):
        meta.append(k.meta_item('person', f'Driver: {m["driver"]}'))
    n = d.get('blockerCount')
    counts = lz({'text': f'{n} blocker{"s" if n != 1 else ""}', 'tone': 'danger'}) if n else ''
    head = k.header('Release readiness', name, ''.join(meta), counts, badge=lz(d.get('verdict')))

    verdict = k.summary_card('Verdict', d.get('summary', []), d.get('generatedFrom', 'Jira'), lead=k.tiles(d.get('tiles', [])))

    def blocker(b):
        wait = f'<div class="waiting">Waiting: {links(b["waiting"])}</div>' if b.get('waiting') else ''
        src = k.source_line(b.get('source'), b.get('when', ''), b.get('sourceLabel', 'Evidence: '))
        return (f'<li class="lrow"><span>{lz(b.get("type", {"text": "Blocker", "tone": "danger"}))}</span>'
                f'<div>{text(b)}{wait}{src}</div></li>')
    bl = d.get('blockers', [])
    p_block = card('flag', 'Blockers', ('<ul class="list">' + ''.join(blocker(b) for b in bl) + '</ul>')
                   if bl else empty(d.get('noBlockers', 'No blockers recorded.')))

    areas = ''.join(f'<li><span class="an">{e(a["name"])}</span><span>{lz(a["state"])}</span>'
                    f'<div>{text(a)}{k.source_line(a.get("evidence"), label="")}</div></li>' for a in d.get('areas', []))
    p_areas = card('check', 'Readiness by area', f'<ul class="list areas">{areas}</ul>')

    conditions = [dict(c, contact='Areas: ' + ', '.join(c['areas'])) for c in d['conditions']]
    p_conditions = card('info', f'Outstanding conditions ({len(conditions)})',
                        k.rows(conditions, 'No outstanding conditions on the evidence checked.'))
    p_find = card('info', 'Other findings', k.rows(d.get('findings', []), 'No other findings.'))

    def wrow(w):
        tag = ''
        if w.get('check'):
            tag = f' <span class="tag">{e(w["check"])}</span>' + (' <span class="fine">Grouped by title</span>' if w.get('byTitle') else '')
        side = ' · '.join(x for x in [e(w.get('assignee', 'Unassigned')), e(w.get('due', ''))] if x)
        return f'<li class="wrow"><span>{lz(w["status"])}</span><div>{link(w["link"])}{tag}</div><span class="m">{side}</span></li>'
    work = d.get('work', [])
    wb = ('<ul class="list">' + ''.join(wrow(w) for w in work) + '</ul>') if work else empty('No open work.')
    if d.get('workMore'):
        wb += f'<p class="fine">{text(d["workMore"])}</p>'
    if d.get('done'):
        wb += f'<p class="fine">{e(d["done"])}</p>'
    p_work = card('task', 'Open work', wb)

    def dec(x):
        holder = f'Holder: {e(x["holder"])}' if x.get('holder') else 'No owner recorded'
        src = (' · ' + links(x['holderSource'])) if x.get('holderSource') else ''
        return f'<li><strong>{text(x)}</strong><div class="src">Suggested · {holder}{src}</div></li>'
    decs = d.get('decisions', [])
    p_dec = card('decision', 'Decisions needed', (f'<ol class="dec">{"".join(dec(x) for x in decs)}</ol>')
                 if decs else empty('No decisions needed on this evidence.'))

    body = f'{head}{verdict}{p_block}{p_areas}{p_conditions}{p_find}{p_work}{p_dec}{k.footer(d.get("footer", {}))}'
    return k.page(f'Release readiness: {name}', body, PAGE_CSS, mockup=d.get('mockup'))


if __name__ == '__main__':
    k.main(render, 'render.py readiness.json release.html')
