---
name: jira-backlog-hygiene
description: >-
  Audit a Jira backlog, board, sprint, project, filter, or JQL scope for hygiene
  problems and fix them in approved batches: stale or abandoned work items,
  in-progress work with no owner, unestimated items in an active sprint, missing
  priority, parent, labels, or components, overdue due dates, sub-tasks whose
  parent is already done, and epics whose children are all done. Use when the
  user asks to groom, clean up, tidy, audit, or bulk-triage a backlog or sprint,
  or asks what is stale, unowned, unestimated, or overdue. Read-only until the
  user approves a specific batch of changes.
---

# Jira Backlog Hygiene

Turn a messy backlog into a short list of concrete fixes. The skill scans one
Jira scope, runs a fixed set of hygiene checks locally on the returned work
items, reports the findings with evidence, and then proposes batches of
changes. Nothing is written to Jira until the user approves a batch by name.

This is a bulk, scope-level complement to `triage-issue` (one bug at a time)
and `jira-sprint-dashboard` (a status view). Use it when the question is "what
in this backlog needs cleaning up?" rather than "is this bug a duplicate?" or
"how is the sprint going?".

## Get The Scope

Do not guess the scope. If the user gives no project key, board, sprint,
filter, JQL, work item keys, or Jira URL, stop and ask for one. A hygiene pass
over a guessed project produces changes nobody asked for.

Default scope queries, by what the user provided:

Project backlog (default):

```jql
project = "KEY" AND statusCategory != Done ORDER BY updated ASC
```

Active sprint only:

```jql
project = "KEY" AND sprint in openSprints() ORDER BY Rank ASC
```

A saved filter:

```jql
filter = "FILTER_ID_OR_NAME" AND statusCategory != Done ORDER BY updated ASC
```

Team-managed boards of type `simple` have no sprints: `sprint in openSprints()`
returns nothing and a board-sprint lookup fails with "The board does not
support sprints". Treat that as a signal to skip the sprint-only checks, not
as an error to retry.

Ask about thresholds only if the user mentions them. Otherwise use the defaults
in the check table and state them in the report.

## Query Jira

Use `searchJiraIssuesUsingJql` (a primary tool) and request only the fields the
checks need. Tolerate missing fields: a check whose field is absent is skipped
and listed as skipped, never reported as clean.

Fields: `key`, `summary`, `issuetype`, `status`, `statusCategory`, `assignee`,
`reporter`, `priority`, `created`, `updated`, `duedate`, `resolutiondate`,
`parent`, `subtasks`, `labels`, `components`, `fixVersions`, `sprint`, and the
site's story point or estimate field.

**Sprint and story points live in custom fields, which the default response
omits.** Pass `view: "evidence"` (or `"full"`), or request the site's
`customfield_*` IDs explicitly. Custom field values come back under
`fields.customFields`, not as top-level `customfield_*` keys.

Start with `maxResults: 100` and paginate until the scope is complete. Run one
complete scope query and derive every check locally from the returned set. Use
a targeted follow-up query only to support a claim the scope data cannot, for
example the status of a parent that sits outside the scope.

## Hygiene Checks

Run every check the returned fields support. Defaults are shown; the user can
override any of them.

| Check | Rule (default) | Evidence | Suggested fix |
|---|---|---|---|
| Stale backlog item | not done and `updated` older than 30 days | `updated`, `status` | nudge comment, or close as Won't Do |
| Stuck in progress | `statusCategory = "In Progress"` and `updated` older than 5 working days | `updated`, `assignee` | nudge comment to assignee |
| In progress, no owner | `statusCategory = "In Progress"` and `assignee` empty | `assignee` | assign (only to a person the user names) |
| In sprint, no owner | in an active sprint and `assignee` empty | `sprint`, `assignee` | assign, or flag for a human to move it out of the sprint |
| In sprint, no estimate | in an active sprint and estimate empty | estimate field | add label `needs-estimate` |
| No priority | `priority` empty, or every item in scope carries the project default | `priority` | set priority |
| No parent | story or task in an active sprint with no `parent` | `parent` | set parent |
| Overdue | `duedate` before today and not done | `duedate` | move due date, or comment |
| Blocked too long | status is Blocked, or label `blocked`, and `updated` older than 10 days | `status`, `labels`, `updated` | nudge comment |
| Orphaned sub-task | sub-task not done while its parent is done | `parent` status | reopen parent, or close sub-task |
| Finished epic still open | epic not done and every child done (at least one child) | children `statusCategory` | transition epic to Done |
| Empty epic | epic with no children and `created` older than 60 days | `subtasks`, child search | comment, or close |
| Possible duplicate | same normalized summary appears twice in scope | `summary` | flag only, never merge |

Skip a check, and say so, when the project plainly does not use the field: for
example skip the estimate check when fewer than one in five done items in the
scope has an estimate, and skip the parent check when no item in scope has one.

"Working days" means Monday to Friday. Do not count weekends as inactivity.

## Report

Keep the report short and ordered. Every claim must trace to a returned field
or a query listed in the appendix.

1. **Scope line**: project or filter, JQL, item count, query time, thresholds.
2. **Totals**: items scanned, items with at least one finding, and a count per
   check. A check that was skipped shows `skipped (field not used)`.
3. **One table per check with findings**: key, summary (short), owner or
   `Unassigned`, age or date that triggered the rule, and the evidence field
   value. Show at most 10 rows per check; state the total when there are more.
4. **Proposed batches**: see the next section.
5. **Source appendix**: exact JQL, fields returned, thresholds used, checks
   skipped and why.

Do not describe a check as clean unless it ran on the full scope. Separate
Jira facts from inferences: "possible duplicate" is inferred; "no assignee" is
a fact.

## Proposed Fixes

Group the fixes into batches. Each batch names one action, one field change or
comment, and the exact list of work item keys. Present all batches, then ask
the user which ones to run. Run only the batches the user approved by name or
number. Never run a batch because it "seems safe".

Batch order, from least to most invasive:

1. **Label**: add `needs-estimate`, `needs-owner`, or `needs-parent`. Use
   `editJiraIssue` and merge into the existing labels; never replace them.
2. **Comment**: post one short nudge on stale, stuck, blocked, or overdue items
   with `addOrEditJiraIssueComment`. Template, adjust the wording once and reuse:
   `Backlog hygiene: no update since {date}. Still needed? Reply, update, or close.`
   Post one comment per item per run, never repeat on a later run within 14
   days.
3. **Set field**: priority, due date, parent. Use `editJiraIssue` with only the
   field being changed.
4. **Assign**: only to a person the user named for this batch. Resolve the
   account with `lookupJiraAccountId` first and show the match before writing.
   Never assign to the reporter, the last assignee, or a guess.
5. **Transition**: close finished epics, close stale items as Won't Do, reopen a
   parent of an orphaned sub-task. Read the available transitions with
   `getTransitionsForJiraIssue` first; if the target transition does not exist
   for an item, drop that item from the batch and say so. Ask for a separate
   confirmation for every transition batch, even when other batches were
   already approved.

Never delete a work item, never move items between projects, never change
sprints, and never merge duplicates. Those are decisions for a person in Jira.

Cap a batch at 50 writes. If a batch is larger, run the first 50, report, and
ask before continuing. Execute writes one at a time in order. On the first
unexpected error, stop the batch, report which keys were done and which were
not, and ask how to proceed.

After each batch, list the keys changed with a link, the field or comment
written, and any keys skipped with the reason.

## Calling non-primary tools

The Atlassian Rovo MCP server exposes only a small set of **primary** tools directly in your tool
list. Everything else lives in the catalog and is reached through meta-tools:

- **`discover`** — describe the goal in natural language when you do not know an operation's name.
  It returns the exact `name` and `inputs` to use. Do not call `discover` for an operation you
  already have as a primary tool.
- **An execute-family tool** — run a catalog operation by name. Check your tool list: some clients
  expose a single **`execute`**, others expose **`executeRead`** / **`executeWrite`** /
  **`executeDestructive`** and expect the tier matching the operation. The arguments are identical:

```
executeWrite(   # or execute(...) if your client exposes a single execute tool
  name="editJiraIssue",
  cloudId="...",
  inputs={"issueIdOrKey": "PROJ-123", "fields": {"labels": ["existing-label", "needs-estimate"]}}
)
```

Operations this skill reaches through the catalog: `editJiraIssue`,
`addOrEditJiraIssueComment`, `getTransitionsForJiraIssue`,
`transitionJiraIssue`, `lookupJiraAccountId`, and `getJiraIssue` for a parent
outside the scope.

Rules that matter:

- **`cloudId` is a top-level argument**, a sibling of `name` and `inputs` — never put it inside
  `inputs`. Operations declared `omitCloudId` take no `cloudId`.
- **`inputs` is a flat object.** The server routes each parameter to path, query, or body itself.
- **Use the exact parameter names from the live tool schema.** Unrecognized parameters are dropped
  rather than reported as an error, so a wrong name fails silently — the call succeeds and your
  value is simply ignored. When in doubt, read the schema or `discover` result first.
- If the call reports an unknown operation, run `discover` with different keywords and use the
  name it returns rather than guessing.

## Self-Check

Before returning the report:

- Scope came from the user; nothing was guessed.
- The scope query was paginated to completion, or the report says it was cut.
- Every check either ran on the full scope or is listed as skipped with a reason.
- Thresholds are stated.
- Findings cite the field value that triggered them.
- No Jira write tool was called.

Before running a batch:

- The user approved this batch by name or number in this conversation.
- The batch lists every key it will touch and the exact change.
- Transition batches got their own confirmation.
- Assignments name a person the user chose, with the resolved account shown.
- The batch is at most 50 writes.
