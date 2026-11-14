---
name: "teamwork-graph-context"
description: "Gather context for a skill from Teamwork Graph through the Atlassian Rovo MCP server, across Atlassian and connected third-party tools such as Slack, Google Drive, GitHub, Zendesk and Salesforce. Falls back on vendor connectors (such as Google Calendar, Gmail or Slack) where the graph has gaps. Labels every source, states every gap, keeps sensitive content out, and confirms structured relationships against product records. Load it from another skill before gathering context, follow that skill's delivery mode, and use its publishing guidance only when publication is requested."
---

# Teamwork Graph context

This is the shared method every skill in this repo uses to gather context and deliver its result. A skill loads it first, then adds what's specific to its job: the anchor, the sources it needs, what the artifact shows and when to stop. Where a skill and this file disagree, the skill wins.

Companion skills mentioned as alternatives or next steps are optional. Check that a suggested skill is installed before offering its slash command. If it is unavailable, describe the next step in ordinary language and use the current host's available capabilities.

## Principles

1. **Use the graph to discover and the records to confirm.** Start from one object in Teamwork Graph and walk its relationships. That's how you find connected work, docs and conversations across tools. For structured facts (dependencies and their direction, linked projects, owners, teams, statuses, dates), the product record is the source of truth. Cross-check, and say when the graph and the record disagree. "What the graph doesn't tell you" lists the known gaps.
2. **Keep sensitive content out.** Search can return HR, performance, legal and other confidential documents even for unrelated queries. Never quote, summarise, cite or title them anywhere. See "Sensitive content".
3. **Third-party sources are first-class.** A Slack thread, a Google Doc or a Zendesk ticket counts as much as a Confluence page or a Jira work item. Never call them fallbacks or rank them below Atlassian sources. Label where each fact came from; don't rank sources by vendor.
4. **Linked and found are different.** A relationship stored in the graph or a product record is confirmed. A search hit that looks related is inferred. Keep them apart in the reasoning and in the artifact.
5. **Never invent.** No made-up titles, owners, dates, statuses, quotes or numbers. If something can't be confirmed, say so.
6. **Say what's missing.** A source that wasn't connected, a search that returned nothing, a record that doesn't exist and a check you couldn't run are all results. Show them.
7. **Read-only by default.** Only write (create, edit, link, comment, post) when the skill's job is the write or the user asks, and confirm first.
8. **Fall back on vendor connectors for what the graph can't do.** When Teamwork Graph and the Atlassian product tools can't answer something a skill needs (a day's meetings, recent email, a full Slack thread), use the vendor's own connector if the client has one. See "Vendor connectors". This is about which tool to call, not how much a source counts: a fact read through a vendor connector counts the same as one from the graph.

## Sensitive content

Searches surface whatever the user can see, and that includes documents nobody wants in a status report. This rule overrides every skill.

- **Never use these, even when they match:** promotion, calibration or performance review material; training, certification or knowledge-check results that name people; compensation, salary, equity or offer details; disciplinary, PIP or termination records; medical, leave or other personal circumstances; legal holds, privileged advice or litigation; security incidents not yet disclosed; M&A, layoffs or other restricted plans.
- **Never use these either, unless the user asks for them:** private and group direct messages, and board or exec-only material. A Slack direct message's title has no channel name ("[Name] in #") and its URL contains `/archives/D`. A group message's channel name starts with `mpdm-`. A channel whose name says leadership, exec, staff or board, or uses a word or abbreviation for them (`leaders`, `leads`, `lt`, `elt`, `slt`), counts as exec-only material whether or not it's private, since search results don't show a channel's privacy.
- **Spot them early.** Titles and snippets often give them away: "calibration", "promo panel", "promotion packet", "level panel", level codes ("P50 to P60", "L4>L5"), "impact bar", "comp review", "PIP", "Knowledge Check" or "Responses" sheets with scores, "offer letter", "legal privileged", "confidential: do not forward". Don't hydrate a result that looks like one. A page that's otherwise ordinary (a runbook, a design doc) can end in a section that is its author's review or promotion evidence (a closing section headed "… evidence" that isn't test evidence, or one that maps the work to a competency or review criteria): drop that section silently and use the rest.
- **Linked records count too.** A legal or HR project linked to the work can be shown with its status, owner and dates, but never quote its advice or the reasons in its updates. A legal or HR record that's only found by search, such as a counsel review work item that matches the product's name, is left out.
- **When the work is itself a people programme** (a development programme, hiring, a reorg), nearly every result sits next to these categories. Use the programme's design, schedule, owners and actions. Never use participant or candidate lists, who was selected or removed, assessments, ratings, or anyone's level or role move. A notes doc, recording or chat message that mixes the two is usable: drop the sensitive items silently and keep the rest. Results whose titles name the programme (a participant page, a ratings sheet) need the check too. In a footer, say only "Some results weren't used".
- **Leave and absence:** never mention anyone's leave, sickness or time off, even when a work record states it. If it affects delivery, say "reduced capacity until [date]" without the reason.
- **Titles can leak too.** If an object's title contains a financial figure, personal data or an internal identifier (an org ID, an account number), cut that part with an ellipsis everywhere the title appears, including `title=""` attributes.
- **If you read one by accident,** drop it. Don't quote it, cite it, list its title, count it, or mention that it exists, in the artifact, your reply or any log. The one exception is a pilot run's log, which gives a count and how they were spotted, never titles, authors or content.
- **Personal data:** never include email addresses, phone numbers or home locations. Refer to end customers' individual staff by account and role ("Admin at Northwind"), not by name.
- **Customer financials** (revenue, ARR, deal size, renewal dates) appear only if they come from a connected CRM, and only when the skill's job needs them. Figures mentioned in chat or tickets stay out.

## Tools

These are the operation names on version 2 of the Atlassian Rovo MCP server, the only version these skills support (version 1 is being deprecated). Clients prefix them with the connector's name (for example `mcp__atlassian__search`). Connect it using the current agent host's documented MCP setup. Access to tools in a conversation does not imply access from an artifact; check the host's live-artifact capabilities separately (see "Live artifact").

### Teamwork Graph tools

| Tool | Use it to | Know this |
| --- | --- | --- |
| `getGraphContext` | Walk from one object to everything linked to it, across Atlassian and connected tools, in one call. Filter with `relationshipTypes`, `targetObjectTypes` and `timeRange`. | Direction is only in the relationship name, and same-type names don't all read the same way. Some links are missing or one-sided, and Atlas project and goal keys don't resolve. See "What the graph doesn't tell you". |
| `getGraphObject` | Read full detail for up to 25 objects at once by ARI or URL. | Full for Atlassian objects and Google Drive docs. Often empty (`raw: {}`) for GitHub, and refused for Slack. Bitbucket pull requests hydrate when passed by the graph ARI (state, approvals, description cut at about 1,000 characters), though `bitbucket.org` URLs don't resolve. Confluence pages come back as raw ADF, which can be huge: use `getConfluenceContent` instead. |
| `search` | Find things the graph hasn't linked. | See "Searching". |
| `getWorkActivity` | What a person or up to 10 people did, were assigned or were mentioned in, across Jira, PRs, docs, goals, calendar and video, over a time window. | Use `countsOnly` when you only need the volume. `topic` can't be combined with `identifiers`. With `identifiers`, trust each item's `ok` over the batch summary, which can count partial coverage as a failure. |
| `getWorkPortfolio` | Projects, goals and focus areas for people, with status. | Large by default, because it includes direct reports. Pass `includeDirectReports: false` unless you need the org, and use `kinds`, `view: compact` and `limitPerCollection`. `includeInferredProjects` can return `SOURCE_FAILURE`. If it does, record the gap and move on. |
| `getPeopleInfo` | Profiles, managers and direct reports. | `manager: true` gives the escalation contact in the same call. Profiles carry a department but no team: take a person's team from the project or work record that names them. |
| `getCollaborators` | Who someone works with most. | |
| `searchCode`, `getCodeFile`, `scanCodeRepo`, `listCodeDirectory` | Search code across connected Bitbucket and GitHub repos (`mode` hybrid, semantic or lexical, filtered by `namespace`, `repo`, `path`, `language`), then read a file, list a repo's paths or browse a directory at a commit. | Reached through `discover` and run with `executeRead`, only when `code-search` is in the site's `products` list. Pass a result's own `workspace`, `repo`, `path` and `version` (as `commitHash`) to the reads, never the search filter. Results are noisy and `getCodeFile` has no line numbers: see "Code and repositories". |

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
| A board's sprints and columns, and a sprint's issues | `getJiraBoardSprintData`, `getJiraBoardConfig` (through `discover`) |

- **Connections are paged, 5 at a time by default.** `getGoal` and `getProject` return 5 items per connection (projects, updates, dependencies, highlights and so on) unless you pass `limits` (up to 20 each). Set `limits` for every connection you include, and page while `hasNextPage` is true. A silently truncated list is a wrong answer. The one exception is updates: the latest 5 are enough unless you need older history.
- **JQL results can be very large.** The compact view can still include long descriptions, and large results arrive as a file you parse with a script. Triage first with `fields: ["summary", "status", "created", "project"]` and `maxResults` of 25 to 50, then read descriptions only for the issues you'll use.
- **Content lost in markdown.** The markdown read of a Confluence page drops some content without a trace in the text, and lists only a feature name in `lostFeatures`:
  - `time`: date elements (shown as date lozenges) disappear. On real data a decision register lost all 47 of its dates. Take each date from its `<time datetime="…">` element in the HTML read.
  - `ac:structured-macro` or `ac:adf-extension`: panels (`panel-note`, `panel-custom`) and macros can vanish whole. On real data a page's "Decision" panel, which held the decision itself, was missing from the markdown, and a heading came back with nothing under it.

  When `lostFeatures` lists either, and the page matters to the answer (a decision, a plan, a spec), re-read it with `content_format: html`. Also re-read when a heading has nothing under it, or when a search snippet quotes text that isn't in the markdown body. `diffConfluenceContentVersions` has the same gap: a markdown diff came back empty for a version that added that panel, so diff with `content_format: html` whenever the change you're looking for could be in a panel or a date.
- **Loom lists come back short.** `listLoomObjects` returned 15 items per page, newest first, even with `limit: 25`, so one call over a long `createdAtRange` covers only its last week or two. List a narrow window around the dates that matter, and say in the footer what the list reached. To page, set `createdAtRange.to` to the oldest `createdAt` returned: `nextOffset` came back as 25 after a 15-item page, and following it skipped ten days of recordings. Each item's `description` is usually the AI meeting summary, so list with `responseFields` set to titles, dates and URLs when the titles need a sensitive-content check first, then read the kept ones with one `getLoomObjectsContent` batch (up to 10, no `expand`), which returns `description` too. Its expand value is `agentBrief` (singular, unlike `getLoomVideo`'s `agentBriefs`), and it usually came back `ABSENT`.
- **Latest update:** use `latestUserUpdate` and its `creationDate`, not system-generated updates. Note `missedUpdate: true` when it's set. A bot's update can be typed `USER` too: see "Automation updates".
- **When an operation isn't in the tool list,** call `discover` with a verb and object ("get goal updates", "list sprint data"), then run it with the matching `executeRead`, `executeWrite` or `executeDestructive`. Pass `cloudId` as a top-level argument, never inside `inputs`. Never guess an operation name.

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

The client may also have connectors from the vendors themselves, such as Google Calendar, Gmail, Google Drive, Slack, GitHub, Microsoft 365 (Outlook, Teams, OneDrive) or Zoom. They show up in the session's tool list under the app's name. Teamwork Graph comes first, because it connects tools and a vendor connector only sees its own app. Always run the graph's own search or read before reaching for a connector, even for an app that has one. Use a vendor connector only to fill a gap the graph has, and say in the footer which gap it filled:

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

- Call `getAccessibleAtlassianResources` once per session and reuse the `cloudId`. Keep the site's `products` list too: it says which Atlassian apps the user can use on the site (see "Atlassian apps on the site").
- Call `atlassianUserInfo` once if the skill needs the current user's account ID.
- `getGraphContext`, `search` and the people tools can each use Rovo credits, so keep calls bounded. Unless a skill sets its own budget, aim for no more than 10 `search` calls and 10 `getGraphContext` calls per run. If a call fails because credits are exhausted, tell the user and stop. Don't retry.

### Fetch in parallel

Most of a run's time goes on calls made one after another. Before each step, list the calls whose inputs you already have, and send them together in one turn: lookups for each person, each candidate video or doc, each search phrasing, and reads of goals and projects already found. Wait only for the calls the next step needs. Calls that don't depend on each other can run together even when they sit in different steps of a skill.

- **Batch first, parallelise second.** One `getGraphObject` call for up to 25 objects beats 25 parallel calls. The same goes for one JQL `key in (...)` query, or `getPeopleInfo` with up to 10 account IDs.
- **Parallel doesn't raise the budget.** Send together only calls you'd make anyway. Don't fire every possible search at once in case one helps.
- **Handle each result on its own.** One failed call doesn't stop the rest. Record its gap as usual. A 429 (rate limited) after a large batch isn't a gap: wait a few seconds, retry that call once, and send smaller batches from then on. On real data, a `getProject` call straight after a batch of 7 parallel calls returned 429 twice.
- **Check each result for sensitive content** before using it, however many arrived together.

## Searching

- **Default to `mode: STANDARD` with a `targetApp`.** `targetApp` only filters in STANDARD mode: `THIRD_PARTY` for connected tools, `JIRA`, `CONFLUENCE`, or `ALL`. `limit` takes 10 to 30.
- **ENHANCED and AGENTIC are optional extras.** They return ranked citations or a synthesised answer, but they ignore `targetApp`, and they may be disabled for the site ("Agentic search is not enabled", 403). If one fails, carry on with STANDARD and don't mention it unless it changes coverage.
- **There's no date filter.** Filter results by `lastModified` after the search, and state the window in the footer. For a strict time window ("since yesterday"), filter the graph results first, and add the vendor connector's own search where the client has one only if that isn't enough (see "Vendor connectors"). Know what the date means per source: GitHub's is last updated, not opened, and a page's is last edited, not written. If a strong hit falls just outside the window, mention it in the footer rather than dropping it silently.
- **The product records can filter by date, even though search can't.** For a window over Atlassian work, list it from the records first: JQL (`updated >= "2026-10-06"`, `status CHANGED DURING (…)`, `resolved >=`), CQL through `searchConfluence` (`lastmodified >= "2026-10-06"` and `created >=` filter the window reliably, but results carry only relative `lastModified` text such as "about 4 hours ago", and `expand` is ignored, so mark pages as new with a separate `created >=` query and take exact edit dates from `listConfluenceContentVersions`), `getProject` with `updateFilters`, `listLoomObjects` with `createdAtRange`, and `getPullRequests` with `updatedSince` or `mergedSince`. Keep JQL `CHANGED` clauses beside a `project =` or `assignee =` clause: across a whole site they can time out. Use `search` for what the records don't hold, and filter it by `lastModified`.
- **Results with no date** (projects, components) aren't windowed. Judge them by their own records.
- **Search isn't good at structured Jira.** For Jira work of a known type, project or field (feedback issue types, an epic's children, a fix version), use JQL. Use `search` with `targetApp: JIRA` for fuzzy discovery only.
- **Write strong, distinct queries.** Use 2 to 4 phrasings built from the anchor's name, key terms and people, not lists of synonyms. Short queries (1 to 3 words) often beat long ones. Lead with the distinctive term, not the company or product-family word.
- **JQL text search matches words, not phrases.** `text ~ "Atlassian MCP"` matches either word, and `text` also searches comments. For a phrase, quote it inside the string (`text ~ "\"Atlassian MCP\""`). For precision, use `summary ~` and `description ~` once you know the project.
- **Follow links in snippets.** Chat messages often link the page that matters, such as an analysis or a decision. Read linked Confluence pages with `getConfluenceContent`.
- **Pass on warnings.** If search says "Some search sources could not be queried", say so in the footer.

## Dating events in a window

For a skill that covers a window ("since the last update", "while I was away"), each item gets one **event time**, the moment the thing happened, from this table. An item is in the window only if its event time is.

| Source | Event time |
| --- | --- |
| Jira status, assignee, due date or priority change | The changelog entry's `created` |
| Jira work item created or resolved | `created` or `resolutiondate` |
| Comment (Jira, Confluence, Loom) | The comment's created time |
| Confluence page edit | The `createdAt` of the version that made the change. When a diff spans many versions and the change can't be pinned to one, show the range ("edited Oct 7 to Oct 21") |
| Project or goal update, or highlight | Its `creationDate` |
| Pull request | `mergedAt`, or `createdAt` for a new one |
| Meeting | Its start time |
| Loom recording | Its creation time |
| Third-party search result | `lastModified`, which is the last edit, so it can say "updated" but never "new" |

- **Jira's `updated` and a page's last-modified date are not events.** A bot, a resync or a later edit moves them. Use them only to pick candidates, then read the history for the event.
- **"New" needs a creation date inside the window.** A page created before the window and edited during it is Updated.
- **Date a page from its versions** (`listConfluenceContentVersions`), never from `getConfluenceContent` metadata: on a live doc, `version.createdAt` came back as the time of the read.
- **Items with no date** (a project with no update, a result with `lastModified: null`) aren't windowed. Judge them by their own record, and never present them as new.

## What the graph doesn't tell you

These gaps showed up on real data. Work around them as described, and say in the footer when one affected the result.

- **Direction.** There's no direction field. The relationship name carries it. When the two object types differ, the name says which is which: `atlassian_user_owns_atlassian_project` means the user owns the project, from either end. When they're the same type, the reading depends on the relationship:
  - `jira_work_item_blocks_jira_work_item`: the target blocks the queried item (upstream).
  - `jira_work_item_is_blocked_by_jira_work_item`: the target is blocked by the queried item (downstream).
  - `atlassian_project_depends_on_atlassian_project`: the queried project depends on the target (upstream). This one reads the other way round.

  For any other same-type name, check it from both ends before trusting it. The graph also indexes only Jira's standard Blocks link type: a site's own blocker link type (one named "Blocker", say) doesn't appear at all. So use the graph's Jira edges as candidates and a cross-check, and confirm every Jira dependency with `getJiraIssue` (`view: evidence`): an `inwardIssue` on a Blocks link blocks this issue (upstream), and an `outwardIssue` is blocked by it (downstream). For many items at once, JQL with `fields: ["summary", "status", "issuelinks"]` returns the same `inwardIssue` and `outwardIssue` entries in one call. On a large site, `view: evidence` returns every custom field (about 25,000 characters per issue), so pass an explicit `fields` list when you only need links.
- **Project dependencies.** `atlassian_project_depends_on_atlassian_project` shows only on the depending project, and some project links are missing from the graph entirely. For project-to-project edges, use `getProject` with `include: ["dependencies"]` and `limits: {dependencies: 20}`. It returns `linkType` relative to the queried project: `DEPENDS_ON` (it waits on the other), `DEPENDED_BY` (the other waits on it) or `RELATED` (no direction).
- **Work under Atlas projects.** Project nodes often carry no work items, pull requests, deployments or docs. Get a project's work from `getProject` with `include: ["links"]` and `linkType: WORK_TRACKING`, from Jira work that tracks it, and from Jira keys and URLs in its update notes.
- **Docs linked by URL only.** Plans and specs are often just a URL in a goal or project description or update, with no graph edge. Read Confluence, Google Docs and SharePoint URLs from descriptions and updates. The same goes the other way: a Confluence page's own links to Jira items, docs and projects aren't edges (a launch plan's graph context held only people, comments and related pages), so parse the page for them, and read an epic's linked docs with `listJiraIssueRemoteIssueLinks`, since a `getGraphContext` summary gives only their count.
- **Teams and owners.** If the graph and the product record list different teams or owners, the product record wins.
- **Automation updates.** Governance and cleanup bots post project and goal updates typed `updateType: USER` (one cancelled a live project as abandoned), so `updateType: USER` doesn't mean a person wrote it, and `latestUserUpdate` can be a bot's. Read the creator and the text (an automation account named like `…-bot`, wording such as "deemed abandoned") before attributing a status change to someone. Treat such an update as a system update when finding the last update a person wrote, and say so. Bots also appear among followers.
- **Resolving anchors.** Atlas project and goal keys (`ATLAS-123`) don't resolve in `getGraphContext`. Pass the home.atlassian.com URL or the ARI, which you get from `getProject` or `getGoal`. Jira keys do resolve.
- **Calendars.** A recurring meeting is stored as its first occurrence plus any instance someone edited, with no recurrence rule, and `getWorkActivity` windows on when the invite last changed. So Teamwork Graph can't list a day's or a week's meetings. On real data, all 602 events from a 60-day window included only one of the next day's meetings. Events also carry only attendee and creator edges, with no links to notes, recordings or other occurrences, and the calendar connector's event URLs don't resolve in the graph. Take meetings, attendees, responses and earlier instances from the calendar's own connector (see "Vendor connectors"), and find notes and recordings by search.
- **Recency.** Neither `search` nor `getWorkActivity` can list what arrived in a window: search ranks by relevance, and activity windows on relationship changes. For "since yesterday" in chat or email, run the graph search and keep results whose `lastModified` is inside the window. Add the vendor connector only when that isn't enough.
- **Notifications.** The Rovo MCP server has no notifications inbox for any app. Activity on the user's own work comes from `getWorkActivity`, product reads such as Loom comments, and search. Don't claim to cover notifications.
- **Accounts.** `ExternalOrganisation` doesn't resolve by name. Use it only with an ARI that came back from a result or an edge.
- **Sprints.** The graph has no sprint node: `getGraphContext` with `JiraSprint` returns "Node type for ATI 'ati:cloud:jira-software:sprint' not found", and a sprint ID doesn't resolve. Read sprints from Jira (`getJiraBoardSprintData`), and the work in them from JQL (`sprint = <id>`). JQL history searches don't support the sprint field, so when an item joined or left a sprint comes only from `listJiraIssueChangelogs`.
- **Code and repositories.** Code search is useful, but it needs handling:
  - **Filter the noise first.** Natural-language searches can return mostly forks of open-source projects, vendored and generated files, dictionaries, changelogs, test data and other products that use the same words. On real data, a whole first round was noise. Drop results by path and workspace before reading anything, then retry with `namespace` set to the organisation's own workspaces (the non-fork one beside a forks organisation). Never conclude "not in the code" before that retry.
  - **Line numbers come from search.** `getCodeFile` returns a file as one string with no line numbers, and counting by eye drifts. Cite a chunk's `lineRange` or a lexical result's `matchedLineNumbers`, and run a lexical search with the file's `path` to pin other lines. Never retype a file to number it.
  - **Link the read, not the result.** Some results link a branch (`/src/master/`) or the repository root. Use `getCodeFile`'s `externalUrl`, which is pinned to the commit.
  - **No dates or history.** Results carry a commit hash with no date, and there's no file history. Say when the code was read, never when the commit was made. A changelog in the repo is the only change history.
  - **Repositories link only to code activity.** A GitHub repository now carries pull request, commit and branch edges (`external_repository_has_external_pull_request` and others), but no edge to an Atlassian project, team or owner, and a Bitbucket repository URL doesn't resolve. So walk from a repository only to its pull requests, never to find who owns it or what it's for. Read its owner from files in the repo instead (a `compass.yml` `ownerId` team ARI, resolved with `getTeam`, a manifest's team field, or `CODEOWNERS`), and say it was declared there.
- **Jira keys in text.** A bare key in a record on this site (a project update, a Jira comment) can be read when its project key fits the team or site. Check that the returned summary or epic matches what the text describes. Read a key range ("PROJ-120 to 148") with one JQL query (`key >= PROJ-120 AND key <= PROJ-148`). A key quoted in a doc may belong to another site, where the same key can be a different issue. Resolve those only from a URL that includes the host, passing the site URL as `cloudId`. If access isn't granted, list the item in the footer as unreadable, and don't count that work as checked.

## The context loop

### 1. Resolve the anchor

Every skill starts from one object, or a small set of the same kind. Work out what the user gave you, resolve it, and confirm it's the right one before going further.

| The user gives you | `objectType` | Resolve with |
| --- | --- | --- |
| A meeting or calendar invite | `ExternalCalendarEvent` (`LoomMeeting`, `LoomMeetingRecurrence` for Loom) | The calendar's own connector (see "Calendars"). In the graph, `getWorkActivity` with `types: calendar` and `activity: all` |
| A Jira work item, release or project | `JiraWorkItem`, `JiraVersion`, `JiraSpace` | The key or URL |
| A Jira sprint | None in the graph (see "Sprints") | `getJiraBoardSprintData` with the board and the sprint's name or ID |
| An Atlassian project or goal | `AtlassianProject`, `AtlassianGoal` | `getProject` or `getGoal`, then the returned ARI or URL |
| A focus area | `FocusFocusArea` | `getFocusArea` |
| A Confluence page, whiteboard or database | `ConfluencePage`, `ConfluenceWhiteboard`, `ConfluenceDatabase` | The URL |
| A person or team | `AtlassianUser`, `AtlassianTeam` | `getPeopleInfo`, `searchTeams` |
| A service or component | `CompassComponent`, `ExternalService` | The URL or ARI |
| A pull request, repo, deployment or design | `ExternalPullRequest`, `ExternalRepository`, `ExternalDeployment`, `ExternalDesign` | The URL. A repository links only to its pull requests, commits and branches (see "Code and repositories"), so start from its code with code search to find what it does or who owns it |
| A Slack or Teams thread | `ExternalConversation` | The URL (may not resolve; see "Hydrate") |
| A Google Drive, SharePoint or Dropbox doc | `ExternalDocument` | The URL |
| A customer account | `ExternalOrganisation` | An ARI from a result only |
| A CMDB object | `AssetsObject` | The key or URL |
| A Loom video | `LoomVideo` | The share URL |

- **A name or topic:** run `search` (STANDARD), compare the plausible candidates by scope, recency and how central they are, and pick one. If two are equally plausible, ask. Don't merge two same-named things.
- **Nothing ("my next meeting", "my week"):** use `getWorkActivity` with `scope: me`.
- If the anchor can't be found, stop and say so. Don't build an artifact around a guess.

### 2. Expand from the anchor

- Call `getGraphContext` on the anchor with `detailLevel: summary`, then `full` only for the relationship types the artifact needs. For anything about change ("since last time", "while I was away"), pass `timeRange`.
- Expand by relationship role, not by count. Follow the edges that can change the answer: parent, blocker, dependent, linked doc, PR, deployment, conversation, owner. Skip the rest.
- **Confirm structured relationships against the record,** as "What the graph doesn't tell you" describes. When the counts differ (the graph shows 4 project links and Projects shows 5), use the record and say so in the footer.
- Go at most two hops from the anchor unless the skill says otherwise. Say where you stopped.

### 3. Sweep for what isn't linked

Much of the useful context, such as a decision in Slack or a customer complaint in Zendesk, was never linked to anything. After expanding, run 2 to 4 searches as "Searching" describes. Keep a hit only if it's clearly about the anchor (same names, keys, people or dates), and mark it as found by search.

### 4. Hydrate

- Read the objects you'll actually show, batching up to 25 per `getGraphObject` call. Use the product tool where the table above names one.
- **When a third-party object won't hydrate** (empty `raw`, "excluded", missing from the response, or a URL that doesn't resolve), read it with the vendor's connector if the client has one. Otherwise the search snippet is the citable text. Quote only words inside the snippet, trim at its ellipses, and don't retry. Note in the footer that full threads, replies or attachments weren't read.

### 5. Bring in people

- `getPeopleInfo` for names, roles and managers. `getWorkActivity` for what people did recently. `getCollaborators` and `getWorkPortfolio` for who works on what.
- Reporting lines don't show expertise, and activity shows involvement, not ownership. Say "worked on", not "owns", unless a record names an owner.
- People named as approvers, DRIs, decision makers or owners in a linked record (an escalation, a decision log, the plan) count as owners for that decision.
- Never judge someone's performance from activity data.

### 6. When to stop

- After the first expand and sweep, check the evidence against what the artifact needs (owners, statuses, dates, sources). If it's covered, stop gathering and write.
- Stop when the next call wouldn't change a status, risk, owner, decision or next action. One extra call is fine when it could change the top finding.
- If a call returns the same error twice, record the gap and move on. If access is denied, don't try to route around it.

## Connector coverage

Skills get better with more of the customer's tools connected, so be explicit about coverage.

- Each skill lists the Atlassian apps and connectors it needs in a "Connectors" section, split into **needed** (the skill is weak without them) and **helpful**, and names the vendor connector that fills each gap it hits. Customers have different combinations of Atlassian apps, so list each app by name rather than "the Atlassian connection".
- Notice which apps show up in results. Only check what's connected when it matters and isn't clear from the results.
- If a needed source isn't connected, keep going with what's available. Say what's missing in the artifact's sources footer and in your reply, with a short suggestion to connect it.
- Never write "none found" for a source you didn't search.

### Atlassian apps on the site

Don't assume a site has every Atlassian app. Check before gathering:

- **Read the `products` list** that `getAccessibleAtlassianResources` returns for the site (`jira`, `confluence`, `goals`, `projects`, `loom`, `bitbucket`, `assets`, `focus`, `teams`, `artifacts` and so on). It lists the apps the user can use there, each with an `access` level. `discover` leaves out the operations for an app that isn't in the list.
- **Jira Service Management and Jira Product Discovery** sit under `jira`, though some sites list Jira Service Management as its own `jsm` entry. Only if a skill needs one, check with a single JQL call, `projectType = service_desk` or `projectType = product_discovery`, with `maxResults: 1` and `fields: ["project"]`. No results means the user has no projects of that type. On a large site that check can time out: then take the type from `projectTypeKey` in `listJiraProjects` results instead.
- **When an app isn't in the list,** skip the steps and calls that use it. Don't call its tools to find out. If a needed app is missing, say so before building, and say what the result can still show. Never infer "nothing found" from an app that isn't there.
- **Being in the list isn't the same as being used.** A site can have Goals or Projects with nothing recorded. When an app is present but empty for this anchor, say "No goals recorded" (or similar), not that the app is missing.
- **Report it in the footer** as a muted tag, "Not available on this site", separate from "Not connected" and "No results from". "Not available" can mean the site doesn't have the app or the user has no access to it. The list doesn't say which, so don't claim either.

### Third-party apps

- No MCP tool lists which third-party apps are connected to Teamwork Graph. (Vendor connectors in the client are visible as tools in the session.) Use "Not connected" only when you know it (the user said so, or a tool error says so). Otherwise, an app that never appeared is listed as "No results from", whether it's needed or helpful.

## Labelling sources

- Every fact in the artifact links to the object it came from, as a smart link chip with the object's real title and, for third-party objects, the app's name ("Slack", "Google Docs", "GitHub"). Atlassian and third-party chips look the same. Icons follow `atlassian-design`. ADS has no third-party logos, so use the object-type icon (`comment` for a chat message, `hashtag` for a channel, `page` for a doc, `pull-request` for a PR, `calendar` for an event, `globe` for anything else).
- **Found by search** marks an item whose relationship to the anchor is inferred: it has a dashed border and a "Found by search" label inside the chip. When nearly everything in an artifact comes from search by design (a feedback explorer, for example), don't label every chip. Say once in the footer that items were found by search, and mark the few that are linked instead.
- When a work fact comes from chat, email or a call rather than a record, say so in the text ("according to Marco in Slack"). Colleagues can be named this way. End customers' individual staff can't (see "Sensitive content").
- The "Generated from" line under a summary lists the apps actually used, not a fixed list.
- Project and goal updates have no title. Show them as "[KEY] update, [date]" ("ATLAS-123 update, Oct 16, 2026").
- Every artifact ends with a sources footer showing:
  - the apps searched, as tags
  - Atlassian apps the skill uses that aren't in the site's `products` list, as muted tags labelled "Not available on this site"
  - apps known not to be connected, as muted tags labelled "Not connected", and apps with no results, as "No results from"
  - a search or check you chose not to run, or couldn't, as "Not run: [reason]". Never write "weren't searched" without saying why, and never imply a skipped check was a data gap
  - gaps from "What the graph doesn't tell you" that affected the result, checks that couldn't be run, and search warnings
  - the window searched, and how far the walk went
  - when the artifact was prepared, as a relative time plus the absolute date, time and timezone

## Copy

- No em dashes or en dashes in your own copy, and sentence case everywhere. Quotes and object titles are exempt: keep them as written, or trim with an ellipsis. The title trimming rule in "Sensitive content" still applies.

## Writes

- Read the current state first, then tell the user exactly what will change (which object, which fields, what text), and wait for a yes unless the request was explicitly to make that change.
- Prefer linking to duplicating. Use `addGraphContext` to connect work to projects and goals, and remote links to point Jira at third-party sources, instead of copying content across.
- After creating something, link it back to the sources that justified it.
- Resolve people to account IDs with `getPeopleInfo` or `lookupJiraAccountId`. Never guess an account ID.

## Publishing

Follow the calling skill's delivery mode. A skill that explicitly selects "Answer-first delivery" uses the flow below. Other skills keep their existing artifact flow: build the static artifact unless a live one is available and the skill's "When live" section says what it adds. Load `atlassian-design` only when building a report or artifact.

### Answer-first delivery (only when the calling skill selects it)

1. **Give the result in the conversation first.** Use the calling skill's assessment, ranking, row limits and content requirements. Cite evidence with ordinary Markdown links, retain Recorded, Proposed and Found by search labels as plain text where required, and include coverage, dates, caps and gaps in a Sources and limitations section. Do not load design guidance, write report data, run a renderer or create an artifact for this initial answer.
2. **Offer the existing HTML report as an optional export.** Ask whether the user wants it and wait for their answer. An ordinary invocation of the skill is not a request for a file. An explicit request for an HTML report, file export or publication already authorises the corresponding report build; do not ask again. Reuse the findings already gathered, and keep all evidence labels and limitations. If new evidence is needed, stay within the skill's budgets and explain what changed.
3. **Check Atlassian Artifacts availability before offering publication.** Reuse the selected site's `products` list from `getAccessibleAtlassianResources`; do not choose another site silently. If `artifacts` is absent, skip publication tools and offers. If it is present, confirm that `createArtifactsUpload` and `publishArtifact` are available in this session, through `discover` if necessary, without creating an upload as a test. If availability cannot be confirmed, say so when relevant and hand over the report file.
4. **Keep export and publication separate.** Agreement to export is not agreement to publish. When the service is confirmed available, offer a private, read-only Atlassian Artifact with the calling skill's name and description. Publish only on an explicit request, using the static publishing steps below. If the user already requested export and publication, complete both without asking again. An unavailable publishing service never blocks the answer or local HTML export.
5. **Keep other writes independent.** Skipping export does not authorise or cancel other writes the calling skill offers. Follow its conditions and confirmations. Share a published artifact only on request, with the people the user approves.

### Static artifact (the default)

Don't publish by default. Publishing is a write, so hand over the file and offer to publish a private, read-only copy as an Atlassian Artifact. Publish only when the user says yes, or has already asked for it in this request.

1. **Build one self-contained HTML file.** Inline all CSS, JavaScript and images, and use no external files. Don't use `localStorage`, `sessionStorage` or IndexedDB, which the artifact viewer may block. Inline only the icons you use, and don't embed raw tool output, so the file stays small.
2. **Hand it over and offer to publish.** Give the user the file, and offer a private, read-only Atlassian Artifact: nobody else can open it until it's shared, and people it's shared with can view it but not edit it. Say what the name and description would be. If they'd rather have a Confluence page, confirm first and create it with `createConfluenceContent`.

When the user agrees:

3. **Measure it exactly.** Byte length: `wc -c < file.html`. Checksum, as base64 SHA-256, not hex: `openssl dgst -sha256 -binary file.html | openssl base64 -A`.
4. **Upload.** Run `createArtifactsUpload` (through `discover` and `executeWrite`) with `length` and `checksum`, then send the exact bytes to the pre-signed URL as its instructions say.
5. **Publish.** Run `publishArtifact` with the `contentId` from step 4, a `name`, `contentType: text/html`, and a `description` that summarises what the artifact actually contains (up to 1000 characters, used for search). To update an artifact you published earlier, pass its `id`. Each publish is a new version that can't be changed.
6. **Share only on request.** `publishArtifact` returns a link that grants nobody access. Offer to share it with the people it's for (attendees, a leader, a team) and, if the user agrees, call `shareArtifact` with `ari:cloud:identity::user/<accountId>` or team ARIs. It only grants view access to named people, never to everyone with the link.

If the client can't upload over HTTP, hand over the HTML file and say why it wasn't published.

A static artifact can't call tools, so it shows what was true when it was built. To keep one fresh, run the skill again and publish with the same `id`, for example from a scheduled task the user set up to publish. Actions are links, or buttons that copy a command such as `/meeting-prep [title]`.

### Live artifact (when the host supports connector access)

A live artifact runs inside a host that explicitly supports tool calls from page code. Having an MCP connection in the agent conversation is not enough. Build one only when the host's documented runtime and permissions are available, the skill has a "When live" section, and the user requests it or that skill explicitly makes it the default. A skill using answer-first delivery still requires a report or live-export request first.

Read `live-artifacts.md` before building one, then load only the adapter for the actual host. Use the host's current documentation when it differs from an included adapter. Do not rename one host's APIs, capability declarations, connector identifiers or error codes to make them look universal. If the host or its capabilities cannot be confirmed, retain the conversational answer or requested static report and explain why live refresh is unavailable.

- **Render the snapshot first.** Label build-time and live data separately, including their times. A missing connector or denied permission must leave the snapshot usable.
- **Respect viewer access.** Do not assume the host uses the author's credentials or the viewer's. Confirm the host's access model in its adapter before building or sharing, and use the viewer's own access for live sections. Build-time data is visible to everyone who can open the artifact.
- **Keep calls narrow and rule-based.** Refresh only the objects and fixed queries the skill lists. Keep open-ended search and sensitive-content judgement at build time. Tools that use Rovo credits run only from a click, never a watch or poll. Each refresh stays inside the skill's budget.
- **Confirm writes.** Show the exact change and wait for a confirm click. A failed write may have run, so re-read before offering it again. If a host cannot support the required consent or action, keep the offer in the conversation.
- **Use host-specific recovery.** Read actual error codes and connector setup instructions from the matching adapter. Keep failures in their own sections and retain a clearly labelled snapshot.
- **Keep the same source labels and design rules.** Show apps actually used, Found by search labels and coverage gaps. The host's actual sharing, storage and permission limits come from its adapter.

A live artifact belongs to its host. Publishing an HTML snapshot to Atlassian Artifacts is a separate, static export, offered only when that service is available and the user requests publication.

## Mockups and sample data

When the user asks for a mockup, or gives sample data:

- Skip the context loop and use only what was given, filling plausible gaps.
- Add a small discovery-coloured note at the top: "Mockup with sample data. People, work and pages are made up."
- Use `#` for every link unless told otherwise.

## Checklist for skill authors

A skill that loads this file should state:

- **Anchor:** what the user provides, which `objectType` it resolves to, and how to resolve it.
- **Connectors:** needed and helpful, naming each Atlassian app separately, what the skill does when a needed one isn't on the site, and the vendor connector to use for each gap in Teamwork Graph the skill hits.
- **Context:** which relationships to follow from the anchor, which product records confirm them, which searches and JQL to run, and the date window.
- **Statuses:** the full vocabulary the source records use (including Pending, Paused, Done and Cancelled), and how each one displays.
- **Stop condition:** what the artifact needs before it can be written, and a call budget if it differs from the default.
- **Writes:** any actions it takes, and what it confirms first.
- **Artifact:** its sections, and the design rules beyond `atlassian-design`.
- **Delivery:** state whether the skill uses answer-first delivery or its existing artifact flow. For answer-first delivery, give the answer, offer optional HTML export, and offer publication only when Atlassian Artifacts availability is confirmed. For either mode, state who to offer sharing with after an approved publication.
- **When live:** what the live version refreshes, which tools it asks for, any writes it offers, and whether it can be shared. Or "Static only".
