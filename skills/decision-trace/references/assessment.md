# assessment

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

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
