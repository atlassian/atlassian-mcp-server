# Detailed readiness rules

Use these rules for collection budgets, check classification and area assessment. The verdict and evidence-gap rules in SKILL.md remain authoritative. With no PR evidence, Code is Not checked; with partial evidence it has Conditions.

## Budget

A release can hold a hundred items, so keep calls bounded unless the user asks for a deeper pass:

| Tool | Cap | Where |
| --- | --- | --- |
| `getJiraProjectVersions` | 2 | Step 1: the version, plus one name lookup in its project |
| `getJiraProjectVersionRelatedWork` | 1 | Step 1 |
| `searchJiraIssuesUsingJql` | 10 | 1 in Step 1 (name lookup), 4 in Step 2 (release items, flagged items, epics' children, unversioned siblings count), 1 in Step 3 (open items with `issuelinks`), up to 3 in Step 3 (upstream items in other projects, one per project key), 1 in Step 5 (open work if not already complete) |
| `getJiraIssue` + `listJiraIssueComments` | 5 issues | Step 3: Blocked or flagged items, to read the blocking reason |
| `listJiraIssueChangelogs` | 2 | Step 6: top 2 blockers, for "Blocked since [date]" |
| `searchConfluence` (CQL) | 2 | Step 4: project space first, then site-wide if empty |
| `search` (Rovo) | 3 | Step 4: rollout/test/decision docs and unrecorded blockers |
| `getConfluenceContent` | 3 reads (+1 review status) | Step 4: related work, linked docs, or search hits |
| `getJiraUser` | Up to 5 | Step 5: only if an approver or assignee is returned as an account ID without display name |

Send independent calls within a step in parallel. Report every cap that applied in Sources and limitations.


6. **Release checks:** Tag an item as a **Testing** check or a **Rollout** check using the first rule that applies:
   1. **Parent epic:** Epic summary contains whole words "readiness", "productionization", "productionisation", "productionize", "operational", "go-live", "GA", "launch", "rollout", or "testing" -> children are checks (Testing if summary matches Testing list or epic says "testing"; Rollout otherwise).
   2. **Issue type:** Test, QA, or Bug Bash -> Testing.
   3. **Labels or components:** `test`, `qa`, `e2e`, `perf` -> Testing; `rollout`, `launch`, `runbook`, `ops`, `release` -> Rollout.
   4. **Summary** (whole words/phrases, case-insensitive, ignoring code identifiers):
      - Testing: "test plan", "test run", "E2E", "end-to-end", "QA", "load test", "perf test", "performance test", "soak", "regression test", "bug bash", "production validation", or starting with "Test"/"Validate" followed by what is tested.
      - Rollout: "runbook", "runbooks", "alert", "alerts", "dashboard", "SLO", "SLOs", "pre-mortem", "rollout", "roll out", "feature flag", "on-call", "launch", "go/no-go", "production metrics", "production readiness".
      - Never tag items starting with "Explore", "Spike", "Investigate", or "Research". Mark summary-matched checks as "Grouped by title".


| Area | Not ready | Conditions | Ready | Not used |
| --- | --- | --- | --- | --- |
| **Work** | Any Blocked item, or any open To do / In progress item that is not a release check | Only In review items and release checks remain open | No open items | Never (0 items = Can't assess) |
| **Code** | A confirmed open PR contradicts a Done implementation issue | Only partial PR evidence was read; with no readable PR evidence use Not checked and add a Gap | Applicable PR evidence was checked and satisfies the release requirements | Explicit confirmation that implementation/code checks do not apply |
| **Testing** | An open Testing check that is Blocked | An open Testing check, or no test evidence found | Test evidence found and no open Testing checks | Explicit confirmation that testing does not apply |
| **Dependencies** | Any open upstream Jira item that is Blocked or has a due date after the release date | Any other open upstream Jira item, any unreadable upstream item, or missing applicable Projects dependency coverage | No open upstream dependencies and all applicable dependency sources checked | Explicit confirmation that no dependencies apply |
| **Rollout** | An open Rollout check that is Blocked, or a version approver who declined | An open Rollout check, a pending approver, no rollout/runbook doc, or unavailable deployment evidence | Rollout checks done, approvals given (or none set), and all applicable rollout/deployment evidence checked with no outstanding condition | Explicit confirmation that rollout does not apply |

*Note on unavailable scopes:* Because pull requests, deployments, and Atlassian Projects are not exposed on this connector, report them transparently in a dedicated coverage line and in Sources and limitations rather than silently omitting them — and do not fabricate Code or Deployment states.
