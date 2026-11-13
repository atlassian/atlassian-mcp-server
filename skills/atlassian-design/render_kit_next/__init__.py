"""The staging kit: the redesigned page frame and parts that replace render_kit, one skill at a time.

A skill on this kit imports only it, from the atlassian-design skill installed beside it, and nothing here
imports render_kit:

    import render_kit_next as k

    def render(d):
        body = k.header('how-it-works', d['question'], d['readFrom']) + k.section('Short answer', k.paragraphs(d['answer']))
        return k.page(f'How it works: {d["question"]}', body)

    if __name__ == '__main__':
        k.main(render, 'render.py data.json page.html')

Each family is a module with its CSS beside it, and each function has a docstring with an example. page() adds
the CSS of the families the body uses, the sprite of its glyphs and logos, and the scripts it needs. README.md
has the rules and the ledger of what each family replaces in render_kit.
"""
from .app_stack import app_stack
from .avatar_group import avatar_group, avatar_hue, initials
from .checklist import checklist
from .code import code_chip, excerpt, trace
from .copy_block import copy_block
from .flow import flow_figure
from .frame import footer, header, mockup_badge, paragraphs, section, small_text, sources_footer
from .glyphs import glyph
from .hover_panel import hover_panel, panel_row
from .links import link, links, status, text
from .logos import logo
from .lozenge import lozenge
from .page import DataError, css_classes, e, inline_code, main, page, texts, unfilled
from .rows import label_rows, numbered_list, rows
from .skill_tag import skill_tag
from .source_rows import source_rows
from .table import table
from .tag import tag
