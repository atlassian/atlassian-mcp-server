# records and history

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

## Budget

Unless the user asks for a deeper pass, stay within these, and say in the footer if one was reached:

| Tool | Cap | Where |
| --- | --- | --- |
| `search` | 5 | 3 in Step 2, 2 in Step 6 |
| `searchConfluence` (CQL) | 1 | Step 2, for registers |
| JQL (`searchJiraIssuesUsingJql`) | 3 | 2 in Step 2, and 1 in Step 3 for an earlier decision a record mentions |
| `getConfluenceContent` | 10 reads, plus up to 3 HTML re-reads | Step 3, including pages linked from records and related pages from Step 5 |
| `getJiraIssue` | 2 | Step 3 |
| `listJiraIssueComments` | 2 total | Steps 3 and 5; reuse reads |
| `getConfluenceApproval` | 1 per Confluence record, up to 3 | Step 4 |
| `listConfluenceContentVersions` and `diffConfluenceContentVersions` | 1 list and up to 5 diffs or probes per record, for up to 2 records | Step 4 |
| `listJiraIssueChangelogs` | 3 | Step 4 |
| `getGraphContext` | 3 | Step 5: a summary and a filtered `full` call on the main record, and one summary on a second record |
| `getGraphObject` and `listConfluenceComments` | 1 batch and 1 list | Step 5, comments only |
| `getPeopleInfo` | 1 batch of up to 10 | Step 5, names for comment authors and approvers returned only as account IDs |
| `searchProjects`, `searchGoals`, `getProject`, `getGoal` | 2 searches and 3 reads | Step 5 |
| `listLoomObjects` and `getLoomObjectsContent` | 3 list pages and 1 batch of up to 10 | Step 6 |
| `discover` | up to 7 | Sent together after Step 2: "get confluence page approval", "list and diff confluence page versions", "list jira issue changelogs", "get atlassian project and goal", "search atlassian projects and goals", "list loom videos" and "list confluence comments". Skip discovery for directly exposed operations, and skip operations confirmed unavailable in this session |

Call exposed operations directly, including approvals, versions, Projects/Goals, changelogs and Loom. Discover an operation and use its matching runner only when it is not directly exposed. `search` and `getGraphContext` use Rovo credits. A typical run makes 25 to 45 calls. Send calls that don't depend on each other together, as "Fetch in parallel" in `teamwork-graph-context` describes: the searches and JQL in Step 2 with the `discover` calls, the record reads in Step 3, and Steps 4 to 6 once the main record is known.

Dates with a time are shown in the user's timezone, which the footer states: a status change at 07:10 AEDT is Oct 22 there and Oct 21 in UTC. A date with no time (a meeting date on a page, a Decision date field) is shown as written.

## Step 1: Pin down the question

1. Call `getAccessibleAtlassianResources` once for the `cloudId` and any returned `products` metadata (absence means unknown availability).
2. Restate the question as **one decision subject**: the thing decided, in a few words ("pausing the Beacon editor", "the name of the Platform CLI"). Write down:
   - the **subject terms:** 2 or 3 short terms people would use in a title, from the subject itself rather than the programme or product family ("editor pause", "Beacon editor", not "Beacon" alone). When the question is whether something is in scope for a programme, environment or product ("is X in scope for Y?"), Y is the **scope term**: keep it, and add it to every query
   - the **kind of question:** why (reasons first), who (decider first), what or "did we decide" (the outcome first), or still current (revisits first). A question that asks two ("what did we decide, and who decided?") leads with the first one asked. The page is the same; the kind sets what the short answer leads with.
   - any **date hint** the user gave ("in the summer", "last quarter")
3. **If the user gave a URL or key** (a Confluence page, a Jira work item, a project or goal, a Slack thread or a Loom video), that's the first candidate record. Resolve it as "Resolve the anchor" in `teamwork-graph-context` says, and still run Step 2, since the same decision is often recorded in more than one place.
4. **Too broad** ("why did we decide our strategy?"): ask which decision, offering 2 or 3 from a first search. If the user can't be asked, pick the one closest to their words and say so in the header.
5. **About a person or another sensitive subject:** stop, as "What this skill will and won't do" says.

## Step 2: Find the records

Send these together, each `search` with and `limit: 20`:

- `targetApp: CONFLUENCE` with the subject terms plus "decision" ("Beacon editor pause decision").
- `targetApp: CONFLUENCE` with the subject terms plus "DACI" or "proposal".
- `searchConfluence` with CQL `type in (page, database) AND (title ~ "register" OR title ~ "decisions" OR title ~ "log") AND text ~ "\"<term 1>\""` (the term quoted, plus the programme or scope name if it's distinctive), for a decision register whose title doesn't match the subject. This doesn't count against the `search` cap.
- `targetApp: ALL` with the subject terms alone, or with the word the record would use instead of "decision" ("Platform CLI naming", "editor staffing"). Records are often titled by their subject, or as a question.

If Jira is on the site, run JQL as the Jira route. `search` with `targetApp: JIRA` returns mostly dashboards named "Decisions" for this job, so don't use it.

1. `issuetype = Decision AND (text ~ "\"<term 1>\"" OR text ~ "\"<term 2>\"") ORDER BY updated DESC`, with `fields: ["summary", "status", "issuetype", "labels", "created", "resolutiondate", "project"]` and `maxResults: 25`. Many sites have a Decision issue type, often in a decision register project. If the query errors because the type doesn't exist, or returns nothing, run the second query.
2. `(text ~ "\"<term 1>\"" OR text ~ "\"<term 2>\"") AND (summary ~ "decision" OR summary ~ "decide" OR summary ~ "DACI" OR labels in (decision, decisions, decision-product, decision-architecture)) ORDER BY updated DESC`, with the same fields. Also keep any result whose labels start with "decision". When Step 1 found a scope term, add `AND text ~ "\"<scope term>\""` to both queries: generic terms alone match many unrelated decisions.

Quoted phrases match exactly, so include the singular and plural forms of a term that has both ("\"help center\"" and "\"help centers\""). A Jira decision's summary is often the question ("Is X in scope for Y?") or the answer ("Yes: …"), not the word "decision".

**Pick the candidate records.** Keep a hit only if it's about the same decision subject (same names, terms or project). Don't drop a likely record on its snippet alone while read slots are free: snippets are short and can be stale. Drop sensitive results first. Sort what's left into shapes:

| Shape | How you spot it |
| --- | --- |
| Decision page | A page whose title or header says decision, with a status, outcome or "we decided" text. Confluence's decision template has Status, Approver or Decider, Stakeholders, Outcome and Due date fields |
| DACI or proposal | A Driver, Approver, Contributors, Informed table, or an Ask, Approver and Decision status header, often with options and a recommendation |
| Decision register | A page, live doc or database with a table of many decisions, one per row. It may have date, approver and status columns, or only some of them |
| Meeting decisions list | Meeting notes or an outcomes page with a "Decisions" heading or panel listing what was agreed |
| Jira decision | A work item whose type, summary or labels say decision, or whose resolution or description states what was decided |
| Highlight | A decision highlight on a project or goal (Step 5) |
| Discussion | Anything else that talks about it: chat, meetings, comments, strategy docs, status reports (Step 6) |

Keep up to 6 records for Step 3 from search, in this order: decision pages, Jira decisions and meeting decisions lists, then DACIs and proposals, then registers, newest first within each. The other 4 reads are for records found by following links in Step 3 and for related pages in Steps 5 and 6. If more qualify, say how many were left in the footer.

**Older records:** related-content edges in Teamwork Graph only reach back about 90 days (see Step 5), so a precursor decision from last year is found only by search or by a link in a record.

If nothing qualifies, skip to Step 6: the verdict may still be "No decision record found", with the discussion listed.

## Step 3: Read the records

1. **Confluence records:** read each with `getConfluenceContent` (`content_format: markdown`, `detail: full`), together.
2. **Content lost in markdown.** Re-read a record with `content_format: html` (up to 3 re-reads, the main candidates first) when its `lostFeatures` lists `time`, `ac:structured-macro` or `ac:adf-extension`, when a heading has nothing under it, or when its search snippet quotes text the markdown doesn't hold. Decision text often sits in a panel, and register dates in date elements: both vanish from markdown. Take dates from `<time datetime="…">`. See "Content lost in markdown" in `teamwork-graph-context`.
3. **Live docs:** the read's `version` can show version 1 with a recent date. Take edit dates only from `listConfluenceContentVersions`.
4. **Jira decisions:** read up to 2 with `getJiraIssue` (`view: evidence`, `responseContentFormat: markdown`). On a large site this returns every custom field, so save it to a file and pick out what you need. Look in `fields.customFields` for fields whose names include Approver, Decider, Accountable, Decision date or DACI, plus the status, resolution and its date, the description's decision line and labels. Read comment bodies separately with `listJiraIssueComments`; issue reads alone do not establish comment coverage.
5. **Follow links.** A record often points to the real one: "Decisions and next steps: [link]", "See the DACI", "Supersedes [page]", "Outcome: [link]". Read linked decision records within the 10-read cap. A Jira decision's remote links and a register row's link count too, but a "cloned from" or "duplicates" issue link doesn't. When a record mentions an earlier decision it doesn't link ("was not in scope for the earlier programme"), run one JQL or `search` for it with that decision's terms.
6. **Take from each record, only what it states:**
   - the **decision text**, word for word where it's short (up to about 40 words), with its heading, panel or field name ("Outcome", "Decision"). When one record holds both an Ask or Recommendation and a Decision or Outcome that differ, the Decision or Outcome is the decision, and the difference goes under "Not in the records". When a decided record's body doesn't state the outcome (an empty Outcome field) but a comment on it does, quote the comment, labelled "[name] commented on [date]", and add "The record's body doesn't state the decision" under "Not in the records". The commenter isn't the decider
   - the **status:** a decision status field in the body first, then a decision heading or panel that states the outcome, then the Confluence page status (`contentState`) or the Jira status. If the page status disagrees with the body ("Decision status: APPROVED" on a page whose status is In progress), show both, and add a line under "Not in the records"
   - the **decider:** the value of an Approver, Decider or Accountable field, a register's approvers column for this row, or a sentence that says who decides this decision ("[Name] to make the final call"). Record which of these it came from. An author, owner, Driver, assignee, reporter or "Informed" person is not a decider. A Driver isn't an approver either
   - the **date of the decision** if a field or row states it ("Decided on", a register's date column, a Decision date field, the meeting's date for a meeting decisions list). Otherwise it comes from Step 4
   - **reasons,** only from a part of the record that explains the decision: a Context, Background, Problem, Why or Rationale section, a summary panel, or a Jira description's text before its decision line
   - **options,** only from an options, alternatives or "considered" section, each with the record's own name for it, and whether the record marks it chosen or recommended
   - **links to other decisions,** such as "supersedes", "revisits", "replaces", or a link to an earlier decision or register row
7. **A register:** use only the rows about the decision subject. Each row is its own record with its own date and approvers. Link the register with the row's decision text in the chip's label. A missing date or approver column goes under "Not in the records".

## Step 4: Date the changes

Pick a provisional main record now, by the rule at the start of Step 5, and confirm it there.

A page's last-modified date is not the decision date. Find when the status or the decision text actually changed. Run this step for the main record (Step 5 names it) and one other record, plus one version list and one probe for a Revisit record whose reopening date isn't stated. Skip it for a record whose decision date comes from a field, an approval, a register row or a Jira changelog, unless the decision text may have changed since. Version probes and diffs each return 50 to 100 KB, so save large results to a file. A meeting decisions list is always checked. If v1 already held the line, the meeting date says when it was agreed ("Agreed at the Mar 3 meeting"). If v1 held a different line for that item, or a question, don't credit the meeting with the new wording: date it by the version range ("Recorded on the page between v4, Mar 5, and v6, Mar 6; the meeting was Mar 3"), and say under "Not in the records" that the wording changed after the meeting. A line still phrased as a question is Proposed.

1. **Confluence approvals.** Approvals work on pages only, not live docs: for a live doc, skip this and say "Not run: approvals don't apply to live docs" in the footer. For each Confluence decision page or DACI (up to 3), call `getConfluenceApproval` with `contentId`, `contentStatus: CURRENT` and `expand: ["history"]`. An approval with a decision and a reviewer is the strongest record of who approved it and when. "Approvals enabled" with no history means nobody used the workflow: say nothing about it in the trace, and don't treat it as missing.
2. **Version history.** Call `listConfluenceContentVersions` (`limit: 50`, and page if there are more). Ignore versions whose message starts with "Automatic conversion". Then use up to 5 `diffConfluenceContentVersions` calls or single-version probes, with `content_format: html`, since a markdown diff can miss the change entirely. Look for two kinds of change: the status becoming Approved, Decided or similar, and the decision text being added or rewritten (a question in v1 that's an answer by v6).
   - **Start from a date hint** if one exists (a linked Jira item's Decision date, a meeting date, a project update that says "in review"): diff the versions on either side of it first.
   - **Otherwise bisect:** diff the first and latest versions, then the midpoint against the side the change is on, and repeat.
   - **Probe with single versions.** A `getConfluenceContentVersion` read of one version (`content_format: html`) is smaller than a diff, which returns both bodies. Use it to check whether a status or panel is there at a midpoint. Probes and diffs share a cap of 5 per record. Don't pass `responseFields` to a probe: it came back as `{"data":{}}`.
   - **A range is a valid answer.** If the cap runs out, say "between v1 (Mar 2) and v9 (Apr 14)".
3. **Write it as "marked Approved on [date], approver named as [name]"**, or "decision text added on [date]". When the decision text was added or reworded after the status became Approved, show both dates, and if the new wording differs from what was approved (a later date, a narrower scope), add under "Not in the records": "No record shows the [date] wording was approved." The person who made the edit is not the decider, and isn't named as such. Never say the approver approved it on that date unless an approval record or the record's own text says so.
4. **Recommendation changes.** If a diff shows the recommendation or the chosen option changing before the status change, note it in the timeline with the version range ("Recommendation changed from A to B between v1 and v11").
5. **Jira.** For a Jira decision, call `listJiraIssueChangelogs` with `maxResults: 1` to read `total`, then read `startAt: max(0, total - 20)` with `maxResults: 20`, and one page further back if the status change isn't there, and take the date the status moved to the decided state (Decision Made, Done, Approved). Don't name who moved it. When a Jira decision names no approver and Step 2 or Step 3 found the project's decision process page, read it inside the record cap. If it covers this kind of item (its scope matches the item's type, label or project), and it or the project's description says who makes that move ("the approver moves it to Decided"), don't combine the two: say "The item names no approver" under "Not in the records", and quote the process line there.
