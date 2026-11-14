# render_kit_next

The staging kit for the skill-by-skill redesign. Skills move onto it one at a time, and once its families
cover most skill pages it replaces `render_kit`.

## Rules

- **A skill moves whole.** Once it moves, its `render.py` imports only `render_kit_next`, with no adapters
  or aliases for old names.
- **It stands alone.** Nothing here imports `render_kit`. It has its own page assembly, command line,
  `tokens.css` (a copy of `render_kit/tokens.css`, plus the tokens new parts need) and `base.css`, and a page loads no `render_kit` CSS.
- **One module per family,** with its CSS beside it, and each function with a docstring and an example.
  `page()` adds the CSS of each family whose classes the body uses, the sprite of the glyphs and logos it
  uses, and the scripts it needs.
- **Generic names.** Names, parameters, classes, ids and copy name no skill's ideas. Copy that's specific to
  a skill comes from that skill's `render.py`.
- **Shared when needed.** A family one skill uses stays its own module, it's shared once a second skill
  needs it, and options are added only when a skill needs them.
- **`render_kit` is frozen.** It matches main and takes only bug fixes until the swap.
- **The swap:** when every skill has moved, `render_kit` is deleted and this folder is renamed.

## Ledger

| Family | Used by | Replaces in `render_kit` | Review |
| --- | --- | --- | --- |
| `page` (`page`, `main`, `e`, `texts`, `inline_code`, `DataError`) | meeting-prep, how-it-works | `page`'s `page`, `main`, `DataError` and `unfilled`, and `links`' `e`, `texts` and `inline_code` | Approved with meeting-prep, 2026-10-30. Unreviewed: adding the copy block's script, and `page`'s width for an 880px page |
| `frame` (`header`, `section`, `paragraphs`, `small_text`, `footer`, `sources_footer`, `mockup_badge`) | meeting-prep, how-it-works | `layout`'s `header`, `meta_item`, `card`, `summary_card`, `empty`, `footer` and `link_button`, and `meetings`' `overview` | Approved with meeting-prep, 2026-10-30. Unreviewed: `small_text` and `sources_footer` |
| `rows` (`label_rows`, `numbered_list`, `rows`) | meeting-prep, how-it-works | `findings`' `rows`, `link_rows`, `numbered` and `labelled_rows`, `meetings`' `occurrences`, and `code`'s `change_rows`, the last two merged into `label_rows` | Approved with meeting-prep, 2026-10-30. Unreviewed: `label_rows`' note and rows that hold only links. `numbered_list`'s circled numbers are shared with `code`'s trace |
| `avatar_group` (`avatar_group`, `initials`, `avatar_hue`) | meeting-prep | `people`'s `attendees` and `avatar_hue` | Approved with meeting-prep, 2026-10-30 |
| `links` (`link`, `links`, `text`, `status`) | meeting-prep, how-it-works | `links`' `link`, `links` and `text`, and `status`' `lz` for a lozenge from data | Approved with meeting-prep, 2026-10-30. No found-by-search variant: neither skill marks links that way |
| `glyphs` (`glyph`) | meeting-prep, how-it-works | `icons`' `icon` and `sprite` | Approved with meeting-prep, 2026-10-30. Unreviewed: `chevron-right` and `copy` |
| `logos` (`logo`) | meeting-prep, how-it-works | New | Approved with meeting-prep, 2026-10-30 |
| `lozenge` (`lozenge`) | meeting-prep, how-it-works | `status`' `lz` | Approved with meeting-prep, 2026-10-30 |
| `skill_tag` (`skill_tag`) | meeting-prep, how-it-works | New | Approved with meeting-prep, 2026-10-30 |
| `hover_panel` (`hover_panel`, `panel_row`) | meeting-prep | New | Approved with meeting-prep, 2026-10-30 |
| `app_stack` (`app_stack`) | meeting-prep | New | Approved with meeting-prep, 2026-10-30 |
| `tag` (`tag`) | how-it-works | The tags in `layout`'s `footer` | Unreviewed, how-it-works draft |
| `code` (`trace`, `code_chip`, `excerpt`) | how-it-works | `code`'s `trace`, `code_chip`, `value_pill` and `excerpt`, its steps now with no kind lozenge or value pill | Unreviewed, how-it-works draft |
| `table` (`table`) | how-it-works | `code`'s `stack_table` | Unreviewed, how-it-works draft |
| `checklist` (`checklist`) | how-it-works | `findings`' `checklist` | Unreviewed, how-it-works draft |
| `source_rows` (`source_rows`) | how-it-works | `code`'s `doc_rows` | Unreviewed, how-it-works draft |
| `copy_block` (`copy_block`) | how-it-works | `evidence`' `quote_copy` and `layout`'s `copy_btn` | Unreviewed, how-it-works draft |
| `flow` (`flow_figure`) | how-it-works | New | Unreviewed, how-it-works flow: nodes in columns joined by labelled edges, scaling to 80% and then scrolling sideways |

## Renames

Names that came from meeting-prep and were made generic on 2026-10-30. Only the names changed.

- `header(skill, title, when, aside)` is `header(skill, title, meta, aside)`, and `.page-when` is
  `.page-header__meta`.
- `avatar_group(people, guests)` is `avatar_group(people, label, heading, id, extra='')`: the caller names
  the button, the panel's heading and id, and the extra line. Each person's `response` is a `status`,
  `{"text", "glyph"?}`, and `.avatar-group__response` is `.avatar-group__status`. Meeting-prep's response
  glyphs are in its `render.py`.
- `topics(items)` is `numbered_list(items)`, and `.topics`, `.topic` and `.topic__number` are
  `.numbered-list`, `.numbered-list__item` and `.numbered-list__number`.
- `reading(items)` is `rows(items)`, and each item's `link` is `links`, a link or a list.

## Skills on this kit

- meeting-prep: approved 2026-10-30.
- how-it-works: a first draft for Peter, 2026-10-30, with the same sections and data as before, and a Where it happens
  flow after Short answer, drawn by `flow`, on an 880px page. Not reviewed.
