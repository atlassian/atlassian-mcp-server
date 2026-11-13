"""Metric tiles for a summary card. CSS: metrics.css."""
from .links import e


def tiles(items):
    """A row of metric tiles: a standalone number, its label, and an optional line under it. Four across, or five when
    there are five, and two on phones.

    Data: [{"value", "label", "sub"?, "tone"?}]. tone (danger, warning or success) colours the number, and the
    label says the same thing in words.

        tiles([{"value": 8, "label": "Waiting on", "sub": "4 done, 4 open"}, {"value": 1, "label": "Not recorded"}])
    """
    out = []
    for x in items:
        tone = f' tile--{e(x["tone"])}' if x.get('tone') else ''
        sub = f'<div class="tile__sub">{e(x["sub"])}</div>' if x.get('sub') else ''
        out.append(f'<div class="tile{tone}"><div class="tile__value">{e(x["value"])}</div><div class="tile__label">{e(x["label"])}</div>{sub}</div>')
    five = ' tiles--5' if len(items) == 5 else ''
    return f'<div class="tiles{five}">' + ''.join(out) + '</div>'
