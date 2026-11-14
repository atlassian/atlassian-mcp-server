# Building a page by hand

Use this when a skill has no renderer, or when Python can't run and a skill's Build step says to build the same page by hand. A skill with a renderer builds its page from data instead: see `data-format.md`.

## Start from the kit's CSS

Paste these files from `render_kit/` in the `atlassian-design` folder into the page's `<style>`, in this order. They are the same CSS the renderers use, so a hand-built page matches a rendered one.

1. **`tokens.css`:** every ADS token, light on `:root` and dark under `:root[data-theme="dark"]`. The artifact contract wants the dark values twice, so paste the dark list again inside `@media (prefers-color-scheme: dark)`, under `:root:not([data-theme="light"])`, as the comment in the file says.
2. **`ads.css`:** the base (`body`, links, the focus ring) and the component recipes: buttons, lozenges, badges, tags, section messages, text fields, cards, tabs, modals, tables, avatars and progress bars. A comment above each one gives its sizes and tokens.
3. **`links.css`:** smart links.

Add only what the page needs on top, using tokens. `layout.css` and the other family files show how the renderers lay out headers, cards, rows and people, if you want the same look.

**Fonts.** Atlassian Sans and Atlassian Mono aren't on Google Fonts, so artifacts fall back to the system stack in `tokens.css`. That fallback is ADS's own, so don't swap in another web font. Semibold (600) falls back to bold on most systems, so prefer medium (500) or bold (653).

### Token naming: code ↔ CSS

ADS code uses `token('color.text.subtle')`. The CSS variable drops the `color.` or `elevation.` prefix and turns dots into dashes:

| ADS token | CSS variable |
|---|---|
| `color.text.subtle` | `--ds-text-subtle` |
| `color.background.brand.bold.hovered` | `--ds-background-brand-bold-hovered` |
| `elevation.surface.raised` | `--ds-surface-raised` |
| `elevation.shadow.overlay` | `--ds-shadow-overlay` |
| `space.150` / `radius.medium` / `font.heading.large` | `--ds-space-150` / `--ds-radius-medium` / `--ds-font-heading-large` |

When the person wants React code for their own codebase rather than an artifact, use the real packages (`@atlaskit/button/new`, `@atlaskit/primitives/compiled` Box/Stack/Inline/Text, `@atlaskit/heading`, `@atlaskit/tokens` `token()`, `@atlaskit/icon/core/<name>`, `@atlaskit/smart-card` for links) instead of these CSS recipes.

### Getting any other token

`tokens.css` covers the core set plus accent and chart essentials. For any other token (for example `background-accent-blue-bolder-hovered`), pull exact values in the sandbox:

```bash
OPENSSL_CONF=/dev/null npm pack @atlaskit/tokens --cache "$TMPDIR/npm-cache" && ls atlaskit-tokens-*.tgz && tar xzf atlaskit-tokens-*.tgz
python3 - <<'PY'
import re
def load(f):
    s=open(f).read(); s=s[s.index('export default "')+16:s.rindex('"')]
    return dict(re.findall(r'(--ds-[\w-]+):\s*([^;]+);', s.encode().decode('unicode_escape')))
d='package/dist/esm/artifacts/themes/'
L,D=load(d+'atlassian-light.js'),load(d+'atlassian-dark.js')
for k in ['--ds-background-accent-blue-bolder-hovered']: print(k, L[k], D[k])
PY
```

Don't load these theme files at runtime. Their selectors expect `html[data-color-mode][data-theme~="light:light"]`, which clashes with the artifact's `data-theme` attribute.

## Foundations

### Color

- **Roles.** `brand` (primary actions, selection, links), `neutral` (default UI), `danger`, `warning`, `success`, `information`, `discovery` (new features, onboarding), plus `accent-*` for categories.
- **Emphasis.** Emphasis runs subtlest → subtler → subtle → default → bold → bolder → boldest. Bolder means more contrast and more attention. Default to subtle backgrounds. Use bold sparingly.
- **Inverse.** On any `*-bold` background, use `--ds-text-inverse` and `--ds-icon-inverse`. On `--ds-background-warning-bold` (yellow), use `--ds-text-warning-inverse` and `--ds-icon-warning-inverse` instead.
- **Text.** `--ds-text` is primary. `--ds-text-subtle` is secondary (labels, metadata). `--ds-text-subtlest` is tertiary (placeholders, timestamps). Never put essential information in `--ds-text-disabled`.
- **Interaction states.** Every interactive background has `-hovered` and `-pressed` versions. Icons have no hover tokens, so give icon-only controls a `--ds-background-neutral-subtle` background (→ `-hovered` → `-pressed`).
- **Selected.** Use `--ds-background-selected` + `--ds-text-selected` / `--ds-icon-selected`, and `--ds-border-selected` at `--ds-border-width-selected`.
- **Accents.** Pair `accent-X-subtlest`/`-subtler` backgrounds with `text-accent-X` or `-bolder` text. Pair `-subtle` backgrounds with `-bolder` text. Pair `-bolder` backgrounds with inverse text. Keep background and foreground in the same hue. Avoid yellow, which turns brown for contrast; use orange instead. Add a `border-accent-X` border to subtler backgrounds when the shape itself must reach 3:1 contrast.

### Elevation

| Level | Surface | Shadow | Use for |
|---|---|---|---|
| Sunken | `--ds-surface-sunken` | none | Wells and backdrops on the default surface only (Kanban columns, side panels) |
| Default | `--ds-surface` | none | Page body. For flat cards, add a `--ds-border` border |
| Raised | `--ds-surface-raised` | `--ds-shadow-raised` | Movable cards (Jira/Trello cards), or one point of emphasis |
| Overlay | `--ds-surface-overlay` | `--ds-shadow-overlay` | Modals, dropdowns, popups, floating toolbars, dragged items |

- Always pair a surface with its matching shadow. In dark mode the surfaces get lighter as they rise.
- Don't put sunken surfaces on raised or overlay surfaces.
- Use `--ds-background-neutral` (transparent) when a fill must adapt to whatever surface it sits on. Use `--ds-surface-sunken` (opaque) for backdrops.
- For hover and press, use `-hovered` / `-pressed` surface tokens.
- For scrolled content, put a `--ds-border` line at the cut-off. Use `--ds-shadow-overflow` only where a border would be missed.
- **Z-index:** navigation 200, inline dialog 300, popup 400, blanket 500, modal 510, flag 600, spotlight 700, tooltip 800.

### Spacing and layout

- 8px base: `space.100` = 8px, `space.200` = 16px, and so on. Use only the scale.
  - **0–8px** (`space.0`–`space.100`): icon-to-text gaps, badge and cell padding, button-group gaps, input padding, title-to-description in a card
  - **12–24px** (`space.150`–`space.300`): component padding, avatar-to-content gaps, card internals
  - **32–80px** (`space.400`–`space.1000`): page sections and layout
- Group by proximity and similarity, keep a steady rhythm in lists and tables, and use size and whitespace for hierarchy.
- Build layouts with flex/grid `gap` in space tokens: Stack is a vertical gap, Inline is a horizontal gap.
- **Grid.** 12 columns. Content spans 3–12 columns.
  - **Fluid** grids fill the width. Use them for dense views such as boards.
  - **Fixed-narrow** grids (about 760px max) are for reading.
  - **Fixed-wide** grids (about 1200px max) are for tables.
  - Small viewports are 320–1023px. Large viewports are 1024px and up. Design at least two breakpoints.
- The Atlassian app shell has a top navigation bar (about 48px, `--ds-surface`, bottom `--ds-border`), an optional left side navigation (about 240–320px), the main content area, and an optional right aside.

### Radius

| Token | Use for |
|---|---|
| `xsmall` 2px | Badges, checkboxes, keyboard-shortcut keys |
| `small` 4px | Lozenges, tags, tooltips, compact buttons, timestamps |
| `medium` 6px | Buttons, inputs, selects, textareas, nav items, smart links |
| `large` 8px | Cards, in-page containers, dropdown menus, popups |
| `xlarge` 12px | Modals, Kanban columns, tables, large containers |
| `xxlarge` 16px | Video players |
| `full` | Avatars, pills, emoji reactions |
| `tile` | Icon and object tiles only |

The focus ring sits 2px outside the element, with a corner radius 2px larger than the element's.

### Typography

- **Headings:** XXL/XL for marketing, XL/L for page titles, M for modals and large components, S/XS for small components (flags, cards), XXS rarely. Use one `<h1>` per page and don't skip levels. Don't style body text as a heading, and don't use heading styles inside components. Inside components, use body text with medium weight.
- **Body:** L (16/24) for long-form reading, M (14/20, the default) for UI, S (12/16) for fine print only.
- **Weights:** regular for paragraphs, medium for component text and any text beside an icon, bold only for rare emphasis.
- **Metric:** use metric styles for standalone numbers (45%, $70, 3 in review, donut centres, single-value tiles). Don't use them for chart titles, legends or long statements.
- **Code:** use `--ds-font-code`, with `--ds-background-neutral` behind inline code.
- Keep lines at 60–80 characters. Don't truncate text without a way to read it all. Links must look different from the surrounding text, and links to objects or pages are smart links (see "Smart links").

### Iconography

- The real ADS icons (Apache-2.0) are 16×16 SVGs with `fill="currentcolor"`. Inline them. Don't hotlink them.
  ```bash
  OPENSSL_CONF=/dev/null npm pack @atlaskit/icon --cache "$TMPDIR/npm-cache" && ls atlaskit-icon-*.tgz && tar xzf atlaskit-icon-*.tgz
  # then read package/svgs/core/<name>.svg
  ```
  Don't add `--silent`: in a sandbox, npm can fail on its OpenSSL config or cache and still look like it succeeded. The `ls` stops the `tar` if no tarball was made. If npm isn't available, draw a simple 16×16 line icon in the same style rather than hotlinking.
- Color icons with `--ds-icon` (default), `--ds-icon-subtle`, `--ds-icon-subtlest` or a role token (`--ds-icon-brand`, `--ds-icon-danger` and so on).
- Sizes are 16px (default) and 12px (small). Pair icons with medium-weight text.
- A meaningful icon needs `role="img"` and an `aria-label`. A decorative icon beside a text label gets `aria-hidden="true"`.
- Core icon names: accessibility add ai-agent ai-chat ai-generative-text-summary ai-sparkle alert align-image-center align-image-left align-image-right align-text-center align-text-left align-text-right angle-brackets api app-switcher-legacy app-switcher app apps archive-box arrow-down-left arrow-down-right arrow-down arrow-left arrow-right arrow-up-left arrow-up-right arrow-up assets atlassian-intelligence attachment audio automation backlog basketball bezier-curve board boards book-with-bookmark border branch briefcase bug calendar-plus calendar camera capture card cash changes chart-bar chart-bubble chart-matrix chart-pie chart-trend-down chart-trend-up chart-trend chat-widget check-circle-unchecked check-circle check-mark checkbox-checked checkbox-indeterminate checkbox-unchecked chevron-double-left chevron-double-right chevron-down chevron-left chevron-right chevron-up child-work-items clipboard clock close cloud-arrow-up collapse-horizontal collapse-vertical comment-add comment commit compass component content-width-narrow content-width-wide content-wrap-left content-wrap-right copy credit-card cross-circle cross curly-brackets customize dashboard data-flow data-number data-string database decision defect delete department device-mobile devices discovery download drag-handle-horizontal drag-handle-vertical edit-bulk edit email emoji-add emoji-casual emoji-neutral emoji-remove emoji epic error exclamation-square expand-horizontal expand-vertical eye-open-filled eye-open-strikethrough eye-open feed feedback field-alert field-checkbox-group field-dropdown field-radio-group field figma-community figma-component-instance-swap figma-component-instance figma-component figma-slot figma file files filter flag-filled flag flask focus-area folder-closed folder-open form fullscreen-enter fullscreen-exit glasses globe goal grid grow-diagonal grow-horizontal grow-vertical hashtag headphones heart highlight home image-fullscreen image-inline image-scaled image inbox incident information-circle information key-result layout-one-column layout-three-columns-sidebars layout-three-columns layout-two-columns-sidebar-left layout-two-columns-sidebar-right layout-two-columns library lightbulb link-broken link-external link list-bulleted list-checklist list-numbered lobby-bell location lock-locked lock-unlocked log-in log-out magic-wand markdown marketplace maximize megaphone mention menu merge-failure merge-success microphone minimize minus-square minus node note notification-muted notification objective office-building on-call operations page pages paint-bucket paint-palette panel-left panel-right pen people-group person-add person-added person-avatar person-offboard person-remove person-warning person phone pin-filled pin plus-square power-plug premium presenter-mode printer priority-blocker priority-critical priority-high priority-highest priority-low priority-lowest priority-major priority-medium priority-minor priority-trivial problem project-status project projection-screen pull-request pulse question-circle quotation-block quotation-mark radio-checked radio-unchecked redo refresh release retry roadmap rovo-chat scales scorecard screen-plus screen search send settings shapes share shield-strikethrough shield shortcut show-more-horizontal show-more-vertical shrink-diagonal shrink-horizontal shrink-vertical sidebar-collapse sidebar-expand smart-link-card smart-link-embed smart-link-inline smart-link-list smart-link snippet sort-ascending sort-descending spreadsheet sprint star-starred star-unstarred status-discovery status-error status-information status-success status-verified status-warning stopwatch story stroke-weight-extra-large stroke-weight-large stroke-weight-medium stroke-weight-small subtasks success support table-cell-clear table-cell-merge table-cell-split table-column-add-left table-column-add-right table-column-delete table-column-move-left table-column-move-right table-columns-distribute table-row-add-above table-row-add-below table-row-delete table-row-move-down table-row-move-up table tag takeout-food target task-in-progress task-to-do task tasks teams text-bold text-heading text-indent-left text-indent-right text-italic text-shorten text-spellcheck text-strikethrough text-style text-underline text-wrap text theme thumbs-down thumbs-up timeline tools transition translate tree undo upload vehicle-car video-next-overlay video-next video-pause-overlay video-pause video-play-overlay video-play video-previous-overlay video-previous video-skip-backward-fifteen video-skip-backward-ten video-skip-forward-fifteen video-skip-forward-ten video-stop-overlay video-stop video volume-high volume-low volume-muted warning whiteboard work-item work-items zoom-in zoom-out

### Data visualization

- **Chart chrome:** title uses `--ds-text` with a heading style, tick labels use `--ds-text-subtle` in body-small, gridlines use `--ds-border`, threshold and reference lines use `--ds-chart-neutral`, and the legend uses `--ds-text`.
- **Single series:** use `--ds-chart-brand`. To make one datum stand out, draw the rest in `--ds-chart-neutral`.
- **Categories:** use `--ds-chart-categorical-1…8` in numeric order. Cap at 5–6 colors and group the rest as "Other."
- **Status and severity:** use `--ds-chart-success`/`-warning`/`-danger`/`-information`/`-discovery`. The `-bold` variant marks the more extreme value (for example, Highest vs High priority).
- **Readability:**
  - Chart colors don't reach 3:1 against each other, so separate adjacent marks with a gap or a `--ds-border-inverse` stroke.
  - Never put text on chart colors. Label beside the mark.
  - Add direct labels, shapes or patterns so color isn't the only signal, and offer a table view.
- **Interaction:** on hover, fade the other marks with `opacity: 0.4` (the `opacity.disabled` value).

## Component recipes

These recipes mirror the compiled `@atlaskit` styles. Use real elements (`<button>`, `<a>`, `<input>`, `<label>`) and don't rebuild controls from `<div>`s.

The CSS is in `render_kit/ads.css`. The comment above each component gives its size, radius and tokens.

**Which message component to use.** Banner is for critical, site-wide messages, one at a time. Flag confirms something after an event. Section message covers one area of the page and stays until it's resolved. Inline message is a small contextual hint. Modal is for a blocking short task. Empty state is for "nothing here" moments.

**Button rules.**

- Use one primary button per section. Default and subtle buttons handle secondary actions. Use danger buttons sparingly.
- In modals and forms, put the primary button on the right.
- Use buttons for actions and links for navigation.
- Label buttons with 1–3 word verbs, never "Submit" or "Click here."

## Smart links (required for every link)

Whenever an artifact links to something (a Confluence page, Jira work item, Loom video, whiteboard, database, folder, Bitbucket PR, Google doc or any web page), render it as an **inline smart link**, the way Atlassian products do. An inline smart link is a small bordered chip that sits in the line of text, with a 16px object icon and the object's title in link blue.

**Rules**

- Use it everywhere: in running text, lists, table cells, cards, section messages and "Sources" lists. The only exception is a primary navigation element that is really a button (use a link-styled button there).
- **Show the object's real title, not the URL.** For third-party objects, add the app's name after the title in subtle text ("Search migration plan · Google Docs"), because the icon alone can't say which app it is.
  Use the title you fetched, or the one the person gave. If you only have a URL, fetch the title (with the Atlassian connector or WebFetch). If you still can't get it, show a readable form such as the domain plus the last path segment (`atlassian.design · tokens`). Never make up a title.
- Keep the surrounding punctuation outside the chip: `(from: [chip])`, not `([chip]):`.
- Jira work items show the key before the title (`ENG-142 Fix login redirect`). They can also show a status lozenge after the title when the status is known.
- Match the icon to the object type (table below). For generic web pages, use `globe`.
- The link opens the real URL with `target="_blank" rel="noopener"`. Put the full title in `title=""` so a truncated title can still be read.
- The accessible name is the title. The icon is decorative (`aria-hidden="true"`). For an external link, add visually hidden text such as "(opens in a new tab)".

**Icon per object type** (inline the SVG from `@atlaskit/icon` `svgs/core/`; see Iconography)

| Object | Icon | Icon color |
|---|---|---|
| Confluence page, blog, live doc | `page` | `--ds-icon-accent-blue` |
| Confluence whiteboard | `whiteboard` | `--ds-icon-accent-blue` |
| Confluence database | `database` | `--ds-icon-accent-blue` |
| Confluence folder or space | `folder-closed` | `--ds-icon-accent-blue` |
| Jira work item: task / story / bug / epic / subtask | `task` / `story` / `bug` / `epic` / `subtasks` | task and subtask `--ds-icon-accent-blue`, story `--ds-icon-accent-green`, bug `--ds-icon-accent-red`, epic `--ds-icon-accent-purple` |
| Jira project, board, plan, Atlassian project | `project` / `board` / `timeline` | `--ds-icon-accent-blue` |
| Loom video | `video` | `--ds-icon-accent-purple` |
| Pull request, branch, commit | `pull-request` / `branch` / `commit` | `--ds-icon-subtle` |
| Goal, or a goal's or project's updates (Home) | `goal` / `project-status` | `--ds-icon-accent-teal` |
| Person or team | avatar (16px circle) or `person` / `teams` | `--ds-icon-subtle` |
| Jira Product Discovery idea | `lightbulb` | `--ds-icon-accent-blue` |
| Chat message (Slack, Teams) / chat channel | `comment` / `hashtag` | `--ds-icon-subtle` |
| Third-party doc (Google Docs, SharePoint, Dropbox) | `page` | `--ds-icon-subtle` |
| Third-party issue or ticket (GitHub issue, Zendesk ticket) | `task` | `--ds-icon-accent-blue` |
| Calendar event | `calendar` | `--ds-icon-subtle` |
| Atlassian Artifact, third-party page (Figma) | `page` | `--ds-icon-accent-blue` |
| Any other web page | `globe` | `--ds-icon-subtle` |

ADS has no third-party logos, and hotlinking them isn't allowed, so third-party objects use the object-type icon from the table plus the app name after the title.

**Markup**

```html
<a class="smart-link" href="https://…/wiki/spaces/HUBS/pages/123" target="_blank" rel="noopener"
   title="Hubs Conceptual Model &amp; Team '25 US plan">
  <span class="smart-link__icon smart-link__icon--page" aria-hidden="true"><!-- inline page.svg --></span><span
   class="smart-link__title">Hubs Conceptual Model &amp; Team '25 US plan</span><span class="visually-hidden"> (opens in a new tab)</span></a>

<!-- Jira work item with status -->
<a class="smart-link" href="https://…/browse/ENG-142" target="_blank" rel="noopener" title="ENG-142 Fix login redirect">
  <span class="smart-link__icon smart-link__icon--story" aria-hidden="true"><!-- story.svg --></span><span
   class="smart-link__title">ENG-142 Fix login redirect</span><span class="lozenge lozenge--information smart-link__status">In progress</span></a>
```

**CSS:** `render_kit/links.css`. It mirrors `@atlaskit/smart-card` InlineCard: raised surface, 1px border, radius.medium, link blue, a blue border on hover, and a 2px selected ring on focus.

If the page shows a long list of sources, stack the chips with `display:flex;flex-wrap:wrap;gap:var(--ds-space-100)` and keep each one as the same inline chip. Don't switch to a different card style.

## Live states (artifacts that refresh)

For a live artifact, show where each section's data came from and when:

- **Freshness:** a small line under each section heading in `--ds-text-subtlest` body-small, with the `refresh` icon: "Snapshot from 8:10 AM" or "Live, updated 9:02 AM". Take a live time from when the result was produced, not from the clock when it's shown.
- **Refresh:** one default button with a refresh icon, in the page header or the page's toolbar, labelled "Refresh" or "Refresh from [source]". While a section refreshes, keep its old content visible and show a skeleton only where there's nothing yet. Honour `prefers-reduced-motion`.
- **A tool that's off or failing:** keep the snapshot and add a warning section message in that card, with the fix for that failure and, where there is one, a button for it ("Reconnect Google Calendar using this host's connector settings. Showing the 8:10 AM snapshot."). Each card shows its own failure. Use one page-level message only when every card fails the same way.
- **Waiting for approval:** an information section message, "Needs your approval", with a default button that makes the call.
- **Confirming a write:** a section message, or an inline panel under the item, that states exactly what will change, with a primary button naming the action ("Mark done") and a subtle "Cancel". Never write on the first click.

## Accessibility checklist

- Every control has an accessible name. Icon-only buttons get `aria-label`.
- Don't disable buttons without explaining why. Tooltips on disabled buttons aren't reachable.
- Every input has a visible `<label for>`. Placeholder text never replaces a label. Errors use `aria-invalid` plus `aria-describedby`, with `role="alert"` on the message. Group related inputs in `fieldset`/`legend`.
- Keyboard: every interactive element is reachable by Tab, Enter and Space activate, Esc closes overlays, focus moves into a modal and is trapped there, then returns to the trigger when it closes.
- Focus is always visible (`--ds-border-focused`, 2px, offset 2px).
- Images: alt text under 125 characters that describes purpose. Decorative images get `alt=""`. Never start with "Image of."
- Headings are in order, landmarks (`header`, `nav`, `main`, `aside`) are present, and tabs use `role="tablist"`/`"tab"`/`"tabpanel"` with `aria-selected`.
- Respect `prefers-reduced-motion`. Keep motion short (150–200ms, `--ds-easing-out-practical`).
- Check contrast in both themes. Dark overlays can fail where light mode passes.

## Before publishing

1. Search the stylesheet for raw hex, rgb or px color and spacing values outside `tokens.css`. Replace each one with a token.
2. Toggle `data-theme="dark"` and check surfaces, shadows, lozenges and charts.
3. Check sentence case on every heading and button, and make sure there's only one primary button per area.
4. Check that every link is a smart link with a real title and the right object icon, with no bare URLs or plain text links.
5. Check keyboard-only navigation and the focus rings.
6. Check the layout at 375px (16px gutters, no horizontal scroll) and at 1280px or wider, and check that no table column is squeezed (see the table check below).
7. If no browser is available (headless Chrome often won't start in a sandbox), check the CSS instead, and say in your reply that layout was checked by reading the code:
   - the stylesheet parses: every `/*` has its `*/`, and braces balance once comments are removed. One unclosed comment turns the rest of the stylesheet into a comment, and the page renders unstyled
   - a 16px gutter at phone width, and no fixed widths wider than 343px outside a scrolling wrapper
   - grids use `minmax(0, 1fr)`, and grid and flex children that hold text have `min-width: 0`
   - wide tables and diagrams sit in an `overflow-x: auto` wrapper
   - long titles, chips, URLs and quotes can wrap (`overflow-wrap: anywhere`), except in table cells: there, `anywhere` lets a column shrink to a few letters, so cells use `break-word`, smart links in tables can wrap, and a column of sentences has a `min-width` (the `prose` class)
   - no table column of text is narrower than about 12 characters at 375px, 800px and 1280px. In a browser, measure each column's width, not only the page's scroll width: a squeezed column doesn't overflow the page
   - multi-column layouts collapse to one column at 600px or narrower
   - `.visually-hidden` elements have a positioned ancestor
