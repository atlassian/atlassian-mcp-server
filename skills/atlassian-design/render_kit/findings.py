"""Finding rows, source lines and excerpts. CSS: findings.css."""
from .layout import empty
from .links import e, link, links, text, texts
from .status import lz


def source_line(src, when='', label='Source: '):
    """Small subtlest text with the source smart links and a date or age. Nothing when both are empty.

        source_line({"title": "Search rollback plan", "url": "#", "icon": "page"}, 'Oct 22')
    """
    parts = [x for x in [(label if src else '') + links(src), e(when)] if x]
    return f'<div class="src">{" · ".join(parts)}</div>' if parts else ''


def quote(x):
    """An excerpt under a row, or nothing.

    Data: {"quote": "...", "quoteFrom": "Slack"?}.

        quote({"quote": "We still need someone to own asset caching.", "quoteFrom": "Slack"})
    """
    if not x.get('quote'):
        return ''
    frm = f'<span class="fine">Excerpt from {e(x["quoteFrom"])}</span>' if x.get('quoteFrom') else ''
    return f'<blockquote class="excerpt">{e(x["quote"])}{frm}</blockquote>'


def row(x, default_lz=None, source_key='source', when_key='when', label='Source: '):
    """A finding row: the lozenge in a fixed left column, the sentence, any excerpt, then the source line.

    Data: {"type": lozenge or [lozenges], "text": text field, "links"?, "contact"?, "source": link or [links],
    "when"?, "quote"?, "quoteFrom"?}. Several lozenges stack in the left column. contact is a text field shown
    under the sentence ("Contact: Riley Novak, Senior engineer"). default_lz is used when the row has no type.

        row({"type": {"text": "Overdue", "tone": "danger"}, "text": "Approve the schema change",
             "source": {"title": "SRCH-412 Split facet fields", "url": "#", "icon": "task"}, "when": "Oct 14"})
    """
    t = x.get('type', default_lz)
    types = f'<span class="lrow__types">{"".join(lz(y) for y in t)}</span>' if isinstance(t, list) else f'<span>{lz(t)}</span>'
    contact = f'<div class="row-contact">{text(x, "contact")}</div>' if x.get('contact') else ''
    return (f'<li class="lrow">{types}<div>{text(x)}{quote(x)}{contact}'
            f'{source_line(x.get(source_key), x.get(when_key, ""), label)}</div></li>')


def numbered(items):
    """A numbered list of one-sentence items in medium weight, each with where it came from in small subtlest text.

    Data: [{"text": text field, "from": "From Sep 24 sync notes"}]. "from" is plain text, not a link.

        numbered([{"text": "Name an owner for the restore step.", "from": "From the rollback plan"}])
    """
    return '<ol class="numbered">' + ''.join(
        f'<li><div class="numbered__text">{text(x)}</div>{f"""<div class="src">{e(x["from"])}</div>""" if x.get("from") else ""}</li>'
        for x in items) + '</ol>'


def link_rows(items, meta=''):
    """One smart link per row, with a line of small subtlest text under it. meta is the line for a row without one.

    Data: [{"link": link, "meta": "Confluence · Marco Ruiz · updated yesterday"}].

        link_rows([{"link": {"title": "Search cutover runbook", "url": "#", "icon": "page"}, "meta": "Confluence"}])
    """
    def line(x):
        m = x.get('meta') or meta
        return f'<div class="src">{e(m)}</div>' if m else ''
    return '<ul class="list">' + ''.join(f'<li>{link(x["link"])}{line(x)}</li>' for x in items) + '</ul>'


def checklist(items):
    """A list of native checkboxes, each labelled with a text field. Ticks aren't saved.

        checklist(['Has a site admin set an idle timeout?', 'Is the `beacon.session.activity-heartbeat` flag on?'])
    """
    return '<ul class="checklist">' + ''.join(
        f'<li><input type="checkbox" id="chk-{i}"><label for="chk-{i}">{text(x)}</label></li>' for i, x in enumerate(texts(items))) + '</ul>'


def labelled_rows(items):
    """Rows with a label in a fixed left column, then a smart link or a text field, with where it came from under it.

    Data: [{"label", "link"? or "text"?, "from"?: text field}].

        labelled_rows([{"label": "Team", "link": {"title": "Team Ledger", "url": "#", "icon": "teams"},
                        "from": "Declared in compass.yml"}])
    """
    def value(x):
        main = link(x['link']) if x.get('link') else text(x)
        return main + (f'<div class="src">{text(x, "from")}</div>' if x.get('from') else '')
    return '<ul class="list">' + ''.join(f'<li class="labelled-row"><span class="labelled-row__label">{e(x["label"])}</span><div>{value(x)}</div></li>'
                                         for x in items) + '</ul>'


def text_rows(items):
    """A plain list of text fields, one per row, such as reasons in a record's words with their source chips.

        text_rows([{"text": "“An in-place upgrade needs the cluster offline for 2 days.” {0}", "links": [link]}])
    """
    return '<ul class="list">' + ''.join(f'<li>{text(x)}</li>' for x in texts(items)) + '</ul>'


def rows(items, empty_msg='', **kw):
    """A list of finding rows, or the empty message when there are none. Keyword arguments go to row().

        rows(d.get('needsYou'), empty_msg='Nothing is waiting on you.')
    """
    if not items:
        return empty(empty_msg) if empty_msg else ''
    return '<ul class="list">' + ''.join(row(x, **kw) for x in items) + '</ul>'
