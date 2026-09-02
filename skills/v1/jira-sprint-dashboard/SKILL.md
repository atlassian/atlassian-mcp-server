---
name: jira-sprint-dashboard
description: >-
  Create a visual Jira sprint dashboard from Jira project, space, sprint, board,
  filter, JQL, work item keys, or Jira URL data. Use when the user asks for a
  Jira sprint dashboard, standup dashboard, sprint review, delivery review,
  engineering manager dashboard, WIP review, planning view, closeout view, or a
  visual snapshot of Jira work that is more useful than a flat report. Use the
  richest dashboard format supported by the current agent, such as Cursor
  Canvas, an interactive artifact, HTML, or Markdown.
---

# Jira Sprint Dashboard

Build a focused dashboard that helps an engineering manager, tech lead, or
senior engineer see current Jira work quickly enough to decide what needs
attention. The output is a dashboard, not a prose report and not a generic
health score.

This skill is read-only by default. Do not create, update, transition, assign,
or comment on Jira work items unless the user explicitly asks for a write action
after reviewing the dashboard.

## Output Mode

Use the richest dashboard renderer supported by the current environment. The
dashboard content, claims, counts, and source appendix must stay consistent
across renderers; only the presentation changes.

Choose the renderer in this order:

1. Cursor Canvas, if running in Cursor with Canvas support.
2. Interactive artifact, if the current agent supports HTML, React, or similar
   artifact output.
3. Static HTML file, if file creation is available and useful.
4. Markdown dashboard, if no richer visual renderer is available.
5. Structured JSON plus concise summary, only if visual rendering is impossible.

Do not mention that Cursor Canvas is unavailable unless the user specifically
asked for Cursor Canvas. If the user asked for a dashboard generally, use the
best available renderer without apologizing for the environment.

## Cursor Canvas Renderer

Use this section only when running in Cursor with Canvas support.

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
- Do not publish or share the canvas unless the user asks.

## Portable Renderers

Use this section when Cursor Canvas is unavailable.

For an interactive artifact renderer:

- Render the same dashboard model as an interactive artifact.
- Prefer tables, compact charts, stat rows, and collapsible source details.
- Keep interactions lightweight: filtering, expanding details, or switching
  chart/table views is fine; do not require live Jira fetching from the artifact.

For static HTML:

- Create a self-contained dashboard file with embedded data.
- Use responsive layout, accessible tables, and simple chart-like visuals when
  chart libraries are unavailable.
- Do not fetch Jira data from the HTML file.

For Markdown:

- Preserve the dashboard order.
- Use compact tables for stats, owner load, risks, highest-priority work, and
  source appendix.
- Use textual chart substitutes only when they remain honest, such as counts,
  percentages, and simple bars.
- Avoid turning the output into a long prose report.

For JSON fallback:

- Return the normalized dashboard model.
- Include a short human-readable summary with the highest-signal risks and the
  source scope.

## Get The Scope

Do not guess the Jira scope. If the user does not provide a project key, space
key, board, sprint, filter, JQL, work item keys, or Jira URL, stop and ask for
one. A dashboard from a random visible project or guessed team context is worse
than no dashboard.

If the user gives a project or space key but no sprint, board, or filter, start
with the Jira JQL `project` field and the user's key:

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

Default to one complete paginated scope query. Derive ordinary dashboard signals
locally from the returned work item set instead of issuing separate JQL calls for
each signal.

Derive these locally when the scope query returned the required fields:

- Recently completed from `statusCategory = Done` and `resolutiondate`.
- Aging unfinished from `statusCategory != Done` and `updated`.
- Unowned unfinished from `statusCategory != Done` and empty `assignee`.
- High-priority unfinished from `statusCategory != Done` and `priority`.
- Status or label blockers from `status`, `statusCategory`, and `labels`.
- Owner load, stale work, due date risk, and planning gaps from the normalized
  scope dataset.

Use targeted follow-up queries only when they are needed to support a visible
claim that cannot be derived safely from the scope data, when the scope is too
large for useful local processing, or when the user asks for an audit-style
dashboard with exact evidence per signal.

Rule of thumb:

- Small or medium sprint dashboard: prefer one full paginated scope query, with
  at most one targeted blocker-text or dependency-status follow-up when needed.
- Large scope dashboard: use narrower follow-up queries when pulling and
  processing the full work-item set would be slow or low-value.
- Evidence-heavy review: multiple focused queries are acceptable when the exact
  JQL evidence matters more than minimizing calls.

Examples of targeted follow-up queries, only when justified:

- Recently completed: `<scope> AND statusCategory = Done ORDER BY resolutiondate DESC`
- Aging unfinished: `<scope> AND statusCategory != Done AND updated <= -3d ORDER BY updated ASC`
- Unowned unfinished: `<scope> AND statusCategory != Done AND assignee is EMPTY ORDER BY priority DESC, updated ASC`
- High-priority unfinished: `<scope> AND statusCategory != Done AND priority in (Highest, High) ORDER BY priority DESC, updated ASC`
- Blocked signal: `<scope> AND statusCategory != Done AND (status = Blocked OR text ~ "blocked" OR labels in (blocked, blocker)) ORDER BY priority DESC, updated ASC`

Do not make negative claims such as "no blockers" or "no dependencies" unless
the source appendix shows the query or returned field coverage that supports the
claim. If only status and labels were checked for blockers, say that no
status/label blockers were found rather than claiming there are no blockers. If
a signal was not checked, say so.

For derived signals, cite the base scope JQL and field coverage in the source
appendix instead of inventing separate support queries. Include additional JQL
only for targeted follow-up queries that were actually run.

For work item links (`issuelinks`), fetch linked work item status/category when
possible. If linked details are unavailable, show dependency status as unknown
rather than resolved.

## Normalize

Before designing the output, create a compact renderer-independent work item
model with:

- Key, URL, summary, type, status, status category, priority
- Assignee display name or `Unassigned`
- Owner status as `active`, `inactive`, `unknown`, or `unassigned`
- Created age, updated age, resolution age when done, due date distance
- Parent/epic/workstream, sprint, estimate, components, versions, labels
- Linked work item keys, direction, link type, and linked status when available

Derived signals should stay explainable from Jira facts: done, active, not
started, stale, very stale, blocked, unowned, inactive owner, time-sensitive,
support-impacting, cross-space dependency, and missing planning data. Mark weak
text-only signals as inferred.

## Dashboard Model

Create a dashboard model before rendering. Every renderer should use this same
model.

Include:

- Context metadata: title, project or space, sprint, board, filter, JQL, window,
  query timestamp, and mode.
- Four top stats: committed or total scope, done or completed, active or in
  progress, and needs attention.
- Scope caveat, only when sprint data is missing, mixed, stale, or blended with
  recent project movement.
- Optional capacity or commitment segments, only when real data exists.
- Optional chart data, only when categories, values, units, and time ranges are
  available.
- Owner load and gaps.
- Risk and attention items.
- Highest-priority work item table.
- Recently completed work.
- Source appendix with exact JQL, field coverage, assumptions, and the
  composition of `Needs attention`.

Do not invent data to fill the model. Empty or unsupported sections should be
omitted.

## Dashboard Shape

Keep the visible dashboard simple and deterministic. When the data exists,
broadly follow this order:

1. **Compact context header**
   - Show title plus project, space, board, sprint, or window metadata.
   - Keep it short. Do not put queries, field coverage, or executive-summary
     prose at the top.

2. **Four-stat top bar**
   - Show exactly four stat values.
   - Default to committed/total scope, done/completed, active/in progress, and
     needs attention.
   - Use work item counts when story points are unavailable.
   - `Needs attention` should combine the highest-signal risks: blocked, stale,
     unassigned, time-sensitive, or unresolved linked work.
   - Put secondary counts below the fold only when they change the readout.

3. **Scope caveat, only when needed**
   - Use one compact caveat below the top bar when sprint data is missing,
     mixed, stale, or blended with recent project movement.
   - Keep it to 1 to 2 short sentences.

4. **Capacity or commitment bar**
   - Render a capacity or commitment visual only when capacity, commitment, or
     allocation segment data is available.
   - Skip it rather than inventing capacity, segment, or buffer values.

5. **Sprint charts**
   - If available, render remaining work over time as a line chart.
   - Beside it, render status distribution as a pie chart or compact status
     visual.
   - Below those, render resolved/completed per working day as a bar chart.
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
   - Use a callout or highlighted row for the single highest delivery risk when
     one stands out.

8. **Highest-priority work item table**
   - Include a compact table of top sprint work items or top attention items.
   - Do not render every low-signal work item by default.

9. **Recently completed and optional detail**
   - If recently completed work exists, put it in a collapsed section or compact
     table below the main readout.
   - Workstream grouping and dependencies should appear only when they change
     what the viewer should inspect next.
   - Keep dependencies to unresolved or unknown-status linked work by default.

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
- Use semantic tones where the renderer supports them: `success` for done,
  `warning` for stale/deadline risk, `danger` for blocked/overdue/severe risk,
  `info` for caveats/linked work, and `neutral` for low-signal facts.
- Pair color with labels. Prefer work item key links over large buttons.
- Keep the first screen focused on status and attention, not process notes.

## Renderer-Specific Style

For Cursor Canvas:

- Use Canvas components and host theme styles.
- Keep the top area compact: context header followed by exactly four stats.
- Prefer Canvas tables and charts over custom layout code.

For interactive artifacts or static HTML:

- Use a restrained dashboard layout with compact cards, tables, and simple
  charts.
- Keep text readable on mobile and desktop.
- Use accessible labels for chart substitutes and status colors.
- Keep source details below the main dashboard.

For Markdown:

- Use short section headings.
- Prefer tables over paragraphs.
- Keep caveats and recommendations concise.
- Put source queries at the bottom.

## Self-Check

Before returning:

- Scope came from the user or a provided URL; missing or ambiguous scope was
  clarified before querying.
- The selected renderer matches the current environment's capabilities.
- Cursor Canvas instructions were used only when Cursor Canvas is available.
- If Cursor Canvas was used, the canvas imports only from `cursor/canvas`.
- The top area is a compact context header followed by exactly four stats.
- There is no query list, field coverage, or executive summary above the top
  bar.
- Ordinary signals were derived from the paginated scope query when possible;
  targeted follow-up queries were used only when they supported a visible claim
  that the scope data could not safely support.
- Counts reconcile with the queried work item set.
- Empty sections are omitted.
- Charts are rendered only when their categories, values, units, and time ranges
  are available.
- Risk labels are explainable from visible Jira data.
- Source appendix includes exact JQL and field coverage for visible claims.
- No Jira write tools were used.
