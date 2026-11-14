# Building the map by hand

Use this only when the user has requested an HTML report and Python can't run. Load the `atlassian-design` skill and follow its `references/hand-built.md`, including its smart link rules. Then build the same map the renderer would: the sections, their order and what each one holds are in the Build step in this skill's `SKILL.md`, and the layout and the diagram's drawing rules are below. The kit's `render_kit/diagram.py` follows the same rules.

## Layout

- Wide layout, 880px max width, on a `--ds-surface-sunken` background, with a 16px gutter at phone width. It's wider than the 760px reading layout so the wide diagram shows at desktop width, and no other page uses it.
- Flat cards with `heading.xsmall` headings led by an ADS core icon in `--ds-icon-subtle`.
- Support light and dark mode. Check the page at the widths `atlassian-design` gives, with no horizontal scroll.

## The dependency diagram

Draw the dependencies as inline SVG, so the reader sees the shape at a glance: what flows into the anchor, what flows out of it, and where the trouble is.

**Structure**
- Columns from left to right: second-hop upstream, upstream, the anchor, downstream, second-hop downstream. Label every column at the top with the tile words: "Second hop", "Waiting on", "This project" (or "This goal", "This epic"), "Waiting on us". Leave out empty second-hop columns. An empty first-hop column stays, with a dashed placeholder node: "Nothing recorded downstream".
- Arrows point the way work flows, from the dependency to the work waiting on it. Upstream → anchor → downstream, and second hop → first hop. A both-ways dependency gets a second, dashed arrow back the other way.
- Compute positions in code; don't place nodes by hand. Use fixed column x positions, rows spaced evenly (node height plus 12px), and the first-hop columns centred vertically on the anchor. Second-hop nodes line up with the node they feed. Spread the arrow ends along the anchor's edge so they don't meet at one point. Size the `viewBox` to fit the tallest column.
- Size columns so the wide diagram fits the card at full page width (about 850px of content at the 880px page width), or the narrow-screen swap will show the vertical version on desktop. With 3 columns, use nodes up to 196px wide, 48px gaps and a 200 to 248px anchor. With 4 columns, use 188px nodes, 36px gaps and a 200px anchor. With all 5, use 150px nodes, 32px gaps and a 180px anchor.
- Keep it readable. Show at most 7 nodes per column, most severe first. Collapse Done dependencies into a single node ("5 done"), and any further On track ones into "+4 on track". A collapsed node links to `#all-deps`, with the accessible name "5 done dependencies, see the list below", and a few lines of script open the `<details>` when it's followed. The full set is in that list.

**Nodes**
- Each node is a rounded rect (6px radius) with a 4px state bar on its left edge. Inside: the title (up to two lines), then a meta line that starts with the state word: "At risk · Team Ledger · Nov 18". If the source isn't Recorded, add it: "At risk · Related · No team · October", "Blocked · Not recorded · Slack". The words are there so the diagram never relies on colour alone.
- **Truncate text in code.** SVG has no `text-overflow`, so estimate widths at 0.55em per character (about 7px at 13px) and cut with an ellipsis. Optionally refine at load time with a short script that uses `getComputedTextLength()`. Put the full title in the node's `<title>` so it shows on hover. The anchor node may wrap its title to two lines.
- The anchor node is wider and taller, with a `--ds-border-selected` outline, a `--ds-background-selected` fill, and its status as a small pill.
- Each node is wrapped in an `<a>` to the object's URL, with the same accessible name as its smart link plus its state.
- **State colours** go on the bar and the arrow: Blocked `--ds-border-danger`, At risk `--ds-border-warning`, On track `--ds-border-success`, Stale handoff `--ds-border-bold`, Done `--ds-border-bold`, Unknown `--ds-border-bold`. These all pass 3:1 contrast against the surface, and `--ds-border` doesn't. The bar always shows state, never source.
- **Source styling:** Not recorded nodes have a dashed outline (`stroke-dasharray: 4 3`). Related and Not recorded arrows are dashed. Recorded nodes and arrows are solid.

**Edges**
- Smooth cubic curves from the right edge of one node to the left edge of the next, with an arrowhead at the waiting end. Use one `<marker>` per state colour, since `context-stroke` isn't supported everywhere.
- Edge colour follows the dependency's state, at 1.5px, or 2px for Blocked. Stale handoff edges are dotted (`stroke-dasharray: 1 3` with round caps), so they don't look the same as Done, which is a thin solid line.

**Styling and theme**
- Style every shape and label with CSS classes that use the `--ds-*` tokens, never hard-coded colours, so the diagram follows light and dark mode with the rest of the page.
- SVG `<text>` can't use the ADS `font` shorthand tokens. Use `font-family: var(--ds-font-family-body)`, the font-weight tokens, and 13px for titles and 12px for meta. 13px is an approved exception for diagrams.

**Narrow screens**
- The wide diagram scales with its container (`width: 100%`, `height: auto`) down to 85% of its natural width (its `viewBox` width), which keeps 13px titles at about 11px. Swap to the vertical version only when the container is narrower than that. Put the diagram in a `<figure>` with `container-type: inline-size`, and have your code write the `@container` rule with that width (for an 896px diagram, `@container (max-width: 762px)`), not a fixed breakpoint.
- Artifacts are often viewed in a frame narrower than the page (an artifact viewer, a site preview or a side panel), so test the wide version at a container about 800px wide as well as at full width.
- **The vertical version** has second-hop upstream at the top, then upstream, the anchor, downstream, and second-hop downstream. Each level is a single column of full-width nodes, labelled like the columns. Draw one neutral arrow between levels, pointing down, rather than one per dependency, which would cross the nodes. The bars and state words carry each dependency's state, and second-hop nodes say which node they feed ("feeds PLAT-221").
- Size it so text stays at 13px and 12px. Give it no `viewBox`, set `width="100%"`, and position shapes in percentages (`width="100%"`, `x1="50%"`). Cut titles to fit a 256px content width (a 320px phone), inset shapes by 1px, and set `overflow: visible`, so strokes at the edges aren't clipped.

**Accessibility**
- Because the nodes are links, give each SVG `role="group"` and `aria-labelledby` pointing at its `<title>` ("Dependencies of [anchor]") and `<desc>` ("7 upstream: 1 at risk, 1 blocked and not recorded, 5 done; nothing recorded downstream"). Don't use `role="img"`, which hides the links from screen readers.
- Below the diagram, an HTML legend shows each state's colour and each source's line style, with names, and says which way the arrows point.
- The "All dependencies as a list" text version carries the same facts, for screen readers and copying.
