# Optional report export

Load this reference only for a requested report or publication. Preserve the findings, condition counts and source gaps from the conversational answer. Run the bundled Python renderer offline with its example and data-format reference; both shared design kits and logos are included. Do not install packages or download assets. Export does not authorize publication. Follow the shared context publication reference for capability checks and consent.

## Step 7: Build the map (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in the skill folder:

```bash
python3 <this skill's folder>/render.py map.json dependency-map-<anchor>.html
```

- **The data** has the shape of `../example.json` beside the skill entrypoint (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **The keys.** `anchor` is a link plus `{"kind", "status", "owner", "team", "needBy", "passed", "history"}`: `kind` is `project`, `goal` or `epic`, `passed` is true when the need-by date has passed, and `history` is the date history, the last meta item, given only when the need-by date has passed. `dependencies` lists every dependency once, as described below. A Blocked, At risk or Stale one adds `why`, one sentence on what's blocked and why, and `contact`, the "Contact: [person], [role]" line with their manager as "Escalate to" and where to reach them. A Not recorded one adds `evidence`, `{"text", "quote", "link"}`: the sentence, the evidence quoted briefly and its source chip, and `offer`, the offer from Step 6 that fits. `summary` is the 2 or 3 sentences, `generatedFrom` the apps actually used, and `nextSteps` the 2 to 4 actions as `{"text", "from"}`, with the person to talk to in the text and where the step came from in `from` ("From PLAT-221 in Jira").
- **For the HTML report, the renderer counts, ranks and draws.** It counts the tiles and the header lozenges, ranks Needs attention, and computes the diagram's layout. Do not precompute the report's renderer-derived counts or write diagram code yourself. For the conversational answer, count from the assessed dependencies using the same definitions below.
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `hand-built.md` beside this reference.

The rules below say what the renderer builds, and what each part of the data must hold.

### What the map holds

Each dependency is a link (`title`, `url`, `icon`, `app`) plus:

- **`side`:** `upstream` (the anchor waits on it) or `downstream` (it waits on the anchor). A second-hop dependency, found in Step 3, has `"hop": 2` and `feeds`, the `id` of the first-hop dependency it feeds, so give that one an `id` (its key works).
- **`state`:** `blocked`, `at-risk`, `stale`, `on-track`, `done` or `unknown`, from Step 5.
- **`source`:** `recorded` (the default), `related` or `not-recorded`. `bothWays: true` when the work also flows the other way.
- **`team`, `date` and `from`:** the team, the date that matters ("Nov 18", "Needs it Nov 1", "Done Oct 2"), and where it came from ("Jira", "Slack").

The diagram puts second-hop upstream, upstream, the anchor, downstream and second-hop downstream in columns, labelled "Second hop", "Waiting on", "This project" (or "This goal", "This epic") and "Waiting on us". Arrows point the way work flows, from the dependency to the work waiting on it, with a second, dashed arrow back for a both-ways dependency. Each column shows at most 7 nodes, most severe first: Done dependencies collapse into one node ("5 done"), and any further ones into "+4 on track", each linking to the list, which holds the full set. An empty first-hop column shows "Nothing recorded downstream" (or upstream). Every node names its state, and its source when it isn't Recorded, so the diagram never relies on colour.

### Sections, in this order

1. **Header** (not a card): eyebrow "Dependency map", the anchor's name as the only `h1`, with the anchor's status lozenge right of it, then a meta line with owner (`person` icon), team (`people-group`) and need-by date (`calendar`), adding "passed" if it has, and last the date history if the need-by has passed. At the right end of the meta line, count lozenges: "1 blocked" (danger), "2 at risk" (warning), each only if the count is above zero.
2. **Summary** (icon `tree`): metric tiles for Waiting on, Waiting on us, Need attention and Not recorded. Waiting on and Waiting on us count every dependency on that side, including Not recorded and Done ones, with a sublabel such as "5 done, 2 open" or "1 both ways". Then 2 or 3 plain sentences on the one or two dependencies that matter most and why, naming teams and people. In small subtlest text underneath, list the apps actually used: "Generated from Projects, Jira and Slack. Check it before sharing."
3. **Map** (icon `link`): the dependency diagram (see "What the map holds"), then a legend, then a collapsed "All dependencies as a list" (`<details id="all-deps">`) with one row per dependency: title smart link, side, state, source, team, date and where it came from.
4. **Needs attention** (icon `priority-blocker`): one row per Blocked, At risk or Stale dependency, whatever its source, most severe first. Each row has a state lozenge, plus a source lozenge if it isn't Recorded. Then one sentence on what's blocked and why, then "Contact: [person], [role]" with their manager as "Escalate to", where to reach them, and a source smart link.
5. **Not recorded** (icon `search`): only if any were found. One row each, with its state, the evidence quoted briefly, the source chip, and the offer from Step 6 that fits ("Add as a Jira link?", "Link this thread to the project?").
6. **Next steps** (icon `arrow-right`): 2 to 4 numbered actions, most urgent first, each with the person to talk to.
7. **Sources footer** (not a card), as `teamwork-graph-context` describes. Include "Followed 2 hops from [anchor]. Did not follow: [edges].", related links left off the map, sub-projects used for Jira work, unreadable keys, differences between the graph and the records, and checks that weren't run.

Lozenges:
- **State:** Blocked = danger, At risk = warning, Stale handoff = neutral, On track = success, Done = neutral, Unknown = neutral.
- **Source** (shown only when the source isn't Recorded): Not recorded = information, Related = discovery, Both ways = discovery.

## When live

Only after the user requests a report or live export, consider a live version if the actual host supports connector-enabled artifacts. Follow "Live artifact" and `live-artifacts.md` in `teamwork-graph-context`, loading only the matching host adapter. Do not assume that agent-side MCP access is available inside page code. With no confirmed runtime, keep the conversational answer or requested static HTML map.

- **Declare:** on the Atlassian connector, `searchJiraIssuesUsingJql` for every Jira dependency on the map, as one `key in (...)` query, and `getGraphObject` for project dependencies, by ARI. Add `executeWrite` only if the page offers the write below, and call it only with `createJiraIssueLink`.
- **Live as the page opens (watched):** each dependency's status, resolution and due date, or its project state and target date. The page then reapplies the state rules in Step 5 that it can compute (Blocked from status, At risk from dates) and redraws the diagram. Stale handoffs need changelogs, so they stay as built.
- **Stays as built:** Not recorded dependencies, which came from search, contacts and next steps.
- **Writes:** "Record this dependency" on a Not recorded row whose two sides are Jira work items, with `executeWrite` and `createJiraIssueLink`, if that tool doesn't need approval for each action. Show the exact link and its direction, wait for a confirm click, call it once, then refresh that row. Otherwise keep the offer in chat.
- **Sharing:** shareable with the anchor's owner and the owners of blocked dependencies.

## Step 8: Deliver the requested report

- Hand over the requested HTML map. Offer a private, read-only Atlassian Artifact only when availability is confirmed as described in `teamwork-graph-context`. Publish only if requested; report export alone does not authorise it. Create a Confluence page instead only if the user asks.
- After an approved publication, offer to share it with the anchor's owner and the owners of blocked dependencies, and share only on request.
- Keep direction, state/source distinctions, unrecorded evidence and limitations from the answer. A live export is separately conditional on the host support described above.
