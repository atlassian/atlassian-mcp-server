---
name: "assess-release"
description: "Assess whether a release, fix version or milestone is ready to ship using Teamwork Graph across Jira, Projects, Confluence, connected code, deployments and chat. Answers in the conversation first with a rule-based verdict (Ready, Ready with conditions or Not ready), linked blockers, readiness by area, open work, decisions and recorded owners, and evidence gaps. Offers the existing HTML report on request and publication only when Atlassian Artifacts is available and requested. Use for release readiness, a go or no-go view, or /assess-release. For dependencies alone, use dependency-map. For goal health, use status-check. For shipped changes, use release-notes."
---

# Assess release

Give a release driver, engineering manager or team lead an answer in the conversation that they can read in three minutes before a go or no-go call: whether the release is ready to ship, what's stopping it, what each area (work, code, testing, dependencies, rollout) shows, what needs deciding and who holds each decision, and what couldn't be checked.

A release page in Jira counts issues by status. The value of this skill is the judgement the release page, the board and the pull request list can't make on their own: which open items actually stop the ship, whether "done" work has merged and deployed code behind it, whether the testing and rollout work exists and is finished, and which dependencies on other teams are still open, all checked against linked records rather than titles.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. Load its `references/graph-context.md` for graph enrichments when those tools are available. This file adds what's specific to a release. An optional HTML report is built by `render.py` in this skill folder (see `references/report-export.md`), which applies the `atlassian-design` skill for you: load that skill only if the script can't run.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## What this skill will and won't do

- **It assesses one release now.** The verdict says whether the release could ship today on the evidence in its records. It never forecasts a ship date, a completion date or a velocity. The release date appears only as a record states it, with its moves if a record shows them.
- **A blocker needs a record.** A Blocked status, a flag, an open upstream issue link whose direction was read from Jira, or a record (a comment, an update, a decision page, a message) that says the release or one of its items is blocked. Never a title ("Coordinate with the Platform team"), and never a priority field alone.
- **A decision's holder needs a record.** The release's driver or approvers, a decision page's driver or approver, or an owner a record names. Otherwise "No owner recorded". The skill suggests decisions; it never assigns anyone.
- **Gaps are results.** Pull requests that couldn't be read, keys on another site, missing test records and checks that weren't run are shown in their area and in the footer, and never counted as done.

## Tool access and coverage

Load `teamwork-graph-context` first. Call tools directly when exposed. If a needed operation is not exposed and discovery is available, discover it and use the matching runner with its returned schema. Skip an operation only after checking the session's capabilities. Missing `products` metadata means unknown availability, not no access.

Use the full workflow when its tools are available. With Jira, Confluence and Rovo Search only, gather those records and use the fallbacks below. Keep unavailable, permission denied, successful empty results and checks not run distinct. List the impact of each gap in Sources and limitations. A Jira project is not an Atlassian Project.

## Resolve and collect

Read [the collection procedures](references/collection.md) before gathering evidence. They define scope, classification, query fields and per-operation budgets. Typical runs use 35 to 50 calls; parallelize independent reads and report caps. Call an exposed operation directly; discovery is needed only for operations absent from the tool list.

1. Resolve the Jira version by URL or project and name with `getJiraProjectVersions`; for a name alone, use JQL to find its project first. Ask if it is ambiguous. A release epic or linked Atlassian Project can also anchor the assessment. If the anchor cannot be read, stop. If already released, report its recorded release date and offer release notes.
2. Read version driver, approvers and related work. Show recorded dates without forecasting. Collect version items and unversioned children of in-scope epics, up to 200 items. Exclude children in other versions. Count open unversioned siblings separately. An epic with in-scope children groups the work rather than adding another item to the total.
3. Group work by Jira status category. Done items with a cancelled, duplicate, rejected or other descoped status/resolution are Descoped, never shipped. Classify Testing and Rollout checks using the collection rules, and label grouping inferred from titles. A title can group a check; it cannot establish a blocker or a completed test.
4. Query issue links on open work. Confirm each dependency using Jira's own inward/outward phrase, not graph direction. Read upstream status with one query per project key, up to three projects. Read the reasons for up to five Blocked or flagged items with `listJiraIssueComments`; do not infer comment bodies from an issue read. Keep unreadable cross-site keys as gaps.
5. If graph and Projects tools are available, cross-check the version's work and resolve its Atlassian Project from version URLs, tracked epics, then a verified search match. Read recorded project dependencies, updates and target dates. Otherwise continue with Jira links and Confluence; record missing applicable Projects dependency coverage. `listJiraProjects` does not fill this gap.
6. Collect code evidence from linked PRs, their reviews and deployments. Use graph edges and object reads when available, then an available standalone code/deployment connector for a known gap. Read at most eight PRs and five deployment contexts. A Jira Done status, a PR URL, or a completed rollout document does not prove a merge or deployment. When these tools are unavailable, mark the evidence Not checked and keep the resulting conditions.
7. Read up to three release docs from version related work, record links and then scoped Confluence search. Use `getConfluenceContent` with `detail: "full"`; re-read HTML if markdown lost decision tables, panels or dates. Use Rovo `search` with `cloudId`, `query` and optional `targetApp`/`limit`, without a `mode` parameter. Search for recent blocker/go or no-go discussion in a 14-day window; search-only relationships stay Found by search. Collect test execution/sign-off evidence and rollout/runbook/approver states. A task to write a test plan requires the plan itself.
8. Show up to 25 open items, ordered Blocked, In review, In progress, To do. Resolve names from records; use `getPeopleInfo` when available, otherwise Jira display names and `getJiraUser` for unresolved account IDs, at most five lookups. Show no emails. Security, privacy and legal reviews expose status, recorded owner and link only.

## Assess and decide

Read [the readiness rules](references/readiness-rules.md) before assigning area states or a verdict. Assess all five areas: Work, Code, Testing, Dependencies and Rollout. Each area is Ready, Conditions, Not ready, Not checked or Not used. Not used requires a source record, release scope or explicit user confirmation of non-applicability. Missing tools or empty searches do not establish it.

Keep one deduplicated list of conditions. Include open checks, partial or unavailable applicable evidence and unreadable upstream records. Count a coverage gap once, not once per issue. Missing PR evidence, deployment evidence and Atlassian Projects dependency evidence are separate gaps when applicable. Never remove a condition because the connector cannot check it. Code readiness needs the PR coverage defined in the readiness rules, including at least two checked PRs when applicable; one checked PR cannot establish release-wide readiness.

Apply the rules in this order:

1. Can't assess: no in-scope work, or Work could not be read.
2. Not ready: a recorded blocker, any area Not ready, or more than five distinct conditions.
3. Ready: zero conditions, with every area Ready or explicitly confirmed Not used.
4. Ready with conditions: otherwise one to five conditions.

A blocker needs a record: a Blocked/flagged item, an open upstream dependency or an explicit blocker statement. Priority or a title alone does not suffice. Rank blockers by waiting in-scope items, then duration. Read changelogs for at most the top two when a blocked-since date matters. Stalled work (10 working days without update) and a passed release date are findings; alone they do not add conditions.

Suggest up to four decisions, with recorded holders only: version approver, driver, decision-page driver/approver or blocker assignee as the rules specify. Otherwise use No owner recorded. Do not invent a date, estimate or assignment.

## Answer

- Lead with the verdict, the readiness rule that decided it, the top blocker and who or what it waits on. Include the recorded release date and scope without forecasting a new date.
- Present readiness by area, named blockers with source links, the explicit outstanding-condition list and its count, open work and decisions needed with the people the records name. Retain the assessment's rules, rankings, caps and uncertainty, and distinguish missing evidence from a failed check. Explain every Not used area with the record or explicit user confirmation that establishes it.
- Before answering, check that every area has a state and the third-party pass ran. In Sources and limitations, name any that did not run and why, and retain the sampled work, deployment coverage, graph gaps and caps required by the report's sources footer.
- After the answer, offer the related-work link write if Step 5 found eligible docs, following Writes, and `/dependency-map` when the full dependency picture would help. Neither action requires an HTML export.


## Writes

One offer, after the conversational result, never without a yes: link docs found in Step 5 (a rollout plan, a test plan) to the version's related work with `manageJiraProjectVersionRelatedWork` (`action: create`, `versionId`, `url`, `title`, `category`). Show each link first as a numbered list with its category and a total ("2 related work links on Ledger 2.4"), mark the category as "Proposed", wait for a yes, create them one call each, and read the related work back to check the count. Everything else (moving items, changing the date, releasing) is the team's call: point to it, don't do it.

## Optional report

Answer in the conversation first. For a requested HTML report, read [the report export instructions](references/report-export.md) and run this skill's existing `render.py` with the bundled design assets. Preserve the same findings and limitations. Offer publication only after confirming the required tools and permission; a static export remains available when publication is unavailable.
