"""Text fields and smart links. CSS: links.css."""
import html
import re

from .icons import icon
from .status import lz

LINK_ICON_CLASS = {'page': 'page', 'whiteboard': 'whiteboard', 'folder': 'folder-closed', 'task': 'task', 'epic': 'epic',
                   'project': 'project', 'goal': 'goal', 'video': 'video', 'lightbulb': 'task'}


def e(s):
    """Escape a value for HTML text or an attribute. None is empty.

        e('Fix <b> tags')  # "Fix &lt;b&gt; tags"
    """
    return html.escape(str(s if s is not None else ''), quote=True)


def link(l):
    """A smart link. With no URL, it renders as plain text that says no link is available.

    Data: {"title", "url", "icon", "app"?, "found"?, "status"?, "note"?}. `app` names a third-party app after
    the title, `found: true` marks it Found by search, `status` is a lozenge after the title, and `note` is
    subtle text inside the chip after the title, such as a recording's length or "No access".

        link({"title": "SRCH-412 Split facet fields", "url": "#", "icon": "task",
              "status": {"text": "In review", "tone": "information"}})
    """
    ic = l.get('icon', 'globe')
    cls = LINK_ICON_CLASS.get(ic, '')
    app = f'<span class="smart-link__app"> · {e(l["app"])}</span>' if l.get('app') else ''
    found = '<span class="found-label">Found by search</span>' if l.get('found') else ''
    note = f'<span class="smart-link__note">{e(l["note"])}</span>' if l.get('note') else ''
    status = lz(l['status']).replace('class="lozenge', 'class="smart-link__status lozenge') if l.get('status') else ''
    inner = (f'<span class="smart-link__icon{" smart-link__icon--" + cls if cls else ""}" aria-hidden="true">'
             f'{icon(ic)}</span><span class="smart-link__title">{e(l["title"])}</span>{app}{note}{status}{found}')
    if not l.get('url'):
        return f'<span class="plain-ref">{inner}<span class="fine"> (no link available)</span></span>'
    return (f'<a class="smart-link{" smart-link--found" if l.get("found") else ""}" href="{e(l["url"])}" target="_blank" '
            f'rel="noopener" title="{e(l["title"])}">{inner}<span class="visually-hidden"> (opens in a new tab)</span></a>')


def placeholder(label, ic):
    """A muted, dashed chip that stands in for a missing object, such as "No notes". It isn't a link.

        placeholder('No recording', 'video')
    """
    return f'<span class="chip-placeholder">{icon(ic)}<span>{e(label)}</span></span>'


def links(x):
    """One smart link or a list of them, as chips separated by spaces. Nothing for an empty value.

        links([{"title": "Search cutover runbook", "url": "#", "icon": "page"}])
    """
    if not x:
        return ''
    return ' '.join(link(l) for l in (x if isinstance(x, list) else [x]))


def inline_code(escaped):
    """Escaped text with each `backticked` run shown as inline code.

        inline_code(e('Set `pageSize` to 200'))
    """
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)


def text(item, key='text'):
    """A text field, escaped, with its {n} placeholders replaced by smart links.

    Data: a plain string, or {"text": "Approved in {0}", "links": [link, ...]}. A single "link" counts as
    links[0]. Text in backticks shows as code. key reads another field of the item.

        text({"text": "Raised in {0}", "links": [{"title": "#search", "url": "#", "icon": "hashtag"}]})
    """
    if isinstance(item, str):
        return inline_code(e(item))
    t = inline_code(e(item.get(key, '')))
    ls = item.get('links') or ([item['link']] if item.get('link') else [])
    for i, l in enumerate(ls):
        t = t.replace('{' + str(i) + '}', link(l))
    return t


def texts(x):
    """One text field or a list of them, as a list, so a lone string isn't read one character at a time. An
    empty list for an empty value.

        texts('The cutover moved to Nov 16.')  # ['The cutover moved to Nov 16.']
    """
    if not x:
        return []
    return [x] if isinstance(x, (str, dict)) else x
