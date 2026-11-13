"""Decisions: decision blocks with their fields, options considered, and a vertical timeline. CSS: decisions.css."""
from .links import e, link, links, text
from .status import lz


def decision(x):
    """One decision in the chain, headed with what it is and its status, then its fields: Decided (the record's
    words, quoted, with its link), When and Who decided (each with how it's known), and Also recorded.

    Data: {"heading", "status": lozenge, "decided", "link", "when", "whenHow"?, "who", "whoHow"?, "also"?: [links],
    "alsoHow"?}.

        decision({"heading": "Newest decision", "status": {"text": "Decided", "tone": "success"},
                  "decided": "Cut over on Nov 16.", "link": {"title": "Search migration decision log", "url": "#", "icon": "page"},
                  "when": "Decided on Oct 16, 2026", "whenHow": "decision log row", "who": "Amara Lindqvist"})
    """
    def how(key):
        return f' <span class="decision__how">({e(x[key])})</span>' if x.get(key) else ''
    fields = [('Decided', f'<blockquote class="decision__quote">{e(x["decided"])}</blockquote>{link(x["link"]) if x.get("link") else ""}'),
              ('When', e(x.get('when', '')) + how('whenHow')),
              ('Who decided', e(x.get('who') or 'No decider recorded') + how('whoHow'))]
    if x.get('also'):
        also = f' <span class="decision__how">{e(x["alsoHow"])}</span>' if x.get('alsoHow') else ''
        fields.append(('Also recorded', links(x['also']) + also))
    dl = ''.join(f'<dt>{e(k)}</dt><dd>{v}</dd>' for k, v in fields)
    return f'<div class="decision"><h3 class="decision__heading">{e(x["heading"])} {lz(x.get("status"))}</h3><dl class="decision__fields">{dl}</dl></div>'


def options(items):
    """Options considered, one row each: the record's name for it, a short description in its words, and a
    "Chosen" or "Recommended" lozenge.

    Data: [{"name", "text", "chosen"?, "recommended"?}].

        options([{"name": "Build a new cluster.", "text": "Run both clusters and switch traffic.", "chosen": True}])
    """
    def mark(x):
        if x.get('chosen'):
            return lz({'text': 'Chosen', 'tone': 'success'})
        return lz({'text': 'Recommended', 'tone': 'information'}) if x.get('recommended') else ''
    return '<ul class="list">' + ''.join(
        f'<li class="option"><div><span class="option__name">{e(x["name"])}</span> {text(x)}</div><span>{mark(x)}</span></li>'
        for x in items) + '</ul>'


def timeline(items):
    """A vertical timeline, oldest first: the date (or "No date"), the type lozenge, one sentence and its smart
    link. At 600px and narrower each date sits above its item.

    Data: [{"date"?, "type": lozenge, "text": text field, "link"?}].

        timeline([{"date": "Jun 12, 2026", "type": {"text": "Recorded decision", "tone": "success"},
                   "text": "The DACI was marked Approved.", "link": {"title": "DACI: Search cluster upgrade path", "url": "#", "icon": "page"}}])
    """
    return '<ol class="timeline">' + ''.join(
        f'<li><div class="timeline__date">{e(x.get("date") or "No date")}</div><div class="timeline__body">{lz(x.get("type"))}'
        f'<p class="timeline__text">{text(x)}</p>{link(x["link"]) if x.get("link") else ""}</div></li>' for x in items) + '</ol>'
