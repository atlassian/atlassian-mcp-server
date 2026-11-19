---
name: "decision-trace"
description: "Trace a decision to its Confluence and Jira records: what was decided, when, who explicitly decided or approved it, the options considered, and whether it was later revisited or reversed. Uses Confluence pages, DACIs, decision registers, meeting notes, page approvals, version diffs, comments, Jira decision issues, changelogs, and Rovo Search. Delivers a grounded conversational trace with source wording, a dated timeline, recorded deciders, contradictions, and transparent gaps. Use for why did we decide, who decided or signed off, what was decided, is it still current, or /decision-trace. For a period's changes, use catch-up."
---

# Decision Trace

Answer "why did we decide X?", "who decided?", or "what did we decide about X?" in the conversation for someone who was not there: a new teammate, a stakeholder defending the decision, or a lead deciding whether to reopen it. Give them what was decided in the record's own words, when it happened, who the record explicitly names as decider or approver, the options weighed, and whether anything since has revisited or reversed it.

The value of this skill is rigor: separating a recorded decision from a proposal or casual talk, taking the decider strictly from an explicit approver/decider field or Confluence approval history, dating when the status or decision wording actually changed via version history and Jira changelogs, keeping chains of related decisions distinct rather than merging them, and stating plainly when no record exists.

Load the `teamwork-graph-context` skill first and follow it for direct v2 tool usage, schema verification, source labeling, sensitive-content filtering, and conversational delivery. Its notes on **Confluence content lost in Markdown** (re-reading HTML when `lostFeatures` drops panels or date lozenges) and **HTML version diffs** are critical here.

## What this skill will and won't do

- **It reports strictly what the records say.** State the decision, reasons, and options only as recorded, quoted or closely paraphrased, with a link. Never fill gaps with guesses and never quote a decision from a search snippet alone (read the actual record).
- **It never infers who decided.** A decider comes ONLY from a Confluence approval record (`getConfluenceApproval`), an Approver / Decider / Accountable field, a register's approvers column, or explicit text stating who makes the final call. Never infer a decider from the page author/owner, the editor who flipped a status, the Jira assignee/reporter, or the person who moved a Jira workflow status. If no record names one, say **"No decider recorded"**.
- **It does not judge the decision.** Offer no opinion on whether it was right and no recommendation to reopen it.
- **Sensitive decisions stay out.** Never trace decisions about people (hiring, levels, reorgs, compensation, performance) or anything covered by "Sensitive content" in `teamwork-graph-context`. Explain that this skill does not cover that topic and stop.

## Sensitive content for decisions

In addition to `teamwork-graph-context`:
- Leave out private messages, group messages, and exec/board-only channels (`leaders`, `leads`, `lt`, `elt`, `slt`, `exec`). Do not read, quote, or count them; add only "Some results were not used" to Sources and limitations if any were dropped.
- Leadership-facing DACIs or review pages that are not marked restricted/confidential and do not contain sensitive personal/legal/HR content are usable decision records.
- Strip customer revenue, deal sizes, headcount, or named customer staff from quoted comments/notes.
- Strip `(Deactivated)` suffixes from account display names; describe rejected options by what they do, never by who they affect.

## Tool Access & Coverage

- **Needed:** Confluence and/or Jira (`getAccessibleAtlassianResources`, `getJiraCurrentUser`, `search`, `searchConfluence`, `getConfluenceContent`, `getConfluenceApproval`, `listConfluenceContentVersions`, `getConfluenceContentVersion`, `diffConfluenceContentVersions`, Confluence comment retrieval (use `searchConfluence` with `type = comment AND container = <id>` when a dedicated comments tool is absent; report its coverage limits), `searchJiraIssuesUsingJql`, `getJiraIssue`, `listJiraIssueComments`, `listJiraIssueRemoteIssueLinks`, `listJiraIssueChangelogs`, `getJiraUser`). Call `getAccessibleAtlassianResources` once for `cloudId` and the site URL, then call Confluence and Jira tools directly (do not block on a `products` field).
- **Unavailable on this connector:** Atlassian Projects (Atlas) highlights/updates, Atlassian Goals highlights/updates, Loom meeting recordings, and Teamwork Graph links are **not** exposed on this Atlassian connector. Do not attempt to call tools for them; state transparently in Sources and limitations that Projects, Goals, and Loom recordings were not checked.
- **Optional standalone session connectors:** If the user's session exposes standalone Slack/Teams or Google Drive connectors, you may optionally search public channels or Drive decision docs read-only (never DMs or exec-only channels), labelling them clearly by app.
- **Direct calls & live schema check:** Call every tool directly by name. If a tool is not in your tool list, it is not available on this connector; say so and use the closest available tool. Always inspect live tool schemas before passing parameters — especially:
  - `search`: Use cloudId and query, with optional targetApp and limit; do not pass mode.
  - `getConfluenceContent`: verify `content_id` vs `contentId`, `content_format`, `detail`.
  - `getConfluenceApproval`, `listConfluenceContentVersions`, `getConfluenceContentVersion`, `diffConfluenceContentVersions`, Confluence comment retrieval (use `searchConfluence` with `type = comment AND container = <id>` when a dedicated comments tool is absent; report its coverage limits): verify `contentId` vs `content_id` and `content_format`.
  - `getJiraIssue`: verify whether `view` is supported or pass explicit `fields` (e.g., `["*all"]` or `["summary", "description", "status", "resolution", "resolutiondate", "labels", "created", "updated"]`) to check custom Approver/Decider/Decision date fields without guessing parameter names.

## Budget

Unless the user asks for more, cap Rovo searches at five, CQL at two, JQL at three, Confluence body reads at ten plus three HTML re-reads, and Jira detail/comment/remote-link reads at three issues. Inspect approvals for three pages; date changes on two records with at most five version probes each. Use up to three Jira changelogs, three Confluence comment searches and six account-name lookups. Read [the detailed budgets and evidence types](references/decision-evidence.md) for per-step limits. Report every applied cap and any unresolved version range.

## Step 1: Pin down the question

1. Call `getAccessibleAtlassianResources` once for `cloudId` and the site base URL, and `getJiraCurrentUser` for timezone.
2. Restate the question as **one decision subject** in a few words, and note:
   - **Subject terms:** 2–3 short distinctive title terms (plus any **scope term** when asking "is X in scope for Y?").
   - **Question focus:** why (lead with reasons), who (lead with decider), what / "did we decide" (lead with outcome), or still current (lead with revisits).
   - Any **date hint** given by the user.
3. If the user supplied a Confluence URL or Jira key, treat it as the first candidate record, but still run Step 2 because decisions are frequently duplicated or superseded across pages/tickets.
4. If the question is too broad ("why did we pick our strategy?"), ask which specific decision using 2–3 hits from a quick search. If it is about a sensitive people/HR/legal topic, stop.

## Step 2: Find the records

Send these in parallel (adapting `search` arguments to its live schema):

- **`search`** x3:
  1. `"<subject terms> decision"`
  2. `"<subject terms> DACI proposal"`
  3. `"<subject terms>"` (records are often titled by subject or as a question without the word "decision")
- **`searchConfluence`** (CQL) x2:
  1. `type in (page, database) AND (title ~ "register" OR title ~ "decisions" OR title ~ "log") AND text ~ "\"<term 1>\""` (for decision registers whose title does not contain the subject)
  2. `type in (page, blogpost) AND (label in ("decision", "decisions", "decision-log") OR title ~ "DACI" OR title ~ "decision") AND text ~ "\"<term 1>\"" ORDER BY lastmodified DESC` (`limit: 25`)
- **`searchJiraIssuesUsingJql`** (Jira decision route):
  1. `issuetype = Decision AND (text ~ "\"<term 1>\"" OR text ~ "\"<term 2>\"") ORDER BY updated DESC`, `fields: ["summary", "status", "issuetype", "labels", "created", "resolutiondate", "project"]`, `maxResults: 25`.
  2. If that errors (type does not exist) or returns nothing: `(text ~ "\"<term 1>\"" OR text ~ "\"<term 2>\"") AND (summary ~ "decision" OR summary ~ "decide" OR summary ~ "DACI" OR labels in (decision, decisions, decision-product, decision-architecture)) ORDER BY updated DESC` (add `AND text ~ "\"<scope term>\""` when a scope term applies).

Drop sensitive results first. Classify remaining candidates into shapes: **Decision page**, **DACI or proposal**, **Decision register**, **Meeting decisions list**, **Jira decision**, or **Discussion**. Keep up to **6** top records for Step 3 (decision pages -> Jira decisions & meeting decisions lists -> DACIs/proposals -> registers, newest first within each), reserving 4 read slots for records linked from inside Step 3. If nothing qualifies, jump to Step 5 ("No decision record found").

## Step 3: Read the records

1. **Confluence records:** Call `getConfluenceContent` (`content_format="markdown"`, `detail="full"`, checking live schema for `content_id` vs `contentId`) in parallel.
2. **HTML re-read when Markdown loses content:** Re-read with `content_format="html"` (up to 3 re-reads, main candidates first) whenever `lostFeatures` lists `time`, `ac:structured-macro`, or `ac:adf-extension`, when a Decision/Outcome heading is empty, or when a search snippet quotes text missing from Markdown. Take register dates from `<time datetime="...">`.
3. **Live docs:** Take edit dates only from `listConfluenceContentVersions` (Step 4), never from top-level read metadata.
4. **Jira decisions:** Read up to 3 with `getJiraIssue` (inspect live schema first; request custom fields via `fields: ["*all"]` or `view` if supported, checking custom fields named Approver, Decider, Accountable, Decision date, or DACI), plus `listJiraIssueComments` and `listJiraIssueRemoteIssueLinks` directly.
5. **Follow links:** Read linked decision pages/DACIs ("Supersedes", "See DACI", "Outcome", remote links, register row links) within the 10-read cap. If a record cites an earlier unlinked decision, spend 1 JQL or `search` call to locate it.
6. **Extract strictly what each record states:**
   - **Decision text:** exact wording when short (<= ~40 words) with its heading/panel/field name. If Ask/Recommendation and Decision/Outcome differ, Decision/Outcome wins and the difference goes in **Not in the records**. If the body leaves Outcome empty but a comment states it, quote the comment as `"[name] commented on [date]"` (not as decider) and flag the empty body in **Not in the records**.
   - **Status:** in-body decision status first -> decision panel/heading -> Confluence page status (`contentState`) or Jira status. If page status disagrees with body status, report both and note the contradiction in **Not in the records**.
   - **Decider:** only from an explicit Approver / Decider / Accountable field, register approvers column, or explicit sentence naming who makes the final call (note which source named them). Driver, author, owner, assignee, reporter, and Informed are **not** deciders.
   - **Decision date:** from an explicit field/register date column/meeting date if present; otherwise establish in Step 4.
   - **Reasons & Options:** strictly from Rationale/Context/Why and Options/Alternatives sections.
   - **Links to other decisions:** supersedes, revisits, replaces, or precursor links.
7. **Decision registers:** Use only rows matching the decision subject; each row is its own record. Note missing date or approver columns in **Not in the records**.

## Step 4: Date the changes & verify approvals

Pick a provisional **main record** (the decided record with the newest decision event, preferring one with an explicit decision status and named decider; if none is decided, the newest decision page, Jira decision, or DACI). Confirm it after Step 4.

A page's last-modified date is **not** the decision date. Run Step 4 on the main record and up to one additional record (plus any Revisit record lacking an explicit date):

1. **Confluence approvals (classic pages only):** Call `getConfluenceApproval` directly for up to 3 Confluence decision pages/DACIs (skip for live docs and note `"Not run: approvals do not apply to live docs"` in Sources and limitations). Check the live schema for `contentId`, `contentStatus`, and `expand`. An approval record with a decision and reviewer is the strongest evidence of who approved and when.
2. **Confluence version history:** Call `listConfluenceContentVersions` directly (`limit: 50`, ignoring `"Automatic conversion"` versions). Use up to **5** `getConfluenceContentVersion` probes or `diffConfluenceContentVersions` calls per record with `content_format="html"` (Markdown diffs can miss panels/dates):
   - Start near a date hint if one exists; otherwise bisect between v1 and latest.
   - Pin when status became Approved/Decided and when decision wording was added or changed. If a meeting decisions list changed wording after v1, date the wording by the version range rather than crediting the meeting date, and flag the post-meeting edit in **Not in the records**.
   - If the 5-call cap runs out, report the bounded version range (e.g., `"between v1 (Mar 2) and v9 (Apr 14)"`).
   - Phrase edits carefully: `"marked Approved on [date], approver named as [name]"` or `"decision text added on [date]"`. If wording changed *after* approval, show both dates and add `"No record shows the [date] wording was approved"` under **Not in the records**. Never name an editor as the decider.
   - Note recommendation flips in the timeline (`"Recommendation changed from A to B between v1 and v11"`).
3. **Jira changelogs:** For Jira decision issues, call `listJiraIssueChangelogs` directly (`maxResults: 1` to get `total`, then read the last 20 entries from `startAt: max(0, total - 20)`) to date when status moved to Decision Made / Approved / Done. Never treat the person who clicked the transition as the decider.

## Step 5: Comments and revisit sweep

Send these in parallel:
1. **Confluence comments on main record(s):** Call Confluence comment retrieval (use `searchConfluence` with `type = comment AND container = <id>` when a dedicated comments tool is absent; report its coverage limits) directly (up to 3 pages) to capture authors, timestamps, and any debate or later comment saying `"we reversed this"` or `"reopening this"`. (Jira comments were already read via `listJiraIssueComments` in Step 3.)
2. **Revisit & broader discussion sweep:** Run up to 2 `search` calls (checking live schema first):
   - `"<subject terms> revisit reopen reverse"` (to catch later challenges or reversals)
   - `"<subject terms> decided decision"` (for broader discussion across indexed content)
3. **Optional standalone session connectors:** If Slack/Teams or Google Drive connectors exist in the session, you may check public channels or Drive docs read-only for announcements or revisits. A public channel announcement counts as Recorded only if it names the decider or is posted by a recorded decider; otherwise classify it as **Discussed** (`"according to [name] in Slack"`).
4. Resolve any approver/commenter account IDs lacking display names with `getJiraUser` (up to 6 calls).

## Step 6: Assess

### Status mapping
- Decided, Decision Made, Approved, Accepted, Agreed, Final, Done (on a decision) -> **Decided**
- Rejected, Declined, Won't do -> **Decided (not to proceed)**
- Proposed, Draft, In review, Pending, Open, In progress, Awaiting decision, Paused/Deferred (unless deferring was itself the decision) -> **Proposed**
- Superseded, Replaced, Revisited, Reopened -> **Decided, later revisited** (newer record holds current state)
- Cancelled, Withdrawn -> **Not decided** (list it; does not count as a decision record)

For distinctions between recorded decisions, proposals, revisits, reversals, meeting summaries and discussion, read [the decision evidence types](references/decision-evidence.md) when classifying timeline records. An AI meeting summary alone cannot establish Decided or identify a decider.

### Chains of decisions
- Same outcome, scope, and team across two records -> one decision (list secondary records under **Also recorded**, and any wording/date differences under **Not in the records**).
- Different outcome, scope, or team, or a later record replacing an earlier one -> **never merge**. Give each decision its own block (newest first); show all in the timeline. The verdict applies to the newest decision on the asked subject.

### Verdict (for the newest decision on the subject)
- **Decided:** a Recorded decision exists, with no later Revisit or Reversed item. (If a newer open proposal exists without explicitly reopening the decision, add a note without changing the verdict.)
- **Decided, later revisited:** a Recorded decision exists, and a later Revisit, Reversed, or reopening Meeting summary exists. State whether a newer decision replaced it or whether it remains reopened with no new decision recorded.
- **Proposed, not recorded as decided:** Proposed items exist, but no Recorded decision.
- **No decision record found:** only Discussed / Meeting summary items (or nothing). List the discussion and suggest writing the decision down; never claim what was decided.

### Options disposition
Mark an option **Chosen** only if the options record (or a record explicitly referencing it) identifies it as chosen. Otherwise show **Recommended** only if the record marks it so, and note if the outcome is recorded separately without an explicit link.

## Writes

None. This skill is strictly read-only. If no decision record exists, suggest in your reply that the team record the decision in Confluence or Jira, without proposing or executing writes.

## Conversational Answer Structure

Deliver the complete trace directly in Markdown:

1. **Header & Verdict:** Question restated, **Verdict**, counts (`Traced from N records and M discussions`), and a 2–3 sentence direct answer leading with what the user asked (`why`, `who`, `what`, or `still current`).
2. **Decision block(s)** (newest first; separate block per distinct decision in a chain):
   - Heading (`Newest decision`, `Earlier decision it revisits`, etc.) and recorded status
   - **Decided:** exact record wording (quoted) + Markdown link
   - **When:** date and how it is known (e.g., `"Marked Approved on Sep 15, 2026 (Confluence approval)"`, `"Between v4 and v6 (page history)"`, `"Moved to Decision Made on Oct 14, 2026 (Jira changelog)"`)
   - **Who decided:** exact recorded decider and field/source (or `"No decider recorded"`; if the user asked "who decided?", you may add `"The page was authored by [name]"` as a starting point, never as decider; qualify if wording changed after approval)
   - **Also recorded:** other records of the same decision, if any
   - Revisit/reversal warning or open-proposal note, if applicable
3. **Why (Reasons recorded):** Up to 5 bullets in the record's words with source links (or `"No record states the reasons"`).
4. **Options considered** (only if present in a record): List each option with recorded summary and `Chosen` / `Recommended` label, citing the source record.
5. **Timeline (oldest first):** Dated list showing date (or `No date`), item type (`Recorded decision`, `Proposed`, `Revisit`, `Reversed`, `Meeting summary`, `Discussed`), 1-sentence summary, and link (marking search-only discussion items as **Found by search**).
6. **Not in the records:** Explicit bullets for missing deciders, missing dates, status/body contradictions, post-approval wording edits, or unclosed earlier proposals.
7. **Sources and limitations:** Records read, HTML re-reads performed, caps reached, open version ranges, timezone used, "Some results were not used" if sensitive hits were dropped, and the explicit statement that **Atlassian Projects, Goals, Loom recordings, and Teamwork Graph links are not exposed on this connector** and were not checked.
## Optional offline report

Answer in the conversation first. When the user requests an HTML report, read [the report export instructions](references/report-export.md), load atlassian-design, and run the bundled render.py from this skill directory using its example.json and data-format reference. Preserve the same facts, verdict, condition count and coverage gaps in the report. Both design kits run offline with Python's standard library; do not install packages or download assets. Export does not authorize publication or sharing. Return static HTML when publication tools are unavailable.
