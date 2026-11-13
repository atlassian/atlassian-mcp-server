---
name: "catch-up"
description: "Catch the current user up on a period they were away, across their own work or a project, goal, space, epic or topic, using Teamwork Graph across Jira, Confluence, Projects, Goals, Loom, the calendar and connected tools. Answers in the conversation first: what needs the user, decisions made, changes, missed meetings and what is coming up. Every item is dated inside the window and linked to its source. Offers an HTML report on request, styled with the Atlassian Design System, and publication only when Atlassian Artifacts is available and requested. Use for catch me up, what did I miss, returning from leave or holiday, getting back to a project, or /catch-up. To write a project's weekly status update, use status-check."
---

# Catch-up

Give someone back from time away a catch-up in the conversation that they can read in five minutes: what needs them first, what was decided without them, what changed in the work they care about, which meetings they missed and what came out of them, and what's coming up in the next few days. Keep it to the window they were away for, and leave out anything that doesn't change what they do next.

The value of this skill is the judgement a notification inbox, a project's update feed or a Slack unread count can't make: across every tool at once, which of hundreds of changes need you, which were decisions, and which happened while you were out rather than just before.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. This file adds what's specific to a period of time. Apply its "Sensitive content" section strictly. A long window over someone's own work turns up more leave, private messages and people-programme pages than a single day does. Leave out a people-programme page entirely, even as a New row, when its title or excerpt carries a level code, selection or assessment language: not quoting it isn't enough. When the user runs the programme, keep its schedule, its meetings and the user's own actions, in neutral words ("Send the programme update to managers"), and drop only the participant and assessment detail. An optional HTML report is built by `render.py` in this folder (Step 8), which applies the `atlassian-design` skill for you: load that skill only if the script can't run.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## Connectors

- **Needed:** Jira and Confluence, for most of what changes in a fortnight. If neither is in the site's `products` list (see "Atlassian apps on the site" in `teamwork-graph-context`), say so before building, and say what the page can still show.
- **Helpful, from Atlassian:** Projects and Goals, for status changes, target date moves and recorded decisions. Loom, for meeting recordings and their action items. Bitbucket, for review requests and merged work. Skip the calls for any app that isn't on the site, and list it in the footer as "Not available on this site".
- **Helpful, from other tools:** Slack or Teams, for decisions and asks made in chat. Google Drive or SharePoint, for docs edited while the user was away. GitHub or GitLab, for merged pull requests. Gmail or Outlook, for asks by email.
- **Vendor connectors,** as `teamwork-graph-context` describes. Teamwork Graph comes first, and a connector fills only a known gap:
  - The calendar's own connector (Google Calendar or Outlook) for the meetings the user missed and what's coming up (Step 5). Teamwork Graph can't list meetings in a window. Without the connector, missed meetings come only from recordings and notes found in Steps 2 and 3, and the page says recurring meetings may be missing.
  - The calendar connector also reads the user's own out-of-office event to set the window when they say "since I've been away" without dates (Step 1).
  - Slack, Teams, Gmail or Outlook connectors for a strict date window when the Teamwork Graph search came back empty or too thin inside the window (Step 4), and to read threads that don't hydrate.
  - Gmail or Outlook once for email asks when the Teamwork Graph results held no email at all (Step 2).

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
2. With the calendar connector, the user's response to each meeting comes from Step 5. A meeting counts as attended when they organised it, when they accepted it and its recording or notes name them as a speaker or give them an action, or when they accepted it and nothing shows otherwise (no recording, or one that wasn't read). Only a meeting they didn't answer, declined after the window started, or whose recording shows they weren't there counts as missed.
3. **If the user was active on more than half the window's working days** and there's no out-of-office event in it, find the longest run of working days with no activity from them (at least 2). Say so before building and offer it: "You were active on 8 of 11 working days. The longest stretch without activity was Oct 7 to Oct 12. Catch up on that, or the whole window, leaving out what you already touched?" Without an answer, keep the whole window. With a topic, count only activity on the topic.
4. **The seen rule:** an item the user already acted on after it happened isn't news. Leave it out of What changed, Decided and Meetings you missed, and count it in the footer ("12 items you'd already seen aren't shown"). That covers a page they edited or commented on after the change, a work item they changed after it, a thread they replied in, a meeting they attended, and that meeting's notes page and recording. Their own changes are never news either.
5. **Done elsewhere.** The rule doesn't take actions out of Needs you: an action the user owes, from a meeting they attended, still needs doing. But check each action and ask against the user's own activity from item 1 before keeping it. An action is done when a later record from the user delivers it (the deck or page it names, the work item it tracks closed). An ask is answered when the user replied to the same person on the same question in any app within a day after it, for example on the Loom when the question came in Slack. When it's unclear, keep it and say when it was asked.

### The anchor

1. Call `atlassianUserInfo` for the account ID, and `getPeopleInfo` (`name: "me"`) for the display name and timezone. You need the name to match mentions in chat snippets and owners in meeting action items.
2. **No topic:** the anchor is the user's own work (`AtlassianUser`, `scope: me`). Call `getWorkPortfolio` with `includeDirectReports: false`, `kinds: ["projects", "goals"]`, `view: "compact"` and `limitPerCollection: 10`. The scope is work assigned to, reported by or watched by the user, pages they created, edited or are mentioned on, and those projects and goals.
3. **A topic:** resolve it to the most specific record, as "Resolve the anchor" in `teamwork-graph-context` describes:
   - A Jira key or URL: an epic (`JiraWorkItem`), a Jira space (`JiraSpace`) or a board.
   - An Atlassian project or goal key, URL or name: `getProject` or `getGoal` (through `discover` and `executeRead`), or `searchProjects` and `searchGoals` with 1 or 2 key terms and `limit: 10`.
   - A Confluence space key or page URL.
   - A plain name ("Ledger"): run `searchProjects`, `searchGoals` and one `search` (`mode: STANDARD`, `targetApp: ALL`, `limit: 20`) together. Compare the candidates by scope and recency. If two are equally plausible, ask. If none matches, stop and say so.
4. **Build the scope set** for a topic. Everything later is filtered against it:
   - For a project, call `getProject` with `include: ["description", "links", "goals", "teams", "contributors"]`, `linkType: WORK_TRACKING` and `limits: {links: 20, goals: 5, teams: 5, contributors: 20}`. Keep the Jira keys and epics from the work-tracking links, the linked goals, and every Confluence, Google Drive or Slack URL in the description.
   - For a goal, call `getGoal` with `include: ["description", "projects", "teams"]` and `limits: {projects: 20, teams: 5}`. Its linked projects (up to 5, most recently updated first) join the scope.
   - Call `getGraphContext` on the anchor's URL or ARI with `detailLevel: summary`, then `full` for linked pages, conversations, repositories and work items only. Atlas keys don't resolve.
   - Note the Jira project keys, epic keys, Confluence space keys, repositories and channel names the records name, and 2 or 3 **distinctive terms** for search: the project or epic name, its key and any codename. Not the team or product-family name.
5. **Who's asking.** The page is about work, for the user who asked. If the topic is a person ("catch me up on what Sam did"), don't build a page about them: offer to catch the user up on a project or area they share instead. Every read runs with the user's own access, and "Needs you" holds only items that wait on the user.

### Dating every item

This is the rule the whole page rests on. Date each item by its event time, as "Dating events in a window" in `teamwork-graph-context` describes. One rule is specific to a catch-up:

- **Items from before the window** are left out, with one exception: things still waiting on the user (an open ask, open work assigned to them, an unreviewed pull request) stay in "Needs you", labelled "Open since [date]".

## Step 2: Find what needs the user

Gather everything waiting on the user from the window. One pass, at most 1 `getWorkActivity` call, 1 JQL query, 1 `getPullRequests` call, up to 4 pages of Confluence tasks, 2 CQL queries, 3 Loom lists, 2 Loom reads and 1 email search.

1. **Work assigned to them.** Run `searchJiraIssuesUsingJql` with `assignee = currentUser() AND statusCategory != Done AND (duedate <= endOfDay("+5d") OR assignee CHANGED TO currentUser() AFTER "<start>" OR created >= "<start>")`, adding the topic's `project in (…)` or `parent in (…)` clause when there is one, `fields: ["summary", "status", "duedate", "priority", "updated", "created", "project", "parent"]` and `maxResults: 25`. Keep `CHANGED` clauses next to an `assignee =` or `project =` clause: across the whole site with only `watcher =` beside it, the query timed out. Don't use `getWorkActivity` with `activity: assigned` for this: it misses work assigned before the window.
2. **Mentions, comments and asks in Atlassian.** Call `getWorkActivity` with `scope: me`, `activity: mentioned,assigned`, `types: jira,docs,comments,videos`, `from` and `to` set to the window, `hydrate: full` and `itemsPerSection: 25`. Leave `commented` out: in a pilot, 23 of 25 comments it returned were the user's own and pushed asks off the page. The user's own comments come from Step 1's call, and show which asks they've already answered. A comment with no author field can't be judged: read its author with the product's own tool (`getLoomObjectsContent` with `expand: ["comments"]` for Loom) or leave it out. Drop a comment along with its page when the page is board, calibration or people-programme material (see "Sensitive content"), even when it asks the user something. Treat other mentions and comments as asks when they name the user and ask a question or make a request ("can you", "could you", "please review"), or reply in a thread the user started. With a topic, keep only items in the scope set or naming a distinctive term.
3. **Review requests.** Run `getPullRequests` (through `discover` and `executeRead`) with `reviewer: "me"`, `state: "open"`, `hydrate: "summary"` and `limit: "10"`. Each open request is an ask, open since it was created. With a topic, keep requests in the scope's repositories or naming a distinctive term.
4. **Confluence tasks.** Run `listConfluenceTasks` (through `discover` and `executeRead`) with `assigned-to` set to the user's account ID, `status: incomplete` and `limit: 250`. It returns the oldest tasks first, so follow the `next` cursor until there is none, up to 4 pages, and say in the footer if more remained. Keep tasks created inside the window, and older ones due inside the next 5 working days.
5. **Actions from meetings in the window, attended or not.** Run `listLoomObjects` (through `discover` and `executeRead`) with `scope: "SHARED_WITH_ME"`, `artifactTypes: ["MEETING_RECORDING"]`, `createdAtRange` set to the window and `limit: 25`, plus the same with `scope: "MINE"`. List items carry each recording's AI summary by default, so pass `responseFields` for the title, creation date and URL only, check the titles against "Sensitive content", and read summaries only for the recordings you keep. With a topic, keep recordings whose name or summary names a distinctive term or a meeting from Step 5. Read up to 6 with one `getLoomObjectsContent` call with `expand: ["actionItems"]`. It returns the full AI summary too, and can't be filtered, so read only recordings whose titles passed the sensitive-content check. Read a people-programme recording only when the user runs the programme, and then use only the action items that start with the user's name. Treat "decisions" or "selection" in such a title as selection language. Loom titles carry the organiser's date, which can be a day off from the user's, so match a recording to a meeting by title and a day either side. Items that start with the user's name are theirs. Also read each AI summary for "[user] will…" lines: action items can miss the user's own promises. Skip 1:1s and mentoring sessions (a title with two names, "1:1" or "mentorship"). The response lists collaborators as email addresses. Never show them.
6. **Comments from others on the user's own work.** This is where people leave asks while someone is away, and no activity call returns it reliably.
   - **Confluence:** take the user's pages created or edited in the last 90 days (`searchConfluence` with `creator = currentUser() AND type in (page, blogpost) AND lastmodified >= "<90 days back>"`, `limit: 50`, or the pages Step 1 found), then run `searchConfluence` with `type = comment AND created >= "<start>" AND creator != currentUser() AND container in (<page ids>)`, `limit: 50`.
   - **Loom:** run `listLoomObjects` with `scope: "MINE"`, `sort: "CREATED_DESC"` and `limit: 25`, with no date range, because comments arrive on older videos. Read the 10 most recent with one `getLoomObjectsContent` call with `expand: ["comments"]`, and keep comments from other people created inside the window.
   - Treat a comment as an ask by the same rules as item 2. A comment that only reacts or thanks is a change for Step 4.6, not an ask.
7. **Asks in chat and email** come from the Step 4 search: results that name the user (use their Slack ID from a snippet, not their name) and ask something. If those results held no email at all and the client has an email connector, run one search for the window (Gmail: `to:me after:2026/10/06 -category:promotions -category:social -category:updates`). Read subjects, senders and snippets only, keep messages from people that ask something, and say in the footer that email was searched through the connector because the graph held none.
8. **Answered asks.** An ask is answered when the user replied in the thread snippet, commented later on the page, or the review is closed. An invitation from someone else to weigh in or override, on a page the user then commented on, is answered too.

Merge duplicates: a Loom action and the Jira item that tracks it are one item with two sources.

## Step 3: Find what was decided

A decision is a choice someone recorded as made: an approach chosen, a date agreed, scope cut, a request approved or declined. One pass, at most 1 CQL query and 1 `search`, plus the project and goal records already read.

1. **Recorded decisions.** For the anchor project and up to 5 linked projects or goals, call `getProject` or `getGoal` with `include: ["highlights"]`, `highlightType: "DECISION"` and `limits: {highlights: 20}`, and keep highlights created inside the window. Without a topic, do this for the projects and goals from `getWorkPortfolio`, most recently updated first.
2. **Decision pages.** Run `searchConfluence` with the scope's spaces (or, with no topic, `contributor = currentUser() OR watcher = currentUser()`) and `AND (label in ("decision", "decisions", "decision-log") OR title ~ "decision") AND lastmodified >= "<start>"`, `limit: 25`. Meeting notes don't share a title pattern (Loom's are "[meeting title] [date]"), so decisions from meetings come from item 4 instead. For each candidate, read the outline (`getConfluenceContent`, `detail: outline`), then the full page only for those with a decision table or a "Decisions" heading, and keep the decisions dated inside the window.
3. **Decisions in chat and docs.** Run one `search` (`mode: STANDARD`, `targetApp: ALL`, `limit: 20`) with the topic's distinctive term (with no topic, the first search term from Step 4.5) plus "decided" or "agreed". Keep a result only if it's inside the window and its snippet states a decision in plain words ("we decided", "agreed to", "we're going with", "approved", "signed off"). A proposal, a question or "let's discuss" is not a decision.
4. **Decisions in meetings** the user missed come from the recordings in Step 2 and the notes in Step 5: AI summary lines that say something was decided or agreed.

**Never infer a decision** from a status change, a closed work item, a moved date or a title. A work item closed as Won't do is a Scope change in Step 4, unless a record says who decided and why. Each decision names what was decided, who decided or recorded it (the highlight's or page's author, or the person the snippet quotes), when, and the source. When a recording says only that the group agreed, write "agreed in the [meeting] on [date]". Never name a decider the source doesn't name.

## Step 4: Find what changed

Changes made by someone else, inside the window, to the work in scope.

1. **Jira.** Run `searchJiraIssuesUsingJql` with the scope clause (`project in (…)`, `parent in (…)`, or with no topic `(assignee = currentUser() OR reporter = currentUser())`) `AND updated >= "<start>" ORDER BY updated DESC`, `fields: ["summary", "status", "issuetype", "assignee", "duedate", "priority", "created", "resolutiondate", "parent", "updated"]` and `maxResults: 50`. If it returns 50, run it once more with `searchResultMode: "count"` for the candidate total, and with `resolved >= "<start>" AND resolved < "<exclusive end>"` for the number done. The updated query finds candidates, including items edited again after the window: count only confirmed events inside the window as changes, and report the candidate total separately. Work items created or resolved inside the window are dated by those fields. For the others, rank as Step 7 describes and read the history of the top 8 with `listJiraIssueChangelogs` (through `discover` and `executeRead`): it's oldest first, so call it with `maxResults: 1` to read `total`, then read the last 10 entries with `startAt: total - 10`. Keep entries inside the window that someone other than the user made, for status (especially to Blocked or Done), assignee, due date, priority and new blocking links. Use `fromString` and `toString` for what changed.
2. **Projects and goals.** For the anchor and up to 5 linked projects or goals (or, with no topic, those from `getWorkPortfolio`), call `getProject` with `include: ["updates", "dependencies"]` and `limits: {updates: 10, dependencies: 20}`, or `getGoal` with `include: ["updates", "projects"]` and `limits: {updates: 10, projects: 20}`. Read target date moves from each update's `previousTargetDate` and `targetDate`, and status changes by comparing each update inside the window with the one before it. Use `latestUserUpdate`, not system updates. A project with no update inside the window is "No update since [date]", which is a finding only if it was due one.
3. **Confluence.** Run `searchConfluence` twice with a parenthesized scope clause (`space in (…)` or `ancestor = <id>`; with no topic, `creator = currentUser() OR contributor = currentUser() OR mention = currentUser() OR watcher = currentUser()`), followed by `AND type in (page, blogpost)`, `limit: 25`: once with `AND created >= "<start>" AND created < "<exclusive end>"` for New pages, and once with `AND lastmodified >= "<start>" ORDER BY lastmodified DESC` for edit candidates. Keep the latter query open-ended: a page edited both during and after the window must still be considered. CQL results carry no dates (their `lastModified` is relative text, "about 4 hours ago", and `expand` is ignored), so the bounded `created` query identifies New pages, while version history dates edits.
   - For the top 6 edited pages, run `listConfluenceContentVersions` with `limit: 100`, following the cursor until a version is older than the window (live docs autosave dozens of versions a week). Choose the baseline as the last version before the start, and the comparison endpoint as the last version before the exclusive end. Ignore later versions even when one is the current version.
   - Run `diffConfluenceContentVersions` only between those chosen versions, and summarise that diff in one sentence. If both endpoints are the same version, there was no edit in the window. A page created during the window is New rather than an edit requiring an older baseline. If complete history shows the page was created after the window, leave it out as a later creation. If history is incomplete and cannot establish the endpoints, report that the change couldn't be checked; never substitute the current version or its body.
   - Any claim about what a page contained during the window, including a New page's summary, must come from the chosen endpoint version or the bounded diff. Read that version's body when needed within the history caps; otherwise report the content check as not run. Current page content changed after the window is not historical evidence.
   - Versions give editors as account IDs: name them with one `getPeopleInfo` batch. Drop edits by the user and pages edited only by them. Keep each edit's source date inside the window; later edits do not supply its date or summary.
4. **Code.** Run `getPullRequests` with `scope: "all"`, `state: "merged"`, `mergedSince` set to the start, the scope's `repo` list or `query` set to a distinctive term, `hydrate: "summary"` and `limit: "20"`. With no topic, use `author: "me"`, `updatedSince` set to the start and `hydrate: "full"` instead, and keep only pull requests someone else reviewed, approved, requested changes on or merged inside the window. The user's own merges are already seen. Merged pull requests are Shipped. With `author: "me"`, leave `scope` out: `scope: "all"` with a person fails ("accountId/name/email require scope user or scope org"). If `mergedAt` is null, date the pull request by `updatedAt` and say "updated", not "merged". If the result says `partial: true`, report "no results", not "none".
5. **Chat, docs and code outside Atlassian.** This pass is required on every run. Teamwork Graph comes first. Run up to 3 `search` calls (`mode: STANDARD`, `targetApp: THIRD_PARTY`, `limit: 30`), one per distinctive term, plus the user's Slack ID once you have it from a snippet. Use 1 to 3 distinctive words of each. With no topic, take the terms in this order: the titles of the user's own most active objects from Step 1 (the pages, decks and videos they made or edited most), then their active projects from `getWorkPortfolio`, then recurring meeting titles. Search has no date filter, so keep results whose `lastModified` is inside the window and drop the rest. A pass with nothing inside the window is a result to report, not a reason to skip it.
   - Drop calendar events, commits, bot and dependency-update pull requests, artifacts the user published, and private and group direct messages unless the user asks for them (see "Sensitive content").
   - Keep a thread or doc only if it names a distinctive term or sits in a channel or folder the scope set names. Generic matches ("roadmap", "blockers", "launch") don't count.
   - Slack and GitHub results often won't hydrate. The snippet is the citable text: quote only words inside it, and say in the footer that full threads weren't read.
   - Use a vendor connector (Slack, Teams, Gmail or Outlook) only when this came back empty or too thin inside the window, with the connector's own date operators (`after:2026-10-06`), and say which gap it filled.
6. **Activity on the user's own work** in other apps (Loom comments, replies to threads they started) comes from Step 2.6 (comments on their pages and Looms) and these search results. No tool reads a notifications inbox, so don't claim to cover notifications.

## Step 5: Meetings missed and coming up

At most 3 calendar connector calls and 1 `search`.

1. **Missed.** With the calendar connector, call `list_events` from the start to the end of the window with `eventType: ["DEFAULT"]`, `orderBy: "startTime"` and `pageSize: 100`. With a topic, pass `fullText` set to the most distinctive term (and a second call for a second term if the first returns nothing). Keep meetings the user was invited to and didn't decline. Leave out personal, leave, travel and wellbeing events by title, and don't count them. Skip 1:1s and mentoring sessions, as Step 2.5 does. Without a topic, keep only recurring meetings with 3 or more attendees and meetings that left a recording or notes. Events from a group calendar with the guest list hidden (`guestsCanSeeGuests: false`) are broadcast sessions: keep them only if the user presented or organised. **Leave out meetings the user attended** (see "What the user already saw"), and count them in the footer.
2. **What came out of them.** Match each kept meeting to a recording from Step 2 (Loom names them "[title] - [Month D, YYYY]") or to notes. Run one `search` (`mode: STANDARD`, `targetApp: ALL`, `limit: 20`) for "Notes - [title]" or "[title] meeting notes" for the most important meeting with no recording. Give each meeting one line: the one decision or action that matters to the user, or "No notes or recording found". Cap at 6 meetings, most relevant first (meetings the user organises, then the topic's own, then the rest).
3. **Coming up.** Call `list_events` from now to 5 working days ahead, with the same filters. Keep up to 5 topic meetings (with no topic, recurring meetings with 3 or more attendees, one-off meetings in the next 2 working days, and any meeting tied to a Needs you item, including a 1:1), plus due dates from Step 2 and project target dates from Step 4 inside those 5 days. Link a meeting to the calendar's day view, not its `htmlLink`.
4. **Without the calendar connector,** missed meetings are the recordings and notes found in Steps 2 and 3 only. Say so at the top of the Meetings card ("Teamwork Graph can't list meetings in a window, so recurring meetings without a recording or notes are missing"), and leave Coming up to due dates and target dates.
5. Never copy passcodes, meeting IDs or dial-in numbers, never say why someone declined or was away, and don't link the calendar event's `htmlLink` (its `eid` encodes an email address).

## Step 6: Hydrate

Read only what the page will show. Batch reads of known objects: one `getGraphObject` call for up to 25 Atlassian objects and Drive docs, one JQL `key in (…)` query for work items mentioned in text, and `getConfluenceContent` (`detail: outline` or `summary`) for pages. Third-party items that won't hydrate are cited by their snippet, as `teamwork-graph-context` describes. Check every result against "Sensitive content" before using it.

## Step 7: Assess

### Needs you

One type per row:
- **Overdue** (danger): work or a task assigned to the user, past its due date.
- **Due soon** (warning): due in the next 5 working days.
- **Blocking** (danger): open work the user owns that blocks someone else's, confirmed with `getJiraIssue` (`view: evidence`).
- **Ask** (information): a question or request for the user, unanswered.
- **Review** (information): an open review request.
- **Assigned** (neutral): newly assigned inside the window, not due soon.
- **Action** (neutral): an action item for the user from a meeting in the window, attended or not, not visibly done.

Leave out asks Step 2 found answered. Drop asks whose moment has passed (a review for a merged pull request, a link wanted for a session that's over). Rank by when it bites: Overdue, then Due soon by date, then Blocking, then Asks and Reviews tied to something dated (a meeting in Coming up, a deck or doc in use, a due date), then other Asks and Reviews oldest first, then Assigned, then Action. Keep up to 8, and count the rest in the footer.

### Decided

One type: **Decided** (success). Rank decisions that change the user's own work or dates first, then scope and approach decisions for the topic, then the rest, newest first within each. Keep up to 6. A decision the user is asked to act on also gets a Needs you row, which links to it.

### What changed

One type per row:
- **Blocked** (danger): moved to Blocked, flagged, or a new blocking link.
- **Off track** (danger) and **At risk** (warning): a project or goal status change.
- **Date moved** (warning): a target or due date moved, with from and to.
- **Scope** (neutral): work added to or removed from the scope, closed as Won't do, or a dependency added.
- **Shipped** (success): work resolved as Done, a pull request merged, a release.
- **New** (information): a page, doc, epic or project created inside the window.
- **Update** (neutral): a notable edit, project update or discussion.

**Relevance.** With a topic, keep a change only if it's in the scope set (Confirmed) or names a distinctive term (Found by search). With no topic, keep it only if it touches work the user owns, is assigned, wrote or is named on. Drop housekeeping: formatting edits, score nudges, attendee tweaks, label changes, and bulk resyncs (many items changed by one actor within a few minutes).

**Ranking.** Blocked, Off track, At risk, Date moved, Scope, Shipped, New, Update. Within a type, changes to the anchor itself come first, then newest first. Don't rank by priority field, number of edits or how long a thread is.

**Grouping.** Group rows by area: the epic or project for Jira and Projects, the space or page tree for Confluence, the channel or folder for third-party items. Show up to 4 groups and 12 rows in total, the group with the highest-ranked row first. Fold groups with a single row into a last group, "Other", whose heading isn't a link and which can mix apps, so a lone Slack or Drive change isn't dropped by the cap. If any third-party change survived ranking, at least one shows. Fold Shipped rows when a group has more than 3: one row, "8 work items done, including ATLAS-101 and ATLAS-104", linking the JQL search. Count everything left out in the footer.

### The summary

"While you were away": two or three sentences, at most 60 words. The first names the one thing to do first and why. The second names the most important decision or change. The third gives the shape ("41 work items moved and 2 projects changed status across Jira, Confluence and Slack"). Use only facts from Steps 2 to 5. Never mention why the user was away.

### Stop gathering

Stop when each pass has run once: needs you (Step 2), decisions (Step 3), changes from each source in Step 4, including the third-party search, and meetings (Step 5). A pass that failed twice is "Not run" in the footer, with the reason. One extra call is fine if it could change the top Needs you item or the top decision.

## Writes

None. This skill is read-only. It doesn't reply, transition work, complete tasks or change meetings. If the user asks to act on an item, confirm the exact change first, as `teamwork-graph-context` describes.

## Answer and offer an export

- Lead with the window, scope and summary from Step 7, including the top Needs you item and the most important decision or change.
- Present Needs you, Decided, What changed, Meetings you missed and Coming up as applicable. Keep Step 7's ranking, grouping and row limits, source links and event dates, seen-item exclusions and required empty-state caveats. The report section below also specifies the content each section retains; use Markdown in the conversation rather than its visual layout.
- Before answering, check that each pass ran: assigned work, Atlassian asks, review requests, Confluence tasks, meeting actions, decisions, Jira, projects and goals, Confluence, code, the third-party search, and meetings. In Sources and limitations, name any that did not run and why, plus the window, timezone, counts left out, caps and coverage gaps required by the report's sources footer.
- After the answer, offer one next step that fits: `/meeting-prep` for the next topic meeting, or `/status-check` or `/dependency-map` when a project or goal changed status.

Ask whether the user wants this exported to an HTML report. If they have already explicitly requested an export, HTML report or publication, proceed with that requested build without asking again. Otherwise stop here until they answer; a normal invocation of this skill does not request a report. Follow the shared availability and confirmation checks before offering or performing publication.

## Step 8: Build the page (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in this folder:

```bash
python3 <this skill's folder>/render.py catchup.json catch-up-<topic>.html
```

- **The data** has the shape of `example.json` in this folder (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **Rows** are `{"type", "text", "source", "when"}`: `type` is the lozenge, `source` is the smart link (or a list of them) for the source line, and `when` is the event date. A row can carry an excerpt as `quote` and `quoteFrom`.
- **Keys to know.** With no topic, leave out `topic`. The renderer counts Needs you and decisions itself. Give `counts.changes` when the changes found are more than the rows shown. Keys the example doesn't use: `summaryHeading` ("Since Oct 5" when Step 1 found the user active), `decisionNotes` and `meetingNotes` (the extra lines under an empty or partial section), and `counts.needYou` and `counts.decisions` when there are more than the rows shown.
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `references/hand-built.md` in this folder.

The rules below say what the renderer builds, and what each part of the data must hold.

Every row is one sentence of about 25 words, with its source and the event date. Use absolute dates ("Oct 9"), because a window is days or weeks long. Old items still waiting say "Open since Sep 29".

### Sections, in this order

1. **Header** (not a card): eyebrow "Catch-up", then the topic's name as the page's only `h1` ("Ledger"), or "Your work" with no topic. Then one row with the meta line on the left and count lozenges on the right (they wrap below on phones).
   - Meta line: `calendar` icon with the window and its length ("Mon, Oct 6 to Fri, Oct 17 · 10 working days"), and "From your calendar" when Step 1 took it from an out-of-office event.
   - Count lozenges, each shown only when above zero: "3 need you" (warning when any is Overdue or Blocking, otherwise information), "2 decisions" (success), "18 changes" (neutral).
2. **While you were away** (icon `ai-sparkle` in `--ds-icon-discovery`), or **Since [start]** when Step 1 found the user active on most of the window's working days: the summary at 24px line height. Underneath, in small subtlest text, the apps actually used: "Generated from Jira, Confluence, Projects, Slack and Google Calendar. Check it before acting on it."
3. **Needs you** (icon `flag`): rows ranked as Step 7 says. If there's nothing, show "Nothing is waiting on you." in subtlest text.
4. **Decided while you were away** (icon `decision`): one row per decision. The sentence says what was decided and who decided it ("Amara Lindqvist decided to keep the old search index until Nov 14"), and the source line has the smart link and date. If there are none, show "No decisions you missed in this window.", add "[N] from meetings you attended aren't repeated." when the seen rule left some out, and add in subtlest text that decisions made only in calls or direct messages can't be seen.
5. **What changed** (icon `changes`): a small subheading per group (the area's name as a smart link, or plain text for "Other" and for a group of the user's own items, such as "Your Loom videos"), then its rows. Items found by search carry the "Found by search" chip as `teamwork-graph-context` describes. If there's nothing, show "No changes to this work between [start] and [end]."
6. **Meetings you missed** (icon `video`): one row per meeting: a fixed-width date column ("Oct 8"), then the title in medium weight, a meta line (attendee count, organiser, "weekly" when recurring), and the one line from Step 5 with its recording or notes smart link. A meeting with no notes says so in subtlest text. With none, show "No meetings you missed in this window." and, when attended meetings were left out, add "[N] meetings you attended aren't shown." With the Teamwork Graph fallback, end the card with its limitation line.
7. **Coming up** (icon `clock`): up to 5 rows for the next 5 working days, with the date, the title and why it matters ("Ledger review, Tue, Oct 22: the plan changed on Oct 14"). Leave it out when there's nothing.
8. **Sources footer** (not a card, small text), as `teamwork-graph-context` describes, plus:
   - the window and timezone, and the dating rule in one line: "Items are dated by when they happened, not when they were last touched."
   - how many items were left out for being outside the window, for being after an explicit end date, and because the user had already seen them (with the active-days count from Step 1 when it applied)
   - every cap that applied, and the counts left out of each section
   - search warnings ("Some search sources could not be queried") once, with how many searches returned them, not once per search
   - what the third-party pass did: "Searched Slack, Google Drive and GitHub through Teamwork Graph (3 queries, 11 results in the window)", "No results from [app]" or "Not run: [reason]". List the query terms, and say whether a Slack ID was used, without the ID.
   - gaps that affected the page: recurring meetings missing without the calendar connector, full threads not read, no notifications inbox, partial pull request results
   - when the page was prepared, as a relative time plus the absolute date, time and timezone

### Copy

- Name people. When a fact came from chat, email or a call rather than a record, say so ("Marco said in Slack that…", "agreed in the Oct 8 sync").
- No em dashes or en dashes in your own copy. Ranges read "Oct 6 to Oct 17". Sentence case everywhere.

### Mockups and sample data

Follow the mockup rules in `teamwork-graph-context`.

## When live

Static only. A catch-up covers a fixed window and is read once, on the way back in. For what changes after that, the user runs `/catch-up` again with a new window.

## Step 9: Deliver the requested report

- Hand over the requested HTML report. If Atlassian Artifacts availability is confirmed as described in `teamwork-graph-context`, offer a private, read-only copy named "Catch-up: [topic], [start] to [end]" ("Catch-up: Ledger, Oct 6 to Oct 17"), or "Catch-up: your work, ..." with no topic. Put the window and counts in the description. Publish only if requested; report export alone does not authorise it. Create a Confluence page instead only if the user asks.
- The report is personal: Needs you is about the user. Do not offer to share it. If the user asks, share only with the people they name.
- Keep the answer's evidence, dates and limitations in the report. Report generation does not replace a check that was not run.
