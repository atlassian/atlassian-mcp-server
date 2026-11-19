---
name: "dependency-map"
description: "Map what a Jira issue, epic, project, or board depends on (upstream) and what depends on it (downstream) using Jira issue links, remote links, changelogs, Confluence specs, and Rovo Search. Delivers a structured conversational dependency map with direction confirmed from Jira link wording, separate State (Blocked, At risk, Stale handoff, On track, Done, Unknown) and Source (Recorded vs Not recorded) columns, second-hop upstream blockers, owners to contact, and optional confirmation-gated Jira link creation. Use for dependencies, cross-team blockers, who is waiting on whom, or /dependency-map."
---

# Dependency Map

Explain in the conversation, for a Jira epic, issue, project, or board, what it is waiting on (upstream), who is waiting on it (downstream), which dependencies are in trouble, and who to talk to about each. Designed for owners who need to chase blockers across Jira projects and teams.

Dependency direction in Jira is easy to misread because custom link types vary across sites and some dependencies are only mentioned in Confluence specs or comments rather than recorded as links. This skill enumerates Jira issue links directly, confirms direction from each link's exact Jira wording (`type.outward` / `type.inward`), expands one hop further on troubled upstream items, checks Confluence specs and Rovo Search for unrecorded dependencies, and presents Recorded and Not recorded dependencies side by side.

Load the `teamwork-graph-context` skill first and follow it for direct v2 tool usage, schema verification, source labeling, sensitive-content filtering, and conversational delivery.

## Tool Access & Coverage

- **Needed:** Jira (`getAccessibleAtlassianResources`, `searchJiraIssuesUsingJql`, `getJiraIssue`, `listJiraIssueLinkTypes`, `listJiraIssueRemoteIssueLinks`, `listJiraIssueChangelogs`, `listJiraIssueComments`, `listJiraBoards`, `listJiraBoardSprints`, `getJiraBoardSprintData`, `getJiraBoardIssueData`, `getJiraUser`). Call `getAccessibleAtlassianResources` once for `cloudId` and the site base URL, then call Jira tools directly (do not block on a `products` field).
- **Helpful, from Atlassian:** Confluence (`searchConfluence`, `getConfluenceContent`) and Rovo `search` for plans, specs, or discussions mentioning unrecorded dependencies.
- **Write tools (only on explicit user confirmation):** `createJiraIssueLink` and `createJiraIssueRemoteIssueLink` (called directly by name).
- **Unavailable on this connector:** Atlassian Projects (Atlas), Goals, Teams, Compass components/services, Bitbucket/code dependencies, Teamwork Graph traversal, and reporting-line/manager escalation directories are **not** exposed on this Atlassian connector. Never attempt to call tools for those scopes; map Jira work items, epics, projects, and boards, and state transparently in Sources and limitations that Atlas Projects, Goals, Teams, Compass, code/PRs, and manager lookups were not checked.
- **Optional standalone session connectors:** If the user's session also exposes Slack/Teams or GitHub connectors, you may optionally check them read-only for unrecorded blocker threads or PR dependencies, labelling those hits by app.
- **Direct calls & live schema check:** Call every tool directly by name. If a tool is not in your tool list, it is not available on this connector; say so and use the closest available tool. Always inspect live tool schemas before passing parameters — especially:
  - `getJiraIssue`: verify whether `view` is supported or pass explicit `fields: ["summary", "status", "assignee", "project", "duedate", "issuelinks", "resolution", "resolutiondate"]` (prefer explicit `fields` to avoid oversized custom-field payloads).
  - `search`: Use cloudId and query, with optional targetApp and limit; do not pass mode.
  - `createJiraIssueLink` / `createJiraIssueRemoteIssueLink`: verify exact parameter names (`cloudId`, `inwardIssue`, `outwardIssue`, `type`, `issueIdOrKey`, `url`, `title`) before writing.

## Two things to track for every dependency

Keep these strictly separate throughout gathering and output:

- **State:** how it is going — **Blocked**, **At risk**, **Stale handoff**, **On track**, **Done**, or **Unknown** (Step 5).
- **Source:** how you know it exists:
  - **Recorded:** a Jira dependency issue link (standard or custom link type) whose meaning and direction are confirmed from Jira's link wording.
  - **Not recorded:** found only in a Confluence spec/risk table, Jira comment, or search result (never silently promoted to Recorded).

A Not recorded dependency can still be **Blocked** (goes in Needs attention, clearly labelled `"Not recorded — from [source]"`).

## Step 1: Resolve the anchor

| The user gives you | Anchor | Resolve with | Scope of "our work" |
| --- | --- | --- | --- |
| A Jira epic or work item key / URL | Jira Work Item | `getJiraIssue` (explicit `fields`) + children via `searchJiraIssuesUsingJql` (`parent in (<key>)`) | The item/epic and its children (up to 50) |
| A Jira project / space key | Jira Project | `searchJiraIssuesUsingJql` for open epics (`project = "<KEY>" AND issuetype = Epic AND statusCategory != Done`) plus items due in the next 6 weeks | Open epics and near-term work (up to 50 items) |
| A Jira board or sprint | Jira Board / Sprint | `listJiraBoards`, `listJiraBoardSprints`, `getJiraBoardSprintData` / `getJiraBoardIssueData` | Active sprint issues or board scope (up to 50 items) |
| An Atlassian Project, Goal, Team, or Compass service | — | Explain that Atlas Projects, Goals, Teams, and Compass are not exposed on this connector, and ask for the backing Jira epic key, project key, or board instead | — |

Capture the anchor's assignee/owner, Jira project, short name (distinctive 1–3 words used in specs/comments), and **need-by date** (due date, target fixVersion release date via `getJiraProjectVersions`, or sprint end date):
- If the need-by date has already passed while the anchor is not Done, highlight `"passed"` in the header.
- If no need-by date is recorded, say `"No need-by date set"` (At risk checks then rely on dependency dates and staleness).

## Step 2: Find the edges (Jira dependency links)

1. **Enumerate all `issuelinks` on scoped work:** Batch scoped Jira keys by site using `searchJiraIssuesUsingJql` (`key in (...)`, `fields: ["summary", "status", "assignee", "project", "duedate", "issuelinks", "resolution", "resolutiondate"]`, `maxResults: 50`, paginating with `nextPageToken`). Call `getJiraIssue` (with explicit `fields`) for any individual item needing fuller link detail.
2. **Read direction strictly from Jira's own wording:**
   - For an entry with `outwardIssue`, read: `"[this item] [type.outward] [other item]"`.
   - For an entry with `inwardIssue`, read: `"[this item] [type.inward] [other item]"`.
   - The other item is **upstream** (our work waits on it) when the phrase says `"is blocked by"`, `"depends on"`, `"requires"`, or `"is caused by"`.
   - The other item is **downstream** (it waits on our work) when the phrase says `"blocks"`, `"is depended on by"`, `"is required by"`, or `"causes"`.
   - Ignore generic non-dependency links (`relates to`, `clones`, `duplicates`, `follows`).
   - For unfamiliar custom link wording, call `listJiraIssueLinkTypes` directly and check issue comments/records or ask the user; until confirmed, leave it off the dependency map and list the unresolved link type in Sources and limitations. Never infer direction from `inwardIssue` vs `outwardIssue` without reading the wording.
   - **Both ways:** If records show both sides waiting on each other, list it once on the upstream side threatening the anchor's date and mark it **Both ways**.
   - Deduplicate links seen from both ends.
3. **Remote links & cross-site keys:** Call `listJiraIssueRemoteIssueLinks` on the anchor (and top epics) to capture linked Confluence specs/plans or external dependencies. For linked Jira keys in other projects, batch `key in (...)` **one project key per query** (so an inaccessible key does not fail the batch); list unreadable or external-site keys as unreadable in Sources and limitations.
4. **Which edges to keep:**
   - Keep all cross-project / cross-owner dependencies.
   - Keep same-project / same-team links only if they are actively blocking or open upstream.
   - Do not skip Done dependencies automatically — verify resolution status (and check for stale handoffs in Step 5).
5. If scoped Jira work has zero `issuelinks`, say so explicitly in Sources and limitations (never silently skip).

## Step 3: Go one hop further on troubled upstream items

For each upstream Jira dependency assessed as **Blocked**, **At risk**, or **Stale handoff** (Step 5), inspect its `issuelinks` once (via a single batched JQL query or `getJiraIssue`) to uncover second-order blockers ("we wait on Search, and Search waits on Platform").

**Stop at two hops from the anchor.** State the 2-hop boundary in Sources and limitations and list any edges not followed.

## Step 4: Find dependencies nobody recorded

1. **Rovo `search` (check live schema first):** Run up to 3 focused searches using the anchor's short name: `"blocking <short name>"`, `"<short name> blocker blocked"`, and `"<short name> waiting on depends on"`. Keep hits from the last 30 days (by `lastModified`; note strong older hits in Sources and limitations).
2. **Linked specs & plans:** Read Confluence pages linked via `listJiraIssueRemoteIssueLinks` or found via `searchConfluence` (CQL for the anchor's key/name + `"dependencies"` or `"risks"`) using `getConfluenceContent` (`detail="full"`, re-reading HTML if `lostFeatures` drops panels/dates). Look for Dependencies or Risks sections.
3. Keep a candidate only if it names a specific team, deliverable, ticket, or person AND references the anchor. Mark its source **Not recorded**, cite the quote/link, and assign a State from what the text says (or **Unknown** if no progress is stated).

## Step 5: Assess each dependency

Fetch current details (`summary`, `status`, `assignee`, `project`, `duedate`, `resolution`, `resolutiondate`, `updated`) for all linked Jira items via batched JQL `key in (...)` (one query per project key). Assign one **State** per dependency:

**Upstream** (our work waits on it):
- **Blocked:** the dependency itself has a Blocked status/flag, our item is marked blocked by it and it is not Done, or a record/comment states it is blocking.
- **At risk:** not Done AND any of: its due date is after our need-by date; our need-by date has passed; it has no due date while our anchor has one; or it has had no update in 14+ days.

**Downstream** (it waits on our work):
- **Blocked:** our work is actively blocking it and records state so.
- **At risk:** its due date is earlier than our anchor's need-by date (or earlier than today if our need-by date passed and our anchor is not Done).

**Both sides:**
- **Stale handoff** (test only items resolved 7 to 30 days ago): the upstream blocker was resolved 7–30 days ago, yet the blocked item's status has not moved since (confirm via `listJiraIssueChangelogs` directly); OR a recorded dependency has no assignee on either side. (Items resolved >30 days ago are **Done**, not stale.)
- **On track:** dated before need-by and actively moving.
- **Done:** resolved/delivered in Jira.
- **Unknown:** no status or progress recorded (common for Not recorded items).

**Contact for each Blocked, At risk, or Stale dependency:**
- Take the assignee/owner from Jira (use `getJiraUser` directly only if returned as an account ID without a display name; never show emails). Note transparently that reporting-line/manager escalation lookup is unavailable on this connector.
- Note in 1 sentence what would unblock it, only if stated in Jira comments (`listJiraIssueComments`) or docs.

Stop gathering once every shown dependency has a confirmed direction, State, Source, owner (or `"Unassigned"`), and due date (or `"No date"`).

## Step 6: Prepare optional offers to record missing links

For each **Not recorded** dependency discovered in Step 4, prepare the matching direct Jira write — present offers *after* the conversational map and **never execute any write without an explicit "yes"**:

- **Both sides are Jira issues:** `createJiraIssueLink` directly (e.g., type `Blocks`). Inspect the live `createJiraIssueLink` tool schema first to confirm exact parameter names (`cloudId`, `inwardIssue`, `outwardIssue`, `type`) and direction!
- **Jira issue to a Confluence page or external URL:** `createJiraIssueRemoteIssueLink` directly (inspect live schema for `cloudId`, `issueIdOrKey`, `url`, `title`).

Always show the exact proposed link(s), issue keys, and direction ("A blocks B") before asking for confirmation.

## Conversational Answer Structure

Deliver the complete dependency map directly in Markdown:

1. **Header & Summary:** Anchor link, Jira project, owner, need-by date (noting if passed or unset), counts (**Waiting on**, **Waiting on us**, **Need attention**, **Not recorded**, plus open/done breakdown), and 2–3 sentences highlighting the highest-impact dependency and who to contact.
2. **Needs attention (Blocked, At risk, Stale handoff — most severe first):** For each: dependency link, direction (`Upstream` / `Downstream` / `Both ways`), **State**, **Source** (if Not recorded), 1-sentence reason, **Contact** (assignee from Jira), and evidence link.
3. **Full dependency map (Markdown tables):**
   - **Waiting on (Upstream — including 2nd-hop blockers indented or tagged `Hop 2 -> feeds <KEY>`)**: Item link | Project/Owner | State | Source | Due/Status date | Evidence
   - **Waiting on us (Downstream)**: Item link | Project/Owner | State | Source | Needed-by date | Evidence
   - State explicitly if either side has nothing recorded ("Nothing recorded downstream in Jira").
4. **Not recorded dependencies** (if any): Item, State, brief evidence quote/link, and the exact recording offer (`createJiraIssueLink` or `createJiraIssueRemoteIssueLink`).
5. **Next steps:** 2 to 4 numbered, prioritized actions naming the specific assignee/contact and issue key.
6. **Sources and limitations:** Scope and hop boundary (`Followed 2 hops from [anchor]; did not follow: [...]`), unresolved custom link types, unreadable/cross-site keys, search window (30 days), caps applied, and the explicit statement that **Atlassian Projects (Atlas), Goals, Teams, Compass, code/PRs, and manager escalation directories are not exposed on this connector** and were not checked.
7. **Write offers (confirmation-gated):** List exact proposed Jira links and directions from Step 6 and wait for an explicit "yes".
## Optional offline report

Answer in the conversation first. When the user requests an HTML report, read [the report export instructions](references/report-export.md), load atlassian-design, and run the bundled render.py from this skill directory using its example.json and data-format reference. Preserve the same facts, verdict, condition count and coverage gaps in the report. Both design kits run offline with Python's standard library; do not install packages or download assets. Export does not authorize publication or sharing. Return static HTML when publication tools are unavailable.
