---
name: jira-sprint-dashboard
description: "Create a structured Jira sprint dashboard from Jira project, space, sprint, board, filter, JQL, work item keys, or Jira URL data. Use when the user asks for a Jira sprint dashboard, standup dashboard, sprint review, delivery review, engineering manager dashboard, WIP review, planning view, closeout view, or a visual snapshot of Jira work that is more useful than a flat prose report. Queries Jira boards, sprints, and issues directly and renders the richest dashboard format supported by the current environment (such as Markdown tables, compact charts, or an interactive artifact)."
---

# Jira Sprint Dashboard

Build a focused dashboard that helps an engineering manager, tech lead, or senior engineer see current Jira work quickly enough to decide what needs attention. The output is a dashboard, not a prose report and not a generic health score.

This skill is read-only by default. Do not create, update, transition, assign, or comment on Jira work items unless the user explicitly asks for a write action after reviewing the dashboard.

## Tool Access & Schema Rules

- All Atlassian Jira tools are exposed directly as top-level tools — call every tool directly by name:
  - `getAccessibleAtlassianResources` — obtain `cloudId` and the site URL once per session.
  - `searchJiraIssuesUsingJql` — run the primary paginated scope query and any justified targeted follow-ups.
  - `listJiraBoards`, `listJiraBoardSprints`, `getJiraBoardSprintData`, `getJiraBoardIssueData`, and `getJiraBoardConfig` — inspect boards, active/past sprints, sprint issues, and column/status configuration when the user provides a board or sprint (or when you need exact sprint metadata).
  - `getJiraIssue` — inspect individual linked work items or unresolved dependencies when needed.
  - `listJiraFilters` — resolve a named Jira filter to its JQL query.
- If a tool is not in your tool list, it is not available on this connector; say so and use the closest available tool.
- **Always inspect the live tool schema before passing parameters.** Unrecognized parameters may be silently dropped or rejected.

## Output Mode

Use the richest dashboard format supported by the current environment. The dashboard content, claims, counts, and source appendix must stay consistent across formats; only the presentation changes.

Choose the format in this order:

1. **Markdown dashboard** (default in conversational environments): preserve the dashboard order using compact tables for stats, owner load, risks, highest-priority work, and the source appendix; use textual chart substitutes (counts, percentages, simple ASCII/Unicode bars) only when honest; avoid turning the output into long prose.
2. **Interactive artifact**, if the current environment explicitly supports rich interactive artifact output (prefer tables, compact charts, stat rows, and collapsible source details; do not require live Jira fetching from the artifact).
3. **Structured JSON plus concise summary**, only if the user explicitly asks for JSON or visual formatting is unavailable.

## Get The Scope

Do not guess the Jira scope. If the user does not provide a project key, space key, board, sprint, filter, JQL, work item keys, or Jira URL, stop and ask for one. A dashboard from a random visible project or guessed team context is worse than no dashboard.

- If the user names a **board or sprint**, call `listJiraBoards`, `listJiraBoardSprints`, and `getJiraBoardSprintData` (or `getJiraBoardIssueData` / `getJiraBoardConfig`) directly to retrieve the real sprint metadata and issues.
- If the user gives a **project or space key** with no sprint, board, or filter, start with `searchJiraIssuesUsingJql` using:

```jql
project = "SPACE_KEY" AND sprint in openSprints() ORDER BY Rank ASC
```

If the open sprint result is empty, stale, or misleading, switch to snapshot mode and say so in a compact caveat below the top bar:

```jql
project = "SPACE_KEY" AND statusCategory != Done ORDER BY priority DESC, updated ASC
project = "SPACE_KEY" AND updated >= -60d ORDER BY updated DESC
```

Use a 60-day recent movement window by default unless the user asks for another period.

Not every board supports sprints. Some boards, including Kanban boards, do not support sprints; inspect the actual board features rather than inferring this solely from its type: `sprint in openSprints()` returns nothing and `listJiraBoardSprints` / `getJiraBoardSprintData` fails with "The board does not support sprints". Treat that as a signal to go straight to snapshot mode rather than an error worth retrying.

## Query Jira

Use read-only Jira tools (`searchJiraIssuesUsingJql`, `getJiraBoardSprintData`, `listJiraBoardSprints`). Request only the fields needed for the dashboard and tolerate missing fields.

Useful fields: `key`, `summary`, `status`, `statusCategory`, `assignee`, `priority`, `issuetype`, `created`, `updated`, `resolutiondate`, `duedate`, `parent`, `issuelinks`, `labels`, `components`, `fixVersions`, `sprint`, and any available estimate/story point field.

**Sprint and story points often live in custom fields, which compact responses may omit.** Before calling `searchJiraIssuesUsingJql`, inspect its live tool schema:
- Use view: "evidence" to retrieve mapped custom fields, or request known site-specific customfield_* IDs explicitly.
- Use fields: ["*all"] only when every field is required; prefer the evidence view or explicit known customfield_* IDs.
- Inspect the returned issue payload to confirm whether custom fields appear under `fields.customFields` or as top-level `fields.customfield_*` keys, and adapt accordingly.

Start with `maxResults: 100`. For complete sprint, board, or filter dashboards, paginate using `nextPageToken` until the scope is complete or too large for useful work-item-level rendering.

Default to one complete paginated scope query. Derive ordinary dashboard signals locally from the returned work item set instead of issuing separate JQL calls for each signal.

Derive these locally when the scope query returned the required fields:

- Recently completed from `statusCategory = Done` and `resolutiondate`.
- Aging unfinished from `statusCategory != Done` and `updated`.
- Unowned unfinished from `statusCategory != Done` and empty `assignee`.
- High-priority unfinished from `statusCategory != Done` and `priority`.
- Status or label blockers from `status`, `statusCategory`, and `labels`.
- Owner load, stale work, due date risk, and planning gaps from the normalized scope dataset.

Use targeted follow-up queries only when they are needed to support a visible claim that cannot be derived safely from the scope data, when the scope is too large for useful local processing, or when the user asks for an audit-style dashboard with exact evidence per signal.

Rule of thumb:

- Small or medium sprint dashboard: prefer one full paginated scope query (plus `getJiraBoardSprintData` / `listJiraBoardSprints` for board/sprint metadata when relevant), with at most one targeted blocker-text or dependency-status follow-up when needed.
- Large scope dashboard: use narrower follow-up queries when pulling and processing the full work-item set would be slow or low-value.
- Evidence-heavy review: multiple focused queries are acceptable when the exact JQL evidence matters more than minimizing calls.

Examples of targeted follow-up queries, only when justified:

- Recently completed: `<scope> AND statusCategory = Done ORDER BY resolutiondate DESC`
- Aging unfinished: `<scope> AND statusCategory != Done AND updated <= -3d ORDER BY updated ASC`
- Unowned unfinished: `<scope> AND statusCategory != Done AND assignee is EMPTY ORDER BY priority DESC, updated ASC`
- High-priority unfinished: `<scope> AND statusCategory != Done AND priority in (Highest, High) ORDER BY priority DESC, updated ASC`
- Blocked signal: `<scope> AND statusCategory != Done AND (status = Blocked OR text ~ "blocked" OR labels in (blocked, blocker)) ORDER BY priority DESC, updated ASC`

Do not make negative claims such as "no blockers" or "no dependencies" unless the source appendix shows the query or returned field coverage that supports the claim. If only status and labels were checked for blockers, say that no status/label blockers were found rather than claiming there are no blockers. If a signal was not checked, say so.

For derived signals, cite the base scope JQL and field coverage in the source appendix instead of inventing separate support queries. Include additional JQL only for targeted follow-up queries that were actually run.

For work item links (`issuelinks`), fetch linked work item status/category via `searchJiraIssuesUsingJql` (`key in (...)`) or `getJiraIssue` (passing explicit `fields` such as `["summary", "status", "assignee", "issuelinks"]` if `view` is not supported in the live schema). If linked details are unavailable, show dependency status as unknown rather than resolved.

## Normalize

Before designing the output, create a compact renderer-independent work item model with:

- Key, URL, summary, type, status, status category, priority
- Assignee display name or `Unassigned`
- Owner status as `active`, `inactive`, `unknown`, or `unassigned`
- Created age, updated age, resolution age when done, due date distance
- Parent/epic/workstream, sprint, estimate, components, versions, labels
- Linked work item keys, direction, link type, and linked status when available

Derived signals should stay explainable from Jira facts: done, active, not started, stale, very stale, blocked, unowned, inactive owner, time-sensitive, support-impacting, cross-space dependency, and missing planning data. Mark weak text-only signals as inferred.

## Dashboard Model

Create a dashboard model before rendering. Include:

- Context metadata: title, project or space, sprint, board, filter, JQL, window, query timestamp, and mode.
- Four top stats: committed or total scope, done or completed, active or in progress, and needs attention.
- Scope caveat, only when sprint data is missing, mixed, stale, or blended with recent project movement.
- Optional capacity or commitment segments, only when real data exists.
- Optional chart/visual data, only when categories, values, units, and time ranges are available.
- Owner load and gaps.
- Risk and attention items.
- Highest-priority work item table.
- Recently completed work.
- Source appendix with exact JQL, tools used, field coverage, assumptions, and the composition of `Needs attention`.

Do not invent data to fill the model. Empty or unsupported sections should be omitted.

## Dashboard Shape

Keep the visible dashboard simple and deterministic. When the data exists, broadly follow this order:

1. **Compact context header**
   - Show title plus project, space, board, sprint, or window metadata.
   - Keep it short. Do not put queries, field coverage, or executive-summary prose at the top.

2. **Four-stat top bar**
   - Show exactly four stat values.
   - Default to committed/total scope, done/completed, active/in progress, and needs attention.
   - Use work item counts when story points are unavailable.
   - `Needs attention` should combine the highest-signal risks: blocked, stale, unassigned, time-sensitive, or unresolved linked work.
   - Put secondary counts below the fold only when they change the readout.

3. **Scope caveat, only when needed**
   - Use one compact caveat below the top bar when sprint data is missing, mixed, stale, or blended with recent project movement.
   - Keep it to 1 to 2 short sentences.

4. **Capacity or commitment summary**
   - Render a capacity or commitment breakdown only when real capacity, commitment, or allocation data is available.
   - Skip it rather than inventing capacity, segment, or buffer values.

5. **Sprint progress and status breakdown**
   - If available, show remaining work over time, status distribution, and resolved/completed per working day as compact visual tables or charts.
   - Skip any chart whose categories, values, units, or time range are missing. Never render placeholder, sample, empty, or guessed charts.

6. **Owner load and gaps**
   - Show active, stale, blocked, support-impacting, and done counts by assignee.
   - Include unassigned, inactive-owner, and unknown-owner-status buckets.
   - Keep it compact; prefer a small table over per-owner cards.

7. **Risk and attention**
   - Place this below owner load.
   - Include only the work items most likely to need manager or lead attention.
   - For each item, show key, reason, evidence, owner, age, and next question.
   - Highlight the single highest delivery risk when one stands out.

8. **Highest-priority work item table**
   - Include a compact table of top sprint work items or top attention items.
   - Do not render every low-signal work item by default.

9. **Recently completed and optional detail**
   - If recently completed work exists, put it in a compact table below the main readout.
   - Workstream grouping and dependencies should appear only when they change what the viewer should inspect next.
   - Keep dependencies to unresolved or unknown-status linked work by default.

10. **Source appendix**
    - Put exact JQL, tools queried, query timestamps, field coverage, assumptions, and the composition of `Needs attention` at the bottom.

If the full data set is unavailable, preserve the same broad order and omit the sections that cannot be rendered honestly.

## Content And Style

- Use tables and compact visual summaries where they beat paragraphs.
- Follow the reference layout order when the data supports it; skip unsupported sections instead of changing the whole shape.
- Keep work item summaries short; avoid full descriptions unless a short excerpt is needed to explain impact.
- Tie every recommendation or next question to work item keys or aggregate counts.
- Separate Jira facts from derived or inferred signals.
- Keep the top screen focused on status and attention, not process notes.
- Use short section headings, concise caveats, and link every work item key to its Jira URL (`https://<site>.atlassian.net/browse/<KEY>`).

## Self-Check

Before returning:

- Scope came from the user or a provided URL; missing or ambiguous scope was clarified before querying.
- Direct Jira tools (`searchJiraIssuesUsingJql`, `getJiraBoardSprintData`, `listJiraBoardSprints`, etc.) were used and their live schemas respected.
- The top area is a compact context header followed by exactly four stats.
- There is no query list, field coverage, or executive summary above the top bar.
- Ordinary signals were derived from the paginated scope query when possible; targeted follow-up queries were used only when they supported a visible claim that the scope data could not safely support.
- Counts reconcile with the queried work item set.
- Empty sections are omitted.
- Progress visuals are shown only when their categories, values, units, and time ranges are available.
- Risk labels are explainable from visible Jira data.
- Source appendix includes exact JQL and field coverage for visible claims.
- No Jira write tools were used.
