# Building the page by hand

Use this only when the user has requested an HTML report and Python can't run. Load the `atlassian-design` skill and follow its `references/hand-built.md`, including its smart link rules. Then build the same page the renderer would: the sections, their order and what each one holds are in the Build step in this skill's `SKILL.md`, and the layout is below.

## Layout

- Fixed-narrow reading layout, 760px max width, on a `--ds-surface-sunken` background, with a 16px gutter at phone width.
- Each section is a flat card (`--ds-surface` plus a `--ds-border` border, `radius.large`), with a `heading.xsmall` heading led by an ADS core icon in `--ds-icon-subtle`.
- Support light and dark mode. No horizontal scroll at any width `atlassian-design` gives.
- Every row is one sentence of about 25 words: a type lozenge in a fixed left column, the sentence, then a source line in small subtlest text with the smart link and the event date. Use absolute dates ("Oct 9"), because a window is days or weeks long. Old items still waiting say "Open since Sep 29".
