"""Rows: label rows, the numbered list and plain rows, each divided by lines. CSS: rows.css."""
from .frame import paragraphs, small_text
from .links import links, text
from .page import e


def label_rows(items):
    """Rows with a label in a 150px column, then the text with its links 8px below, then any note in small text
    8px below that. On phones the label stacks above the content.

    Data: [{"label", "title"?, "text"?, "links"?, "source"?: link or [links], "note"?}]. text and links are the
    row's text field, as in the kit's rows, or text holds a whole text field. A row with no text holds only its
    links. title sits above the text in medium weight, for a related item's name. note is a text field, such as
    where the row came from.

        label_rows([{"label": "Key risk", "text": "Design sign-off is blocking the search migration.",
                     "source": {"title": "PLAT-221 Design sign-off", "url": "#", "icon": "task"}}])
    """
    def row(x):
        title = f'<div class="label-row__title">{e(x["title"])}</div>' if x.get('title') else ''
        return (f'<li class="label-row"><span class="label-row__label">{e(x["label"])}</span>'
                f'<div>{title}{paragraphs(x) if x.get("text") else ""}{links(x.get("source"))}'
                f'{small_text(x["note"]) if x.get("note") else ""}</div></li>')
    return '<ul class="row-list label-rows">' + ''.join(row(x) for x in items) + '</ul>'


def numbered_list(items):
    """A numbered list, each number in a 20px circle, then the item's text.

    Data: [{"text": text field}].

        numbered_list([{"text": "Ask who owns design sign-off, and by when."}])
    """
    return '<ol class="numbered-list">' + ''.join(
        f'<li class="numbered-list__item"><span class="numbered-list__number">{i}</span><span>{text(x)}</span></li>'
        for i, x in enumerate(items, 1)) + '</ol>'


def rows(items):
    """One row per item: its text, then its links 8px below.

    Data: [{"text": text field, "links": link or [links]}].

        rows([{"text": "It sets the beta window.", "links": {"title": "Q4 launch plan", "url": "#", "icon": "page"}}])
    """
    return '<ul class="row-list">' + ''.join(f'<li>{paragraphs(x["text"])}{links(x["links"])}</li>' for x in items) + '</ul>'
