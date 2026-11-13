"""The page frame: the mockup badge, the header, section cards, paragraphs, small text, the footer and the sources
footer. CSS: frame.css."""
from .app_stack import app_stack
from .glyphs import glyph
from .links import text
from .lozenge import lozenge
from .page import e, texts
from .skill_tag import skill_tag
from .tag import tag


def mockup_badge():
    """The sample data note: an Example data lozenge in the page's top right corner. Put it first in the body.

        body = mockup_badge() + body
    """
    return f'<div class="mockup-badge" role="note">{lozenge("Example data", "discovery", glyph("information-circle"))}</div>'


def header(skill, title, meta, aside=''):
    """The page header: the skill tag, the page's only h1, then the meta line, a text field, with the aside HTML at
    its right, centred on it. On phones the aside wraps below the meta line.

        header('meeting-prep', 'Platform roadmap sync', 'Thursday, October 8 · 10:00 to 10:45 AM PT', aside)
    """
    return (f'<header class="page-header">{skill_tag(skill)}<h1 class="page-title">{e(title)}</h1>'
            f'<div class="page-header__row"><p class="page-header__meta">{text(meta)}</p>{aside}</div></header>')


def section(title, body):
    """A section card: its title, then the body HTML.

        section('Overview', paragraphs(d['summary']))
    """
    return f'<section class="section-card"><h2 class="section-card__title">{e(title)}</h2>{body}</section>'


def paragraphs(items):
    """Text fields as paragraphs of body-large subtle text, 16px apart, across the card.

        paragraphs(['The search migration slipped a week.'])
    """
    return ''.join(f'<p class="paragraph">{text(x)}</p>' for x in texts(items))


def small_text(item):
    """A text field as a line of small subtlest text across the card, 16px under what's above it, for a note such as
    how the content was made.

        small_text('Generated from Code search, Bitbucket and Slack. Check it before relying on it.')
    """
    return f'<p class="small-text">{text(item)}</p>'


def footer(created, apps):
    """The footer: "Created" and when, then the AI note, with the app stack of the connections used at the right.

        footer('Oct 7, 4:12 PM PT', ['Google Calendar', 'Confluence', 'Jira'])
    """
    return (f'<footer class="page-footer"><p class="page-footer__created">Created {e(created)}. Uses AI. Verify results.</p>'
            f'{app_stack(apps)}</footer>')


def sources_footer(f):
    """The sources footer: a tag for each app searched, then a list of lines on
    what was read and how.

    Data: {"tags": [{"text"}], "lines": [text fields]}.

        sources_footer({"tags": [{"text": "Jira"}, {"text": "No results from Zoom"}],
                        "lines": ["Prepared just now, Oct 27, 9:05 AM PT."]})
    """
    tags = ''.join(tag(t['text']) for t in f.get('tags', []))
    lines = ''.join(f'<li>{text(x)}</li>' for x in texts(f.get('lines')))
    return (f'<footer class="sources-footer">{f"""<div class="sources-footer__tags">{tags}</div>""" if tags else ""}'
            f'{f"""<ul class="sources-footer__lines">{lines}</ul>""" if lines else ""}</footer>')
