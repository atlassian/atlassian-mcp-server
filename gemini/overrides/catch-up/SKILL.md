---
name: "catch-up"
description: "Catch the current user up on a period they were away, across their own work or a Jira project, epic, Confluence space, or topic, using Jira, Confluence, and Rovo Search (plus optional standalone calendar, email, or chat connectors if available in the session). Delivers a concise conversational briefing covering what needs the user now, decisions recorded while away, confirmed Jira and Confluence changes dated inside the window, missed meeting notes, and upcoming due dates. Use for catch me up, what did I miss, returning from leave or holiday, getting back to a project, or /catch-up."
---

# Catch-Up

Give someone returning from time away a focused catch-up in the conversation that they can read in five minutes: what needs them first, what was decided without them, what changed in Jira and Confluence while they were out, any meeting notes they missed, and what is coming up in the next few days. Keep it strictly to the requested window and leave out anything the user already touched or that does not change what they do next.

Load the `teamwork-graph-context` skill first and follow it for direct v2 tool usage, schema verification, source labeling, sensitive-content filtering, event dating, and conversational delivery. Apply its "Sensitive content" rules strictly: drop leave/absence details, private messages, and people-programme assessment/selection pages completely.

## Tool Access & Coverage

- **Needed:** Jira (`getAccessibleAtlassianResources`, `atlassianUserInfo`, `getJiraCurrentUser`, `getMyWork`, `searchJiraIssuesUsingJql`, `getJiraIssue`, `listJiraIssueChangelogs`, `listJiraIssueComments`, `getJiraUser`) and Confluence (`searchConfluence`, `getConfluenceContent`, `listConfluenceContentVersions`, `diffConfluenceContentVersions`, Confluence comment retrieval (use `searchConfluence` with `type = comment AND container = <id>` when a dedicated comments tool is absent; report its coverage limits), `listConfluenceTasks`), plus Rovo `search`. Call `getAccessibleAtlassianResources` once for `cloudId` and the site base URL, then call Jira and Confluence tools directly (do not block on a `products` field).
- **Unavailable on this connector:** Atlassian Projects (Atlas), Goals, Loom video recordings, Bitbucket/GitHub pull requests, and org-chart/cross-app activity feeds are **not** exposed on this Atlassian connector. Never attempt to call tools for those scopes; rely on Jira, Confluence, and Rovo Search, and state transparently in the summary and Sources and limitations that Atlassian Projects, Goals, pull requests, and Loom recordings were not checked.
- **Optional standalone session connectors:** If the user's session also provides standalone connectors (Google Calendar / Outlook for out-of-office dates, missed meetings, and upcoming meetings; Gmail / Outlook for email asks; Slack / Teams for chat asks or decisions), use them read-only to fill those gaps and label each fact by app. If absent, say so in Sources and limitations and rely on Confluence meeting notes and Jira due dates.
- **Direct calls & live schema check:** Call every tool directly by name. If a tool is not in your tool list, it is not available on this connector; say so and use the closest available tool. Always inspect live tool schemas before passing parameters — especially:
  - `listConfluenceTasks`: verify the assignee parameter name (`assigned-to` vs `assignedTo` / account ID), `status`, `limit`, and pagination cursor.
  - `getJiraIssue`: check whether `view` is supported or pass explicit `fields: ["summary", "status", "issuelinks", "assignee", "duedate", "updated"]`.
  - `search`: Use cloudId and query, with optional targetApp and limit; do not pass mode.
  - `getConfluenceContent`: verify `content_id` vs `contentId` and `content_format`.

## Budget

A multi-week window produces many candidates, so keep calls bounded unless the user asks for a deeper pass:

- `getMyWork`: 1 call (recent items touched by the user)
- `searchJiraIssuesUsingJql`: up to 5 queries (assigned/due work, user's own activity, topic/window changes, candidate count, resolved count)
- `searchConfluence` (CQL): up to 6 queries (user's own activity, user's recent pages, comments on user's pages, decision pages, new pages, edited page candidates)
- `search` (Rovo): up to 5 calls (topic resolution if needed, decisions, meeting notes, broader cross-content sweep)
- `listConfluenceTasks`: up to 4 paginated calls
- History reads: `listJiraIssueChangelogs` capped at **8** top changed Jira issues; `listConfluenceContentVersions` + `diffConfluenceContentVersions` capped at **6** top edited Confluence pages
- `listJiraIssueComments` / Confluence comment retrieval (use `searchConfluence` with `type = comment AND container = <id>` when a dedicated comments tool is absent; report its coverage limits): up to 6 active items where discussion matters
- `getJiraUser`: up to 8 calls to resolve editor/author account IDs when display names are absent
- Optional standalone calendar/email/chat connectors (if available in session): up to 3 calendar calls and 1–2 email/chat searches

Report every cap that applied in Sources and limitations (for example, "Read changelog history for 8 of 31 updated Jira issues").

## Step 1: Set the window, seen items, and anchor

### The window

- **Start and end:** Take them from the user's request ("two weeks" = 14 days back from the start of that day; "since Oct 6"; "Oct 6 to Oct 17"). A date-only end includes that whole day in the user's timezone (exclusive upper bound = start of the following day). Leave out events strictly after an explicit end date and count them in Sources and limitations.
- **Timezone:** Call `atlassianUserInfo` (for account ID and display name) and `getJiraCurrentUser` (for the user's Jira `timeZone`) alongside `getAccessibleAtlassianResources`. Format JQL and CQL date filters as `"YYYY-MM-DD"`.
- **"Since I've been away" with no dates:** If a standalone calendar connector is available in the session, check the user's most recent out-of-office block ending within the last 7 days (state only the dates used, never the event title or reason). Without a calendar connector or OOO event, ask the user for the start and end dates — never guess.
- **Bounds:** Under 2 days, cover as asked; over 6 weeks, cover the last 6 weeks and note that cap at the top. Count working days (Mon–Fri) in the window for the header.

### What the user already saw ("the seen rule")

Before gathering news, check what the user touched during the window so you do not repeat things they already acted on:

1. Call getMyWork and scoped JQL/CQL to identify candidates. Those results do not prove that the user saw an event.
2. **Seen rule:** Exclude an event only when a dated edit, comment or transition by this user after that event confirms it was handled. If that evidence cannot be read, do not infer seen-state from assignee/reporter/creator/contributor fields; retain the item and disclose incomplete seen-state coverage.
3. **Needs you exception:** Do not remove open work or unanswered tasks from **Needs you** just because the user opened the item — only drop an ask or task if a later comment or resolution shows the user already answered or completed it.

### The anchor

- **No topic (default):** Anchor on the signed-in user's own work across Jira (assigned, reported, or watched) and Confluence (created, contributed, mentioned, or watched).
- **Named topic:** Resolve it to a Jira project key, epic (`getJiraIssue`), Confluence space key (`getConfluenceSpace`), page URL (`getConfluenceContent`), or via Rovo `search` + JQL/CQL. If two candidates are equally plausible, ask. Build a concise scope set (project keys, epic keys, space keys, and 2–3 distinctive terms).
- **Never profile another person:** If asked "catch me up on what Sam did", explain that this skill catches the user up on work and offer to catch them up on a shared Jira project, epic, or Confluence space instead.

### Dating rule

Date every item by its confirmed **event time** (per `teamwork-graph-context`). Drop events outside the window, with one exception: open items still waiting on the user stay in **Needs you**, labelled `"Open since [date]"`.

## Step 2: Find what needs the user

Run these in parallel (adding topic `project in (...)` / `parent in (...)` / `space in (...)` filters when a topic was given):

1. **Assigned Jira work:** `searchJiraIssuesUsingJql` with:
   `assignee = currentUser() AND statusCategory != Done AND (duedate <= endOfDay("+5d") OR assignee CHANGED TO currentUser() AFTER "<start>" OR created >= "<start>")`
   Request `fields: ["summary", "status", "duedate", "priority", "updated", "created", "project", "parent", "issuelinks"]`, `maxResults: 25`. (Always keep `CHANGED` paired with `assignee =` or `project =` to avoid timeouts.)
2. **Jira comments / asks on active assigned work:** For up to 6 assigned or watched Jira issues updated inside the window, call `listJiraIssueComments` directly to spot recent questions or requests directed to the user by someone else (skipping comments the user already replied to).
3. **Confluence inline tasks:** Call `listConfluenceTasks` directly. **Check the live tool schema first** to verify the assignee parameter (`assigned-to` vs `assignedTo` with the user's account ID), `status: "incomplete"`, `limit: 250`, and pagination cursor (follow up to 4 pages, noting in Sources and limitations if more remain). Keep tasks created inside the window plus older tasks due within the next 5 working days.
4. **Comments from others on the user's Confluence pages:**
   - Find pages the user created or edited in the last 90 days: `searchConfluence` with `creator = currentUser() AND type in (page, blogpost) AND lastmodified >= "<90 days back>"` (`limit: 50`).
   - Find comments from others inside the window: `searchConfluence` with `type = comment AND created >= "<start>" AND creator != currentUser() AND container in (<page ids>)` (`limit: 50`), or Confluence comment retrieval (use `searchConfluence` with `type = comment AND container = <id>` when a dedicated comments tool is absent; report its coverage limits) on key pages. Treat comments asking a question or requesting review/input (and unanswered by the user) as **Ask** items.
5. **Optional standalone email/chat connectors (only if present in the session):** If the session has Gmail/Outlook or Slack/Teams connectors, run 1 targeted search for unanswered asks in the window, respecting all sensitive-content rules (skip DMs unless explicitly asked, read snippets only, label by app).

Deduplicate overlapping items (for example, a Confluence task and the Jira ticket tracking it become one item citing both).

## Step 3: Find what was decided

A decision is a choice explicitly recorded as made (approach chosen, date agreed, scope cut, request approved/declined). Never infer a decision solely from a status transition or moved date.

1. **Confluence decision pages:** `searchConfluence` with the topic's space clause (or, with no topic, `(contributor = currentUser() OR watcher = currentUser() OR mention = currentUser())`) plus `AND (label in ("decision", "decisions", "decision-log") OR title ~ "decision" OR title ~ "DACI") AND lastmodified >= "<start>"` (`limit: 25`). Read promising pages with `getConfluenceContent` (`detail="full"`, re-reading as HTML if `lostFeatures` drops panels or date lozenges) and keep decisions dated inside the window.
2. **Jira decision items (if used on site):** Include any `issuetype = Decision` or `labels in (decision, decisions)` items updated in the window from Jira.
3. **Rovo `search` for decisions:** Run 1 `search` call (checking live schema first) with the topic's distinctive term (or user's active project/page topic) plus `"decided agreed approved"`. Keep hits inside the window whose text explicitly states a decision made, noting who decided/recorded it and when. Never invent a decider the record does not name.

## Step 4: Find what changed

Changes made by **someone else**, inside the window, to work in scope:

1. **Jira changes:**
   - Call `searchJiraIssuesUsingJql` with the scope clause (`project in (...)`, `parent in (...)`, or `(assignee = currentUser() OR reporter = currentUser())`) `AND updated >= "<start>" ORDER BY updated DESC`, `fields: ["summary", "status", "issuetype", "assignee", "duedate", "priority", "created", "resolutiondate", "parent", "updated"]`, `maxResults: 50`.
   - If 50 items return, check candidate total and `resolved >= "<start>" AND resolved < "<exclusive end>"` (using `searchResultMode: "count"` if supported by the live schema).
   - Items created or resolved inside the window are dated directly by `created` / `resolutiondate`. For up to **8** top-ranked updated items, call `listJiraIssueChangelogs` directly (oldest first: check `total` with `maxResults: 1`, then fetch the last 10–20 entries with `startAt`). Keep entries inside the window made by someone other than the user for status (especially Blocked or Done), assignee, due date, priority, and new blocking links.
2. **Confluence page creations and bounded-window diffs:**
   - Call `searchConfluence` twice with a parenthesized scope clause (`(space in (...) OR ancestor = <id>)`, or `(creator = currentUser() OR contributor = currentUser() OR mention = currentUser() OR watcher = currentUser())`) plus `AND type in (page, blogpost)` (`limit: 25`):
     - Once with `AND created >= "<start>" AND created < "<exclusive end>"` for **New** pages.
     - Once with `AND lastmodified >= "<start>" ORDER BY lastmodified DESC` for **edit candidates** (open-ended so pages edited both during and after the window are not missed).
   - For the top **6** edited pages, call `listConfluenceContentVersions` directly (`limit: 100`, paging until older than `<start>`). Choose the **baseline** as the last version before `<start>` and the **endpoint** as the last version before `<exclusive end>` (ignoring edits after an explicit end date).
   - Call `diffConfluenceContentVersions` strictly between those two versions (using `content_format="html"` if panels or dates might have changed) and summarize the diff in one sentence. If both endpoints are identical, no edit occurred inside the window. If history is incomplete, report the check as unable to verify rather than substituting current page content.
   - If version editors appear only as account IDs, resolve display names with `getJiraUser` (dropping edits made solely by the user).
3. **Broader Rovo `search` sweep:** Run up to 2–3 `search` calls (checking live schema first) using the topic's distinctive terms (or the user's top active page/project titles from `getMyWork`) to catch unlinked Confluence or Jira updates. Filter hits by `lastModified` inside the window and label search-only matches **Found by search**.

## Step 5: Missed meeting notes and coming up

- **If a standalone calendar connector is present in the session:** Call its read-only event listing for the window (skipping 1:1s, mentoring, personal/leave events, and attended meetings) and for the next 5 working days. Never copy passcodes/dial-ins or link Google Calendar `htmlLink` URLs. Match missed meetings to Confluence meeting notes via `searchConfluence` / `search`.
- **Without a calendar connector (Atlassian-only):** Search Confluence (`searchConfluence` / `search`) for meeting notes pages created or edited in the window matching the topic or the user's spaces (`title ~ "notes" OR title ~ "sync" OR title ~ "meeting"`). State clearly that calendar attendance and meetings without Confluence notes could not be checked.
- **Coming up (next 5 working days):** Always include Jira due dates and incomplete Confluence task due dates falling in the next 5 working days (plus upcoming calendar meetings if a calendar connector ran).

## Step 6: Assess and rank

### Needs you (up to 8 rows; count the rest in Sources and limitations)
Assign one label per row:
- **Overdue**: assigned Jira issue or Confluence task past due date
- **Due soon**: due in the next 5 working days
- **Blocking**: open Jira issue owned by the user that blocks another team's work — confirm `issuelinks` direction via `getJiraIssue` (check live schema before using `view`; prefer explicit `fields: ["summary", "status", "issuelinks"]`)
- **Ask**: unanswered question or request in Jira/Confluence comments (or session email/chat)
- **Assigned**: newly assigned inside the window, not due soon
- **Action / Task**: open Confluence inline task or meeting-notes action item for the user

Rank: Overdue -> Due soon (earliest first) -> Blocking -> dated Asks -> older Asks -> Assigned -> Action/Task.

### Decided (up to 6 rows)
Rank decisions changing the user's own work/dates first, then topic scope/approach decisions, newest first. Cite who decided (only if named by a record), when, and the link.

### What changed (up to 4 groups, 12 rows total)
Assign one label per row: **Blocked**, **Date moved** (with from -> to), **Scope** (added/removed/Won't do/new dependency), **Shipped** (resolved Done / released), **New** (created in window), **Update** (notable edit or discussion). Drop housekeeping noise (formatting tweaks, bulk bot resyncs, trivial label churn). Rank in that order (anchor changes first, then newest first). Group by Jira epic/project or Confluence space (folding singletons into **Other**; folding >3 Shipped items in one group into a single summary row with key links).

### Summary ("While you were away")
Write 2 to 3 crisp sentences (at most 60 words):
1. The single highest-priority thing to do first and why.
2. The most important decision or change.
3. The overall shape of activity across Jira and Confluence.
Never mention why the user was away.

## Writes

None. This skill is strictly read-only. If the user asks to act on an item afterward, confirm the exact change before calling any write tool.

## Conversational Answer Structure

Deliver the complete catch-up directly in Markdown:

1. **Header & Summary:** Scope (topic or "Your work"), window dates, working-day count, timezone, key counts (Needs you / Decisions / Changes), and the <=60-word summary.
2. **Needs you:** Ranked list/table (up to 8 rows), each ~1 sentence with label, event date (or `"Open since [date]"`), and Markdown source link (or "Nothing is waiting on you in Jira or Confluence").
3. **Decided while you were away:** Up to 6 decisions with what was decided, recorded decider, date, and source link (or "No recorded decisions found in this window", noting that decisions made only in calls or chat without Confluence/Jira records cannot be seen).
4. **What changed:** Up to 4 groups / 12 rows with change type, 1-sentence summary, event date, and link (keeping **Found by search** hits labelled).
5. **Meetings & Notes** (if any meeting notes or calendar data found) and **Coming up (next 5 working days)** (due dates, tasks, and upcoming meetings if calendar connector ran).
6. **Sources and limitations:** Exact window and timezone, dating rule ("dated by event time, not last touched"), counts excluded (outside window, after end date, already touched by user), every cap reached, search warnings, optional standalone connectors used (or absent), and the explicit statement that **Atlassian Projects, Goals, pull requests, and Loom recordings are not exposed on this connector** and were not checked. Mention `dependency-map` if a blocked dependency needs deeper mapping.
## Optional offline report

Answer in the conversation first. When the user requests an HTML report, read [the report export instructions](references/report-export.md), load atlassian-design, and run the bundled render.py from this skill directory using its example.json and data-format reference. Preserve the same facts, verdict, condition count and coverage gaps in the report. Both design kits run offline with Python's standard library; do not install packages or download assets. Export does not authorize publication or sharing. Return static HTML when publication tools are unavailable.
