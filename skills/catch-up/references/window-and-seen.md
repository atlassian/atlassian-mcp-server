# window and seen

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

## Budget

A long window means many more candidate changes than a daily brief, so the caps matter more. Each step states its own. In total, unless the user asks for a deeper pass:

- 7 `search` calls: 1 to resolve a named topic, 4 for the third-party sweep (3 terms and the Slack ID), 1 for decisions and 1 for meeting notes
- 2 `getWorkActivity` calls: one for the user's own activity (Step 1), one for mentions and assignments (Step 2)
- 4 JQL queries and 5 CQL queries (1 for comments on the user's pages, 1 for decisions, 2 for page changes, and 1 to list the user's pages when Step 1 didn't)
- 2 `getGraphContext` calls, on the anchor only
- 2 `getPullRequests` calls
- 3 calendar connector calls, and 1 email connector call
- 3 Loom lists and 2 `getLoomObjectsContent` reads (up to 10 recordings each)
- 1 `getPeopleInfo` batch to name editors and authors that records give only as account IDs
- the anchor's `getProject` or `getGoal`, plus up to 5 linked projects or goals

History reads (`listJiraIssueChangelogs`, `listConfluenceContentVersions`, `diffConfluenceContentVersions`) are capped at 8 work items and 6 pages, chosen as Step 7 ranks them. A retry after an input error doesn't count against a cap. Other reads of known objects don't count, but batch them. A run is usually 35 to 50 calls. The footer reports every cap that applied ("Read the history of 8 of 31 changed work items").

## Step 1: Set the window and the anchor

### The window

- **Start and end.** Take them from what the user says: "two weeks" (14 days back from now, from the start of that day), "since Oct 6", or "Oct 6 to Oct 17". A window with no end runs to now. A date-only end includes that whole day in the user's timezone: use the start of the following day as an exclusive upper bound. Preserve an exact end time when the user supplies one. In the sections covering that window, leave out later events and say in the footer how many that left out ("4 later changes aren't included"). Coming up uses its separate look-ahead in Step 5.
- **Out-of-office events.** With the calendar connector, always make one `list_events` call for the user's own out-of-office events (`eventType: ["OUT_OF_OFFICE"]`), from 6 weeks back to now. It sets the window when the user gives no dates, and "What the user already saw" needs it either way. It's one of the 3 calendar calls.
- **"Since I've been away", with no dates.** From that call with `eventType: ["OUT_OF_OFFICE"]` on the user's own calendar, and use the most recent block that ended in the last 7 days. Say which dates you used ("Oct 6 to Oct 17, from your calendar"), never the event's title or reason. Without the connector, or with no such event, ask the user for the dates. Don't guess.
- **Timezone.** Use `zoneinfo` from the user's `getPeopleInfo` profile. Pass bounds as ISO datetimes with the offset (`2026-10-06T00:00:00+11:00`), because `getWorkActivity` reads a bare date as UTC. JQL and CQL take dates as `"2026-10-06"`.
- **Bounds.** Under 2 days, cover it as asked. Over 6 weeks, cover the last 6 weeks and say so at the top. For an area that's new to the user rather than one they're returning to, suggest `/ramp-up`.
- **Working days.** Count the working days in the window (Monday to Friday) for the header, including the first and last day. A window that runs to now includes today.

### What the user already saw

A catch-up is for what the user didn't see, and people aren't always fully away: they check in on leave, or they're back on a project after working on something else. So before gathering, look at what the user did themselves in the window.

1. Call `getWorkActivity` with `scope: me`, `activity: authored,commented,updated`, `types: jira,docs,comments,pr,videos`, `from` and `to` set to the window, `hydrate: full` and `itemsPerSection: 25`. `hydrate: full` gives each of the user's comments its parent page, which the seen rule needs. Check each parent page's title against "Sensitive content" before using a comment's body, and drop both together. Note the dates of the user's own actions and the objects they touched. This call also shows which asks they've already answered (Step 2).
2. With an available calendar connector, read meeting responses in Step 5. Confirm attendance from a recording, notes or another timestamped record naming the user as present or speaking. Being the organiser or accepting an invitation alone does not prove attendance. A declined or explicitly missed meeting can be shown as missed; otherwise preserve unknown attendance rather than inventing it. Attendance does not establish that the user read a later notes page or recording.
3. **If the user was active on more than half the window's working days** and there's no out-of-office event in it, find the longest run of working days with no activity from them (at least 2). Say so before building and offer it: "You were active on 8 of 11 working days. The longest stretch without activity was Oct 7 to Oct 12. Catch up on that, or the whole window, leaving out what you already touched?" Without an answer, keep the whole window. With a topic, count only activity on the topic.
4. **The seen rule:** exclude a changed item from What changed or Decided only when a confirmed timestamped user action on that record happened after the event. A page edit/comment, issue change or reply must identify the relevant record and event. Assignee, creator, contributor, invitation response and search-match metadata do not establish seen state. Retain the item or mark seen state unknown when the necessary activity is unavailable. Do not propagate attendance to later notes or recordings. Count confirmed exclusions in the footer; the user's own authored change is not news to them. Meeting attendance separately determines whether it belongs in Meetings you missed.
5. **Done elsewhere.** The rule doesn't take actions out of Needs you: an action the user owes, from a meeting they attended, still needs doing. But check each action and ask against the user's own activity from item 1 before keeping it. An action is done when a later record from the user delivers it (the deck or page it names, the work item it tracks closed). An ask is answered when the user replied to the same person on the same question in any app within a day after it, for example on the Loom when the question came in Slack. When it's unclear, keep it and say when it was asked.

### The anchor

1. Call `atlassianUserInfo` for the account ID, and `getPeopleInfo` (`name: "me"`) for the display name and timezone. You need the name to match mentions in chat snippets and owners in meeting action items.
2. **No topic:** the anchor is the user's own work (`AtlassianUser`, `scope: me`). Call `getWorkPortfolio` with `includeDirectReports: false`, `kinds: ["projects", "goals"]`, `view: "compact"` and `limitPerCollection: 10`. The scope is work assigned to, reported by or watched by the user, pages they created, edited or are mentioned on, and those projects and goals.
3. **A topic:** resolve it to the most specific record, as "Resolve the anchor" in `teamwork-graph-context` describes:
   - A Jira key or URL: an epic (`JiraWorkItem`), a Jira space (`JiraSpace`) or a board.
   - An Atlassian project or goal key, URL or name: `getProject` or `getGoal`, or `searchProjects` and `searchGoals` with 1 or 2 key terms and `limit: 10`.
   - A Confluence space key or page URL.
   - A plain name ("Ledger"): run `searchProjects`, `searchGoals` and one `search` (`targetApp: ALL`, `limit: 20`) together. Compare the candidates by scope and recency. If two are equally plausible, ask. If none matches, stop and say so.
4. **Build the scope set** for a topic. Everything later is filtered against it:
   - For a project, call `getProject` with `include: ["description", "links", "goals", "teams", "contributors"]`, `linkType: WORK_TRACKING` and `limits: {links: 20, goals: 5, teams: 5, contributors: 20}`. Keep the Jira keys and epics from the work-tracking links, the linked goals, and every Confluence, Google Drive or Slack URL in the description.
   - For a goal, call `getGoal` with `include: ["description", "projects", "teams"]` and `limits: {projects: 20, teams: 5}`. Its linked projects (up to 5, most recently updated first) join the scope.
   - Call `getGraphContext` on the anchor's URL or ARI with `detailLevel: summary`, then `full` for linked pages, conversations, repositories and work items only. Atlas keys don't resolve.
   - Note the Jira project keys, epic keys, Confluence space keys, repositories and channel names the records name, and 2 or 3 **distinctive terms** for search: the project or epic name, its key and any codename. Not the team or product-family name.
5. **Who's asking.** The page is about work, for the user who asked. If the topic is a person ("catch me up on what Sam did"), don't build a page about them: offer to catch the user up on a project or area they share instead. Every read runs with the user's own access, and "Needs you" holds only items that wait on the user.

### Dating every item

This is the rule the whole page rests on. Date each item by its event time, as "Dating events in a window" in `teamwork-graph-context` describes. One rule is specific to a catch-up:

- **Items from before the window** are left out, with one exception: things still waiting on the user (an open ask, open work assigned to them, an unreviewed pull request) stay in "Needs you", labelled "Open since [date]".
