"""Shared kit for skills that render an ADS page from a JSON data file.

A skill keeps a small layout script, render.py, beside its SKILL.md that imports this package from the
atlassian-design skill installed beside it:

    import render_kit as k
    from render_kit import e, icon, lz, text, card

    def render(d):
        body = k.header('Catch-up', d['topic'], ...) + card('flag', 'Needs you', k.rows(d.get('needsYou')))
        return k.page('Catch-up: ' + d['topic'], body, css=PAGE_CSS, mockup=d.get('mockup'))

    if __name__ == '__main__':
        k.main(render, 'render.py data.json page.html')

Each family is a module with its CSS beside it, and references/components.md lists every component, generated
from these docstrings by index.py. Text fields are plain text, escaped here, and can hold {0}, {1} and so on,
replaced by the item's "links" in order. Only the icons a page uses go into its sprite, and only the CSS of
the families it uses into its stylesheet.
"""
from .diagram import DIAGRAM_JS, SEVERITY, SOURCES, STATES, dependency_list, diagram, legend
from .board import board, board_script, board_state
from .code import change_rows, code_chip, doc_rows, excerpt, stack_table, trace, value_pill
from .efforts import effort, efforts
from .decisions import decision, options, timeline
from .evidence import evidence, evidence_item, quote_copy
from .findings import checklist, labelled_rows, link_rows, numbered, quote, row, rows, source_line, text_rows
from .icons import ICONS, icon, sprite
from .layout import card, copy_btn, empty, footer, header, link_button, meta_item, note, summary_card, tabs
from .links import e, link, links, placeholder, text, texts
from .page import DataError, main, page, unfilled
from .meetings import occurrences, overview
from .metrics import tiles
from .people import attendees, avatar, person
from .status import lz, lz_text

# The modules in reading order, for index.py.
MODULES = ('page', 'icons', 'links', 'status', 'layout', 'findings', 'people', 'evidence', 'meetings', 'metrics', 'diagram', 'code', 'efforts', 'decisions', 'board')
