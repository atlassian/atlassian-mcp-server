"""Page layout: the header, cards, section messages, the footer and the copy button. CSS: layout.css."""
from .icons import icon
from .links import e, text, texts


def header(eyebrow, title, meta, counts='', badge='', lede=''):
    """The page header: the eyebrow, the page's only h1 with its badge on the right, then the meta line, with its
    counts at the right end, then the lede.

    meta, counts and badge are HTML. Build each meta item with meta_item. badge holds the page's verdict or the
    anchor's own status, as one or more lozenges. counts holds count lozenges, or the page's one action or live
    state. lede is a text field: one line of small subtlest text on how the page was made.

        header('Catch-up', 'Search migration', meta_item('calendar', 'Oct 12 to Oct 23'),
               counts=lz({"text": "3 need you", "tone": "warning"}))
    """
    m = f'<div class="meta">{meta}</div>' if meta else ''
    if counts:
        m = f'<div class="meta-row">{m}<div class="counts">{counts}</div></div>'
    h1 = f'<div class="title-row"><h1>{e(title)}</h1><div class="title-row__badge">{badge}</div></div>' if badge else f'<h1>{e(title)}</h1>'
    lede = f'<div class="fine lede">{text(lede)}</div>' if lede else ''
    return f'<header><div class="eyebrow">{e(eyebrow)}</div>{h1}{m}{lede}</header>'


def meta_item(ic, item, tip=''):
    """One item of a header's meta line: an optional icon, then a text field. tip is a tooltip.

        meta_item('calendar', 'Thu, Oct 29, 2:00 to 2:45 PM PT, in 2 days')
        meta_item(None, {"text": "Atlassian project · {0}", "link": link})
    """
    title = f' title="{e(tip)}"' if tip else ''
    return f'<span class="mi"{title}>{icon(ic) if ic else ""}{text(item)}</span>'


def link_button(label, url, ic=None):
    """A link styled as a default (outlined) button, for a page's one action that opens somewhere else, such as
    joining a meeting. Use smart links for everything else.

        link_button('Join Google Meet', 'https://meet.google.com/abc-defg-hij', 'video')
    """
    return (f'<a class="btn" href="{e(url)}" target="_blank" rel="noopener">{icon(ic) if ic else ""}<span>{e(label)}</span>'
            f'<span class="visually-hidden"> (opens in a new tab)</span></a>')


def card(ic, title, body, extra='', ic_cls='ic-subtle'):
    """A flat section card with an icon-led heading. body is HTML, and extra adds attributes to the section.

        card('flag', 'Needs you', rows(items, empty_msg='Nothing is waiting on you.'))
    """
    return f'<section class="card"{extra}><h2 class="card-h">{icon(ic, ic_cls)}{e(title)}</h2>{body}</section>'


def summary_card(title, paras, generated_from, check='acting on', extra='', lead='', more=''):
    """The AI summary card: any lead HTML (such as metric tiles), paragraphs as text fields, any more HTML, the
    "Generated from" line, then any extra HTML.

        summary_card('While you were away', ['The cutover moved to Nov 16.'], 'Jira, Confluence and Slack')
    """
    return card('sparkle', title, lead + '<div class="summary">' + ''.join(f'<p>{text(s)}</p>' for s in texts(paras))
                + f'</div>{more}<p class="fine">Generated from {e(generated_from)}. Check it before {check} it.</p>' + extra,
                ic_cls='ic-disc')


def tabs(items, label):
    """Tabs: the tab list, then one panel per tab, with the first selected. The page script switches them, with
    clicks and the arrow keys, and keeps the choice in the URL hash, and print shows every panel. label names the
    tab list for screen readers.

    Data: [{"key", "label", "icon", "count"?, "body", "card"?}]. body is HTML, and count shows after the label when
    given. With card, the panel is itself a card, for a tab holding one section. Without it, the panel holds cards.

        tabs([{"key": "read", "label": "Read first", "icon": "book", "count": 4, "body": card('book', 'Read first', rows)},
              {"key": "trace", "label": "Trace", "icon": "task", "body": trace, "card": True}], 'Guide sections')
    """
    tab_list = ''.join(
        f'<button role="tab" id="t-{e(x["key"])}" aria-controls="p-{e(x["key"])}" aria-selected="{"true" if i == 0 else "false"}" '
        f'tabindex="{0 if i == 0 else -1}">{icon(x["icon"])}{e(x["label"])}'
        + (f' <span class="count">{e(x["count"])}</span>' if x.get('count') is not None else '') + '</button>'
        for i, x in enumerate(items))
    panels = ''.join(f'<div class="panel{" card" if x.get("card") else ""}" role="tabpanel" id="p-{e(x["key"])}" '
                     f'aria-labelledby="t-{e(x["key"])}" tabindex="0">{x["body"]}</div>' for x in items)
    return f'<nav class="tabs-wrap" aria-label="{e(label)}"><div class="tabs" role="tablist">{tab_list}</div></nav>{panels}'


def empty(msg):
    """A line of small subtlest text, for a section with nothing in it.

        empty('No decisions you missed in this window.')
    """
    return f'<p class="fine">{e(msg)}</p>'


def note(item, ic='info', tone='', title='', after=''):
    """A section message holding a text field, with an optional title, and after it an optional text field in
    small text. tone is warning, danger, success, information or discovery, for the section message of that kind.

        note({"text": "{0} says the limit is 100.", "links": [link]}, ic='warning', tone='warning',
             title='A support article disagrees with the code')
    """
    cls = f' section-msg--{e({"danger": "error"}.get(tone, tone))}' if tone else ''
    head = f'<h3>{e(title)}</h3>' if title else ''
    tail = f'<p class="fine">{text(after)}</p>' if after else ''
    return f'<div class="section-msg{cls} notice">{icon(ic)}<div>{head}{text(item)}{tail}</div></div>'


def copy_btn(target, label='Copy', cls='btn btn--compact', fallback=False):
    """A copy button. target is an element id, or the text itself. With fallback, the text is shown and selected
    if the clipboard is blocked.

        copy_btn('notes-md', 'Copy as Markdown')
    """
    b = f'<button class="{cls}" type="button" data-copy="{e(target)}">{icon("copy")}<span>{e(label)}</span></button>'
    return b + (f'<code class="copy-fallback" hidden>{e(target)}</code>' if fallback else '')


def footer(f):
    """The sources footer.

    Data: {"tags": [{"text", "muted"?}], "lines": [text fields]}. A muted tag is for an app with no results.

        footer({"tags": [{"text": "Jira"}, {"text": "No results from Zoom", "muted": True}],
                "lines": ["Prepared just now, Oct 27, 9:05 AM PT"]})
    """
    tags = ''.join(f'<span class="tag{" tag--muted" if t.get("muted") else ""}">{e(t["text"])}</span>' for t in f.get('tags', []))
    return f'<footer><div class="tags">{tags}</div><ul>{"".join("<li>" + text(x) + "</li>" for x in texts(f.get("lines")))}</ul></footer>'
