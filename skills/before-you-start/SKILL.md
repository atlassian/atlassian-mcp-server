---
name: "before-you-start"
description: "Before starting an idea, plan or project, find who in the organisation is already doing, or has done, something similar, using Teamwork Graph across Projects, Jira, Confluence and connected tools. Answers in the conversation first with up to 4 efforts: each one's recorded owner, linked evidence kept apart from search findings, overlap class and recommended move (Talk, Join, Differentiate or Reuse) with its reason. Offers the existing HTML report on request and publication only when Atlassian Artifacts is available and requested. Use for whether anyone is already working on something, whether it has been tried, who else is building it, duplication checks, or /before-you-start. For who to ask, use whos-the-expert. For dependencies, use dependency-map."
---

# Before you start

Give someone an answer in the conversation that they can read in two minutes before committing time to an idea: which other efforts in the organisation already do, or did, something like it, who owns each one, how close each is, and what to do about it. It's for the person about to start, so they can talk to the right people first, join work that's already moving, draw a line between their work and someone else's, or reuse what was built.

Nothing in Projects, Jira or Confluence links an effort to the other efforts like it. Two teams can build the same thing under different names for months, and a project cancelled last quarter leaves no trace in the next team's plan. The value of this skill is the judgement a project directory or a search results page can't make: it finds efforts named differently from the idea, reads what each one actually does rather than what it's called, sorts them into a fixed set of overlap classes, and turns each into one move with an owner to contact.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. Its "Searching" and "Sensitive content" sections matter most here. This file adds what's specific to finding similar efforts.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## What this skill will and won't do

- **It answers "is anyone already doing this?"** The input is always an idea, a plan or a project. People appear only as the owners and contributors of an effort, as its records name them.
- **It never judges an effort or its people.** Classes say how close an effort is to the idea, not whether it's good. Don't say an effort failed, stalled or was abandoned unless a person wrote that in its record. Never rank or describe owners by seniority.
- **It leaves out the user's own work.** The user is never shown as an effort's owner, and the user's own items are dropped (see Step 3).
- **Who's asking doesn't change the card.** Call `atlassianUserInfo` once, only to recognise the user's own work. Make no manager or reporting-line lookups: don't call `getPeopleInfo` with `manager` or `directReports`, and don't use `getWorkPortfolio` or `getCollaborators`, which describe people rather than an idea.
- **It doesn't decide for the user.** The move is a recommendation from the records, labelled "Suggested". The user decides whether to start.

## Tool access and coverage

Load `teamwork-graph-context` first. Call tools directly when exposed. If a needed operation is not exposed and discovery is available, discover it and use the matching runner with its returned schema. Skip an operation only after checking the session's capabilities. Missing `products` metadata means unknown availability, not no access.

Use the full workflow when its tools are available. With Jira, Confluence and Rovo Search only, gather those records and use the fallbacks below. Keep unavailable, permission denied, successful empty results and checks not run distinct. List the impact of each gap in Sources and limitations. A Jira project is not an Atlassian Project.

## Frame the idea and search

Read [the discovery procedures](references/discovery.md) for query budgets, relevance filters, clustering and owner resolution before searching. Frame the intended outcome, users, system and distinctive terms. Ask for a missing detail only when it changes the search. Resolve the current site and user once. Exclude the user's own previously generated artifacts only when artifact listing is available; absence of that tool does not block research.

1. Search for existing efforts across Projects, Confluence, Jira and connected sources. Use the available graph/project operations and the bounded sweep and echo pass in the reference. With Jira/Confluence/Search only, use JQL for structured Jira constraints, CQL for Confluence constraints and Rovo Search for language-based discovery. `search` takes no `mode` parameter.
2. Filter for the actual outcome, audience and system, rather than a shared buzzword. Follow the reference's false-positive rules and cluster records for the same effort. Reuse source records and stable IDs; do not merge distinct initiatives solely because their names resemble one another.
3. Use terms, teams and system names found in the best matches for one echo pass. Stop when the next search would not change the top finding. Do not keep broadening a search to fill a quota.
4. Confirm up to four top efforts with product records. Use `getProject` and filtered graph reads when available. Otherwise read linked Jira issues and full Confluence records, retaining Found by search labels for inferred relationships. Use HTML if markdown lost tables or panels. Check status, recency, outcome, scope and recorded owner. Show inactive, paused, cancelled and completed work using its actual state; it can still contain reusable context.
5. Bring in people only after confirming the records. A recorded project/decision owner takes precedence over graph involvement. A document author or active contributor is a contact, not automatically an owner. Follow inactive-owner fallbacks and at most two batches of ten `getPeopleInfo` lookups in the reference; do not request managers. If people tools are unavailable, use recorded display names or bounded Jira account lookup and disclose unresolved contacts. Never invent an owner from activity.

## Assess

Read [the assessment rules](references/assessment.md) before ranking and recommending. Compare the proposed effort with each match on outcome, scope, current state and evidence of overlap. Distinguish an active effort to join, a completed or stopped effort to learn from, adjacent work to coordinate with, and weak or uncertain matches. A matching title alone proves none of these.

Keep the reference's classification, ranking and evidence requirements. Label inferred overlap as Suggested or Found by search. A failed or unavailable search is a coverage gap; a successful empty search means no matches in that scope. Neither proves nobody has done the work.

## Answer

- Lead with Step 7's headline and verdict, and restate the idea in one sentence.
- Show up to 4 efforts checked in Step 5, in the established ranking. For each, retain what its records say it does, its overlap class and main difference, recorded status, owner label and contributors, and the suggested move with its evidence-based reason. Keep Linked evidence and Found by search evidence separate, with ordinary Markdown links.
- Include the suggested first message when there is a top effort, labelled Suggested. Keep it as draft text; do not send it. Include names that matched but could not be checked, if any.
- In Sources and limitations, retain the searched apps and terms, echo-pass coverage, candidate and result counts, own-item exclusions, caps and gaps required by the report's sources footer. For Nothing close found, say which words were searched and suggest one other name the work might go by; never claim that no similar effort exists.


## Writes

None. The card suggests a move and a first message, but the user acts on it. Don't message, follow, join, link, comment or create anything for the user.

## Optional report

Answer in the conversation first. For a requested HTML report, read [the report export instructions](references/report-export.md) and run this skill's existing `render.py` with the bundled design assets. Preserve the same findings and limitations. Offer publication only after confirming the required tools and permission; a static export remains available when publication is unavailable.
