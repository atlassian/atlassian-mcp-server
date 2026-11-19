---
name: "assess-release"
description: "Assess whether a Jira release, fix version, or release epic is ready to ship using Jira versions, related work, JQL, issue links, changelogs, Confluence docs, and Rovo Search. Delivers a structured conversational readiness readout with a rule-based verdict (Ready, Ready with conditions, Not ready, or Can't assess), ranked blockers, readiness by area (Work, Code, Testing, Dependencies, Rollout), open work, decisions needed with recorded owners, and transparent coverage gaps (explicitly noting that pull requests, deployments, and Atlassian Projects are not checked on this connector). Use for release readiness, go/no-go reviews, or /assess-release. For full dependency mapping, use dependency-map."
---

# Assess Release

Give a release driver, engineering manager, or team lead a concise readiness readout in the conversation before a go/no-go call: whether the release is ready to ship on the evidence in Jira and Confluence, what is stopping it, what each area (Work, Code, Testing, Dependencies, Rollout) shows, what needs deciding and who holds each decision, and what could not be checked.

A release page in Jira counts issues by status. The value of this skill is the judgement the release page cannot make on its own: which open items actually stop the ship, whether testing and rollout checks and docs exist and are finished, and which upstream Jira dependencies on other projects or teams are still open — all confirmed against linked records rather than titles.

Load the `teamwork-graph-context` skill first and follow it for direct v2 tool usage, schema verification, source labeling, sensitive-content filtering, and conversational delivery. This file adds what is specific to a release.

## What this skill will and won't do

- **It assesses one release now.** The verdict says whether the release could ship today on the evidence in its Jira and Confluence records. It never forecasts a ship date, completion date, or velocity. The release date appears only as recorded.
- **A blocker needs a record.** A Blocked status, a flag, an open upstream Jira issue link whose direction was read from Jira's link wording, or a record (comment, decision page, doc) that states the release or an in-scope item is blocked. Never a title ("Coordinate with Platform"), and never a priority field alone.
- **A decision's holder needs a record.** The release's driver or approvers from Jira, a decision page's driver or approver, or an owner a record names. Otherwise "No owner recorded". The skill suggests decisions; it never assigns anyone.
- **Unavailable scopes are stated transparently.** This Atlassian connector exposes Jira, Confluence, and Rovo Search only — it does **not** expose Bitbucket/GitHub pull requests, deployments, Atlassian Projects (Atlas), Compass, or Teams. Always state clearly in the answer and in Sources and limitations that pull requests, deployments, and Atlassian Projects were not checked (unless a separate standalone code/deployment connector was explicitly used in the session).

## Tool Access & Coverage

- **Needed:** Jira (`getAccessibleAtlassianResources`, `getJiraProjectVersions`, `getJiraProjectVersionRelatedWork`, `searchJiraIssuesUsingJql`, `getJiraIssue`, `listJiraIssueComments`, `listJiraIssueChangelogs`, `getJiraUser`). Call `getAccessibleAtlassianResources` once for `cloudId` and the site base URL, then call Jira tools directly (do not block on a `products` field). If Jira tools are unavailable or return no access, say so and stop.
- **Helpful, from Atlassian:** Confluence (`searchConfluence`, `getConfluenceContent`, `getConfluenceApproval`) and Rovo `search` for specs, test plans, rollout plans, runbooks, and decision pages.
- **Unavailable on this connector:** Pull requests, deployments, Atlassian Projects (Atlas), Compass, and Teams. Do not attempt to call tools for these scopes; state in the readiness readout and Sources and limitations that they were not checked.
- **Optional standalone session connectors:** If the current session exposes a standalone GitHub/GitLab or Slack/Teams connector, you may optionally check linked PRs or blocker threads read-only and label them explicitly.
- **Direct calls & live schema check:** Call every tool directly by name. If a tool is not in your tool list, it is not available on this connector; say so and use the closest available tool. Always inspect the live tool schema before passing parameters (especially for `search`, `searchJiraIssuesUsingJql`, `getJiraIssue`, `getConfluenceContent`, and `manageJiraProjectVersionRelatedWork`).

## Budget

Keep the pass bounded: at most 10 Jira searches, two version lookups, five blocker issue/comment reads, two blocker changelogs, three Rovo searches and three key Confluence documents, unless the user asks for more. Report applied caps. Consult [the detailed collection and readiness rules](references/readiness-rules.md) for per-step budgets and check classification.

## Step 1: Resolve the release

| The user gives you | Anchor | Resolve with |
| --- | --- | --- |
| A Jira version URL (`/projects/<KEY>/versions/<id>`) | Jira Version | `getJiraProjectVersions` with `versionId` (check live schema for exact param name) |
| A project key and version name ("LEDGER 2.4") | Jira Version | `getJiraProjectVersions` with `projectIdOrKey` and name/status filter (check live schema) |
| A version name only ("Ledger 2.4") | Jira Version | `searchJiraIssuesUsingJql` with `fixVersion = "<name>"`, `fields: ["project", "fixVersions"]`, `maxResults: 5`, then `getJiraProjectVersions` in that project. If it matches versions in multiple projects, ask which one |
| A release epic | Jira Work Item | `getJiraIssue` with explicit `fields: ["summary", "status", "fixVersions", "duedate", "assignee", "parent"]`. If it carries one unreleased fix version, offer to assess that version instead |
| A milestone/goal with no Jira record | — | Explain that this skill assesses a Jira release version or release epic, and ask for the Jira version or epic key |

- When calling `getJiraProjectVersions`, request driver and approvers if the live schema supports `include: ["driver", "approvers"]`. Capture the version name, project, description, start and release dates, `released`, `overdue`, driver, and each approver with their status.
- **Already released:** Say "Released on [date]" with the release link and stop (unless the user explicitly asks to review the released items anyway).
- **Release date:** Show it as recorded. If it has passed and the version is unreleased, record a **Date passed** finding. With no release date, say "No release date set".
- Call `getJiraProjectVersionRelatedWork` directly with the version ID. Each entry has a category (e.g., Designs, Testing, Documentation) and URL — keep these for Step 4.
- Keep any Confluence or Jira URLs found in the version description for Step 4.
- If the anchor cannot be found, stop and say so. Do not guess.

## Step 2: Find the release's work

1. **The release's items:** Call `searchJiraIssuesUsingJql` with `fixVersion = <id>`, `fields: ["summary", "status", "issuetype", "priority", "assignee", "duedate", "updated", "resolution", "resolutiondate", "statuscategorychangedate", "parent", "labels", "components", "project"]`, and `maxResults: 100`. Paginate with `nextPageToken` until complete (up to 200 items, noting in Sources and limitations if more exist). Find flagged items with a separate JQL query: `fixVersion = <id> AND Flagged is not EMPTY`, `fields: ["summary", "status"]`, `maxResults: 25`.
2. **Epics' children:** A fix version often sits on epics while work lives in child items. For each epic in the result, query `parent in (<epic keys>) AND (fixVersion is EMPTY OR fixVersion = <id>)` with the same fields. Note any children assigned to other versions in Sources and limitations.
3. **Unversioned siblings:** For up to 4 parent epics with the most in-scope items, check `parent in (<epic keys>) AND fixVersion is EMPTY AND statusCategory != Done` (use `searchResultMode: "count"` if supported by the live schema, otherwise `maxResults: 50` with `fields: ["summary"]`) and report in Sources and limitations how many open unversioned sibling items sit under the release's epics.
4. **Scope rule:** The scope consists of items from (1) and (2). An epic counts as an item only if it has no children in scope; otherwise its children carry the work and the epic groups them.
5. **Statuses:** Group every item by Jira status category: To do (`new`), In progress (`indeterminate`), and Done (`done`).
   - Within Done, items whose resolution or status name is Won't do, Cancelled, Canceled, Duplicate, Declined, Rejected, Abandoned, or Obsolete are **Descoped** (never counted as shipped).
   - **Blocked:** status name contains "block" (case-insensitive) or the item came back from the flagged-items query.
   - **In review:** status name contains "review", "QA", "verify", or "test" within the In progress category.
   - Link every issue using the base site URL from `getAccessibleAtlassianResources` (`https://<site>.atlassian.net/browse/<KEY>`).
6. **Release checks:** Classify Testing and Rollout checks from the recorded parent/type/labels/components and then title rules in [the readiness rules](references/readiness-rules.md). Mark title-based grouping as such and do not infer a completed test from a task to write its plan.

## Step 3: Blockers and Jira dependencies

1. **Issue links on open work:** Run one `searchJiraIssuesUsingJql` query for `fixVersion = <id> AND statusCategory != Done` (plus open epic children by key) with explicit `fields: ["summary", "status", "issuelinks"]` and `maxResults: 100`.
2. **Read direction from Jira's own wording:** In `issuelinks`, `outwardIssue` reads `"[this item] [type.outward] [other]"` and `inwardIssue` reads `"[this item] [type.inward] [other]"`. The other item is **upstream** when the phrase is "is blocked by", "depends on", "requires", or "is caused by", and **downstream** when it is "blocks", "is depended on by", or "is required by". Ignore non-dependency links (relates to, follows, clones, duplicates).
3. **Upstream items outside scope:** Fetch their status with one `searchJiraIssuesUsingJql` `key in (...)` query per project key (`fields: ["summary", "status", "assignee", "project", "duedate"]`, up to 3 project keys). Never mix project keys in a single `key in (...)` query. List any unreadable keys or external-site keys as unreadable in Sources and limitations.
4. **Blocked and flagged items:** For up to 5 blockers (ranked as Step 6 specifies), call `getJiraIssue` (passing explicit `fields: ["summary", "status", "issuelinks", "updated", "assignee"]` — check live schema before using `view`) and `listJiraIssueComments` directly to read recent comments explaining what it is waiting on. Paraphrase the reason in at most 20 words, note the comment date, keep any linked ticket/page URL as evidence, and never display email addresses.
5. **Cross-project dependencies:** Note when an upstream Jira item lives in another Jira project (likely cross-team); for same-project links, say "in this release" or "same project".

## Step 4: Testing, rollout, and unrecorded blockers

1. **Release docs (run in parallel):**
   - Version related work collected in Step 1 (`getJiraProjectVersionRelatedWork`).
   - `searchConfluence` with CQL `type in (page, blogpost) AND title ~ "<distinctive term>" AND (title ~ "rollout" OR title ~ "release" OR title ~ "test plan" OR title ~ "spec" OR title ~ "runbook" OR title ~ "launch" OR title ~ "readiness" OR title ~ "go/no-go" OR title ~ "DACI")` (`limit: 25`), scoped to `AND space = "<Jira project key>"` first (retry once site-wide if empty, marking those results Found by search).
   - `search` (Rovo Search — use cloudId, query and optional targetApp/limit without mode; for query, pass `"<release name> rollout plan test plan"`).
   - Read up to 3 key docs with `getConfluenceContent` (check live schema for `content_id` vs `contentId`; use `detail="full"`, and re-read with `content_format="html"` if `lostFeatures` drops panels or dates). Prioritize related work links first, then record-linked docs, then search results naming the release. Capture page status, checklist/sign-off state, dates, and decision tables.
2. **Testing evidence:** Any of: a completed Testing release check (a task to write a test plan counts only with the plan itself); version related work in a testing category; a linked test plan doc (or one naming the release/epic/in-scope key). If none exists, report "No test evidence found" in Testing. Never infer testing from a status name alone.
3. **Rollout evidence:** Any of: Rollout release checks and their status; a rollout plan or runbook doc and its status; related work in a rollout/documentation category; Jira version approvers and their status.
4. **Unrecorded blockers:** Run up to 2 `search` calls (checking live schema first): `"<release name> blocked"` and `"<top blocker key or distinctive epic term> blocked go no-go"`. Keep a hit only if its `lastModified` is in the last 14 days, it passes sensitive-content checks, and it explicitly indicates a blocker for this release or an in-scope item. Label search-only hits clearly as **Found by search (not recorded in Jira)**.
5. **Security, privacy, or legal reviews:** Show only the ticket/page status, recorded owner, and link — never quote or summarize review findings. If a blocker links a review Confluence page on this site, read it once with `getConfluenceContent` (`detail="summary"`) for status only.

## Step 5: Open work and people

- **Open work:** Order open in-scope items from Step 2 (or one follow-up JQL query if needed): Blocked first, then In review, In progress, and To do, ordered by most recent update. Show up to 25 rows with key link, status name, Testing/Rollout tag if any, assignee, and due date; count and summarize the rest.
- **People:** Use display names directly from Jira issues and version metadata. Only if a blocker assignee or approver appears as an account ID with no display name, call `getJiraUser` directly (up to 5 calls). Never display emails, job titles, or locations.

## Step 6: Assess

### Areas

Assess all five areas (**Work**, **Code**, **Testing**, **Dependencies**, **Rollout**) with one state each: **Ready**, **Conditions**, **Not ready**, **Not checked**, or **Not used**. Explicitly list **Code & Deployments** (pull requests, builds, rollouts) and **Atlassian Projects** as **Not checked (unavailable on connector)** unless checked via a separate standalone session connector.

**Not used** requires the release scope, a record, or explicit user confirmation that the area does not apply. Missing docs or empty searches produce **Conditions**, never **Not used**.

Read [the area assessment table](references/readiness-rules.md) before deciding area states. Mark Code Not checked when no PR evidence can be read. Partial code evidence, unavailable deployment evidence or missing applicable Projects dependency coverage creates Conditions; it does not establish Ready or Not used. Keep evidence gaps in the condition list.

### Findings

Use this fixed set, ranked in order:

1. **Blocker**: a Blocked or flagged item, an open item with an open upstream Jira dependency, or a record stating the release/item is blocked. Rank blockers by number of waiting in-scope items first, then by duration blocked (call `listJiraIssueChangelogs` directly for up to 2 top blockers to show "Blocked since [date]").
2. **Open check**: open Testing or Rollout checks (grouped by kind for readability, while counting each open check separately in conditions).
3. **Stalled**: an In progress or In review item with no update in 10+ working days.
4. **Dependency**: an open upstream Jira item that is not already a Blocker.
5. **Date passed**: the recorded release date has passed and the version is unreleased.
6. **Gap**: missing evidence within Jira/Confluence (no test evidence, no rollout doc, unreadable upstream keys) plus unavailable scopes (PRs, deployments, Atlas Projects).

### The verdict

Build one deduplicated list of outstanding conditions. An applicable area that cannot be checked contributes an evidence-gap condition, including unavailable PR, deployment and Projects dependency evidence. Count a single coverage gap once, not once per issue; six different open checks remain six conditions. Never discard a gap just because the connector lacks the tool.

Decide in order and state the rule:
1. Can't assess: no in-scope work, or Work could not be read.
2. Not ready: a recorded blocker, any area Not ready, or more than five distinct conditions.
3. Ready: zero conditions and every area Ready or explicitly confirmed Not used.
4. Ready with conditions: otherwise one to five conditions.

An unavailable capability does not establish non-applicability. Never return an unqualified Ready while applicable code or deployment evidence is missing. Keep the same condition count and verdict in the answer and any report. Stalled and Date passed findings alone do not add a condition.

### Decisions needed

List up to 4 plain-sentence decisions, most urgent first, each labelled **Suggested** with its recorded holder (version approver -> version driver -> linked decision page driver/approver -> blocker assignee; otherwise "No owner recorded"). Typical decisions: moving open items out of the release, shipping without missing test/rollout evidence, waiting on an upstream project, confirming a passed release date, or closing an open in-scope decision page. Never invent a new date, estimate, or assignee.

## Writes

One optional offer, only after delivering the readiness readout and never without an explicit "yes": link testing or rollout docs found in Step 4 to the version's related work via `manageJiraProjectVersionRelatedWork`.
- **Inspect the live `manageJiraProjectVersionRelatedWork` schema first** to confirm exact parameter names (such as `cloudId`, `action`, `versionId`, `url`, `title`, `category`).
- Present each proposed link in a numbered list with its category marked **Proposed** and total count, wait for confirmation, create them, then call `getJiraProjectVersionRelatedWork` to verify.
- Never move issues, change release dates, or mark a version released unless explicitly instructed.

## Conversational Answer Structure

Deliver the complete readout directly in Markdown:

1. **Header & Verdict:** Version name, Jira project, recorded release date (noting if passed or unset), version driver, **Verdict** + the exact rule that decided it, key counts (Open / Total, Done, Descoped, Blockers, Open checks), and a 2–3 sentence summary naming the top blocker and key scope caveat.
2. **Blockers:** Ranked list with why each is blocked, which in-scope items wait on it, and Markdown evidence links (or "No blockers recorded in Jira or Confluence").
3. **Readiness by area:** Compact table covering Work, Code, Testing, Dependencies and Rollout with evidence links and the same condition list. Mark Code Not checked when PRs cannot be read; include missing deployment evidence under Rollout and missing Projects dependency coverage under Dependencies. Do not mark those areas Ready solely because Jira tasks or documents are complete.
4. **Outstanding conditions:** Numbered, deduplicated list matching the verdict count (or "None on the Jira and Confluence evidence checked").
5. **Other findings:** Open checks, Stalled items, Dependencies, Date passed, and Gaps.
6. **Open work:** Compact Markdown table (up to 25 rows, ranked Blocked -> In review -> In progress -> To do) with key link, status, check tag, assignee, and due date, plus count of remaining items.
7. **Decisions needed:** Up to 4 numbered items labelled **Suggested** with recorded holder.
8. **Sources and limitations:** Exact Jira/Confluence queries and scope rules (fix version, epics' children, unversioned sibling count), caps applied, unreadable keys, search terms and 14-day window, and the explicit statement that **pull requests, deployments, and Atlassian Projects were not checked** because those scopes are unavailable on this connector.
9. **Next steps:** Offer the related-work link write if Step 4 found unlinked rollout/test docs, and mention `dependency-map` if a deeper two-hop Jira dependency map would help.
## Optional offline report

Answer in the conversation first. When the user requests an HTML report, read [the report export instructions](references/report-export.md), load atlassian-design, and run the bundled render.py from this skill directory using its example.json and data-format reference. Preserve the same facts, verdict, condition count and coverage gaps in the report. Both design kits run offline with Python's standard library; do not install packages or download assets. Export does not authorize publication or sharing. Return static HTML when publication tools are unavailable.
