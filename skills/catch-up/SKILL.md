---
name: "catch-up"
description: "Catch the current user up on a period they were away, across their own work or a project, goal, space, epic or topic, using Teamwork Graph across Jira, Confluence, Projects, Goals, Loom, the calendar and connected tools. Answers in the conversation first: what needs the user, decisions made, changes, missed meetings and what is coming up. Every item is dated inside the window and linked to its source. Offers an HTML report on request, styled with the Atlassian Design System, and publication only when Atlassian Artifacts is available and requested. Use for catch me up, what did I miss, returning from leave or holiday, getting back to a project, or /catch-up. To write a project's weekly status update, use status-check."
---

# Catch-up

Give someone back from time away a catch-up in the conversation that they can read in five minutes: what needs them first, what was decided without them, what changed in the work they care about, which meetings they missed and what came out of them, and what's coming up in the next few days. Keep it to the window they were away for, and leave out anything that doesn't change what they do next.

The value of this skill is the judgement a notification inbox, a project's update feed or a Slack unread count can't make: across every tool at once, which of hundreds of changes need you, which were decisions, and which happened while you were out rather than just before.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. This file adds what's specific to a period of time. Apply its "Sensitive content" section strictly. A long window over someone's own work turns up more leave, private messages and people-programme pages than a single day does. Leave out a people-programme page entirely, even as a New row, when its title or excerpt carries a level code, selection or assessment language: not quoting it isn't enough. When the user runs the programme, keep its schedule, its meetings and the user's own actions, in neutral words ("Send the programme update to managers"), and drop only the participant and assessment detail. An optional HTML report is built by `render.py` in this folder (Step 8), which applies the `atlassian-design` skill for you: load that skill only if the script can't run.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## Tool access and coverage

Load `teamwork-graph-context` first. Call tools directly when exposed. If a needed operation is not exposed and discovery is available, discover it and use the matching runner with its returned schema. Skip an operation only after checking the session's capabilities. Missing `products` metadata means unknown availability, not no access.

Use the full workflow when its tools are available. With Jira, Confluence and Rovo Search only, gather those records and use the fallbacks below. Keep unavailable, permission denied, successful empty results and checks not run distinct. List the impact of each gap in Sources and limitations. A Jira project is not an Atlassian Project.

## Set the window and anchor

Read [the window and seen-state rules](references/window-and-seen.md) before collecting. Resolve the user, timezone and exact start/end bounds, with a project, team or topic anchor when supplied. Report the interpreted window. Use the specified budget and preserve the distinction between event time, record update time and collection time.

Use `getWorkActivity`, `getWorkPortfolio` and graph expansion when exposed or discoverable. If they are unavailable, continue from Jira and Confluence records and any available user-authorized calendar or other connector. Use JQL/CQL for structured/date constraints and Rovo Search for language-based discovery, without a `mode` parameter. Report the loss of activity, portfolio, meeting or seen-state coverage.

An assignee, creator, contributor or current-user search match does not show that the user saw an event. Exclude an item as already seen only with a confirmed timestamped user action after the event, as the reference defines. Otherwise retain it or mark seen state unknown. A relationship's last-changed time and a record's `updated` time are candidate filters, not proof of a new event.

## Collect the catch-up

Read [the collection procedures](references/collection.md) before gathering. Run independent reads together and stay inside the reference's per-query and hydration limits.

1. Find work needing the user: current assignments, mentions, approvals, unanswered requests and changed dependencies. Read the record before claiming action is required. With Jira only, start from the user's issues and explicit requests in readable comments; do not invent mentions or approvals that the connector cannot expose.
2. Find decisions made in the window. Follow linked decision records, project/goal updates, comments or meeting records when their tools are available. Separate a Decided record with a recorded decision maker from a proposal, discussion or AI-generated meeting note. Keep source wording for approval states.
3. Find changes to anchored work, plans, issues, PRs and releases. Date Jira changes with changelog entries, comments by creation time and Confluence edits with version history. Read the relevant old/new content when a claimed change depends on it. A page last-modified time alone cannot establish what changed or when a decision happened.
4. Include missed and upcoming work meetings only when calendar/meeting capabilities are available. Follow the reference's recurrence, attendance and relevance rules. Drop personal/leave events before reading them. Do not read private messages or personal email unless requested. If meeting coverage is unavailable, disclose it and continue with work records.
5. Hydrate the selected records and necessary context before writing the summary. Keep Jira keys on other sites and unhydrated search snippets visibly incomplete. Use Confluence HTML when markdown drops comments, tables, panels or dates. Confirm comment coverage with the shared context fallback when `listConfluenceComments` is absent.

## Assess

Read [the assessment rules](references/assessment.md) before ranking. Lead with what needs the user now, then decisions and changes, then relevant meetings. Group repeated activity about the same underlying item, rank by recorded urgency and impact, and distinguish Recorded facts from suggested next actions. A busy activity stream is not a measure of a person's performance.

Keep event dates, source links, recorded owners, whether an action is outstanding and any unknown seen state. Explain why each top item matters without inventing a deadline, owner or decision. Show the source window, queries, caps, apps checked and omissions in Sources and limitations. Preserve uncertainty when a source or history could not be read. The answer comes first; a report is optional.

## Writes

None. This skill is read-only. It doesn't reply, transition work, complete tasks or change meetings. If the user asks to act on an item, confirm the exact change first, as `teamwork-graph-context` describes.

## Answer

- Lead with the window, scope and summary from Step 7, including the top Needs you item and the most important decision or change.
- Present Needs you, Decided, What changed, Meetings you missed and Coming up as applicable. Keep Step 7's ranking, grouping and row limits, source links and event dates, seen-item exclusions and required empty-state caveats. The report export reference also specifies the content each section retains; use Markdown in the conversation rather than its visual layout.
- Before answering, check that each pass ran: assigned work, Atlassian asks, review requests, Confluence tasks, meeting actions, decisions, Jira, projects and goals, Confluence, code, the third-party search, and meetings. In Sources and limitations, name any that did not run and why, plus the window, timezone, counts left out, caps and coverage gaps required by the report's sources footer.
- After the answer, offer one next step that fits: `/meeting-prep` for the next topic meeting, or `/status-check` or `/dependency-map` when a project or goal changed status.


## Optional report

Answer in the conversation first. For a requested HTML report, read [the report export instructions](references/report-export.md) and run this skill's existing `render.py` with the bundled design assets. Preserve the same findings and limitations. Offer publication only after confirming the required tools and permission; a static export remains available when publication is unavailable.
