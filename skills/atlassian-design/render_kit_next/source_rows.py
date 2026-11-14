"""Source rows: what each source says, checked against the page, divided by lines. CSS: source_rows.css."""
from .frame import paragraphs
from .links import links, status
from .page import e


def source_rows(items):
    """One row per source: its smart link on its own line, then the claim, then the verdict lozenge and the meta
    in small text, 8px apart, so a long title doesn't squeeze the claim.

    Data: [{"link", "claim": text field, "verdict"?: lozenge, "meta"?}].

        source_rows([{"link": {"title": "Beacon support runbook", "url": "#", "icon": "page"},
                      "claim": "Says the default is 30 minutes.", "verdict": {"text": "Matches", "tone": "success"},
                      "meta": "Runbook · Updated Aug 19, 2026"}])
    """
    def row(x):
        meta = (status(x['verdict']) if x.get('verdict') else '') + (f'<span>{e(x["meta"])}</span>' if x.get('meta') else '')
        return (f'<li class="source-row">{links(x["link"])}{paragraphs(x["claim"])}'
                + (f'<div class="source-row__meta">{meta}</div>' if meta else '') + '</li>')
    return '<ul class="row-list">' + ''.join(row(x) for x in items) + '</ul>'
