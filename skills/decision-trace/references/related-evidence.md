# related evidence

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

## Step 5: Expand from the main record

The **main record** is the record with a decided status whose decision event (the date from Step 3 or Step 4, not the last edit) is newest. When two records state the same decision, prefer the one with a decision status field and a named decider. If none is decided, it's the newest decision page, Jira decision or DACI, in that order.

1. Call `getGraphContext` on the main record with `detailLevel: summary`. If it shows related content beyond the comments already read, call it once more with `full`, filtered with `relationshipTypes` to those relationships. If the newest decision record isn't the main record and hasn't been walked, and the answer still lacks something it could hold (a decider, a revisit), run one more summary call on it.
2. Read Confluence comments with one `listConfluenceComments` call on the page (it has authors and dates), and other comments in one `getGraphObject` batch. Read related pages with `getConfluenceContent`, inside Step 3's cap: `getGraphObject` returns Confluence pages as raw ADF.
3. **Related-content edges reach back about 90 days.** A precursor older than that won't appear here: Step 2's search and the links in records are what find it. Say in the footer that the walk covered the last 90 days of related content.
4. **Projects and Goals,** if their tools are available. If a record or the search results name a project or goal, read it directly. Otherwise run up to 2 `searchProjects` or `searchGoals` calls with the subject terms and `limit: 10`. `getProject` and `getGoal` take `identifier` (a key or ARI), `cloudId`, `include`, `highlightType` and `limits`. Read up to 3 that a record links or names, or whose name matches the decision's scope, with `getProject` or `getGoal`: `include: ["highlights", "updates"]`, `highlightType: DECISION`, `limits: {highlights: 20, updates: 10}`. A decision highlight is a record. An update that says a decision was made ("we decided to…") or is pending ("decision in review") is evidence for the timeline, dated by its `creationDate`. When none has a decision highlight, the footer says "No decision highlights recorded".
5. **Comments** on the main record can hold the real debate, or a later "we've reversed this". Keep comments that say something was decided, questioned or reopened, dated by their created time. Graph comment objects can come back without one: date Confluence comments with one `listConfluenceComments` call on the page instead, and read Jira comment bodies and dates with `listJiraIssueComments` (up to two issue comment reads across Steps 3 and 5). Reuse a previous read of the same issue.

## Step 6: Sweep for discussion

Send these together:

- `search` (`targetApp: THIRD_PARTY`, `limit: 20`) with the subject terms plus "decided" or "decision", for Slack, Teams and Google Drive.
- `search` (`targetApp: ALL`, `limit: 20`) with the subject terms and a word for change ("revisit", "reopen", "reverse"), to catch revisits.
- If Loom is on the site, up to 2 `listLoomObjects` calls with `scope: ALL`, `artifactTypes: ["MEETING_RECORDING"]`, `limit: 25` and `responseFields: ["items.title", "items.createdAt", "items.url", "hasNextPage", "nextOffset"]`, titles only. A page can come back empty with `hasNextPage: true`: one with `createdAtRange` 7 days either side of the main record's decision date (the date its status became decided, when that differs from when the text was written), and one for the last 30 days, skipped when the decision date is inside those 30 days. A third page, if one is needed, goes to the decision-date window first. A list returns about 15 items, newest first, so a longer window misses its start. If a list has `hasNextPage: true` and hasn't reached its window's start, read the next page by setting `createdAtRange.to` to the oldest `createdAt` returned, not with `nextOffset`, which can skip items (see "Loom lists come back short" in `teamwork-graph-context`). Check titles first: drop one-to-ones and anything "Sensitive content" covers by title, so their summaries are never fetched. Then keep recordings whose title could be about the subject, or whose date is within a day of a record's date. Say in the footer which dates the lists covered, and that they show only recordings the user can see.

Then:

- **Drop excluded results first,** as "Sensitive content for decisions" says, and count nothing about them.
- **Meeting summaries:** read up to 10 kept recordings with one `getLoomObjectsContent` batch and no `expand`: each result's `description` is its AI summary. Keep those whose summary names the subject. Add `expand: ["transcript"]` (up to 5) only for a recording whose summary mentions the decision but not what it was. `agentBrief` usually comes back `ABSENT`.
- A public channel message that **announces** a decision ("We've decided to…", "Approved:") counts as a Recorded decision only when it names who decided or is posted by someone a record names as the decider. Otherwise it's Discussed, with the poster named as "according to [name] in Slack".
- Follow a decision page or Jira link inside a kept result: read it in Step 3 if a slot is free.
