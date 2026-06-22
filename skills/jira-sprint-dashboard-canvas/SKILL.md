---
name: jira-sprint-dashboard-canvas
description: >-
  Render a focused Cursor Canvas sprint dashboard from Jira space, sprint,
  board, filter, JQL, work item keys, or Jira URL data. Use when the user asks
  for a Jira sprint dashboard, standup dashboard, sprint review, delivery
  review, engineering manager dashboard, WIP review, planning view, closeout
  view, or a visual snapshot of Jira work that is more useful than a flat report.
---

# Jira Sprint Dashboard Canvas

Build a Cursor Canvas that helps an engineering manager, tech lead, or senior
engineer see current Jira work quickly enough to decide what needs attention.
The output is a dashboard, not a prose report and not a generic health score.

This skill is read-only by default. Do not create, update, transition, assign,
or comment on Jira work items unless the user explicitly asks for a write action
after reviewing the dashboard.

## Canvas Grounding

Read `~/.cursor/skills-cursor/canvas/SKILL.md` before writing canvas code. If
you need exact exports or prop shapes, read the files in
`~/.cursor/skills-cursor/canvas/sdk/`.

Canvas constraints:

- Create one `.canvas.tsx` file in the Cursor canvases directory.
- Import only from `cursor/canvas`. Do not import `react`, `CSSProperties`,
  `JSX`, Atlaskit, or other packages.
- Embed Jira data inline in the canvas; do not fetch from the canvas.
- Prefer Canvas primitives such as `Stack`, `Grid`, `Card`, `Stat`, `Table`,
  `Pill`, `Callout`, `UsageBar`, `BarChart`, `LineChart`, `PieChart`, and `Code`
  over raw HTML.
- Use `useHostTheme()` for custom styles. Do not hardcode hex colors, gradients,
  box shadows, ADS variables, unsupported CSS frameworks, or `@atlaskit/*`.

## Get The Scope

Do not guess the Jira scope. If the user does not provide a space key, board,
sprint, filter, JQL, work item keys, or Jira URL, stop and ask for one. A
dashboard from a random visible space or guessed team context is worse than no
dashboard.

If the user gives a space key but no sprint, board, or filter, start with the
Jira JQL `project` field and the user's space key:

```jql
project = "SPACE_KEY" AND sprint in openSprints() ORDER BY Rank ASC
```

If the open sprint result is empty, stale, or misleading, switch to snapshot
mode and say so in a compact caveat below the top bar:

```jql
project = "SPACE_KEY" AND statusCategory != Done ORDER BY priority DESC, updated ASC
project = "SPACE_KEY" AND updated >= -60d ORDER BY updated DESC
```

Use a 60-day recent movement window by default unless the user asks for another
period.

## Query Jira

Use read-only Jira search. Request only fields needed for the dashboard and
tolerate missing fields.

Useful fields: `key`, `summary`, `status`, `statusCategory`, `assignee`,
`priority`, `issuetype`, `created`, `updated`, `resolutiondate`, `duedate`,
`parent`, `issuelinks`, `labels`, `components`, `fixVersions`, `sprint`, and any
available estimate/story point field.

Start with `maxResults: 100`. For complete sprint, board, or filter dashboards,
paginate until the scope is complete or too large for useful work-item-level
rendering.

Run only the follow-up queries needed to support visible claims:

- Recently completed: `<scope> AND statusCategory = Done ORDER BY resolutiondate DESC`
- Aging unfinished: `<scope> AND statusCategory != Done AND updated <= -3d ORDER BY updated ASC`
- Unowned unfinished: `<scope> AND statusCategory != Done AND assignee is EMPTY ORDER BY priority DESC, updated ASC`
- High-priority unfinished: `<scope> AND statusCategory != Done AND priority in (Highest, High) ORDER BY priority DESC, updated ASC`
- Blocked signal: `<scope> AND statusCategory != Done AND (status = Blocked OR text ~ "blocked" OR labels in (blocked, blocker)) ORDER BY priority DESC, updated ASC`

Do not make negative claims such as "no blockers" or "no dependencies" unless
the source appendix shows the query or returned field coverage that supports the
claim. If a signal was not checked, say so.

For work item links (`issuelinks`), fetch linked work item status/category when
possible. If linked details are unavailable, show dependency status as unknown
rather than resolved.

## Normalize

Before designing the canvas, create a compact work item model with:

- Key, URL, summary, type, status, status category, priority
- Assignee display name or `Unassigned`
- Owner status as `active`, `inactive`, `unknown`, or `unassigned`
- Created age, updated age, resolution age when done, due date distance
- Parent/epic/workstream, sprint, estimate, components, versions, labels
- Linked work item keys, direction, link type, and linked status when available

Derived signals should stay explainable from Jira facts: done, active, not
started, stale, very stale, blocked, unowned, inactive owner, time-sensitive,
support-impacting, cross-space dependency, and missing planning data. Mark
weak text-only signals as inferred.

## Dashboard Shape

Keep the visible dashboard simple and deterministic. When the data exists,
broadly follow this order:

1. **Compact context header**
   - Show title plus space/board/sprint/window metadata.
   - Keep it short. Do not put queries, field coverage, or executive-summary
     prose at the top.

2. **Four-stat top bar**
   - Show exactly four `Stat` values.
   - Default to committed/total scope, done/completed, active/in progress, and
     needs attention. Use work item counts when story points are unavailable.
   - `Needs attention` should combine the highest-signal risks: blocked, stale,
     unassigned, time-sensitive, or unresolved linked work.
   - Put secondary counts below the fold only when they change the readout.

3. **Scope caveat, only when needed**
   - Use one compact `Callout` below the top bar when sprint data is missing,
     mixed, stale, or blended with recent space movement.
   - Keep it to 1 to 2 short sentences.

4. **Capacity or commitment bar**
   - Render a `UsageBar` only when capacity, commitment, or allocation segment
     data is available.
   - Skip it rather than inventing capacity, segment, or buffer values.

5. **Sprint charts**
   - If available, render remaining work over time as a `LineChart`.
   - Beside it, render status distribution as a `PieChart` or compact status
     visual.
   - Below those, render resolved/completed per working day as a `BarChart`.
   - Skip any chart whose categories, values, units, or time range are missing.
     Never render placeholder, sample, empty, or guessed charts.

6. **Owner load and gaps**
   - Show active, stale, blocked, support-impacting, and done counts by assignee.
   - Include unassigned, inactive-owner, and unknown-owner-status buckets.
   - Keep it compact; prefer a small table or bar chart over per-owner cards.

7. **Risk and attention**
   - Place this below owner load.
   - Include only the work items most likely to need manager or lead attention.
   - For each item, show key, reason, evidence, owner, age, and next question.
   - Use a `Callout` for the single highest delivery risk when one stands out.

8. **Highest-priority work item table**
   - Include a compact table of top sprint work items or top attention items.
   - Do not render every low-signal work item by default.

9. **Recently completed and optional detail**
   - If recently completed work exists, put it in a collapsed card or compact
     table below the main readout.
   - Workstream grouping and dependencies should appear only when they change
     what the viewer should inspect next. Keep dependencies to unresolved or
     unknown-status linked work by default.

10. **Source appendix**
   - Put exact JQL, query timestamps, field coverage, assumptions, and the
     composition of `Needs attention` at the bottom.

If the full data set is unavailable, preserve the same broad order and omit the
sections or charts that cannot be rendered honestly.

## Content And Style

- Use charts and tables where they beat paragraphs.
- Follow the reference layout order when the data supports it; skip unsupported
  charts instead of changing the whole page shape.
- Keep work item summaries short; avoid full descriptions unless a short excerpt
  is needed to explain impact.
- Tie every recommendation or next question to work item keys or aggregate
  counts.
- Separate Jira facts from derived or inferred signals.
- Use semantic tones: `success` for done, `warning` for stale/deadline risk,
  `danger` for blocked/overdue/severe risk, `info` for caveats/linked work, and
  `neutral` for low-signal facts.
- Pair color with labels. Prefer work item key links over large buttons.
- Do not publish or share the canvas unless the user asks.

## Self-Check

Before returning:

- Scope came from the user or a provided URL; missing or ambiguous scope was
  clarified before querying.
- The canvas imports only from `cursor/canvas`.
- The top area is a compact context header followed by exactly four stats.
- There is no query list, field coverage, or executive summary above the top bar.
- Counts reconcile with the queried work item set.
- Empty sections are omitted.
- Charts are rendered only when their categories, values, units, and time ranges
  are available.
- Risk labels are explainable from visible Jira data.
- Source appendix includes exact JQL and field coverage for visible claims.
- No Jira write tools were used.
