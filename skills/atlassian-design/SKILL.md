---
name: "atlassian-design"
description: "Apply the Atlassian Design System (ADS) to artifacts, pages, mockups and prototypes — official tokens (light and dark), type, spacing, elevation, icons, component recipes, smart links, content and accessibility rules. Use when asked for Atlassian-style or ADS-styled UI."
---

# Atlassian Design System (ADS) for artifacts

Use this skill to make an artifact look and read like an Atlassian app (Jira, Confluence, Loom, Atlas style): pages, dashboards, prototypes, mockups, trackers and reports.

This skill is distilled from the official ADS MCP server (`https://mcp.atlassian.com/v1/ads/public/mcp`) and the `@atlaskit/tokens`, `@atlaskit/button`, `@atlaskit/lozenge`, `@atlaskit/smart-card` and `@atlaskit/icon` packages. Token values match `@atlaskit/tokens` 20.x.

## How this fits with other skills

- **The page contract.** If the session has an artifact skill or quickstart, follow its page contract, and use this skill for the palette, typography and components. Where they conflict on look and feel, ADS wins. Where they conflict on the contract, the contract wins. Without one, use this contract:
  - one self-contained HTML file, with all CSS, JavaScript, icons and images inline, and no CDN or other external requests
  - a meaningful `<title>` and `<meta name="viewport" content="width=device-width, initial-scale=1">`
  - a 16px gutter at phone width, and no horizontal page scroll
  - light values on `:root`, dark values under `:root[data-theme="dark"]` and under `@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])` (see `render_kit/tokens.css`)
  - no `localStorage`, `sessionStorage` or IndexedDB
  - a small file: inline only the icons you use, and don't embed raw data you don't display
  - for a live artifact whose host supports connectors (see `teamwork-graph-context`), data comes only through the host's connectors and storage, never by fetching URLs, and browser storage is still off
- **When to load this skill.** For an answer-first skill, use ordinary Markdown and source links in the initial response. Load this design guidance only after the user requests an HTML report or other visual artifact. Other skills keep their existing artifact flow.
- **The page kit.** Skills with a `render.py` build their page through the kit in `render_kit/` in this folder: the agent writes a JSON data file, and the renderer builds the page from the kit's components, with the ADS tokens in light and dark, smart links, icons, tabs and copy buttons. Their Build step says when to read `references/data-format.md`. To build a page by hand, follow `references/hand-built.md`.
- For charts, use a charting skill for form and interaction only if one is available in the session. Otherwise use the data visualization rules in `references/hand-built.md`. In either case, use ADS chart tokens and palette; do not assume an extra skill is installed.
- If the Atlassian Design System connector (tools named like `ads_plan`, `ads_search_tokens`, `ads_search_components`, `ads_search_icons`, `ads_get_guidelines`, `ads_get_a11y_guidelines`) is enabled in the session, call `ads_plan` first to look up tokens, icons and components for the task, and `ads_get_guidelines` for foundations and content questions. The connector is more current than this file.
- Without the connector, this skill and its references are enough for most artifacts. For anything it doesn't cover, fetch the public docs at `https://atlassian.design` (for example `/components/<name>/usage`, `/foundations/color`, `/components/tokens/all-tokens`).

## Non-negotiables

1. **Never hard-code a color, space, radius, shadow or font value.** Use the `--ds-*` custom properties in `render_kit/tokens.css`. If you need a value it doesn't have, pull it from the npm package (see "Getting any other token" in `references/hand-built.md`).
2. **Choose tokens by role, not by how they look.** Brand is for primary actions and selection. Danger, warning, success, information and discovery carry meaning. Accents (blue, teal, green, lime, yellow, orange, red, magenta, purple, gray) are for categories and user-chosen colors only.
3. **Support light and dark.** Every token has a dark value. Ship both.
4. **Use sentence case everywhere**: titles, headings, buttons, tabs, labels and menu items. Use all caps only for acronyms and the legacy lozenge.
5. **Meet WCAG AA.** Text under 24px needs 4.5:1 contrast. Large text and essential UI need 3:1. Never use color alone to carry meaning.
6. **Every link to a page, work item or other object is an inline smart link.** Never show a bare URL, a plain blue text link or "click here". A renderer builds them from the link data in `references/data-format.md`. By hand, follow "Smart links" in `references/hand-built.md`.

## Content (voice and writing)

- **Voice.** Bold, optimistic, practical with a wink. Be direct and concise, and put the important bits first. Know when to be serious.
- **Case and punctuation.** Use sentence case for all UI text. No periods in headings, titles, buttons or list fragments. Rephrase question headings as statements. Avoid gerunds in UI headings ("Create a space," not "Creating a space").
- **Contractions.** Use contractions and curly apostrophes (’).
- **Abbreviations.** Avoid "e.g.", "i.e.", "etc." and "&". Spell out product and feature names.
- **Errors.** Say what happened and what to do next. Use "we," don't blame the person ("We couldn't save your changes," not "You entered invalid data").
- **Warnings.** State the consequence before the action.
- **Success.** Confirm the result, then get out of the way.
- **Empty states.** Use a short title, one or two sentences on why it's empty and what's next, and one primary CTA with an imperative verb ("Create," "Try"). The tone is motivating for a blank slate, celebratory for all-done and neutral for no results.
- **Language.** Use inclusive language. Use "they" when a person's pronouns aren't known.
- **Dates and times.** Use relative times for recent events ("5 minutes ago"). Use unambiguous dates such as "Sep 30, 2026" rather than 09/30/26.

## Where to go next

- **Writing the data for a skill's renderer:** `references/data-format.md`. The skill's own Build step and `example.json` give its keys.
- **Building a page by hand, or when Python can't run:** `references/hand-built.md`. It has the foundations, the component recipes, the smart link rules, live states, the accessibility checklist and the checks before publishing.
- **Building or changing a renderer:** `references/components.md`, every component in the kit, generated from its docstrings. New visual pieces go into the kit as components, not into a skill's `render.py`.
