# assessment

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

## Step 7: Assess

### Needs you

One type per row:
- **Overdue** (danger): work or a task assigned to the user, past its due date.
- **Due soon** (warning): due in the next 5 working days.
- **Blocking** (danger): open work the user owns that blocks someone else's, confirmed with `getJiraIssue` (`view: evidence`).
- **Ask** (information): a question or request for the user, unanswered.
- **Review** (information): an open review request.
- **Assigned** (neutral): newly assigned inside the window, not due soon.
- **Action** (neutral): an action item for the user from a meeting in the window, attended or not, not visibly done.

Leave out asks Step 2 found answered. Drop asks whose moment has passed (a review for a merged pull request, a link wanted for a session that's over). Rank by when it bites: Overdue, then Due soon by date, then Blocking, then Asks and Reviews tied to something dated (a meeting in Coming up, a deck or doc in use, a due date), then other Asks and Reviews oldest first, then Assigned, then Action. Keep up to 8, and count the rest in the footer.

### Decided

One type: **Decided** (success). Rank decisions that change the user's own work or dates first, then scope and approach decisions for the topic, then the rest, newest first within each. Keep up to 6. A decision the user is asked to act on also gets a Needs you row, which links to it.

### What changed

One type per row:
- **Blocked** (danger): moved to Blocked, flagged, or a new blocking link.
- **Off track** (danger) and **At risk** (warning): a project or goal status change.
- **Date moved** (warning): a target or due date moved, with from and to.
- **Scope** (neutral): work added to or removed from the scope, closed as Won't do, or a dependency added.
- **Shipped** (success): work resolved as Done, a pull request merged, a release.
- **New** (information): a page, doc, epic or project created inside the window.
- **Update** (neutral): a notable edit, project update or discussion.

**Relevance.** With a topic, keep a change only if it's in the scope set (Confirmed) or names a distinctive term (Found by search). With no topic, keep it only if it touches work the user owns, is assigned, wrote or is named on. Drop housekeeping: formatting edits, score nudges, attendee tweaks, label changes, and bulk resyncs (many items changed by one actor within a few minutes).

**Ranking.** Blocked, Off track, At risk, Date moved, Scope, Shipped, New, Update. Within a type, changes to the anchor itself come first, then newest first. Don't rank by priority field, number of edits or how long a thread is.

**Grouping.** Group rows by area: the epic or project for Jira and Projects, the space or page tree for Confluence, the channel or folder for third-party items. Show up to 4 groups and 12 rows in total, the group with the highest-ranked row first. Fold groups with a single row into a last group, "Other", whose heading isn't a link and which can mix apps, so a lone Slack or Drive change isn't dropped by the cap. If any third-party change survived ranking, at least one shows. Fold Shipped rows when a group has more than 3: one row, "8 work items done, including ATLAS-101 and ATLAS-104", linking the JQL search. Count everything left out in the footer.

### The summary

"While you were away": two or three sentences, at most 60 words. The first names the one thing to do first and why. The second names the most important decision or change. The third gives the shape ("41 work items moved and 2 projects changed status across Jira, Confluence and Slack"). Use only facts from Steps 2 to 5. Never mention why the user was away.

### Stop gathering

Stop when each pass has run once: needs you (Step 2), decisions (Step 3), changes from each source in Step 4, including the third-party search, and meetings (Step 5). A pass that failed twice is "Not run" in the footer, with the reason. One extra call is fine if it could change the top Needs you item or the top decision.
