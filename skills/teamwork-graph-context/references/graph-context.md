# graph context

Follow the tool-access and coverage rules in the shared skill entrypoint. Examples name operations; use direct calls when available, otherwise the discovered runner and schema.

## What the graph doesn't tell you

These gaps showed up on real data. Work around them as described, and say in the footer when one affected the result.

- **Direction.** There's no direction field. The relationship name carries it. When the two object types differ, the name says which is which: `atlassian_user_owns_atlassian_project` means the user owns the project, from either end. When they're the same type, the reading depends on the relationship:
  - `jira_work_item_blocks_jira_work_item`: the target blocks the queried item (upstream).
  - `jira_work_item_is_blocked_by_jira_work_item`: the target is blocked by the queried item (downstream).
  - `atlassian_project_depends_on_atlassian_project`: the queried project depends on the target (upstream). This one reads the other way round.

  For any other same-type name, check it from both ends before trusting it. The graph also indexes only Jira's standard Blocks link type: a site's own blocker link type (one named "Blocker", say) doesn't appear at all. So use the graph's Jira edges as candidates and a cross-check, and confirm every Jira dependency with `getJiraIssue` (`view: evidence`): read `[this issue] [type.inward] [inwardIssue]` or `[this issue] [type.outward] [outwardIssue]`; the phrase "is blocked by" means upstream and "blocks" means downstream. For many items at once, JQL with `fields: ["summary", "status", "issuelinks"]` returns the same `inwardIssue` and `outwardIssue` entries in one call. On a large site, `view: evidence` returns every custom field (about 25,000 characters per issue), so pass an explicit `fields` list when you only need links.
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

- **A name or topic:** run `search` , compare the plausible candidates by scope, recency and how central they are, and pick one. If two are equally plausible, ask. Don't merge two same-named things.
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
