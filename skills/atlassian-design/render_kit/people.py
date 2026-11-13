"""People: initials avatars, person rows and the attendee grid. CSS: people.css."""
from .evidence import evidence
from .links import e


def avatar(name, small=False):
    """A 32px initials avatar, or 24px with small, from the first letters of the first two words of the name.

        avatar('Priya Nair')  # "PN"
    """
    cls = 'avatar-initials avatar-initials--small' if small else 'avatar-initials'
    return f'<span class="{cls}" aria-hidden="true">{e("".join(w[0] for w in name.split()[:2]).upper())}</span>'


def person(p, first=False):
    """A person row for a list, with their evidence lines. first adds "Try first".

    Data: {"name", "team"?, "role"?, "lastWorked"?, "evidence": [evidence items]}. role is a tag after the name.

        person({"name": "Priya Nair", "team": "Team Ledger", "role": "Named contact", "evidence": [...]}, first=True)
    """
    tag = f'<span class="tag role-tag">{e(p["role"])}</span>' if p.get('role') else ''
    try_first = '<span class="person-row__first">Try first</span>' if first else ''
    team = f'<div class="person-row__team">{e(p["team"])}</div>' if p.get('team') else ''
    last = f'<div class="fine">Last worked on this {e(p["lastWorked"])}</div>' if p.get('lastWorked') else ''
    return (f'<li class="person-row">{avatar(p["name"])}<div><div class="person-row__name">{e(p["name"])}{tag}{try_first}</div>'
            f'{team}{last}{evidence(p["evidence"])}</div></li>')


def attendees(people, guests=''):
    """Attendees as initials avatars in a two-column grid (one column on phones), then the guests line.

    Data: [{"name", "role"?, "response"?, "optional"?, "you"?, "organiser"?}]. response is "Accepted",
    "Tentative", "Declined" or "Not responded", left out without a calendar. you and organiser add a tag after
    the name. guests is plain text, such as "2 external guests".

        attendees([{"name": "Marco Ruiz", "role": "Engineering manager", "response": "Accepted", "organiser": True}],
                  guests='1 external guest')
    """
    items = []
    for p in people:
        tags = ''.join(f'<span class="tag">{t}</span>' for t, on in (('You', p.get('you')), ('Organiser', p.get('organiser'))) if on)
        role = f'<div class="attendee__role">{e(p["role"])}</div>' if p.get('role') else ''
        status = ' · '.join(x for x in (p.get('response'), 'Optional' if p.get('optional') else '') if x)
        status = f'<div class="attendee__response">{e(status)}</div>' if status else ''
        items.append(f'<li class="attendee">{avatar(p["name"])}<div><div class="attendee__name">{e(p["name"])}{tags}</div>{role}{status}</div></li>')
    more = f'<p class="fine">{e(guests)}</p>' if guests else ''
    return f'<ul class="attendee-grid">{"".join(items)}</ul>{more}'
