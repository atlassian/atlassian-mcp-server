# Building the trace by hand

Use this only when the user has requested an HTML report and Python can't run. Load the `atlassian-design` skill and follow its `references/hand-built.md`, including its smart link rules. Then build the same trace the renderer would: the sections, their order and what each one holds are in the Build step in this skill's `SKILL.md`, and the layout is below.

## Layout

- Reading layout, 760px max width, on a `--ds-surface-sunken` background, with a 16px gutter at phone width.
- Each section is a flat card with a `heading.xsmall` heading led by an ADS core icon in `--ds-icon-subtle`.
- Support light and dark mode, with no horizontal scroll at 375px. At 600px and narrower, the answer's field lists stack, label above value, and the timeline puts each date above its item.
