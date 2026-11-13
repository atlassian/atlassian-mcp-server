---
name: "dependency-map"
description: "Map what a project, goal, epic, team or service depends on and what depends on it, across teams and tools, using Teamwork Graph and Projects and Jira records. Answers in the conversation first with dependency direction, state and source, blocked or at-risk work, stale handoffs, unrecorded dependencies and the owner to contact. Offers an HTML report with the existing SVG dependency diagram on request, and publication only when Atlassian Artifacts is available and requested. Use for dependencies, cross-team blockers, who is waiting on whom, or /dependency-map."
---

# Dependency map

Explain in the conversation, for a piece of work, what it's waiting on, who's waiting on it, which of those links are in trouble, and who to talk to about each. It's written for the person who owns the work and has to chase other teams.

Dependencies live in Projects, Jira links, service catalogues, code and, often, only in a Slack thread. Teamwork Graph helps find them, but its edge names don't all read the same way, it misses some project links, and it skips custom Jira link types. So this skill finds candidates in the graph, then takes direction and status from the product records. The map shows recorded and unrecorded dependencies side by side.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. Its section "What the graph doesn't tell you" matters most here. This file adds what's specific to dependencies.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## Connectors

- **Needed:** Projects or Jira, either one. Projects holds project-to-project dependencies, and Jira holds issue dependency links. With only one on the site (see "Atlassian apps on the site" in `teamwork-graph-context`), map from it and say in the footer which kind of dependency wasn't checked. With neither, say so before building: the map can show only dependencies found by search, all of them Not recorded.
- **Helpful, from Atlassian:** Goals, for goal anchors. Teams, for team anchors. Compass, for service anchors and runtime dependencies. Confluence, for plans with a dependencies or risks section.
- **Helpful, from other tools:** Slack or Teams, for handoffs and blockers discussed only in chat. GitHub or GitLab, for code and pull request dependencies. A service catalogue connected to the graph, for runtime dependencies.
- **Vendor connectors,** as `teamwork-graph-context` describes: Slack or Teams, to read a handoff thread in full and check whether its last question was answered (the chat check for stale handoffs). GitHub or GitLab, to read pull request bodies and reviews that the graph returns empty.

## Two things to record for every dependency

Keep these separate all the way through, from gathering to the diagram.

- **State:** how it's going. One of Blocked, At risk, Stale handoff, On track, Done or Unknown (see Step 5).
- **Source:** how you know it exists.
  - **Recorded:** a DEPENDS_ON or DEPENDED_BY link, or a Jira dependency link, including a custom type, whose meaning and direction are confirmed.
  - **Related:** a RELATED link whose direction comes from another record.
  - **Not recorded:** found only in chat, a doc or a search.

A Not recorded dependency can be Blocked. If chat says it's blocking, it's Blocked and goes in Needs attention, labelled with where it came from ("from Slack, not recorded").

## Step 1: Resolve the anchor

| The user gives you | Anchor | Resolve with | Scope of "our work" |
| --- | --- | --- | --- |
| An Atlassian project | `AtlassianProject` | `getProject` (use the returned URL or ARI for graph calls) | The project and its tracked Jira work |
| A goal | `AtlassianGoal` | `getGoal` with `limits: {projects: 20}` | Its linked projects, each treated as a project anchor (up to 5) |
| An epic or work item | `JiraWorkItem` | The key | It and its children |
| A Jira space or board | `JiraSpace` | The key | Open epics, plus work due in the next 6 weeks |
| A team | `AtlassianTeam` | `searchTeams`, then the team's projects | Its active projects (up to 5) |
| A service or component | `CompassComponent` or `ExternalService` | The URL or ARI | The service itself |

Capture the anchor's owner, team (from the record's teams field), short name (the words people use for it in chat), and **need-by date**: the target date, due date or sprint end the anchor is working towards.
- **A month or quarter target** ("October") means the end of that range. Say so: "October, no day set".
- **A need-by date that has already passed** while the anchor isn't done is a finding in itself. Show "passed" in the header. Under the header meta, summarise the anchor's date history from its updates, since each update carries the previous target date ("The target has moved 8 times: May 14, Jul 3 ... Oct 16").
- **No date:** say so. "At risk" checks then use dependency dates and staleness only.

## Step 2: Find the edges

Collect edges from each source below. For each one, record which side waits, its source (Recorded, Related or Not recorded), and the record it came from.

### Project to project (project anchors)

- Call `getProject` with `include: ["dependencies", "links", "teams", "updates", "highlights"]` and `limits: {dependencies: 20, links: 20, updates: 5, highlights: 20}`. Don't filter by `linkType`. Split the links into work tracking and related yourself, because related links often hold the plan and other docs. This is the source of truth.
  - `DEPENDS_ON`: the anchor waits on the other project (upstream).
  - `DEPENDED_BY`: the other project waits on the anchor (downstream).
  - `RELATED`: no direction. Read the other project's updates and decision highlights too (`getProject` with `include: ["updates", "highlights"]`, `highlightType: DECISION`). Place it only when a record says which side waits, such as an update ("ship once upload is live") or a decision. Label it Related, and cite the record that gave the direction. Otherwise list it in the footer as related, and leave it off the map.
  - **Both ways:** if records show each side waiting on the other, it's a both-ways dependency. Show it once, on the side that threatens the anchor's date (usually upstream), and say "Both ways" in its meta line. The diagram adds a return arrow, and it counts in both tiles ("1 both ways").
- Cross-check with `getGraphContext` on the project URL (`atlassian_project_depends_on_atlassian_project`, `atlassian_project_links_atlassian_project`). The graph shows depends-on only from the depending side and can miss links. If the counts differ, use `getProject` and say so in the footer.

### Jira dependency links

- Find the anchor's Jira work: work tracking links from `getProject`, `jira_work_item_tracks_atlassian_project` edges in the graph, and their children (up to 50, with JQL `parent in (...)`). A project's tracked epics are part of the project, not an extra hop.
- If the anchor only has placeholders (an item titled "sdf", "test" or similar), also collect the work tracking links and Jira keys from projects linked to it as Related or DEPENDS_ON. Name the projects you used in the footer.
- **Enumerate every issue link on the scoped work.** Batch known keys by site with `searchJiraIssuesUsingJql`, `key in (...)`, `fields: ["summary", "status", "assignee", "project", "issuelinks"]` and `maxResults: 50`, paging with `nextPageToken` until the known scoped work has been read. Keep the scope limits above. Inspect all `issuelinks` entries, including custom types; queries limited to the names "blocks" and "is blocked by" miss them. Use `getJiraIssue` with `view: evidence` when the batch doesn't provide the link details needed to confirm an edge.
- **Read direction from each link's own wording.** For an entry with `outwardIssue`, read "[this item] [type.outward] [other item]"; with `inwardIssue`, read "[this item] [type.inward] [other item]". The other item is upstream when the phrase says "is blocked by", "depends on", "requires" or "is caused by", and downstream for "blocks", "is depended on by", "is required by" or "causes". Generic relates, clones, duplicates and follows links do not establish a dependency. For unfamiliar custom wording, confirm which side waits from the records or ask the user; until confirmed, leave the edge off the map and name the unresolved link type in the footer. An inward or outward field alone does not establish which side waits.
- The graph adds candidates, not direction: it can miss custom link types. Confirm every displayed Jira edge against the product record above. If the graph disagrees, the record wins; say so in the footer. Deduplicate the same recorded link found from both ends.
- Jira keys on other sites follow the rules for Jira keys in text in `teamwork-graph-context`. If one can't be read, list it as unreadable and don't count that work as checked.
- If the anchor has no usable Jira work at all, say so in the footer ("No Jira work is linked to this project, so Jira blockers weren't checked"). Don't imply there are none.

### Services and code

- For service anchors, call `getGraphContext` on the component or service for its dependencies and consumers.
- For project or Jira anchors, reach code only through linked components or the development info on tracked epics. If there's none, say in the footer that services and code weren't checked.

### Which edges to keep

- Always keep project-to-project dependencies.
- For Jira links, keep edges where the other item has a different owner or team. Same-team links appear only if they're blocking.
- Don't skip a dependency because it looks Done. For a project, check the latest user update says it's delivered. For Jira, check it's resolved and, for code, that there's a merged pull request or deployment.

## Step 3: Go one hop further on the ones in trouble

For each upstream dependency that's Blocked, At risk or Stale (see Step 5), check once what it's waiting on, using the same sources as Step 2. This catches second-order blockers ("we're waiting on Search, and Search is waiting on Platform").

Stop at two hops from the anchor. Say so in the footer, and name any edges you didn't follow.

## Step 4: Find dependencies nobody recorded

- Run `search` (STANDARD, `targetApp: THIRD_PARTY`, then `ALL`) with the anchor's short name. Lead with "blocking [short name]", "[short name] blocker" and "[short name] blocked", then try "waiting on" and "depends on", which return more noise. Keep results from the last 30 days, by `lastModified`, and mention any strong older hit in the footer.
- Read the anchor's plan or spec for a dependencies or risks section. Find it from related links and URLs in the project's description and updates, as well as graph links.
- Keep a candidate only if it names a specific team, deliverable or person, and the anchor. Its source is Not recorded. Give it a state from what the message or doc says (Step 5). If it says nothing about progress, its state is Unknown.

## Step 5: Assess each dependency

The `getProject` dependency results already include each linked project's status, target date and owner. Hydrate further only where you need more: `getProject` (`include: ["updates", "teams"]`) for dependencies that aren't Done or need delivery evidence, and `getJiraIssue` for Jira work (status, assignee, due date, sprint or fix version, resolution date).

Give each one a state. Use the rule for its side.

**Upstream** (the anchor waits on it):
- **Blocked:** it's itself blocked (a Blocked status or flag), or the anchor's work is marked blocked by it and it isn't done, or a message says it's blocking.
- **At risk:** it isn't done, and any of these is true: its date (the end of the range for month or quarter targets) is after the need-by date; the need-by date has passed; it has no date while the anchor has one; its own status is At risk or Off track; or it has had no user update or activity in 14 or more days.

**Downstream** (it waits on the anchor):
- **At risk:** the date it needs the anchor by (its own start or target date, or a date it states) is earlier than the anchor's target date, or earlier than today when the anchor's need-by has passed and the anchor isn't done.
- **Blocked:** the anchor's work is blocking it, and it says so.

**Both sides:**
- **Stale handoff:** a recent handoff that nobody picked up. Only test handoffs from the last 30 days.
  - Jira: the blocker was resolved 7 to 30 days ago, and the blocked item's status hasn't changed since. Check with `listJiraIssueChangelogs`.
  - Projects: the dependency was done 7 to 30 days ago, and the anchor hasn't moved forward since. Moving forward means a phase or status change, or a user update that mentions the dependency or reports shipping the work that used it.
  - Either: the link exists but one side has no owner.
  - Chat: if the thread can be read, its last message is an unanswered question more than 7 days old. If it can't be read, list the chat check as not run in the footer.
  - A dependency that was done more than 30 days ago is Done, not stale.
- **On track:** dated before the need-by date and moving.
- **Done:** delivered, with evidence.
- **Unknown:** found but with no information about progress (usually Not recorded).

For each Blocked, At risk or Stale dependency, find:
- **Owner to contact:** the assignee, or the project or service owner. Use `getPeopleInfo` with `manager: true` for their role and their manager, so the user knows where to escalate.
- **Where to reach them:** the Slack or Teams channel where the dependency was discussed, if one was found. Link the channel, or the message in it.
- **What would unblock it**, in one sentence, only if the records or chat say.

Stop gathering when every shown dependency has a state, a source, an owner (or "no owner") and a date (or "no date").

## Step 6: Prepare offers to record what's missing

For each Not recorded dependency, and each Related one with a known direction, prepare the write that fits. Present these offers after the conversational answer, and do not make a write without a yes:
- **Both sides are Jira work items:** `createJiraIssueLink` with type Blocks.
- **Jira to a third-party item** (a GitHub issue, a Slack thread): `createJiraIssueRemoteIssueLink`.
- **A project and a Slack thread or doc:** `addConnectionsToProjects` with type `EXTERNAL_LINK`.
- **Project to project:** there's no MCP write for project dependencies yet. Tell the user which dependency to add in Projects, and on which side.

Show exactly which links you'll create, in which direction, first.

## Answer and offer an export

- Lead with the anchor, need-by date or its absence, dependency counts, and the most important blocked, at-risk or stale dependency with who to contact.
- Show upstream and downstream dependencies in Markdown lists or a table. Say explicitly which work waits on which; keep State and Source separate, retain second-hop and both-ways relationships, and link the evidence. Use the same scope, ranking, counts and caveats as the report below, without generating its SVG diagram or report files.
- Include Needs attention, Not recorded dependencies with their evidence and possible recording actions, and 2 to 4 next steps with the person to contact. Do not turn an inferred dependency into a recorded one.
- In Sources and limitations, retain how far the walk went, edges left unfollowed, related links omitted, unreadable keys, graph/record differences, caps and checks not run. After the result, offer the writes prepared in Step 6 with the exact links and direction; make none without the required confirmation.

Ask whether the user wants this exported to an HTML report. If they have already explicitly requested an export, HTML report or publication, proceed with that requested build without asking again. Otherwise stop here until they answer; a normal invocation of this skill does not request a report. Follow the shared availability and confirmation checks before offering or performing publication.

## Step 7: Build the map (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in this folder:

```bash
python3 <this skill's folder>/render.py map.json dependency-map-<anchor>.html
```

- **The data** has the shape of `example.json` in this folder (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **The keys.** `anchor` is a link plus `{"kind", "status", "owner", "team", "needBy", "passed", "history"}`: `kind` is `project`, `goal` or `epic`, `passed` is true when the need-by date has passed, and `history` is the date history, the last meta item, given only when the need-by date has passed. `dependencies` lists every dependency once, as described below. A Blocked, At risk or Stale one adds `why`, one sentence on what's blocked and why, and `contact`, the "Contact: [person], [role]" line with their manager as "Escalate to" and where to reach them. A Not recorded one adds `evidence`, `{"text", "quote", "link"}`: the sentence, the evidence quoted briefly and its source chip, and `offer`, the offer from Step 6 that fits. `summary` is the 2 or 3 sentences, `generatedFrom` the apps actually used, and `nextSteps` the 2 to 4 actions as `{"text", "from"}`, with the person to talk to in the text and where the step came from in `from` ("From PLAT-221 in Jira").
- **For the HTML report, the renderer counts, ranks and draws.** It counts the tiles and the header lozenges, ranks Needs attention, and computes the diagram's layout. Do not precompute the report's renderer-derived counts or write diagram code yourself. For the conversational answer, count from the assessed dependencies using the same definitions below.
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `references/hand-built.md` in this folder.

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
