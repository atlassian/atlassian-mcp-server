"""The app stack: ✦ AI Components' App stack at small (54649:17649), like @atlassian/app-stack, opening a panel of
the connections used. CSS: app_stack.css.
"""
from .hover_panel import hover_panel, panel_row
from .logos import LOGOS, logo, names
from .page import DataError, e


def app_stack(apps):
    """Up to 6 app logos, 24px and overlapping by 4px, the 2nd, 4th and 6th tilted, opening a panel that lists
    every app with its 24px logo. Nothing with no apps. An app outside the logo list stops the render.

        app_stack(['Google Calendar', 'Confluence', 'Jira'])
    """
    for a in apps:
        if a not in LOGOS:
            raise DataError(f'unknown app "{a}" in the app stack. Use one of: {", ".join(names())}')
    if not apps:
        return ''
    tiles = ''.join(f'<span class="app-stack__tile">{logo(a, 24)}</span>' for a in apps[:6])
    rows = ''.join(panel_row(logo(a, 24), e(a)) for a in apps)
    n = len(apps)
    return hover_panel(f'<span class="app-stack">{tiles}</span>', f'Connections used, {n}', f'{n} connection{"" if n == 1 else "s"} used', rows, 'connections')
