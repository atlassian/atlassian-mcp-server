"""Code: a trace of numbered steps with code chips and excerpts, value pills, a table that stacks on phones,
stacked findings from docs, and change rows. CSS: code.css."""
from .icons import icon
from .links import e, link, text
from .status import lz


def code_chip(c, commit=''):
    """A chip linking a file at the cited lines: "idleTimer.ts · lines 8 to 31", with the path and commit in its
    tooltip. A test chip adds the test's name.

    Data: {"path", "lines": [first, last], "url", "name"?}. name marks a supporting test.

        code_chip({"path": "api/search/params.py", "lines": [12, 30], "url": "#"}, commit='4e91c07')
    """
    first, last = c['lines']
    at = f' at {commit}' if commit else ''
    name = c['path'].rsplit('/', 1)[-1]
    test = f'<span class="smart-link__app"> · test: {e(c["name"])}</span>' if c.get('name') else ''
    return (f'<a class="smart-link code-chip{" code-chip--test" if c.get("name") else ""}" href="{e(c["url"])}" target="_blank" '
            f'rel="noopener" title="{e(c["path"])} · lines {e(first)}-{e(last)}{e(at)}"><span class="smart-link__icon" aria-hidden="true">'
            f'{icon("angle-brackets")}</span><span class="smart-link__title">{e(name)} · lines {e(first)} to {e(last)}</span>{test}'
            f'<span class="visually-hidden"> (opens in a new tab)</span></a>')


def excerpt(lines):
    """A collapsed "Show the code" disclosure: up to 12 lines in monospace with their numbers, an ellipsis row
    between runs that aren't next to each other, scrolling inside its own box.

    Data: [{"n": 18, "code": "export function createIdleTimer() {"}, {"gap": true}, ...]. Cut secrets first.

        excerpt([{"n": 12, "code": "DEFAULT_PAGE_SIZE = 50"}, {"gap": True}, {"n": 28, "code": "if size > MAX:"}])
    """
    rows = '\n'.join('<span class="code-ln" aria-hidden="true"> </span><span class="code-gap">…</span>' if x.get('gap')
                     else f'<span class="code-ln" aria-hidden="true">{e(x["n"])}</span>{e(x["code"])}' for x in lines)
    return (f'<details class="code-excerpt"><summary>{icon("angle-brackets")}<span>Show the code</span></summary>'
            f'<div class="code-box" tabindex="0" role="region" aria-label="Code excerpt"><pre><code>{rows}</code></pre></div></details>')


def value_pill(v):
    """A small pill for a default or a limit: "Default **30 minutes**".

    Data: {"label": "Default", "value": "30 minutes"}.

        value_pill({"label": "Warning shown", "value": "2 minutes before sign-out"})
    """
    return f'<span class="value-pill"><span class="value-pill__label">{e(v["label"])}</span> <span class="value-pill__value">{e(v["value"])}</span></span>'


def trace(steps, commit=''):
    """The trace as a numbered list. Each step has its sentence, its kind lozenge and value pill if any, its code
    chip and any test chip, then the excerpt.

    Data: [{"text": text field, "kind"?: lozenge, "value"?: value pill, "code"?: code chip, "test"?: code chip,
    "excerpt"?: excerpt lines}].

        trace([{"text": "The API falls back to the default.", "value": {"label": "Default", "value": "50 invoices"},
                "code": {"path": "api/search/params.py", "lines": [12, 30], "url": "#"}}], commit='4e91c07')
    """
    out = []
    for i, s in enumerate(steps, 1):
        meta = ''.join(x for x in (lz(s.get('kind')), value_pill(s['value']) if s.get('value') else '') if x)
        chips = ''.join(code_chip(s[k], commit) for k in ('code', 'test') if s.get(k))
        out.append(f'<li class="trace-step"><span class="trace-step__num" aria-hidden="true">{i}</span><div class="trace-step__body">'
                   f'<p class="trace-step__text"><span class="visually-hidden">Step {i}. </span>{text(s)}</p>'
                   + (f'<div class="trace-step__meta">{meta}</div>' if meta else '')
                   + (f'<div class="trace-step__chips">{chips}</div>' if chips else '')
                   + (excerpt(s['excerpt']) if s.get('excerpt') else '') + '</div></li>')
    return '<ol class="trace">' + ''.join(out) + '</ol>'


def stack_table(headers, rows):
    """A table whose rows become stacked blocks at 600px and narrower, each cell under its label, so a long
    setting name keeps the full width. Cells are text fields, or {"text", "sub"} with a small line under it.

        stack_table(['Setting or flag', 'What it changes', 'Who controls it'],
                    [[{"text": "`pageSize`", "sub": "Request parameter"}, "How many invoices a page holds", "The caller"]])
    """
    def cell(h, c):
        sub = f'<div class="stack-table__sub">{text(c, "sub")}</div>' if isinstance(c, dict) and c.get('sub') else ''
        return f'<td data-label="{e(h)}">{text(c)}{sub}</td>'
    head = ''.join(f'<th scope="col">{e(h)}</th>' for h in headers)
    body = ''.join('<tr>' + ''.join(cell(h, c) for h, c in zip(headers, r)) + '</tr>' for r in rows)
    return f'<div class="stack-table__wrap"><table class="stack-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def doc_rows(items):
    """Findings from docs and chat as stacked items: the smart link on its own line, the claim, then its lozenge
    and what it was checked against, so long titles don't squeeze the claim.

    Data: [{"link": link, "claim": text field, "verdict": lozenge, "meta": "Runbook · Updated Aug 19, 2026"}].

        doc_rows([{"link": {"title": "Ledger search API reference", "url": "#", "icon": "page"},
                   "claim": "Says the default page size is 100.", "verdict": {"text": "Disagrees", "tone": "danger"}}])
    """
    return '<ul class="list">' + ''.join(
        f'<li class="doc-row"><div>{link(x["link"])}</div><div class="doc-row__claim">{text(x, "claim")}</div>'
        f'<div class="doc-row__meta">{lz(x.get("verdict"))}{f"""<span>{e(x["meta"])}</span>""" if x.get("meta") else ""}</div></li>'
        for x in items) + '</ul>'


def change_rows(items):
    """Recent changes: the version and date in a column, then the line and its link.

    Data: [{"version"?, "date", "text": text field, "link"?}].

        change_rows([{"version": "2.12", "date": "Aug 4, 2026", "text": "Lower the default page size to 50.",
                      "link": {"title": "ledger-api: smaller default search pages", "url": "#", "icon": "pull-request"}}])
    """
    return '<ul class="list">' + ''.join(
        f'<li class="change-row"><div class="change-row__when">{f"""<span class="change-row__version">{e(x["version"])}</span>""" if x.get("version") else ""}'
        f'<span>{e(x["date"])}</span></div><div>{text(x)}{" " + link(x["link"]) if x.get("link") else ""}</div></li>'
        for x in items) + '</ul>'
