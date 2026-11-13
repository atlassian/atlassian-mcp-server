---
name: "decision-trace"
description: "Trace a decision to its records: what was decided, when, who decided, the options considered, and whether it was revisited or reversed. Uses Teamwork Graph to find decision pages, DACIs, registers, meeting decisions, Jira work items, project and goal highlights, Loom summaries and public chat, then reads records and version history. Answers in the conversation first with source wording, a dated timeline, deciders and gaps. Offers the existing HTML report on request and publication only when Atlassian Artifacts is available and requested. Use for why did we decide, who decided or signed off, what was decided, is it still current, or /decision-trace. For a period's changes, use catch-up. For behaviour in code, use how-it-works. For an expert, use whos-the-expert."
---

# Decision trace

Answer "why did we decide X?", "who decided?" or "what did we decide about X?" in the conversation for someone who wasn't there: a new team member, a stakeholder who's been asked to defend the decision, or a lead deciding whether to reopen it. In a few minutes they get what was decided in the record's own words, when, who the record names as the decider, the options it weighed, and whether anything since has reopened it.

Decisions are scattered. The record might be a decision page, a DACI table, one row in a register, a list in meeting notes, a Jira work item or a highlight on a project, and the discussion that led to it is somewhere else again. The value of this skill is the judgement a search results page can't make. It tells a recorded decision apart from a proposal and from talk, takes the decider only from a field that names one, dates when a status or the decision text actually changed, keeps a chain of related decisions apart instead of merging them, and says plainly when no record exists.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. Its "Content lost in markdown" and "Loom lists come back short" notes under "Product tools" matter most here. This file adds what's specific to tracing decisions.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## What this skill will and won't do

- **It reports what the records say.** The decision, its reasons and its options appear only as a record states them, quoted or closely paraphrased, with a link. It never fills a gap with what the decision probably was, and never quotes a decision from a search snippet: snippets can carry text that no version of the page holds.
- **It never infers who decided.** The decider comes only from an Approver, Decider or Accountable field, a register's approvers column, or a record that names who decides. Never from the page's author or owner, the person who edited the status or moved the work item, the most senior person in a meeting, or the exec sponsor. A process page that says "the approver moves it to Decision Made" doesn't make whoever moved it the approver. When no record names one, say "No decider recorded".
- **It doesn't judge the decision.** No view on whether it was right, and no recommendation to reopen it.
- **Sensitive decisions stay out.** Decisions about people (hiring, levels, reorgs, performance) and anything "Sensitive content" in `teamwork-graph-context` covers are never traced, even when the user names one. Say that this skill doesn't cover that kind of decision, and stop.

## Sensitive content for decisions

These add to "Sensitive content" in `teamwork-graph-context`.

- **Where decisions happen privately.** Real decisions are often made in direct messages, group messages and leadership channels. Leave them all out, even when they hold the answer: a Slack direct message (URL contains `/archives/D`, or a title with no channel name), a group message (channel name starts with `mpdm-`), and a channel whose name says leadership, exec, staff or board, or uses a word or abbreviation for them (`leaders`, `leads`, `lt`, `elt`, `slt`, `exec`), whether or not it shows as private: search results don't say. A Slack URL with `/archives/G` is a private channel, so its name needs the check too. Don't read, quote or count them. When any were left out, the footer says "Some results weren't used", and nothing more.
- **Documents written for leadership** (a leadership-team DACI, an exec review page) are usable decision records, unless they're marked confidential or restricted, or hold a category "Sensitive content" lists. The exec-only rule covers restricted channels and material marked as such, not every page a leader reads.
- **Comments and meeting notes** on a decision often carry customer revenue, deal sizes, headcount or named customers' staff. Drop those parts and keep the rest.
- **Calendar events** found by search are pointers to a meeting. Their snippets can hold dial-in passcodes, and their links encode an email address. Use the meeting's recording or notes if there are any. Otherwise name the event and its date in plain text, with no link or snippet.
- **One-to-one recordings:** a Loom meeting recording between two people counts as a private conversation, like a direct message. Leave it out. The list doesn't return participants, so judge by the title: "1:1", "1-1", "one on one", "mentorship", "coaching", or two names joined by "/", "|", "&", ",", "<>" or "and". The leadership words above apply to recording and event titles too.
- **Account labels:** drop "(Deactivated)" and similar suffixes from names.
- **Rejected options can name people** ("move Sam's team to…"). Describe the option by what it does, not by who it affects.

## Connectors

- **Needed:** Confluence or Jira, either one. They hold most decision records. With neither on the site (see "Atlassian apps on the site" in `teamwork-graph-context`), say so before building: the trace can only use third-party discussion, so the verdict can be no better than "Proposed, not recorded as decided".
- **Helpful, from Atlassian:** Projects and Goals, for decision highlights and updates that report a decision. Loom, for meeting recordings and their AI summaries around the decision dates.
- **Helpful, from other tools:** Slack or Teams public channels, where a decision is announced or questioned. Google Drive or SharePoint, for decision docs kept outside Confluence.
- **Vendor connectors,** as `teamwork-graph-context` describes: Slack or Teams, to read a public thread in full when only the snippet comes back. Google Drive, to read a decision doc that hydrates empty. Never use them to read direct or group messages for this skill.

## Budget

Unless the user asks for a deeper pass, stay within these, and say in the footer if one was reached:

| Tool | Cap | Where |
| --- | --- | --- |
| `search` | 5 | 3 in Step 2, 2 in Step 6 |
| `searchConfluence` (CQL) | 1 | Step 2, for registers |
| JQL (`searchJiraIssuesUsingJql`) | 3 | 2 in Step 2, and 1 in Step 3 for an earlier decision a record mentions |
| `getConfluenceContent` | 10 reads, plus up to 3 HTML re-reads | Step 3, including pages linked from records and related pages from Step 5 |
| `getJiraIssue` | 2 | Step 3 |
| `getConfluenceApproval` | 1 per Confluence record, up to 3 | Step 4 |
| `listConfluenceContentVersions` and `diffConfluenceContentVersions` | 1 list and up to 5 diffs or probes per record, for up to 2 records | Step 4 |
| `listJiraIssueChangelogs` | 3 | Step 4 |
| `getGraphContext` | 3 | Step 5: a summary and a filtered `full` call on the main record, and one summary on a second record |
| `getGraphObject` and `listConfluenceComments` | 1 batch and 1 list | Step 5, comments only |
| `getPeopleInfo` | 1 batch of up to 10 | Step 5, names for comment authors and approvers returned only as account IDs |
| `searchProjects`, `searchGoals`, `getProject`, `getGoal` | 2 searches and 3 reads | Step 5 |
| `listLoomObjects` and `getLoomObjectsContent` | 3 list pages and 1 batch of up to 10 | Step 6 |
| `discover` | up to 7 | Sent together after Step 2: "get confluence page approval", "list and diff confluence page versions", "list jira issue changelogs", "get atlassian project and goal", "search atlassian projects and goals", "list loom videos" and "list confluence comments". Skip any for an app that isn't on the site |

Operations that aren't primary tools (`getConfluenceApproval`, the version tools, the Projects and Goals tools, `listJiraIssueChangelogs`, `listLoomObjects`) are reached through `discover` and run with `executeRead`. `search` and `getGraphContext` use Rovo credits. A typical run makes 25 to 45 calls. Send calls that don't depend on each other together, as "Fetch in parallel" in `teamwork-graph-context` describes: the searches and JQL in Step 2 with the `discover` calls, the record reads in Step 3, and Steps 4 to 6 once the main record is known.

Dates with a time are shown in the user's timezone, which the footer states: a status change at 07:10 AEDT is Oct 22 there and Oct 21 in UTC. A date with no time (a meeting date on a page, a Decision date field) is shown as written.

## Step 1: Pin down the question

1. Call `getAccessibleAtlassianResources` once for the `cloudId` and the site's `products` list.
2. Restate the question as **one decision subject**: the thing decided, in a few words ("pausing the Beacon editor", "the name of the Platform CLI"). Write down:
   - the **subject terms:** 2 or 3 short terms people would use in a title, from the subject itself rather than the programme or product family ("editor pause", "Beacon editor", not "Beacon" alone). When the question is whether something is in scope for a programme, environment or product ("is X in scope for Y?"), Y is the **scope term**: keep it, and add it to every query
   - the **kind of question:** why (reasons first), who (decider first), what or "did we decide" (the outcome first), or still current (revisits first). A question that asks two ("what did we decide, and who decided?") leads with the first one asked. The page is the same; the kind sets what the short answer leads with.
   - any **date hint** the user gave ("in the summer", "last quarter")
3. **If the user gave a URL or key** (a Confluence page, a Jira work item, a project or goal, a Slack thread or a Loom video), that's the first candidate record. Resolve it as "Resolve the anchor" in `teamwork-graph-context` says, and still run Step 2, since the same decision is often recorded in more than one place.
4. **Too broad** ("why did we decide our strategy?"): ask which decision, offering 2 or 3 from a first search. If the user can't be asked, pick the one closest to their words and say so in the header.
5. **About a person or another sensitive subject:** stop, as "What this skill will and won't do" says.

## Step 2: Find the records

Send these together, each `search` with `mode: STANDARD` and `limit: 20`:

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
4. **Jira decisions:** read up to 2 with `getJiraIssue` (`view: evidence`, `responseContentFormat: markdown`). On a large site this returns every custom field, so save it to a file and pick out what you need. Look in `fields.customFields` for fields whose names include Approver, Decider, Accountable, Decision date or DACI, plus the status, resolution and its date, the description's decision line, labels and comments.
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

## Step 5: Expand from the main record

The **main record** is the record with a decided status whose decision event (the date from Step 3 or Step 4, not the last edit) is newest. When two records state the same decision, prefer the one with a decision status field and a named decider. If none is decided, it's the newest decision page, Jira decision or DACI, in that order.

1. Call `getGraphContext` on the main record with `detailLevel: summary`. If it shows related content beyond the comments already read, call it once more with `full`, filtered with `relationshipTypes` to those relationships. If the newest decision record isn't the main record and hasn't been walked, and the answer still lacks something it could hold (a decider, a revisit), run one more summary call on it.
2. Read Confluence comments with one `listConfluenceComments` call on the page (it has authors and dates), and other comments in one `getGraphObject` batch. Read related pages with `getConfluenceContent`, inside Step 3's cap: `getGraphObject` returns Confluence pages as raw ADF.
3. **Related-content edges reach back about 90 days.** A precursor older than that won't appear here: Step 2's search and the links in records are what find it. Say in the footer that the walk covered the last 90 days of related content.
4. **Projects and Goals,** if they're on the site. If a record or the search results name a project or goal, read it directly. Otherwise run up to 2 `searchProjects` or `searchGoals` calls with the subject terms and `limit: 10`. `getProject` and `getGoal` take `identifier` (a key or ARI), `cloudId`, `include`, `highlightType` and `limits`. Read up to 3 that a record links or names, or whose name matches the decision's scope, with `getProject` or `getGoal`: `include: ["highlights", "updates"]`, `highlightType: DECISION`, `limits: {highlights: 20, updates: 10}`. A decision highlight is a record. An update that says a decision was made ("we decided to…") or is pending ("decision in review") is evidence for the timeline, dated by its `creationDate`. When none has a decision highlight, the footer says "No decision highlights recorded".
5. **Comments** on the main record can hold the real debate, or a later "we've reversed this". Keep comments that say something was decided, questioned or reopened, dated by their created time. Graph comment objects can come back without one: date Confluence comments with one `listConfluenceComments` call on the page instead, and Jira comments from `getJiraIssue`.

## Step 6: Sweep for discussion

Send these together:

- `search` (STANDARD, `targetApp: THIRD_PARTY`, `limit: 20`) with the subject terms plus "decided" or "decision", for Slack, Teams and Google Drive.
- `search` (STANDARD, `targetApp: ALL`, `limit: 20`) with the subject terms and a word for change ("revisit", "reopen", "reverse"), to catch revisits.
- If Loom is on the site, up to 2 `listLoomObjects` calls with `scope: ALL`, `artifactTypes: ["MEETING_RECORDING"]`, `limit: 25` and `responseFields: ["items.title", "items.createdAt", "items.url", "hasNextPage", "nextOffset"]`, titles only. A page can come back empty with `hasNextPage: true`: one with `createdAtRange` 7 days either side of the main record's decision date (the date its status became decided, when that differs from when the text was written), and one for the last 30 days, skipped when the decision date is inside those 30 days. A third page, if one is needed, goes to the decision-date window first. A list returns about 15 items, newest first, so a longer window misses its start. If a list has `hasNextPage: true` and hasn't reached its window's start, read the next page by setting `createdAtRange.to` to the oldest `createdAt` returned, not with `nextOffset`, which can skip items (see "Loom lists come back short" in `teamwork-graph-context`). Check titles first: drop one-to-ones and anything "Sensitive content" covers by title, so their summaries are never fetched. Then keep recordings whose title could be about the subject, or whose date is within a day of a record's date. Say in the footer which dates the lists covered, and that they show only recordings the user can see.

Then:

- **Drop excluded results first,** as "Sensitive content for decisions" says, and count nothing about them.
- **Meeting summaries:** read up to 10 kept recordings with one `getLoomObjectsContent` batch and no `expand`: each result's `description` is its AI summary. Keep those whose summary names the subject. Add `expand: ["transcript"]` (up to 5) only for a recording whose summary mentions the decision but not what it was. `agentBrief` usually comes back `ABSENT`.
- A public channel message that **announces** a decision ("We've decided to…", "Approved:") counts as a Recorded decision only when it names who decided or is posted by someone a record names as the decider. Otherwise it's Discussed, with the poster named as "according to [name] in Slack".
- Follow a decision page or Jira link inside a kept result: read it in Step 3 if a slot is free.

## Step 7: Assess

### Statuses

Use the record's own word in the timeline, and map it to one of these for the verdict:

| Records say | Means |
| --- | --- |
| Decided, Decision Made, Approved, Accepted, Agreed, Final, Done (on a decision) | Decided |
| Proposed, Draft, In review, Ready for review, Pending, Open, In progress, Problem identified, Problem defined, Not started, Awaiting decision | Proposed |
| Rejected, Declined, Won't do | Decided (the decision was not to) |
| Superseded, Replaced, Revisited, Reopened | Decided, later revisited (the newer record carries the current state) |
| Paused, On hold, Deferred | Proposed, unless a record says deferring was itself the decision |
| Cancelled, Withdrawn | Not decided: list it, and it doesn't count as a decision record |

A meeting decisions list states decisions as made, so its items are Decided unless the list marks one as open.

### Item types

Each timeline item is one of these, with its lozenge:

| Type | Use it when | Lozenge |
| --- | --- | --- |
| Recorded decision | A record (page, register row, meeting decisions list, Jira decision, approval, decision highlight) states the decision as made | Recorded decision (success) |
| Proposed | A record proposes or asks for a decision that it doesn't record as made | Proposed (information) |
| Revisit | A later record or meeting refers to this decision (by link, title or its wording) and says it's reopened, under review or being reconsidered | Revisit (warning) |
| Reversed | A later record states the decision was reversed or replaced by an opposite one | Reversed (danger) |
| Meeting summary | An AI meeting summary or action items, from Loom or synced into a page (a section marked "AI generated", or "Synced from" a calendar or Loom) | Meeting summary (neutral) |
| Discussed | Chat, comments, status reports or docs that talk about it without recording or reopening it | Discussed (neutral) |

- **Follow-on questions aren't revisits, but undoing questions are.** A later record that accepts the decision and asks how to carry it out (who owns the new direction, what replaces it, how to staff the replacement) is Proposed, for a new decision in the chain. A record that asks whether to undo, restart or reverse what was decided ("should we bring the team back?") is a Revisit, even when it's framed as a staffing or ownership question. Judge the record's own question, not its list of options: a question about who owns the work is follow-on even if one option would undo the decision.
- **Questions in comments are Discussed.** A comment asking "won't this confuse customers?", or a status line saying "still with leadership" that doesn't refer to the decision, is Discussed. If it's newer than the decision, mention it in the answer.
- **Comments that state the outcome are Discussed.** "Agreed, let's go ahead" from the assignee doesn't make them the decider.
- **AI meeting summaries are summaries, never records.** "Participants agreed to…" or "[Name] recommended…" in an AI summary was written by a machine. Show it as "The meeting summary says…", typed Meeting summary. It never makes the verdict Decided on its own, and never names a decider. It can support a Revisit when it says the question was reopened.
- **Version changes are timeline items,** typed by what they did: a status change to Approved is a Recorded decision, a rewritten recommendation is Proposed. Otherwise one item per record, dated by its event time as "Dating events in a window" in `teamwork-graph-context` says. A record that states no decision date is placed by its page or work item creation date, marked "Created [date]". Only a record with no date at all goes last, marked "No date".

### Chains of decisions

**One decision or two?** Records hold the same decision when they state the same outcome for the same scope and team, even in different words or with dates a month apart: show it as one decision, with the other records under "Also recorded", and put any difference in wording or dates under "Not in the records". They're two decisions when the outcome, scope or team differs, or one record replaces the other.


One subject often holds several linked decisions: an original decision, a proposal that revisits it, a newer one that replaces it, and follow-on decisions. **Never merge them into one.** Each decision gets its own block in the answer, newest first, and the timeline shows them all. The verdict is about the newest decision on the subject the user asked about. The answer says what a decision replaced only when a record says so.

- **A related decision in another scope** (the same question decided earlier for a different environment, product or region) gets its own block labelled with that scope ("Earlier decision, for the EU region"). It doesn't change the verdict.
- **A decider named for a follow-on question** ("[Name] decides how to staff it") goes on that decision's block only.

### The verdict

One of these, for the newest decision on the subject:

- **Decided** (success): a Recorded decision exists, and nothing after it is a Revisit or Reversed.
- **Decided, later revisited** (warning): a Recorded decision exists, and a later item is a Revisit or Reversed, or a Meeting summary that says the decision itself is being reopened. That summary stays typed Meeting summary, and the warning message quotes it as "The meeting summary says…". If a later record states a new decision, say the current decision is the newer one. If the revisit is still open, say "Reopened on [date], no new decision recorded".
- **Proposed, not recorded as decided** (information): Proposed items exist, but no Recorded decision.
- **No decision record found** (neutral): nothing beyond Discussed and Meeting summary items. List the discussion, and never say what was decided.

Never: name a decider from authorship, ownership, edits or status moves; state a reason or option no record gives; call a meeting summary a decision; or say a decision was reversed without a record that says so.

### Who decided

Show it as the record gives it, with where it came from: "Approver: [name] (DACI table)", "Approvers: [names] (register row)", "Decides: [name] (named on the decision page)". If records disagree (the DACI names one approver, the approval workflow another), show both with their sources. If none names one, say "No decider recorded". Only when the user asked who decided, you can add "The page was written by [name]" so they know where to start, never as the decider.

### Options

Mark an option "Chosen" only when the options record, or a record that names it, says which was chosen. An outcome on another record matches an option only when it makes the same choice for the same scope: if every option assumes something the outcome doesn't (a single merged tool, when the outcome keeps two), none matches. If the outcome on another record matches an option but neither record links the two, show the options record's own "Recommended" marker, if any, and say in the section that the choice is recorded elsewhere.

### Stop condition

Stop gathering when the verdict and the newest decision's what, when and who are each either found or known to be missing from the records read. One extra call is fine if it could change the verdict, such as a diff to date an approval.

## Writes

None. The skill is read-only. If no record exists, suggest in the reply that the decision be written down, and offer nothing more.

## Answer and offer an export

- Lead with the verdict and the answer to the question as asked, using the record's words. State the newest decision, when it was decided, who is explicitly recorded as decider or that no decider is recorded, and whether it was reopened.
- Keep each decision in a chain separate. For each, show the source wording, date and how it is known, decider and how that is known, and other records of the same decision. Retain the later-wording, approval-date, revisit and newer-proposal qualifications from the report's answer section below.
- Present recorded reasons, options and their recorded dispositions when available, plus the dated timeline. Keep proposals and discussion separate from decisions and mark inferred relationships found by search.
- Include Not in the records and Sources and limitations: contradictions, missing deciders or dates, record/discussion counts, version ranges left open, search windows, HTML re-reads, Loom date coverage and caps. If no decision record was found, say so and suggest recording the decision; offer no write.

Ask whether the user wants this exported to an HTML report. If they have already explicitly requested an export, HTML report or publication, proceed with that requested build without asking again. Otherwise stop here until they answer; a normal invocation of this skill does not request a report. Follow the shared availability and confirmation checks before offering or performing publication.

## Step 8: Build the trace (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in this folder:

```bash
python3 <this skill's folder>/render.py trace.json decision-trace-<topic>.html
```

- **The data** has the shape of `example.json` in this folder (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **The keys.** `question` and `verdict` head the page, and `traced` is `{"records", "discussions", "date"}` for the "Traced from" line, counted as the header rule below says. `answer` is the 2 or 3 sentences, and `generatedFrom` the apps actually used. Each of `decisions`, newest first, is `{"heading", "status", "decided", "link", "when", "whenHow", "who", "whoHow", "also", "alsoHow"}`: `decided` the record's words, `whenHow` and `whoHow` how each is known ("page history", "DACI table"), shown in brackets after it, so keep them out of `when` and `who`. `also` lists other records of the same decision, and `alsoHow` is a note on them only when one says something the main record doesn't ("The decision page states the same outcome and names no approver"). `revisit` is the warning message as `{"title", "text", "links"}`, and `newer` the information message. `why` lists the reasons as text fields with their source chips, `options` is `{"heading", "items", "from"}` with each item `{"name", "text", "chosen", "recommended"}`, `timeline` is `{"date", "type", "text", "link"}` oldest first, and `notInRecords` the lines for what's missing.
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `references/hand-built.md` in this folder.

The rules below say what the renderer builds, and what each part of the data must hold.

### Sections, in this order

1. **Header** (not a card): eyebrow "Decision trace", the question as the page's only `h1`, and the verdict lozenge on the right. Under it, in small subtlest text: "Traced from [N] records and [M] discussions, on [date]. Every claim links to where it came from." N and M count distinct objects the page shows, not timeline items: records are the objects behind items typed Recorded decision, Proposed, Revisit or Reversed, and discussions are the rest. Comments on a record count as discussions.
2. **The answer** (icon `sparkle` in `--ds-icon-discovery`): 2 or 3 plain sentences that answer the question as asked, led by what its kind needs (Step 1). Then one block per decision in the chain, newest first, each headed with what it is ("Newest decision", "Earlier decision it revisits", "Earlier decision, for [scope]") and its status lozenge, with a field list:
   - **Decided:** the decision text in a quote block, with its smart link
   - **When:** the date and how it's known ("Marked Approved on Sep 15, 2026 (page history)", "Decided on Mar 4, 2025 (register row)", "Moved to Decision Made on Oct 14, 2026 (work item history)")
   - **Who decided:** as "Who decided" says, or "No decider recorded". When the quoted wording was added after the approval, qualify it here: "Approver: [name], for the status marked Approved on [date]. The quoted wording was added later (DACI table)."
   - **Also recorded:** other records of the same decision, if any
   If the verdict is "Decided, later revisited", a warning section message after the blocks says what reopened it and when, with its link. If the verdict is Decided but a proposal on the same question is still open and newer than the decision, or a later report says the question is still pending, an information section message there says so ("A newer proposal is still a draft: [link], recommending [option]"). It doesn't change the verdict. Underneath, in small subtlest text, the apps actually used: "Generated from Confluence, Jira and Slack. Check it before relying on it."
3. **Why** (icon `comment`), if any record states reasons: up to 5 bullets in the record's words, each with its source chip. If none does: "No record states the reasons."
4. **Options considered** (icon `list-checklist`), only if a record has an options section: one row per option, with the record's name for it, a short description in its words, and a "Chosen" success lozenge or a "Recommended" information lozenge as "Options" says. Under the list, which record the options came from. When they belong to an earlier decision in the chain, head the section with that decision's block name ("Options considered for the 2025 decision"). Otherwise leave the section out, and say in the footer "No options section in the records".
5. **Timeline** (icon `clock`): every item, oldest first, as a vertical list. Each item: the date (or "No date"), its type lozenge, one sentence on what it says, and its smart link. Version changes appear as their own items ("v9, Sep 15: decision text added"). Items found by search, including JQL hits, are marked as `teamwork-graph-context` describes. The records that answer the question (the decision blocks in the answer) are never marked: finding them is the skill's job. Mark discussion and related items found by search that no record links to.
6. **Not in the records** (icon `warning`), if anything the question asked for is missing or contradicted: one line each ("No decider recorded on the decision page", "The register row has no date", "The page status is In progress, but its decision status says Approved"). An earlier proposal on the same question that's still open (Draft, In review) and that no record closes gets a line too ("The pricing DACI is still a draft, and no record closes it"). This is where the gaps the user would otherwise assume were checked go.
7. **Sources footer** (not a card), as `teamwork-graph-context` describes, plus: how many records were read, any cap reached, version ranges left open, "Related content checked for the last 90 days only", records re-read from HTML, the dates the Loom lists covered, the timezone dates are shown in, and "Some results weren't used" when any were left out.

Lozenges: verdicts and item types as above. Record statuses: Decided, Decision Made and Approved = success, Proposed, In review and Problem identified = information, Rejected = neutral, Superseded and Reopened = warning. Icons: a Jira decision work item uses `task` (or the site's own type icon if the design skill has one), a Jira or Confluence comment `comment`, a Loom recording `video`, a Slack message `hashtag`.

### Writing the answer

- Use the record's words for the decision. Paraphrase only to shorten, and never change what was decided.
- Name people only as deciders when a record names them, and as speakers in chat or comments ("according to [name] in Slack", "[name] commented").
- No hype, no judgement of the decision, and no "not X but Y" framing.

## When live

Static only. The trace depends on judging which records count and on the sensitive-content rules, which page code can't apply. To check for a newer decision, run the skill again.

## Step 9: Deliver the requested report

- Hand over the requested HTML trace. If Atlassian Artifacts availability is confirmed as described in `teamwork-graph-context`, offer a private, read-only copy named "Decision trace: [the decision subject]". Publish only if requested; export alone does not authorise it.
- After an approved publication, offer sharing only with the people the user names, and share only on request.
- Preserve decision chains, evidence wording, qualifications, timeline and limitations from the answer.
