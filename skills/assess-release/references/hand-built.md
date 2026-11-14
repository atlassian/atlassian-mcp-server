# Building the page by hand

Use this only when the user has requested an HTML report and Python can't run. Load the `atlassian-design` skill and follow its `references/hand-built.md`, including its smart link rules. Then build the same page the renderer would: the sections, their order and what each one holds are in the Build step in this skill's `SKILL.md`, and the layout is below.

## Layout

- Reading layout, 760px max width, on a `--ds-surface-sunken` background, with a 16px gutter at phone width. Light and dark mode. No horizontal scroll at 375px: the areas table becomes stacked rows on phones.
- Each section is a flat card with a `heading.xsmall` heading led by an ADS core icon in `--ds-icon-subtle`.
- After Readiness by area, show Outstanding conditions with the distinct entry count and one sourced row per condition, including the affected areas. Use the same list counted in the verdict. Show Not used area lozenges in neutral, with the explicit applicability reason and its source.
