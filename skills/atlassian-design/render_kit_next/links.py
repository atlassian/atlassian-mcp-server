"""Smart links as frame 6:2977 draws them, with their app's logo, a row of them, and text fields with links in
them. CSS: links.css."""
from .glyphs import glyph
from .logos import LOGOS, logo
from .lozenge import lozenge
from .page import e, inline_code

# The app an Atlassian object comes from, by its data's icon name, for a link whose data names no app.
APPS = {'page': 'Confluence', 'whiteboard': 'Confluence', 'folder': 'Confluence', 'task': 'Jira', 'epic': 'Jira',
        'goal': 'Goals', 'project': 'Projects', 'video': 'Loom'}
# A link's icon when its app has no logo, as @atlaskit/object draws it: the glyph and its tone. Any other name
# draws its own glyph in icon.subtle.
OBJECTS = {'page': ('page', 'blue'), 'task': ('task', 'blue'), 'whiteboard': ('whiteboard', 'teal'),
           'epic': ('epic', 'purple'), 'lightbulb': ('lightbulb', 'yellow'), 'pull-request': ('pull-request', 'green'),
           'flag': ('incident', 'red'), 'goal': ('goal', 'teal'), 'project': ('project', 'blue'),
           'folder': ('folder-closed', 'blue'), 'doc': ('page', ''), 'repo': ('angle-brackets', '')}


def app(l):
    """A link's app: the one its data names, or else the Atlassian app its object comes from.

        app({"title": "Q4 launch plan", "icon": "page"})  # 'Confluence'
    """
    return l.get('app') or APPS.get(l.get('icon'))


def icon(l):
    """A link's icon: its app's logo, or its object glyph when the app has no logo.

        icon({"title": "Beta review", "icon": "calendar", "app": "Google Calendar"})
    """
    if app(l) in LOGOS:
        return logo(app(l))
    return glyph(*OBJECTS.get(l.get('icon'), (l.get('icon', 'globe'), '')))


def status(s):
    """A status lozenge from data, such as a link's status or a page's verdict: {"text", "tone"?}, or a plain string
    for a neutral one.

        status({"text": "Blocked", "tone": "warning"})
    """
    s = {'text': s} if isinstance(s, str) else s
    return lozenge(s['text'], s.get('tone', ''))


def link(l):
    """A smart link: the app's logo, the title and any status, opening in a new tab. The app's name is in the
    accessible name, not shown. With no URL, it isn't a link and says so.

    Data: {"title", "url"?, "icon"?, "app"?, "status"?}. icon is the object type, app a name in LOGOS, and status a
    lozenge.

        link({"title": "PLAT-221 Design sign-off", "url": "#", "icon": "task", "status": {"text": "Blocked", "tone": "warning"}})
    """
    name = f'<span class="visually-hidden"> {e(app(l))}</span>' if app(l) else ''
    inner = (f'{icon(l)}<span class="inline-card__title">{e(l["title"])}{name}</span>'
             + (status(l['status']) if l.get('status') else ''))
    if not l.get('url'):
        return f'<span class="inline-card inline-card--unlinked">{inner}<span class="inline-card__none"> (no link available)</span></span>'
    return (f'<a class="inline-card" href="{e(l["url"])}" target="_blank" rel="noopener" title="{e(l["title"])}">{inner}'
            '<span class="visually-hidden"> (opens in a new tab)</span></a>')


def links(x):
    """One smart link or a list of them, in a row that wraps, 4px apart. Nothing for an empty value.

        links([{"title": "Q4 launch plan", "url": "#", "icon": "page"}])
    """
    ls = x if isinstance(x, list) else [x] if x else []
    return f'<div class="link-row">{"".join(f"<span>{link(l)}</span>" for l in ls)}</div>' if ls else ''


def text(item, key='text'):
    """A text field, escaped, with its {n} placeholders replaced by smart links, as the kit's text() does. When the
    item's key holds a whole text field, that field is used.

        text({"text": "Raised in {0}", "links": [{"title": "#search", "url": "#", "icon": "hashtag", "app": "Slack"}]})
    """
    if isinstance(item, str):
        return inline_code(e(item))
    if isinstance(item.get(key), dict):
        return text(item[key])
    t = inline_code(e(item.get(key, '')))
    for i, l in enumerate(item.get('links') or ([item['link']] if item.get('link') else [])):
        t = t.replace('{' + str(i) + '}', link(l))
    return t
