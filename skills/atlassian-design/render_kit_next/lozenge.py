"""Lozenges like the new @atlaskit/lozenge 17.0.6, for a link's status and the page's Example data badge.
CSS: lozenge.css."""
from .page import e

TONES = ('success', 'warning', 'danger', 'information', 'discovery')


def lozenge(text, tone='', icon=''):
    """A lozenge: 20px, a 1px border in its tone's subtle border colour, body-small regular, with the icon HTML 4px
    before the text. An unknown tone is neutral.

        lozenge('Blocked', 'warning')
        lozenge('Example data', 'discovery', glyph('information-circle'))
    """
    cls = f'status-lozenge status-lozenge--{tone}' if tone in TONES else 'status-lozenge'
    return f'<span class="{cls}">{icon}{e(text)}</span>'
