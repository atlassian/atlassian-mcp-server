# Optional report export

Load this reference only for a requested report or publication. Preserve the findings, condition counts and source gaps from the conversational answer. Run the bundled Python renderer offline with its example and data-format reference; both shared design kits and logos are included. Do not install packages or download assets. Export does not authorize publication. Follow the shared context publication reference for capability checks and consent.

## Step 9: Build the page (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in the skill folder:

```bash
python3 <this skill's folder>/render.py readiness.json release-<name>.html
```

- **The data** has the shape of `../example.json` beside the skill entrypoint (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **Conditions are explicit.** Supply `conditions` as the same deduplicated list used for the verdict, or `[]` when none remain. Each entry has `id`, `areas` (the affected area names), `type`, `text` and its source links, using the shared row format. One entry represents one underlying condition; do not replace several with a grouped count. The renderer displays the entries and their count, while the skill supplies the assessed verdict. For a Not used area, put its positive applicability reason in the area's `text` and cite its evidence, or state that the user explicitly confirmed it.
- **Optional keys** left out of the example: `meta.datePassed: true` (adds "passed" to the release date), `noBlockers` (the line when there are no blockers, "No blockers recorded." by default) and `sourceLabel` on a blocker (the words before its source, "Evidence: " by default).
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `hand-built.md` beside this reference.

### Sections, in this order

1. **Header** (not a card): eyebrow "Release readiness", the version name as the page's only `h1`, then a meta line: the Jira project, the release date ("Nov 14, 2026", with "passed" when it has), the project's target date when it differs (`meta.projectTarget`), and the driver (`person` icon) as the record names them. Right of the `h1`, the verdict lozenge (Ready success, Ready with conditions warning, Not ready danger, Can't assess neutral). At the right end of the meta line, a "2 blockers" danger lozenge when there are any.
2. **Verdict** (icon `sparkle` in `--ds-icon-discovery`): four metric tiles (Open items "14 of 41", Blockers, Open pull requests, Open checks), then two or three sentences: the verdict and what decided it in plain words ("Not ready: 1 blocker is open, and 23 items haven't started"), not the rule's wording, then the one or two findings that matter most, and how much is open with how long until the release date as recorded. Name items and teams. Use only facts from Steps 1 to 8. Underneath, in small subtlest text, the apps actually used: "Generated from Jira, Projects, Bitbucket, Spinnaker and Slack. Check it before acting on it."
3. **Blockers** (icon `flag`): one row per Blocker, ranked: the lozenge, one sentence on what's blocked and why ("Waiting on a security review; the review ticket was opened Aug 14"), "Waiting:" with the in-scope items that wait on it, and the evidence smart links. Items from chat carry their source label. "No blockers recorded" when there are none.
4. **Readiness by area** (icon `check`): five rows (Work, Code, Testing, Dependencies, Rollout), each with its state lozenge (Ready success, Conditions warning, Not ready danger, Not checked neutral, Not used neutral), one sentence with the numbers or applicability reason behind it, and up to 3 evidence links. A Not used row identifies the confirming record or user statement.
5. **Outstanding conditions** (icon `info`): the count in the heading, then one row per condition with its type, explanation, affected areas and source links. Show "No outstanding conditions on the evidence checked." for an empty list. This is the same list counted in the verdict, including when another rule already makes the verdict Not ready.
6. **Other findings** (icon `info`): the rest of the findings, ranked, one row each with its type lozenge, one sentence and the source. Findings may group checks for readability; the conditions list still contains each underlying check separately.
7. **Open work** (icon `task`): the Step 6 rows: the status lozenge (Blocked danger, In review information, In progress neutral, To do neutral), the item as a smart link with its key, a "Testing" or "Rollout" tag for release checks (with "Grouped by title" in small subtlest text when that's how it was tagged), the assignee and the due date. Then the count line with its JQL link, and "Done: 36 (2 descoped)".
8. **Decisions needed** (icon `decision`): a numbered list, each decision in medium weight with "Suggested · Holder: [name], [role from the record]" or "Suggested · No owner recorded" underneath, and the record that names the holder.
9. **Sources footer** (not a card, small text), as `teamwork-graph-context` describes, plus: how the scope was found (fix version, epics' children, and the graph count if it differed), every cap that applied ("Checked pull requests for 8 of 21 open items", "Deployments checked for 3 items"), unreadable items and sites, what the third-party pass searched and the 14-day window, and "Not run: [reason]" for any check skipped.

### Copy

- Plain sentences, sentence case, no em dashes or en dashes in your own copy. Item titles are kept as written.
- Say "the records show", not "the team has", for anything a record implies.

### Mockups and sample data

Follow the mockup rules in `teamwork-graph-context`. Set `"mockup": true` in the data file to add the note at the top.

## When live

Static only for now. The blockers, testing evidence and decisions depend on comments, pull request descriptions and search, which need the sensitive-content judgement page code can't make. A future live version could re-read the open items' statuses (`searchJiraIssuesUsingJql` with the scope's `key in (…)`) and the version's approvers (`getJiraProjectVersions`) from a Refresh button, flag rows "Changed since the report" without rewriting the verdict, and offer the related work write with a confirm click. To refresh today, run the skill again. Export or republish only if the user requests it; when updating an existing artifact, use its same `id`.

## Step 10: Deliver the requested report

- Hand over the requested HTML report, preserving the verdict, evidence and coverage limitations from the answer.
- If Atlassian Artifacts availability is confirmed as described in `teamwork-graph-context`, offer a private, read-only copy named "Release readiness: [version]" ("Release readiness: Ledger 2.4"). Put the verdict and counts in the description. Publish only if requested; report export alone does not authorise publication.
- After an approved publication, offer to share it with the release's driver and approvers as the records name them, and share only on request.
