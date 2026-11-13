"""Page assembly, the command line, and the helpers every family uses: escaping, text fields and data errors.

The stylesheet is tokens.css (with its dark list repeated under the prefers-color-scheme media query), then
base.css, then every other .css file in this folder, in name order, whose classes the page uses.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
WIDTH = 760


def e(s):
    """Escape a value for HTML text or an attribute. None is empty.

        e('Fix <b> tags')  # "Fix &lt;b&gt; tags"
    """
    return html.escape(str(s if s is not None else ''), quote=True)


def inline_code(escaped):
    """Escaped text with each `backticked` run shown as inline code.

        inline_code(e('Set `pageSize` to 200'))
    """
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)


def texts(x):
    """One text field or a list of them, as a list, so a lone string isn't read one character at a time. An
    empty list for an empty value.

        texts('The cutover moved to Nov 16.')  # ['The cutover moved to Nov 16.']
    """
    if not x:
        return []
    return [x] if isinstance(x, (str, dict)) else x


def css_classes(css):
    """The components a stylesheet styles: the leading class of each of its selectors.

        css_classes('.row-list > li{margin:0}')  # {'row-list'}
    """
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    selectors = re.findall(r'([^{}]+)\{[^{}]*\}', css)
    return {m.group(1) for s in selectors for part in s.split(',') if (m := re.search(r'\.(-?[_a-zA-Z][\w-]*)', part))}


def tokens():
    """tokens.css, with its dark list repeated under the prefers-color-scheme media query."""
    t = (HERE / 'tokens.css').read_text()
    dark = re.search(r'^:root\[data-theme="dark"\] \{\n(.*?)^\}', t, re.M | re.S).group(1)
    return t + '@media (prefers-color-scheme: dark) {\n:root:not([data-theme="light"]) {\n' + dark + '}\n}\n'


def stylesheet(body):
    """The page's CSS: the tokens, base.css, then the CSS of each family whose classes the body uses."""
    used = set(' '.join(re.findall(r'class="([^"]*)"', body)).split())
    families = (f.read_text() for f in sorted(HERE.glob('*.css')) if f.name not in ('tokens.css', 'base.css'))
    return '\n'.join([tokens(), (HERE / 'base.css').read_text(), *(css for css in families if css_classes(css) & used)])


def page(title, body, width=WIDTH):
    """The whole self-contained HTML file: the CSS the body needs, the body, the sprite of the glyphs and logos it
    uses at the end of main, and the script of each part that needs one: the hover panel's and the copy block's.
    width is the page's max width: 760px for a text page, or 880px for a page whose diagram needs more room.

        k.page('How it works: session timeout', body, 880)
    """
    from . import glyphs, logos
    from .copy_block import SCRIPT as COPY
    from .hover_panel import SCRIPT as HOVER

    symbols = glyphs.symbols(body) + logos.symbols(body)
    if symbols:
        body += f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{symbols}</svg>'
    scripts = (HOVER if 'class="hover-panel"' in body else '') + (COPY if 'class="copy-block"' in body else '')
    script = f'<script>{scripts}</script>' if scripts else ''
    light, dark = re.findall(r'--ds-surface-sunken:([^;]+);', (HERE / 'tokens.css').read_text())
    theme = ''.join(f'<meta name="theme-color" media="(prefers-color-scheme: {s})" content="{c}">' for s, c in (('light', light), ('dark', dark)))
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'{theme}<title>{e(title)}</title><style>\n{stylesheet(body)}</style></head>'
            f'<body><main class="wrap" style="max-width:{width}px">{body}</main>{script}</body></html>\n')


def unfilled(out):
    """The {n} link placeholders left in the page's text, outside its CSS and script.

        unfilled(html)  # ["{1}"] when a text field had fewer links than placeholders
    """
    out = re.sub(r'<(style|script)\b[^>]*>.*?</\1\s*>', '', out, flags=re.I | re.S)
    return sorted(set(re.findall(r'\{\d+\}', out)))


class DataError(KeyError):
    """A required key missing from the data, with where it was missing."""

    def __str__(self):
        return self.args[0]


class Data(dict):
    """A data object that names its path when a required key is missing. .get() works as usual."""

    def __init__(self, items, path):
        super().__init__(items)
        self.path = path

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            raise DataError(f'{self.path}: missing "{key}"' if self.path else f'missing "{key}"') from None


def wrap(x, path=''):
    """The loaded JSON, with every object wrapped in Data."""
    if isinstance(x, dict):
        return Data({k: wrap(v, f'{path}.{k}' if path else k) for k, v in x.items()}, path)
    if isinstance(x, list):
        return [wrap(v, f'{path}[{i}]') for i, v in enumerate(x)]
    return x


def main(render, usage):
    """The renderer's command line: data.json page.html. It renders, refuses unfilled placeholders and names
    any missing key's path, for example `data error: steps[1]: missing "text"`.

        if __name__ == '__main__':
            k.main(render, 'render.py data.json page.html')
    """
    if len(sys.argv) < 3:
        sys.exit('usage: ' + usage)
    try:
        out = render(wrap(json.loads(Path(sys.argv[1]).read_text())))
    except DataError as err:
        sys.exit(f'data error: {err}')
    left = unfilled(out)
    if left:
        sys.exit(f'unfilled link placeholders: {left}')
    Path(sys.argv[2]).write_text(out)
    print(f'wrote {sys.argv[2]} ({len(out)} bytes)')
