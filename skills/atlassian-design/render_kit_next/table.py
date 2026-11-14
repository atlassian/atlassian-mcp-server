"""Tables: after ADS DynamicTable (@atlaskit/dynamic-table 19.3.8), stacking each row into labelled blocks on
narrow screens. CSS: table.css."""
from .links import text
from .page import e


def table(headers, rows):
    """A table with a header row. At 600px and narrower, each row becomes a block with every cell under its
    header's name, so a long setting name keeps the full width.

    Cells are text fields, or {"text", "sub"} with a small line under the text.

        table(['Setting or flag', 'What it changes', 'Who controls it'],
              [[{"text": "`idleTimeoutMinutes`", "sub": "Site security settings"}, "The timeout", "Set by the site admin"]])
    """
    def cell(h, c):
        sub = f'<div class="table__sub">{text(c, "sub")}</div>' if isinstance(c, dict) and c.get('sub') else ''
        return f'<td data-label="{e(h)}">{text(c)}{sub}</td>'
    head = ''.join(f'<th scope="col">{e(h)}</th>' for h in headers)
    body = ''.join('<tr>' + ''.join(cell(h, c) for h, c in zip(headers, r)) + '</tr>' for r in rows)
    return f'<table class="table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'
