"""The avatar group: ADS AvatarGroup's stack at size small (@atlaskit/avatar-group 14.4.6), with initials, opening a
panel of every person. CSS: avatar_group.css.
"""
import zlib

from .glyphs import glyph
from .hover_panel import hover_panel, panel_row
from .page import e

AVATAR_HUES = ('blue', 'teal', 'green', 'orange', 'purple', 'magenta')


def avatar_hue(name):
    """The ADS accent hue of a person's initials avatar, picked by a hash of their name, so they're the same colour
    on every page: blue, teal, green, orange, purple or magenta.

        avatar_hue('Priya Nair')  # "teal"
    """
    return AVATAR_HUES[zlib.crc32(name.encode()) % len(AVATAR_HUES)]


def initials(name):
    """A 24px initials avatar, 32px in a panel row, from the first letters of the first two words of the name, in
    the hue the kit's avatar_hue picks for the name, so a person is the same colour on every page.

        initials('Riley Novak')  # "RN"
    """
    return f'<span class="initials initials--{avatar_hue(name)}" aria-hidden="true">{e("".join(w[0] for w in name.split()[:2]).upper())}</span>'


def avatar_group(people, label, heading, id, extra=''):
    """Up to 5 initials avatars, or 4 and "+N", in a button named by label, opening the panel id: the heading,
    then every person with their role and status, then the extra line. Nothing with no people.

    Data: [{"name", "role"?, "status"?: {"text", "glyph"?}}]. A status's glyph is drawn 12px before its text.
    extra is plain text, such as "2 people outside the company".

        avatar_group([{"name": "Riley Novak", "role": "Product lead", "status": {"text": "Approved", "glyph": "check-circle"}}],
                     'Reviewers, 1', '1 reviewer', 'reviewers')
    """
    if not people:
        return ''
    shown = people if len(people) <= 5 else people[:4]
    more = f'<span class="avatar-group__more">+{len(people) - 4}</span>' if len(people) > 5 else ''
    group = f'<span class="avatar-group">{"".join(initials(p["name"]) for p in shown)}{more}</span>'
    rows = ''
    for p in people:
        s = p.get('status')
        status = f'<span class="avatar-group__status">{glyph(s["glyph"]) if s.get("glyph") else ""}{e(s["text"])}</span>' if s else ''
        rows += panel_row(initials(p['name']), e(p['name']), *(x for x in (e(p.get('role')), status) if x))
    if extra:
        rows += f'<li class="hover-panel__row hover-panel__line">{e(extra)}</li>'
    return hover_panel(group, label, heading, rows, id)
