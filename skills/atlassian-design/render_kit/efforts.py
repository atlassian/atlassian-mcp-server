"""Efforts: ranked rows for the work an idea overlaps with. CSS: efforts.css."""
from .links import e, links, text
from .people import avatar
from .status import lz


def effort(x):
    """One effort, as a plain block of stacked lines that wrap on phones: the main record, its class and status,
    what it does, the owner, the move, then its evidence.

    Data: {"link", "class": lozenge, "status", "does": text field, "facets", "owner": {"name", "label", "team"?}
    or {"label"} alone, "contributors"?, "move": {"label", "why"}, "linked"?: [links], "found"?: [links],
    "earlier"?: [links], "next"?: [links], "note"?, "connected"?}. Linked and found-by-search evidence stay two
    lists, and an empty one is left out.

        effort({"link": {"title": "Search alerts for Confluence spaces", "url": "#", "icon": "project"},
                "class": {"text": "Same idea", "tone": "danger"}, "status": "Projects · On track",
                "does": "Sends a daily email when new pages match a saved query.", "owner": {"name": "Priya Nair",
                "label": "Owner", "team": "Team Ledger"}, "move": {"label": "Join", "why": "Updated this week"}})
    """
    o = x.get('owner') or {}
    name = o.get('name')
    who = (avatar(name, small=True) if name else '') + f'<span><span class="effort__label">{e(o.get("label", "Owner not recorded"))}</span>'
    who += (f' {e(name)}' if name else '') + (f' <span class="effort__team">· {e(o["team"])}</span>' if o.get('team') else '')
    if x.get('contributors'):
        who += f' <span class="effort__team">· with {e(" and ".join(x["contributors"]))}</span>'
    who += '</span>'
    move = x.get('move') or {}
    parts = [
        f'<div class="effort__top">{links(x["link"])}{lz(x.get("class"))}<span class="effort__status">{e(x.get("status", ""))}</span></div>',
        f'<p class="effort__does">{text(x, "does")}</p>' if x.get('does') else '',
        f'<div class="fine">{e(x["facets"])}</div>' if x.get('facets') else '',
        f'<div class="effort__owner">{who}</div>',
        f'<p class="effort__move"><b>{e(move["label"])}</b> · {text(move, "why")}</p>' if move.get('label') else '',
    ]
    for key, label in (('linked', 'Linked'), ('found', 'Found by search'), ('earlier', 'Earlier phases'), ('next', 'Next phase')):
        if x.get(key):
            parts.append(f'<div class="effort__evidence"><div class="effort__evidence-label">{label}</div><ul>'
                         + ''.join(f'<li>{links(l)}</li>' for l in x[key]) + '</ul></div>')
    if x.get('note'):
        parts.append(f'<div class="fine">{e(x["note"])}</div>')
    if x.get('connected'):
        parts.append(f'<div class="effort__connected">{e(x["connected"])}</div>')
    return f'<li class="effort">{"".join(parts)}</li>'


def efforts(items):
    """The efforts as a ranked list.

        efforts([effort_data, ...])
    """
    return '<ol class="efforts">' + ''.join(effort(x) for x in items) + '</ol>'
