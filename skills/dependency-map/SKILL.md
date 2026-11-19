---
name: "dependency-map"
description: "Map what a project, goal, epic, team or service depends on and what depends on it, across teams and tools, using Teamwork Graph and Projects and Jira records. Answers in the conversation first with dependency direction, state and source, blocked or at-risk work, stale handoffs, unrecorded dependencies and the owner to contact. Offers an HTML report with the existing SVG dependency diagram on request, and publication only when Atlassian Artifacts is available and requested. Use for dependencies, cross-team blockers, who is waiting on whom, or /dependency-map."
---

# Dependency map

Explain in the conversation, for a piece of work, what it's waiting on, who's waiting on it, which of those links are in trouble, and who to talk to about each. It's written for the person who owns the work and has to chase other teams.

Dependencies live in Projects, Jira links, service catalogues, code and, often, only in a Slack thread. Teamwork Graph helps find them, but its edge names don't all read the same way, it misses some project links, and it skips custom Jira link types. So this skill finds candidates in the graph, then takes direction and status from the product records. The map shows recorded and unrecorded dependencies side by side.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. Load its `references/graph-context.md` for graph enrichments when those tools are available. This file adds what's specific to dependencies.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## Two things to record for every dependency

Keep these separate all the way through, from gathering to the diagram.

- **State:** how it's going. One of Blocked, At risk, Stale handoff, On track, Done or Unknown (see Step 5).
- **Source:** how you know it exists.
  - **Recorded:** a DEPENDS_ON or DEPENDED_BY link, or a Jira dependency link, including a custom type, whose meaning and direction are confirmed.
  - **Related:** a RELATED link whose direction comes from another record.
  - **Not recorded:** found only in chat, a doc or a search.

A Not recorded dependency can be Blocked. If chat says it's blocking, it's Blocked and goes in Needs attention, labelled with where it came from ("from Slack, not recorded").

## Tool access and coverage

Load `teamwork-graph-context` first. Call tools directly when exposed. If a needed operation is not exposed and discovery is available, discover it and use the matching runner with its returned schema. Skip an operation only after checking the session's capabilities. Missing `products` metadata means unknown availability, not no access.

Use the full workflow when its tools are available. With Jira, Confluence and Rovo Search only, gather those records and use the fallbacks below. Keep unavailable, permission denied, successful empty results and checks not run distinct. List the impact of each gap in Sources and limitations. A Jira project is not an Atlassian Project.

## Resolve and collect

Read [the recorded-link procedures](references/recorded-links.md) before resolving the anchor or expanding dependencies. Support the original Jira issue/epic/version, Atlassian Project/Goal, service and code anchors when their tools are available. A Jira-only session needs a Jira anchor or a readable linked Jira record; ask for one when necessary rather than treating a Jira project as an Atlassian Project.

1. Resolve the supplied anchor and gather its recorded relationships. Use product reads to confirm graph candidates. For Projects, `getProject` with dependencies is authoritative: DEPENDS_ON is upstream, DEPENDED_BY downstream and RELATED has no direction. Use recorded work-tracking links and URLs to reach Jira work, rather than assuming a Project node contains it.
2. Confirm every Jira dependency using the actual issue-link wording. With `outwardIssue`, read `[this issue] [type.outward] [other issue]`; with `inwardIssue`, use `type.inward`. The other issue is upstream for "is blocked by", "depends on", "requires" or "is caused by", and downstream for "blocks", "is depended on by" or "is required by". Relates to, follows, clones and duplicates do not imply waiting. Custom Jira link types can be absent from graph results.
3. Read upstream/downstream status, due date and recorded owner. Keep unreadable or other-site keys as gaps. Query distinct Jira project keys separately so one inaccessible project cannot fail the entire batch. Expand one further hop only for dependencies in trouble, under the reference's limits; do not crawl the graph without a bound.
4. Look for unrecorded dependencies in explicit statements in readable updates, issue comments, plans and discussion. Use JQL/CQL constraints and Rovo Search without `mode`. Keep these Found by search and distinguish them from recorded links. A title or shared keyword cannot establish a dependency or direction.
5. With Jira/Confluence/Search only, perform the same bounded one/two-hop analysis from Jira links and linked docs. Report missing Projects, Goals, code, service or discussion coverage where it affects the map. If graph/code tools are available, preserve those relationships and verify their direction rather than defaulting to the reduced view.

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
- **Owner to contact:** the assignee, or the project or service owner. When available, use `getPeopleInfo` with `manager: true` for the recorded role and manager. Otherwise use the source display name or a bounded Jira user lookup and disclose unresolved contacts; do not infer an escalation contact.
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

## Answer

- Lead with the anchor, need-by date or its absence, dependency counts, and the most important blocked, at-risk or stale dependency with who to contact.
- Show upstream and downstream dependencies in Markdown lists or a table. Say explicitly which work waits on which; keep State and Source separate, retain second-hop and both-ways relationships, and link the evidence. Use the same scope, ranking, counts and caveats as the report export reference, without generating its SVG diagram or report files.
- Include Needs attention, Not recorded dependencies with their evidence and possible recording actions, and 2 to 4 next steps with the person to contact. Do not turn an inferred dependency into a recorded one.
- In Sources and limitations, retain how far the walk went, edges left unfollowed, related links omitted, unreadable keys, graph/record differences, caps and checks not run. After the result, offer the writes prepared in Step 6 with the exact links and direction; make none without the required confirmation.


## Optional report

Answer in the conversation first. For a requested HTML report, read [the report export instructions](references/report-export.md) and run this skill's existing `render.py` with the bundled design assets. Preserve the same findings and limitations. Offer publication only after confirming the required tools and permission; a static export remains available when publication is unavailable.
