"""Evidence lines, and a quote with a copy button. CSS: evidence.css."""
from .layout import copy_btn
from .links import e, link


def evidence_item(x):
    """One evidence line: the verb, the smart link, then the month and year.

    Data: {"verb": "Wrote", "link": link, "date"?: "Oct 2026"}.

        evidence_item({"verb": "Wrote", "link": {"title": "Search cutover runbook", "url": "#", "icon": "page"},
                       "date": "Oct 2026"})
    """
    date = f' <span class="evidence-list__date">{e(x["date"])}</span>' if x.get('date') else ''
    return f'<span class="evidence-list__verb">{e(x["verb"])}</span> {link(x["link"])}{date}'


def evidence(items, limit=4):
    """A list of evidence lines, Strong items ({"strong": true}) first, with "and N more" past the limit.

        evidence([{"verb": "Wrote", "link": link, "strong": True}, {"verb": "Commented on", "link": link}])
    """
    items = sorted(items, key=lambda x: not x.get('strong'))
    more = f'<p class="fine">and {len(items) - limit} more</p>' if len(items) > limit else ''
    return '<ul class="evidence-list">' + ''.join(f'<li>{evidence_item(x)}</li>' for x in items[:limit]) + '</ul>' + more


def quote_copy(q):
    """A quote block with a button that copies it.

        quote_copy("Hi Priya, is the 5-second pool timeout back in place?")
    """
    return f'<div class="quote-copy"><blockquote>{e(q)}</blockquote>{copy_btn(q)}</div>'
