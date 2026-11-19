# Optional report export

Run commands from this skill directory, not from references/. Local paths in command examples are relative to the skill directory. Keep the same answer, evidence gaps and verdict in the report.

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
