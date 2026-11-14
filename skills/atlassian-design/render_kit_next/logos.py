"""App logos: the ADS brand exports for the apps a page can show, drawn from the page's sprite. CSS: logos.css.

The files in logos/ are copies of internal/connectors/logos/, the Figma exports behind the Rovo connector cheat
sheet, since internal/ isn't distributed. An Atlassian (1p) logo includes its tile. A third-party (3p) logo is
the bare mark, drawn on a white tile.
"""
import re
from pathlib import Path

from .page import e

HERE = Path(__file__).parent / 'logos'

# Each app by its name in internal/connectors/connectors.json: its logo file, and 1p or 3p.
LOGOS = {
    'Confluence': ('confluence', '1p'),
    'Jira': ('jira', '1p'),
    'Loom': ('loom-charlie', '1p'),
    'Goals': ('goals', '1p'),
    'Projects': ('projects', '1p'),
    'Google Calendar': ('google-calendar', '3p'),
    'Outlook Calendar': ('microsoft-outlook', '3p'),
    'Outlook mail': ('microsoft-outlook', '3p'),
    'Gmail': ('gmail', '3p'),
    'Slack': ('slack', '3p'),
    'Microsoft Teams': ('microsoft-teams', '3p'),
    'Google Drive': ('google-drive', '3p'),
    'SharePoint/OneDrive': ('microsoft-sharepoint', '3p'),
    'Zoom': ('zoom', '3p'),
}


def names():
    """The app names logo() knows, for data errors.

        names()  # ['Confluence', 'Jira', ...]
    """
    return list(LOGOS)


def logo(name, size=20):
    """An app's logo, 20px in a smart link or 24px. A third-party mark sits on a white tile with a border, white in dark
    mode too.

        logo('Google Calendar', 24)
    """
    file, kind = LOGOS[name]
    cls = 'app-logo app-logo--3p' if kind == '3p' else 'app-logo'
    return f'<svg class="{cls}" width="{size}" height="{size}" aria-hidden="true"><use href="#l-{e(file)}"/></svg>'


def symbols(body):
    """The sprite symbols for the logos the body uses, with each logo's own ids prefixed by its file name.

        symbols('<use href="#l-jira"/>')
    """
    out = []
    for file in sorted(set(re.findall(r'href="#l-([\w-]+)"', body))):
        inner = re.sub(r'^\s*<svg[^>]*>|</svg>\s*$', '', (HERE / f'{file}.svg').read_text())
        out.append(f'<symbol id="l-{file}" viewBox="0 0 48 48">' + re.sub(r'(id="|url\(#|href="#)', rf'\1l-{file}-', inner) + '</symbol>')
    return ''.join(out)
