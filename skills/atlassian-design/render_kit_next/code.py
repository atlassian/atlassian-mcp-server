"""Code: the trace of a behaviour through the code, as numbered steps with code chips and excerpts.
CSS: code.css."""
from .glyphs import glyph
from .links import text
from .page import e


def code_chip(c, commit=''):
    """A chip shaped like a smart link, linking a file at the cited lines: the angle-brackets glyph, then the file
    name, "idleTimer.ts". Its tooltip holds the path, the lines and the commit, and screen readers hear the lines
    after the name. A test chip adds the test's name to both.

    Data: {"path", "lines": [first, last], "url", "name"?}. name marks a supporting test.

        code_chip({"path": "packages/session/src/idleTimer.ts", "lines": [8, 31], "url": "#"}, commit='4f2c9a1')
    """
    first, last = c['lines']
    at = f' at {commit}' if commit else ''
    test = f'Test: {c["name"]}' if c.get('name') else ''
    tip = f'{c["path"]} · lines {first} to {last}{at}' + (f' · {test}' if test else '')
    hidden = f', lines {first} to {last}' + (f', {test}' if test else '')
    return (f'<a class="inline-card code-chip" href="{e(c["url"])}" target="_blank" rel="noopener" title="{e(tip)}">'
            f'{glyph("angle-brackets")}<span class="inline-card__title">{e(c["path"].rsplit("/", 1)[-1])}'
            f'<span class="visually-hidden">{e(hidden)}</span></span>'
            '<span class="visually-hidden"> (opens in a new tab)</span></a>')


def excerpt(lines):
    """A collapsed "Show the code" disclosure holding numbered lines, after ADS CodeBlock: the code font, line
    numbers in subtlest text in their own column, an ellipsis row between runs that aren't next to each other,
    and scrolling inside its own box, which takes keyboard focus.

    Data: [{"n", "code"}, {"gap": true}, ...], up to 12 lines with secrets cut.

        excerpt([{"n": 4, "code": "export const DEFAULT_IDLE_TIMEOUT_MINUTES = 30;"}, {"gap": True}, {"n": 9, "code": "}"}])
    """
    digits = max((len(str(x['n'])) for x in lines if not x.get('gap')), default=1)
    rows = '\n'.join('<span class="code-block__number"></span><span class="code-block__gap">…</span>' if x.get('gap')
                     else f'<span class="code-block__number">{e(x["n"])}</span>{e(x["code"])}' for x in lines)
    return (f'<details class="code-excerpt"><summary class="code-excerpt__toggle">{glyph("chevron-right")}Show the code</summary>'
            f'<div class="code-block" tabindex="0" role="region" aria-label="Code excerpt" style="--code-block-digits:{digits}ch">'
            f'<pre><code>{rows}</code></pre></div></details>')


def trace(steps, commit=''):
    """The trace as a numbered list divided by lines, each number in the numbered list's 20px circle. Each step has
    its sentence, then its code and test chips, then the excerpt, 8px apart.
    Screen readers hear "Step 1." before the sentence.

    Data: [{"text": text field, "code"?: code chip, "test"?: code chip, "excerpt"?: excerpt lines}].

        trace([{"text": "If the site sets no timeout, it's 30 minutes.",
                "code": {"path": "packages/session/src/config.ts", "lines": [4, 9], "url": "#"}}], commit='4f2c9a1')
    """
    out = ''
    for i, s in enumerate(steps, 1):
        chips = ''.join(f'<span>{code_chip(s[k], commit)}</span>' for k in ('code', 'test') if s.get(k))
        out += (f'<li class="trace__step"><span class="numbered-list__number" aria-hidden="true">{i}</span><div class="trace__body">'
                f'<p class="paragraph"><span class="visually-hidden">Step {i}. </span>{text(s)}</p>'
                + (f'<div class="link-row">{chips}</div>' if chips else '')
                + (excerpt(s['excerpt']) if s.get('excerpt') else '') + '</div></li>')
    return f'<ol class="trace">{out}</ol>'
