"""Page assembly and the command line: the stylesheet, the sprite, the page scripts, the mockup note and the
checks every page passes.

The stylesheet is tokens.css (with its dark list repeated under the prefers-color-scheme media query), ads.css,
links.css and layout.css, then every other .css file in this folder, in name order, whose classes the page
uses, then the renderer's own CSS.
"""
import json
import re
import sys
from pathlib import Path

from .icons import icon, sprite
from .links import e

HERE = Path(__file__).parent
ALWAYS = ('tokens.css', 'ads.css', 'links.css', 'layout.css')
MOCKUP_NOTE = 'Mockup with sample data. People, work and pages are made up.'
WIDTHS = {'reading': 760, 'wide': 880, 'board': 1240}

# Tabs (role=tab with id t-<key>, panel p-<key>, selection kept in the URL hash) and copy buttons.
JS = '''
(function(){
  var tabs=[].slice.call(document.querySelectorAll('[role=tab]'));
  function show(id,focus){tabs.forEach(function(t){var on=t.id==='t-'+id;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;
    document.getElementById('p-'+t.id.slice(2)).hidden=!on;if(on&&focus)t.focus();});}
  tabs.forEach(function(t,i){
    t.addEventListener('click',function(){var id=t.id.slice(2);show(id);history.replaceState(null,'','#'+id);});
    t.addEventListener('keydown',function(ev){var d=ev.key==='ArrowRight'?1:ev.key==='ArrowLeft'?-1:0;if(!d)return;ev.preventDefault();
      var n=tabs[(i+d+tabs.length)%tabs.length];show(n.id.slice(2),true);history.replaceState(null,'','#'+n.id.slice(2));});});
  if(tabs.length){var h=location.hash.slice(1);show(document.getElementById('t-'+h)?h:tabs[0].id.slice(2));}
  [].forEach.call(document.querySelectorAll('[data-copy]'),function(b){var lab=b.lastChild,o=lab.textContent;
    b.addEventListener('click',function(){
    var s=b.getAttribute('data-copy'),el=document.getElementById(s),t=el?el.textContent:s,fb=b.nextElementSibling;
    function done(){lab.textContent='Copied';setTimeout(function(){lab.textContent=o},1500);}
    function fail(){if(!fb||!fb.classList.contains('copy-fallback'))return;fb.hidden=false;
      var r=document.createRange();r.selectNodeContents(fb);var sel=getSelection();sel.removeAllRanges();sel.addRange(r);}
    if(navigator.clipboard)navigator.clipboard.writeText(t).then(done,fail);else fail();});});
})();
'''


def css_classes(css):
    """The components a stylesheet styles: the leading class of each of its selectors."""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    selectors = re.findall(r'([^{}]+)\{[^{}]*\}', css)
    return {m.group(1) for s in selectors for part in s.split(',') if (m := re.search(r'\.(-?[_a-zA-Z][\w-]*)', part))}


def tokens():
    """tokens.css, with its dark list repeated under the prefers-color-scheme media query."""
    t = (HERE / 'tokens.css').read_text()
    dark = re.search(r'^:root\[data-theme="dark"\] \{\n(.*?)^\}', t, re.M | re.S).group(1)
    return t + '@media (prefers-color-scheme: dark) {\n:root:not([data-theme="light"]) {\n' + dark + '}\n}\n'


def stylesheet(body):
    """The page's CSS: the foundations, then each family's CSS the body uses."""
    used = set(' '.join(re.findall(r'class="([^"]*)"', body)).split())
    parts = [tokens()] + [(HERE / f).read_text() for f in ALWAYS[1:]]
    for f in sorted(p for p in HERE.glob('*.css') if p.name not in ALWAYS):
        css = f.read_text()
        if css_classes(css) & used:
            parts.append(css)
    return '\n'.join(parts)


def page(title, body, css='', js='', width='reading', mockup=False):
    """The whole self-contained HTML file: the kit's CSS, the renderer's CSS, the sprite and the scripts.

    width is the page's max width: reading (760px, the default) for every text page, wide (880px) only for a page
    whose diagram needs more room than reading gives (dependency-map), or board (1240px) for a work board. mockup
    adds the sample data note at the top.

        k.page('Catch-up: Search migration', body, css=PAGE_CSS, mockup=d.get('mockup'))
    """
    if width not in WIDTHS:
        raise ValueError(f'width is reading, wide or board, not {width!r}')
    if mockup:
        body = f'<div class="mock-note" role="note">{icon("info")}<span>{e(MOCKUP_NOTE)}</span></div>' + body
    main_ = f'<main class="wrap" style="max-width:{WIDTHS[width]}px">{body}</main>'
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(title)}</title><style>\n{stylesheet(main_)}{css}</style></head>'
            f'<body>{sprite(main_)}{main_}<script>{JS}{js}</script></body></html>\n')


def unfilled(out):
    """The {n} link placeholders left in the page's text, outside its CSS and script.

        unfilled(html)  # ["{1}"] when a text field had fewer links than placeholders
    """
    return sorted(set(re.findall(r'\{\d+\}', re.sub(r'<style>.*?</style>|<script>.*?</script>', '', out, flags=re.S))))


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
    any missing key's path, for example `data error: people[1].evidence[0]: missing "link"`.

        if __name__ == '__main__':
            k.main(render, 'render.py card.json who-to-ask.html')
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
