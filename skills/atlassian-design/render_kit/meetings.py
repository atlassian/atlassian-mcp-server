"""Meetings: the overview of an invite and its prep summary, and rows of earlier occurrences. CSS: meetings.css."""
from .icons import icon
from .links import e, link, placeholder, text, texts


def overview(invite, summary, generated_from, join_label=''):
    """A meeting overview's two blocks, divided by a line: the invite's description, quoted as written, and the
    prep summary.

    Data: invite is {"text", "recordedIn"?}, or None when the invite has no description. summary is a list of
    text fields, and generated_from names what it came from. With join_label, the invite block says joining
    details were removed and points to that button.

        overview({"text": "Weekly go/no-go for the search cutover."}, ["This call decides the date."],
                 "the Oct 22 notes, Google Calendar and Jira", join_label='Join Google Meet')
    """
    if invite:
        notes = []
        if join_label:
            notes.append(f'Joining details removed. Use {join_label} above. It may ask for the passcode in your calendar invite.')
        if invite.get('recordedIn'):
            notes.append(f'This meeting is recorded in {invite["recordedIn"]}.')
        quoted = f'<blockquote class="invite-quote">{e(invite["text"])}</blockquote>'
        quoted += f'<p class="fine">{e(" ".join(notes))}</p>' if notes else ''
    else:
        quoted = '<p class="fine">The invite has no description.</p>'
    paras = ''.join(f'<p>{text(s)}</p>' for s in texts(summary))
    return (f'<div class="overview-block"><div class="overview-label">From the invite</div>{quoted}</div>'
            f'<div class="overview-block"><div class="overview-label">{icon("sparkle", "ic-disc")}Prep summary</div>'
            f'<div class="summary">{paras}</div>'
            f'<p class="fine">Generated from {e(generated_from)}. Check it before sharing.</p></div>')


def occurrences(rows):
    """Earlier occurrences, one line each, newest first: the date in a fixed column with the relative time in its
    tooltip, then the notes and the recording as smart links. A missing one is a dashed placeholder chip.

    Data: [{"date", "ago"?, "title"?, "notes"?, "recording"?}]. title is only for a related meeting, shown
    after the date. notes and recording are links: put a recording's length, or "No access", in its "note".

        occurrences([{"date": "Thu, Oct 22", "ago": "Last week", "notes": {"title": "Go/no-go, Oct 22", "url": "#",
                      "icon": "page"}, "recording": {"title": "Go/no-go", "url": "#", "icon": "video", "note": "41 min"}}])
    """
    out = []
    for r in rows:
        tip = f' title="{e(r["ago"])}"' if r.get('ago') else ''
        title = f'<span class="occurrence__title"> · {e(r["title"])}</span>' if r.get('title') else ''
        notes = link(r['notes']) if r.get('notes') else placeholder('No notes', 'page')
        rec = link(r['recording']) if r.get('recording') else placeholder('No recording', 'video')
        out.append(f'<li class="occurrence"><div class="occurrence__date"><span{tip}>{e(r["date"])}</span>{title}</div>'
                   f'<div class="occurrence__links">{notes} {rec}</div></li>')
    return '<ul class="occurrences">' + ''.join(out) + '</ul>'
