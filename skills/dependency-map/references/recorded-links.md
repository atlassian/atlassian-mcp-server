# recorded links

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

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

- Run `search` (`targetApp: THIRD_PARTY`, then `ALL`) with the anchor's short name. Lead with "blocking [short name]", "[short name] blocker" and "[short name] blocked", then try "waiting on" and "depends on", which return more noise. Keep results from the last 30 days, by `lastModified`, and mention any strong older hit in the footer.
- Read the anchor's plan or spec for a dependencies or risks section. Find it from related links and URLs in the project's description and updates, as well as graph links.
- Keep a candidate only if it names a specific team, deliverable or person, and the anchor. Its source is Not recorded. Give it a state from what the message or doc says (Step 5). If it says nothing about progress, its state is Unknown.
