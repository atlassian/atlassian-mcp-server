# Optional report export

Load this reference only for a requested report or publication. Preserve the findings, condition counts and source gaps from the conversational answer. Run the bundled Python renderer offline with its example and data-format reference; both shared design kits and logos are included. Do not install packages or download assets. Export does not authorize publication. Follow the shared context publication reference for capability checks and consent.

## Step 8: Build the page (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in the skill folder:

```bash
python3 <this skill's folder>/render.py catchup.json catch-up-<topic>.html
```

- **The data** has the shape of `../example.json` beside the skill entrypoint (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **Rows** are `{"type", "text", "source", "when"}`: `type` is the lozenge, `source` is the smart link (or a list of them) for the source line, and `when` is the event date. A row can carry an excerpt as `quote` and `quoteFrom`.
- **Keys to know.** With no topic, leave out `topic`. The renderer counts Needs you and decisions itself. Give `counts.changes` when the changes found are more than the rows shown. Keys the example doesn't use: `summaryHeading` ("Since Oct 5" when Step 1 found the user active), `decisionNotes` and `meetingNotes` (the extra lines under an empty or partial section), and `counts.needYou` and `counts.decisions` when there are more than the rows shown.
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `hand-built.md` beside this reference.

The rules below say what the renderer builds, and what each part of the data must hold.

Every row is one sentence of about 25 words, with its source and the event date. Use absolute dates ("Oct 9"), because a window is days or weeks long. Old items still waiting say "Open since Sep 29".

### Sections, in this order

1. **Header** (not a card): eyebrow "Catch-up", then the topic's name as the page's only `h1` ("Ledger"), or "Your work" with no topic. Then one row with the meta line on the left and count lozenges on the right (they wrap below on phones).
   - Meta line: `calendar` icon with the window and its length ("Mon, Oct 6 to Fri, Oct 17 · 10 working days"), and "From your calendar" when Step 1 took it from an out-of-office event.
   - Count lozenges, each shown only when above zero: "3 need you" (warning when any is Overdue or Blocking, otherwise information), "2 decisions" (success), "18 changes" (neutral).
2. **While you were away** (icon `ai-sparkle` in `--ds-icon-discovery`), or **Since [start]** when Step 1 found the user active on most of the window's working days: the summary at 24px line height. Underneath, in small subtlest text, the apps actually used: "Generated from Jira, Confluence, Projects, Slack and Google Calendar. Check it before acting on it."
3. **Needs you** (icon `flag`): rows ranked as Step 7 says. If there's nothing, show "Nothing is waiting on you." in subtlest text.
4. **Decided while you were away** (icon `decision`): one row per decision. The sentence says what was decided and who decided it ("Amara Lindqvist decided to keep the old search index until Nov 14"), and the source line has the smart link and date. If there are none, show "No decisions you missed in this window.", add "[N] from meetings you attended aren't repeated." when the seen rule left some out, and add in subtlest text that decisions made only in calls or direct messages can't be seen.
5. **What changed** (icon `changes`): a small subheading per group (the area's name as a smart link, or plain text for "Other" and for a group of the user's own items, such as "Your Loom videos"), then its rows. Items found by search carry the "Found by search" chip as `teamwork-graph-context` describes. If there's nothing, show "No changes to this work between [start] and [end]."
6. **Meetings you missed** (icon `video`): one row per meeting: a fixed-width date column ("Oct 8"), then the title in medium weight, a meta line (attendee count, organiser, "weekly" when recurring), and the one line from Step 5 with its recording or notes smart link. A meeting with no notes says so in subtlest text. With none, show "No meetings you missed in this window." and, when attended meetings were left out, add "[N] meetings you attended aren't shown." With the Teamwork Graph fallback, end the card with its limitation line.
7. **Coming up** (icon `clock`): up to 5 rows for the next 5 working days, with the date, the title and why it matters ("Ledger review, Tue, Oct 22: the plan changed on Oct 14"). Leave it out when there's nothing.
8. **Sources footer** (not a card, small text), as `teamwork-graph-context` describes, plus:
   - the window and timezone, and the dating rule in one line: "Items are dated by when they happened, not when they were last touched."
   - how many items were left out for being outside the window, for being after an explicit end date, and because the user had already seen them (with the active-days count from Step 1 when it applied)
   - every cap that applied, and the counts left out of each section
   - search warnings ("Some search sources could not be queried") once, with how many searches returned them, not once per search
   - what the third-party pass did: "Searched Slack, Google Drive and GitHub through Teamwork Graph (3 queries, 11 results in the window)", "No results from [app]" or "Not run: [reason]". List the query terms, and say whether a Slack ID was used, without the ID.
   - gaps that affected the page: recurring meetings missing without the calendar connector, full threads not read, no notifications inbox, partial pull request results
   - when the page was prepared, as a relative time plus the absolute date, time and timezone

### Copy

- Name people. When a fact came from chat, email or a call rather than a record, say so ("Marco said in Slack that…", "agreed in the Oct 8 sync").
- No em dashes or en dashes in your own copy. Ranges read "Oct 6 to Oct 17". Sentence case everywhere.

### Mockups and sample data

Follow the mockup rules in `teamwork-graph-context`.

## When live

Static only. A catch-up covers a fixed window and is read once, on the way back in. For what changes after that, the user runs `/catch-up` again with a new window.

## Step 9: Deliver the requested report

- Hand over the requested HTML report. If Atlassian Artifacts availability is confirmed as described in `teamwork-graph-context`, offer a private, read-only copy named "Catch-up: [topic], [start] to [end]" ("Catch-up: Ledger, Oct 6 to Oct 17"), or "Catch-up: your work, ..." with no topic. Put the window and counts in the description. Publish only if requested; report export alone does not authorise it. Create a Confluence page instead only if the user asks.
- The report is personal: Needs you is about the user. Do not offer to share it. If the user asks, share only with the people they name.
- Keep the answer's evidence, dates and limitations in the report. Report generation does not replace a check that was not run.
