# tool reference

Follow the tool-access and coverage rules in the shared skill entrypoint. Examples name operations; use direct calls when available, otherwise the discovered runner and schema.

## Tools

These are the operation names on version 2 of the Atlassian Rovo MCP server, the only version these skills support (version 1 is being deprecated). Clients prefix them with the connector's name (for example `mcp__atlassian__search`). Connect it using the current agent host's documented MCP setup. Access to tools in a conversation does not imply access from an artifact; check the host's live-artifact capabilities separately (see [publication](publication.md)).

### Teamwork Graph tools

| Tool | Use it to | Know this |
| --- | --- | --- |
| `getGraphContext` | Walk from one object to everything linked to it, across Atlassian and connected tools, in one call. Filter with `relationshipTypes`, `targetObjectTypes` and `timeRange`. | Direction is only in the relationship name, and same-type names don't all read the same way. Some links are missing or one-sided, and Atlas project and goal keys don't resolve. See [graph context](graph-context.md). |
| `getGraphObject` | Read full detail for up to 25 objects at once by ARI or URL. | Full for Atlassian objects and Google Drive docs. Often empty (`raw: {}`) for GitHub, and refused for Slack. Bitbucket pull requests hydrate when passed by the graph ARI (state, approvals, description cut at about 1,000 characters), though `bitbucket.org` URLs don't resolve. Confluence pages come back as raw ADF, which can be huge: use `getConfluenceContent` instead. |
| `search` | Find things the graph hasn't linked. | See "Searching". |
| `getWorkActivity` | What a person or up to 10 people did, were assigned or were mentioned in, across Jira, PRs, docs, goals, calendar and video, over a time window. | Use `countsOnly` when you only need the volume. `topic` can't be combined with `identifiers`. With `identifiers`, trust each item's `ok` over the batch summary, which can count partial coverage as a failure. |
| `getWorkPortfolio` | Projects, goals and focus areas for people, with status. | Large by default, because it includes direct reports. Pass `includeDirectReports: false` unless you need the org, and use `kinds`, `view: compact` and `limitPerCollection`. `includeInferredProjects` can return `SOURCE_FAILURE`. If it does, record the gap and move on. |
| `getPeopleInfo` | Profiles, managers and direct reports. | `manager: true` gives the escalation contact in the same call. Profiles carry a department but no team: take a person's team from the project or work record that names them. |
| `getCollaborators` | Who someone works with most. | |
| `searchCode`, `getCodeFile`, `scanCodeRepo`, `listCodeDirectory` | Search code across connected Bitbucket and GitHub repos (`mode` hybrid, semantic or lexical, filtered by `namespace`, `repo`, `path`, `language`), then read a file, list a repo's paths or browse a directory at a commit. | Use only when exposed or discoverable and permitted. Omitted `products` metadata does not rule out code search. Pass a result's own `workspace`, `repo`, `path` and `version` (as `commitHash`) to the reads, never the search filter. Results are noisy and `getCodeFile` has no line numbers: see "Code and repositories". |

### Product tools

Use these for structured facts, and for detail the graph doesn't carry:

| Need | Tool |
| --- | --- |
| A goal's projects, sub-goals, metric targets, updates and highlights | `getGoal` |
| A project's dependencies, links, teams, updates and highlights | `getProject`, `getProjectUpdate` |
| Jira issue links with direction | `getJiraIssue` with `view: evidence` (`issuelinks[].inwardIssue` and `outwardIssue`) |
| A Jira issue's web links to pages and URLs | `listJiraIssueRemoteIssueLinks` |
| When a Jira field changed (status, assignee) | `listJiraIssueChangelogs` |
| Lists of Jira work by structured criteria | `searchJiraIssuesUsingJql` |
| A Confluence page body | `getConfluenceContent` with `content_format: markdown` and `detail: full` (the default is a short excerpt) |
| A Loom transcript or AI action items | `getLoomVideo` |
| Release approvers, capacity, teams | `getJiraProjectVersions`, `getCapacityPlanAllocations`, `searchTeams` |
| A board's sprints and columns, and a sprint's issues | `getJiraBoardSprintData`, `getJiraBoardConfig` |

- **Connections are paged, 5 at a time by default.** `getGoal` and `getProject` return 5 items per connection (projects, updates, dependencies, highlights and so on) unless you pass `limits` (up to 20 each). Set `limits` for every connection you include, and page while `hasNextPage` is true. A silently truncated list is a wrong answer. The one exception is updates: the latest 5 are enough unless you need older history.
- **JQL results can be very large.** The compact view can still include long descriptions, and large results arrive as a file you parse with a script. Triage first with `fields: ["summary", "status", "created", "project"]` and `maxResults` of 25 to 50, then read descriptions only for the issues you'll use.
- **Content lost in markdown.** The markdown read of a Confluence page drops some content without a trace in the text, and lists only a feature name in `lostFeatures`:
  - `time`: date elements (shown as date lozenges) disappear. On real data a decision register lost all 47 of its dates. Take each date from its `<time datetime="…">` element in the HTML read.
  - `ac:structured-macro` or `ac:adf-extension`: panels (`panel-note`, `panel-custom`) and macros can vanish whole. On real data a page's "Decision" panel, which held the decision itself, was missing from the markdown, and a heading came back with nothing under it.

  When `lostFeatures` lists either, and the page matters to the answer (a decision, a plan, a spec), re-read it with `content_format: html`. Also re-read when a heading has nothing under it, or when a search snippet quotes text that isn't in the markdown body. `diffConfluenceContentVersions` has the same gap: a markdown diff came back empty for a version that added that panel, so diff with `content_format: html` whenever the change you're looking for could be in a panel or a date.
- **Loom lists come back short.** `listLoomObjects` returned 15 items per page, newest first, even with `limit: 25`, so one call over a long `createdAtRange` covers only its last week or two. List a narrow window around the dates that matter, and say in the footer what the list reached. To page, set `createdAtRange.to` to the oldest `createdAt` returned: `nextOffset` came back as 25 after a 15-item page, and following it skipped ten days of recordings. Each item's `description` is usually the AI meeting summary, so list with `responseFields` set to titles, dates and URLs when the titles need a sensitive-content check first, then read the kept ones with one `getLoomObjectsContent` batch (up to 10, no `expand`), which returns `description` too. Its expand value is `agentBrief` (singular, unlike `getLoomVideo`'s `agentBriefs`), and it usually came back `ABSENT`.
- **Latest update:** use `latestUserUpdate` and its `creationDate`, not system-generated updates. Note `missedUpdate: true` when it's set. A bot's update can be typed `USER` too: see "Automation updates".
- **When an operation is not directly exposed and discovery is available,** call `discover` with a verb and object ("get goal updates", "list sprint data"), then run it with the matching `executeRead`, `executeWrite` or `executeDestructive`. Pass `cloudId` as a top-level argument, never inside `inputs`. Never guess an operation name.

### Relationship names

`getGraphContext` returns and filters on underscore names. `addGraphContext` takes hyphenated names. Names seen so far:

| Read with `getGraphContext` | Write with `addGraphContext` |
| --- | --- |
| `jira_work_item_blocks_jira_work_item`, `jira_work_item_is_blocked_by_jira_work_item` | `jira-work-item-blocks-jira-work-item` |
| `jira_work_item_tracks_atlassian_project` | `jira-work-item-tracks-atlassian-project` |
| `jira_work_item_contributes_to_atlassian_goal` | `jira-work-item-contributes-to-atlassian-goal` |
| `jira_work_item_has_child_jira_work_item`, `jira_work_item_has_parent_jira_work_item` | (use the issue's parent field) |
| `jira_work_item_links_jira_work_item_remote_link` | `jira-work-item-links-jira-work-item-remote-link` |
| `atlassian_project_depends_on_atlassian_project`, `atlassian_project_links_atlassian_project` | (use Projects) |
| `atlassian_project_contributes_to_atlassian_goal` | (use `addConnectionsToGoals` with type `PROJECT`) |
| `atlassian_project_has_atlassian_project_update` | |
| `atlassian_user_owns_atlassian_project`, `atlassian_user_contributes_to_atlassian_project` | |

Call `getGraphContext` with `detailLevel: summary` first to see which relationship types an object actually has, then filter the `full` call to the ones you need.

### Vendor connectors

The client may also have connectors from the vendors themselves, such as Google Calendar, Gmail, Google Drive, Slack, GitHub, Microsoft 365 (Outlook, Teams, OneDrive) or Zoom. They show up in the session's tool list under the app's name. Teamwork Graph comes first, because it connects tools and a vendor connector only sees its own app. When available, run the graph's own search or read before reaching for a connector. If the required graph capability is unavailable, that is a known gap an authorized connector can fill. Use a vendor connector only to fill a gap the graph has, and say in the footer which gap it filled:

| Gap in Teamwork Graph | Use the vendor connector to |
| --- | --- |
| Lists by time. `getWorkActivity` windows on when a relationship last changed, recurring meetings have no daily instances, and `search` has no date filter. | List a day's calendar events. For email and chat, filter graph search results by `lastModified` first, and use the connector's date operators (such as `newer_than:1d` or `after:2026-10-18`) only when that came back empty or too thin to trust. |
| Third-party objects that won't hydrate (Slack messages left out of `getGraphObject`, GitHub `raw: {}`, Drive docs with no body). | Read the full thread, replies, pull request body and reviews, or doc, instead of settling for the search snippet. |
| Facts only the vendor holds. | Read RSVPs, recurrence and attendee lists for meetings, whole email threads, and file revision history. |

- **Read-only.** Never create, edit, send, reply, accept, decline or share through a vendor connector unless the skill's job is that write and the user confirms it, as "Writes" describes.
- **Sensitive content applies, more strictly.** Vendor connectors see private and group messages, personal email and personal calendar entries that Teamwork Graph may not index. Don't read private messages or personal email unless the user asks. Drop leave, out-of-office and personal events by title before reading them.
- **Same access only.** Never use a vendor connector to reach something the user can't otherwise see, or to get around a denied permission.
- **Links can carry personal data.** A Google Calendar event's `htmlLink` encodes the calendar owner's email address in its `eid`. Don't use it as a smart link: name the event in plain text, or link the day view.
- **Label and report as usual.** Chips name the app ("Google Calendar", "Slack"). The footer lists vendor connectors with the other apps searched, and says which gap each one filled.
- **If it's missing,** carry on with Teamwork Graph, say what the gap cost (for example "Recurring meetings are missing"), and suggest connecting the vendor connector. If the client can suggest connectors, use that.
- **Tool names differ by client.** Read the connector's tools and schemas in the session before calling it, and don't guess names. Bound the calls as you would for `search`.

### Setup

- Call `getAccessibleAtlassianResources` once per session and reuse the `cloudId`. Keep `products` metadata when present, but confirm exposed/discoverable operations and access. Its absence means unknown availability.
- Call `atlassianUserInfo` once if the skill needs the current user's account ID.
- `getGraphContext`, `search` and the people tools can each use Rovo credits, so keep calls bounded. Unless a skill sets its own budget, aim for no more than 10 `search` calls and 10 `getGraphContext` calls per run. If a call fails because credits are exhausted, tell the user and stop. Don't retry.

### Fetch in parallel

Most of a run's time goes on calls made one after another. Before each step, list the calls whose inputs you already have, and send them together in one turn: lookups for each person, each candidate video or doc, each search phrasing, and reads of goals and projects already found. Wait only for the calls the next step needs. Calls that don't depend on each other can run together even when they sit in different steps of a skill.

- **Batch first, parallelise second.** One `getGraphObject` call for up to 25 objects beats 25 parallel calls. The same goes for one JQL `key in (...)` query, or `getPeopleInfo` with up to 10 account IDs.
- **Parallel doesn't raise the budget.** Send together only calls you'd make anyway. Don't fire every possible search at once in case one helps.
- **Handle each result on its own.** One failed call doesn't stop the rest. Record its gap as usual. A 429 (rate limited) after a large batch isn't a gap: wait a few seconds, retry that call once, and send smaller batches from then on. On real data, a `getProject` call straight after a batch of 7 parallel calls returned 429 twice.
- **Check each result for sensitive content** before using it, however many arrived together.

## Searching

- **Use the v2 search schema.** Pass `cloudId`, `query` and optional `targetApp` (`THIRD_PARTY`, `JIRA`, `CONFLUENCE` or `ALL`) and `limit` (10 to 30). There is no `mode` parameter.
- **There's no date filter.** Filter results by `lastModified` after the search, and state the window in the footer. For a strict time window ("since yesterday"), filter the graph results first, and add the vendor connector's own search where the client has one only if that isn't enough (see "Vendor connectors"). Know what the date means per source: GitHub's is last updated, not opened, and a page's is last edited, not written. If a strong hit falls just outside the window, mention it in the footer rather than dropping it silently.
- **The product records can filter by date, even though search can't.** For a window over Atlassian work, list it from the records first: JQL (`updated >= "2026-10-06"`, `status CHANGED DURING (…)`, `resolved >=`), CQL through `searchConfluence` (`lastmodified >= "2026-10-06"` and `created >=` filter the window reliably, but results carry only relative `lastModified` text such as "about 4 hours ago", and `expand` is ignored, so mark pages as new with a separate `created >=` query and take exact edit dates from `listConfluenceContentVersions`), `getProject` with `updateFilters`, `listLoomObjects` with `createdAtRange`, and `getPullRequests` with `updatedSince` or `mergedSince`. Keep JQL `CHANGED` clauses beside a `project =` or `assignee =` clause: across a whole site they can time out. Use `search` for what the records don't hold, and filter it by `lastModified`.
- **Results with no date** (projects, components) aren't windowed. Judge them by their own records.
- **Search isn't good at structured Jira.** For Jira work of a known type, project or field (feedback issue types, an epic's children, a fix version), use JQL. Use `search` with `targetApp: JIRA` for fuzzy discovery only.
- **Write strong, distinct queries.** Use 2 to 4 phrasings built from the anchor's name, key terms and people, not lists of synonyms. Short queries (1 to 3 words) often beat long ones. Lead with the distinctive term, not the company or product-family word.
- **JQL text search matches words, not phrases.** `text ~ "Atlassian MCP"` matches either word, and `text` also searches comments. For a phrase, quote it inside the string (`text ~ "\"Atlassian MCP\""`). For precision, use `summary ~` and `description ~` once you know the project.
- **Follow links in snippets.** Chat messages often link the page that matters, such as an analysis or a decision. Read linked Confluence pages with `getConfluenceContent`.
- **Pass on warnings.** If search says "Some search sources could not be queried", say so in the footer.
