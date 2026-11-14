"""Icons: 16x16 line icons in the ADS style, used through one inline sprite per page."""
import re

ICONS = {
    'page': '<path d="M4 1.5h5.5L13 5v9.5H4zM9.5 1.5V5H13"/>',
    'doc': '<path d="M4 1.5h5.5L13 5v9.5H4zM9.5 1.5V5H13M6 8.5h4M6 11h4"/>',
    'whiteboard': '<rect x="1.5" y="2.5" width="13" height="9" rx="1"/><path d="M5 14l1.5-2.5M11 14l-1.5-2.5M4.5 8l2-2 2 1.5 3-3"/>',
    'folder': '<path d="M1.5 4a1 1 0 0 1 1-1h3.5l1.5 1.5h6a1 1 0 0 1 1 1V12a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1z"/>',
    'task': '<rect x="2.5" y="2.5" width="11" height="11" rx="2"/><path d="M5.5 8l1.8 1.8 3.2-3.6"/>',
    'epic': '<path d="M9 1.5L3.5 9H8l-1 5.5L12.5 7H8z"/>',
    'project': '<path d="M2.5 4.5h11v8h-11zM5.5 4.5V3h5v1.5"/>',
    'goal': '<circle cx="8" cy="8" r="6"/><circle cx="8" cy="8" r="3"/><circle cx="8" cy="8" r=".6"/>',
    'video': '<rect x="1.5" y="3.5" width="9" height="9" rx="1.5"/><path d="M10.5 7l4-2.5v7l-4-2.5"/>',
    'pull-request': '<circle cx="4.5" cy="3.5" r="1.5"/><circle cx="4.5" cy="12.5" r="1.5"/><circle cx="11.5" cy="12.5" r="1.5"/><path d="M4.5 5v6M11.5 11V6.5a2 2 0 0 0-2-2H7.5M9 3L7.5 4.5 9 6"/>',
    'repo': '<path d="M3.5 2.5h8.5v9H5a1.5 1.5 0 0 0-1.5 1.5V2.5zM3.5 13a1.5 1.5 0 0 0 1.5 1.5h7v-3"/>',
    'comment': '<path d="M2.5 3h11v7.5h-6L4.5 13v-2.5h-2z"/>',
    'hashtag': '<path d="M6 2l-1 12M11 2l-1 12M2.5 5.5h11M2 10.5h11"/>',
    'calendar': '<path d="M5 1v2M11 1v2M2.5 6h11M3.5 3h9a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-9a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z"/>',
    'person': '<circle cx="8" cy="5.5" r="2.5"/><path d="M3 14c.4-2.8 2.4-4.5 5-4.5s4.6 1.7 5 4.5"/>',
    'teams': '<circle cx="6" cy="5.5" r="2.25"/><path d="M1.75 13c.3-2.2 2-3.5 4.25-3.5S9.95 10.8 10.25 13"/><path d="M10.5 3.5a2 2 0 0 1 0 4M12 9.7c1.3.4 2.1 1.5 2.3 3.3"/>',
    'people-group': '<circle cx="8" cy="5" r="2"/><path d="M4.75 13c.3-2.1 1.6-3.25 3.25-3.25s2.95 1.15 3.25 3.25"/><circle cx="3.5" cy="6.5" r="1.5"/><path d="M1 12.5c.2-1.5 1-2.4 2.3-2.6"/><circle cx="12.5" cy="6.5" r="1.5"/><path d="M15 12.5c-.2-1.5-1-2.4-2.3-2.6"/>',
    'globe': '<circle cx="8" cy="8" r="6"/><path d="M2 8h12M8 2c1.8 1.7 2.7 3.7 2.7 6S9.8 12.3 8 14C6.2 12.3 5.3 10.3 5.3 8S6.2 3.7 8 2z"/>',
    'search': '<circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14"/>',
    'book': '<path d="M2.5 3h4a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 0 6.5 12h-4zM13.5 3h-4A1.5 1.5 0 0 0 8 4.5v9A1.5 1.5 0 0 1 9.5 12h4z"/>',
    'decision': '<path d="M8 14.5V9M8 9L4 5M8 9l4-4M4 5V2.5M4 5H1.5M12 5V2.5M12 5h2.5"/>',
    'location': '<path d="M8 14.5s4.5-4.2 4.5-8a4.5 4.5 0 0 0-9 0c0 3.8 4.5 8 4.5 8z"/><circle cx="8" cy="6.5" r="1.6"/>',
    'check': '<circle cx="8" cy="8" r="6"/><path d="M5.5 8.2l1.8 1.8 3.2-3.6"/>',
    'copy': '<rect x="5" y="5" width="8.5" height="8.5" rx="1.5"/><path d="M11 5V3.5A1 1 0 0 0 10 2.5H3.5a1 1 0 0 0-1 1V10a1 1 0 0 0 1 1H5"/>',
    'sparkle': '<path d="M8 1.5l1.4 3.6 3.6 1.4-3.6 1.4L8 11.5 6.6 7.9 3 6.5l3.6-1.4zM12.5 10.5l.6 1.4 1.4.6-1.4.6-.6 1.4-.6-1.4-1.4-.6 1.4-.6z"/>',
    'changes': '<path d="M2.5 5h9M9 2.5L11.5 5 9 7.5M13.5 11h-9M7 8.5L4.5 11 7 13.5"/>',
    'info': '<circle cx="8" cy="8" r="6"/><path d="M8 7.5v3.5M8 5v.1"/>',
    'flag': '<path d="M3.5 14.5V2M3.5 2.5h8l-1.5 3 1.5 3h-8"/>',
    'clock': '<circle cx="8" cy="8" r="6"/><path d="M8 4.5V8l2.5 1.5"/>',
    'note': '<rect x="2.5" y="2" width="11" height="12" rx="1.5"/><path d="M5 5.5h6M5 8h6M5 10.5h3.5"/>',
    'list-numbered': '<path d="M7 4h7M7 8h7M7 12h7M2.5 2.75l1-.5V5.5M2.5 5.5h2M2.4 9.6c.2-.7 1.9-.8 2 .1.1.8-1.9 1.5-2 2.6h2.1"/>',
    'tree': '<rect x="6" y="1.5" width="4" height="3.5" rx=".75"/><rect x="1.5" y="11" width="4" height="3.5" rx=".75"/><rect x="10.5" y="11" width="4" height="3.5" rx=".75"/><path d="M8 5v3M3.5 11V8h9v3"/>',
    'link': '<path d="M6.5 9.5l3-3M7 4.5l1.2-1.2a2.6 2.6 0 0 1 3.7 3.7L10.7 8.2M9 11.5l-1.2 1.2a2.6 2.6 0 0 1-3.7-3.7L5.3 7.8"/>',
    'priority-blocker': '<circle cx="8" cy="8" r="6"/><path d="M4 8h8"/>',
    'arrow-right': '<path d="M2.5 8h11M9.5 4l4 4-4 4"/>',
    'angle-brackets': '<path d="M5.5 4L1.5 8l4 4M10.5 4l4 4-4 4"/>',
    'warning': '<path d="M8 1.8L14.7 13.5H1.3z"/><path d="M8 6.2v3.3M8 11.6v.1"/>',
    'settings': '<circle cx="8" cy="8" r="2.2"/><path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M3.4 12.6l1.4-1.4M11.2 4.8l1.4-1.4"/>',
    'list-checklist': '<path d="M7 4h7M7 8h7M7 12h7"/><path d="M1.8 4l1 1 1.9-2M1.8 8l1 1 1.9-2M1.8 12l1 1 1.9-2"/>',
    'lightbulb': '<path d="M6 12.5h4M6.5 14.5h3M8 1.5a4.5 4.5 0 0 0-2.5 8.2V11h5V9.7A4.5 4.5 0 0 0 8 1.5z"/>',
}


def icon(name, cls=''):
    """An icon from the set, drawn from the page's sprite. An unknown name draws `globe`.

        icon('flag', 'ic-subtle')
    """
    name = name if name in ICONS else 'globe'
    return f'<svg class="ic {cls}" width="16" height="16" aria-hidden="true"><use href="#i-{name}"/></svg>'


def sprite(body):
    """The inline icon sprite, holding only the icons the body uses. page() adds it.

        sprite('<svg class="ic"><use href="#i-flag"/></svg>')
    """
    used = set(re.findall(r'href="#i-([\w-]+)"', body))
    return '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + ''.join(
        f'<symbol id="i-{k}" viewBox="0 0 16 16">{v}</symbol>' for k, v in ICONS.items() if k in used) + '</svg>'
