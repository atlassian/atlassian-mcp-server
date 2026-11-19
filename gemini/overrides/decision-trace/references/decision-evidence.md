# Decision evidence types

### Timeline item types
- **Recorded decision**: page, register row, meeting decisions list, Jira decision, or Confluence approval stating the decision as made.
- **Proposed**: record proposing or requesting a decision not yet recorded as made.
- **Revisit**: later record referring to this decision and reopening or reconsidering it (undoing questions are Revisits; follow-on implementation/staffing questions accepting the decision are **Proposed** for a new decision).
- **Reversed**: later record stating the decision was reversed or replaced by an opposite choice.
- **Meeting summary**: AI-generated meeting notes/summary section synced into a page — quote as `"The meeting summary says..."`; never makes a verdict **Decided** on its own and never names a decider.
- **Discussed**: comments, status reports, or chat talking about the decision without recording or formally reopening it.

## Budget

Unless the user asks for a deeper pass, stay within these caps and report any cap reached in Sources and limitations:

| Tool | Cap | Where |
| --- | --- | --- |
| `search` (Rovo) | 5 | 3 in Step 2, 2 in Step 5 |
| `searchConfluence` (CQL) | 2 | Step 2 (decision registers & decision pages) |
| `searchJiraIssuesUsingJql` | 3 | 2 in Step 2, 1 in Step 3 for an earlier decision cited in text |
| `getConfluenceContent` | 10 reads (+ up to 3 HTML re-reads) | Step 3 (initial candidates + linked records) |
| `getJiraIssue` + `listJiraIssueComments` + `listJiraIssueRemoteIssueLinks` | 3 issues | Step 3 |
| `getConfluenceApproval` | Up to 3 | Step 4 (classic Confluence pages only) |
| `listConfluenceContentVersions` / `getConfluenceContentVersion` / `diffConfluenceContentVersions` | 1 list + up to 5 probes/diffs per record (up to 2 records) | Step 4 |
| `listJiraIssueChangelogs` | 3 | Step 4 |
| Confluence comment retrieval (use `searchConfluence` with `type = comment AND container = <id>` when a dedicated comments tool is absent; report its coverage limits) | Up to 3 | Step 5 (comments on main decision records) |
| `getJiraUser` | Up to 6 | Only when approver/commenter appears as account ID without name |

Send independent calls in parallel. Display timestamps in the user's timezone (from `getJiraCurrentUser`, stating the timezone in Sources and limitations); display date-only fields as written.
