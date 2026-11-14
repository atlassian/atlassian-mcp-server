# Building the card by hand

Use this only when the user has requested an HTML report and Python can't run. Load the `atlassian-design` skill and follow its `references/hand-built.md`, including its smart link rules. Then build the same card the renderer would: the sections, their order and what each one holds are in the Build step in this skill's `SKILL.md`, and the layout is below.

## Layout

- Reading layout, 760px max width, on a `--ds-surface-sunken` background, with a 16px gutter at phone width.
- Each section is a flat card with a `heading.xsmall` heading led by an ADS core icon in `--ds-icon-subtle`.
- Each effort row is a plain block of stacked lines, with no fixed heights. Put the title chip, class lozenge and status in one `display: flex; flex-wrap: wrap` line, so they wrap onto new lines on a phone rather than leaving gaps.
- Support light and dark mode, with no horizontal scroll at 375px.
