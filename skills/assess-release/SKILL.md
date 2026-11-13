---
name: "assess-release"
description: "Assess whether a release, fix version or milestone is ready to ship using Teamwork Graph across Jira, Projects, Confluence, connected code, deployments and chat. Answers in the conversation first with a rule-based verdict (Ready, Ready with conditions or Not ready), linked blockers, readiness by area, open work, decisions and recorded owners, and evidence gaps. Offers the existing HTML report on request and publication only when Atlassian Artifacts is available and requested. Use for release readiness, a go or no-go view, or /assess-release. For dependencies alone, use dependency-map. For goal health, use status-check. For shipped changes, use release-notes."
---

# Assess release

Give a release driver, engineering manager or team lead an answer in the conversation that they can read in three minutes before a go or no-go call: whether the release is ready to ship, what's stopping it, what each area (work, code, testing, dependencies, rollout) shows, what needs deciding and who holds each decision, and what couldn't be checked.

A release page in Jira counts issues by status. The value of this skill is the judgement the release page, the board and the pull request list can't make on their own: which open items actually stop the ship, whether "done" work has merged and deployed code behind it, whether the testing and rollout work exists and is finished, and which dependencies on other teams are still open, all checked against linked records rather than titles.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. Its section "What the graph doesn't tell you" matters most here. This file adds what's specific to a release. An optional HTML report is built by `render.py` in this folder (Step 9), which applies the `atlassian-design` skill for you: load that skill only if the script can't run.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## What this skill will and won't do

- **It assesses one release now.** The verdict says whether the release could ship today on the evidence in its records. It never forecasts a ship date, a completion date or a velocity. The release date appears only as a record states it, with its moves if a record shows them.
- **A blocker needs a record.** A Blocked status, a flag, an open upstream issue link whose direction was read from Jira, or a record (a comment, an update, a decision page, a message) that says the release or one of its items is blocked. Never a title ("Coordinate with the Platform team"), and never a priority field alone.
- **A decision's holder needs a record.** The release's driver or approvers, a decision page's driver or approver, or an owner a record names. Otherwise "No owner recorded". The skill suggests decisions; it never assigns anyone.
- **Gaps are results.** Pull requests that couldn't be read, keys on another site, missing test records and checks that weren't run are shown in their area and in the footer, and never counted as done.

## Connectors

- **Needed:** Jira, for the release's work and its issue links. If Jira isn't in the site's `products` list (see "Atlassian apps on the site" in `teamwork-graph-context`), there's no release to assess: say so and stop.
- **Helpful, from Atlassian:** Projects, for the project behind the release, its target date and its dependencies. Confluence, for the spec, test plan, rollout plan and decision pages. Bitbucket, for pull requests and deployments linked to the work. Compass, for the services the release touches. Skip the calls for an app that isn't on the site, and list it in the footer as "Not available on this site".
- **Helpful, from other tools:** GitHub or GitLab, for pull requests linked to the work. A deployment tool connected to the graph (Spinnaker, Bitbucket Pipelines), for how far each change has rolled out. Slack or Teams, for blockers and go or no-go discussion that never reached Jira. Google Drive or SharePoint, for specs and rollout plans kept outside Confluence.
- **Vendor connectors,** as `teamwork-graph-context` describes. Teamwork Graph comes first, and a connector fills only a known gap:
  - GitHub or GitLab, to read a pull request's state and reviews when the graph returns it with `raw: {}`.
  - Slack or Teams, to read a blocker thread in full when search returns only a snippet.

## Budget

A release can hold a hundred items, so every step states its cap. In total, unless the user asks for a deeper pass:

| Tool | Cap | Where |
| --- | --- | --- |
| `getJiraProjectVersions` | 2 | Step 1: the version, and one name lookup in its project |
| `getJiraProjectVersionRelatedWork` | 1 | Step 1 |
| JQL | 10 | 1 in Step 1 (name lookup), 4 in Step 2 (the release's items, flagged items, epics' children, unversioned siblings count), 1 in Step 3 (open items with links), up to 3 in Step 3 (other projects' upstream items, one per project key), 1 in Step 6 (open work shown) |
| `getJiraIssue` | 5 | Step 3: Blocked or flagged items, for the reason |
| `getGraphContext` | 16 | 3 in Step 2 (the version, and up to 2 epics for the project), up to 8 in Step 4 (pull requests), up to 5 in Step 5 (deployments, pages included) |
| `getGraphObject` | 2 batches | Step 4 (pull requests), Step 5 (deployments) |
| `searchProjects`, `getProject` | 1 (only as a fallback) and 1 | Step 2 |
| `search` | 3 | Step 5: 1 Confluence (spec, test or rollout docs), 2 third-party (blockers, go or no-go) |
| CQL (`searchConfluence`) | 2 | Step 5: the space first, then site-wide only if that returns nothing |
| `getConfluenceContent` | 3 reads, plus 1 | Step 5, plus one status read for a review page a blocker links |
| `getPeopleInfo` | 1 batch | Step 7, up to 10 people |

`search`, `getGraphContext`, `getPeopleInfo` and `getPullRequests` use Rovo credits. A typical run makes 35 to 50 calls, including a `discover` for each operation reached through `executeRead`. A retry after an input error doesn't count against a cap. Don't use `getPullRequests` with `scope: "all"` across a project: on real data it came back degraded ("GraphStore PR relationship query failed", with a hint not to retry), so pull requests come from the work items' graph edges instead. Don't use `getJiraIssue` with `view: evidence` here: on a large site it returns every custom field (about 25,000 characters per item), including template defaults that read like facts. Pass an explicit `fields` list. The footer reports every cap that applied ("Checked pull requests for 8 of 21 open items").

Calls in the same step that don't depend on each other go out together, as "Fetch in parallel" in `teamwork-graph-context` describes.

### Run order

1. **Setup:** `getAccessibleAtlassianResources`, and one `discover` each for "jira project version" (it returns both version operations) and "get atlassian project".
2. **Resolve (Step 1):** the version read, the related work read and, for a name, the JQL lookup, together.
3. **Scope (Step 2):** the release's items, the flagged-items query and the version's graph summary, together. Then the epics' children, the epics' project walks and the project read.
4. **Evidence:** the open-items links query and the Blocked items' reads (Step 3), the pull request walks (Step 4), and the Step 5 searches and CQL, together. Then the other projects' upstream items, the `getGraphObject` batches, the deployment walks and the doc reads.
5. **People and open work (Steps 6 and 7):** the open work query and the `getPeopleInfo` batch.

Then assess (Step 8) and answer in the conversation. Write the report data and run `render.py` (Step 9) only if the user requests the HTML report or publication.

## Step 1: Resolve the release

| The user gives you | Anchor | Resolve with |
| --- | --- | --- |
| A Jira version URL (`/projects/<KEY>/versions/<id>`) | `JiraVersion` | `getJiraProjectVersions` with `versionId` |
| A project key and a version name ("LEDGER 2.4") | `JiraVersion` | `getJiraProjectVersions` with `projectIdOrKey`, `query` set to the name, `status: ["unreleased", "released"]` |
| A version name only ("Ledger 2.4") | `JiraVersion` | JQL `fixVersion = "<name>"`, `fields: ["project", "fixVersions"]`, `maxResults: 5`, then the version read in that project. If the name matches versions in two projects, ask which one |
| A release epic | `JiraWorkItem` | `getJiraIssue` with `fields: ["summary", "status", "fixVersions", "duedate", "assignee", "parent"]`. If it carries one unreleased fix version, offer to assess that version instead |
| An Atlassian project | `AtlassianProject` | `getProject` (Step 2). If most of its tracked work shares one unreleased fix version, offer to assess that version |
| A goal or "milestone" with no Jira record | | Say that this skill assesses a release, and offer `/status-check` for a goal |

- Read the version with `include: ["driver", "approvers"]`. The skill's job is the go or no-go call, so the driver and approvers are what it's for: this overrides the tool's hint to leave `include` unset unless asked. Capture the name, project, description, start and release dates, `released`, `overdue`, the driver and each approver with their status.
- **Already released:** say "Released on [date]" and stop. Offer `/release-notes` for what shipped.
- **The release date:** show it as recorded. If it has passed and the version isn't released, that's a Date passed finding. With no release date, say "No release date set".
- Read the version's related work with `getJiraProjectVersionRelatedWork` (`versionId`). Each item has a category (such as "Designs", "Testing", "Documentation" or a team's own) and a URL. These are the release's own docs and checks: keep them for Step 5.
- If the read returns a description, URLs in it (a project, a spec, a rollout plan) join the scope too. Single-version reads often return no description field: then say nothing about one.
- If the anchor can't be found, stop and say so. Don't build a page around a guess.

## Step 2: Find the release's work

At most 4 JQL queries, 3 `getGraphContext` calls, 1 `searchProjects` (only as a fallback) and 1 `getProject` read.

`release-notes` resolves a version and its work with the same rules as Step 1 and this step, so the two skills agree on what is in a release. Change them together.

1. **The release's items:** `searchJiraIssuesUsingJql` with `fixVersion = <id>`, `fields: ["summary", "status", "issuetype", "priority", "assignee", "duedate", "updated", "resolution", "resolutiondate", "statuscategorychangedate", "parent", "labels", "components", "project"]` and `maxResults: 100`. Page with `nextPageToken` until `isLast`, up to 200 items, and say in the footer if there were more. The result can arrive as a file: parse it with a script. JQL doesn't return the Flagged field by that name, so find flagged items with a separate clause: `fixVersion = <id> AND Flagged is not EMPTY`, `fields: ["summary", "status"]`, `maxResults: 25`.
2. **Epics' children:** a fix version often sits on epics while the work is in their children. For every epic in the result, read its children with `parent in (<epic keys>) AND (fixVersion is EMPTY OR fixVersion = <id>)` and the same fields. Children with another fix version aren't in this release: count them in the footer ("4 children of release epics are in other versions").
3. **Unversioned siblings:** for the parent epics of in-scope items (up to 4, most items first), count `parent in (<epic keys>) AND fixVersion is EMPTY AND statusCategory != Done` with `searchResultMode: "count"`. They aren't in scope, but say in the footer how many open items sit under the release's epics with no fix version, since some may belong to the release.
4. **The scope** is the items from 1 and 2. An epic counts as an item only when it has no children in scope. Otherwise its children carry the work and the epic groups them.
5. **The graph, once:** `getGraphContext` on the version (`objectType: JiraVersion`, the version URL, `detailLevel: summary`). Compare its `jira_version_links_jira_work_item` count with the JQL count. JQL is the record: if they differ, use JQL and say so in the footer ("The graph links 40 items to this release; Jira has 41").
6. **The project behind it,** if Projects is on the site. Find it from the work, not by name, because a release name is often too generic to search (on real data, a release name matched 20 projects):
   1. a project URL in the version description, if there is one
   2. otherwise the parent epics of the items in scope: for the 2 epics with the most items in scope, `getGraphContext` (`objectType: JiraWorkItem`, the epic key, `detailLevel: full`, `relationshipTypes: ["jira_work_item_tracks_atlassian_project"]`). The target is the project's ARI
   3. only if neither gives one, `searchProjects` with the version name in quotes (`limit: 20`, `filters: {archived: false}`)
   Read the project with `getProject` (`include: ["dependencies", "links", "updates", "teams"]`, `linkType: WORK_TRACKING`, `limits: {dependencies: 20, links: 20, updates: 3, teams: 5}`). A project found by search counts only if its work-tracking links include an item or epic in scope. Otherwise say "No project found for this release" and don't count project dependencies as checked.
   The project's updates are records like any other: an update that says an in-scope item or the release is blocked, waiting on something, prevented or not ready is a Blocker record (Step 5 item 5), cited as "[KEY] update, [date]", and one that reports testing or rollout progress is evidence for that area. Show the project's own target date beside the release date when they differ ("Project target: Feb 28"), as recorded, with no finding and no forecast.
7. **Statuses.** Group every item by Jira's status category: To do (`new`), In progress (`indeterminate`) and Done (`done`). Within Done, a resolution or a status name of Won't do, Cancelled, Canceled, Duplicate, Declined, Rejected, Abandoned or Obsolete is **Descoped**, never shipped. Many workflows never set a resolution and close dropped work in a Done-category "Cancelled" status, so check the status name too. Within the others:
   - **Blocked:** the status name contains "block" in any case ("Blocked", "Blocked.", "Blocked by vendor"), or the item came back from the flagged-items query.
   - **In review:** the status name contains "review", "QA", "verify" or "test", in the In progress category.
   - Keep each item's own status name for the page.
   - **Links on the page** use the site URL from `getAccessibleAtlassianResources` (`https://<site>.atlassian.net/browse/<KEY>`), even when the user's link or a graph `webUrl` uses another host for the same site, such as `*.jira.atlassian.cloud`.
8. **Release checks.** Tag an item as a **Testing** check or a **Rollout** check, using the first of these that applies:
   1. **Its parent epic:** when the epic's summary contains, as whole words, "readiness", "productionization", "productionisation", "productionize", "operational", "go-live", "GA", "launch", "rollout" or "testing", every child is a check. Its kind is Testing when the child's summary matches the Testing list in item 4 (or the epic says "testing"), and Rollout otherwise. An epic counts too when most of its children are tagged as checks by item 4.
   2. **Its issue type:** Test, QA or Bug Bash is Testing.
   3. **Its labels or components:** test, qa, e2e, perf: Testing. rollout, launch, runbook, ops, release: Rollout.
   4. **Its summary,** matching whole words or phrases, case-insensitive, and ignoring words inside code identifiers (ALL_CAPS tokens, anything with an underscore, dot or slash, such as `MONITORING_ONLY`). Simple plurals match ("perf tests"). A summary that starts with "Test" or "Validate" followed by what's tested ("Test the import API with real keys") is Testing. Testing: "test plan", "test run", "E2E", "end-to-end", "QA", "load test", "perf test", "performance test", "soak", "regression test", "bug bash", "production validation". Bare "test" and "testing" don't count: they name a task's purpose as often as a check ("Update the client for testing"). Rollout: "runbook", "runbooks", "alert", "alerts", "dashboard", "SLO", "SLOs", "pre-mortem", "rollout", "roll out", "feature flag", "on-call", "launch", "go/no-go", "production metrics", "production readiness". When both lists match, it's Testing. A summary that starts with "Explore", "Spike", "Investigate" or "Research" is never a check.
   This only groups an item: it never makes it a blocker. Items tagged by summary words are marked "Grouped by title" in the page.

## Step 3: Blockers and dependencies

At most 4 JQL queries and 5 `getJiraIssue` reads.

1. **Issue links on open work:** one JQL query, `fixVersion = <id> AND statusCategory != Done` (plus the epics' open children by key), with `fields: ["summary", "status", "issuelinks"]` and `maxResults: 100`. This returns every link with its direction, so no per-item read is needed.
2. **Read each link's direction from Jira's wording,** never from the graph (`teamwork-graph-context`, "Direction"). In an item's `issuelinks`, an entry with `outwardIssue` reads "[this item] [type.outward] [other]", and one with `inwardIssue` reads "[this item] [type.inward] [other]". The other item is **upstream** (this item waits on it) when that phrase is "is blocked by", "depends on", "requires" or "is caused by". It's **downstream** when the phrase is "blocks", "is depended on by" or "is required by". Every other type (relates to, follows, clones, duplicates) carries no wait and isn't a dependency.
3. **Upstream items outside the scope:** read their status with one JQL `key in (…)` query per project key, `fields: ["summary", "status", "assignee", "project", "duedate"]`, for up to 3 project keys. Never mix project keys in one query: one key that isn't on the site fails the whole list with 400 "Issue does not exist or you do not have permission to see it". A 400 for a project key means its items can't be read here: list them as unreadable and don't count them as checked. A link to an item on another Jira site gets one try with that site's URL as `cloudId`, as "Jira keys in text" in `teamwork-graph-context` says.
4. **Blocked and flagged items:** for up to 5, ranked as Step 8 ranks blockers, read `getJiraIssue` with `fields: ["summary", "status", "issuelinks", "comment", "updated", "assignee"]` for the reason. Take the reason only from the latest comments that say what it's waiting on, even when they predate the move to Blocked, and say when ("from a comment on Aug 14"). Paraphrase in at most 20 words, never quote, and keep any URL a comment gives (a ticket, a thread, a page) as the evidence link. Comment authors come with email addresses: never show them.
5. **Project dependencies:** from the Step 2 `getProject` read. `DEPENDS_ON` is upstream, `DEPENDED_BY` is downstream, and `RELATED` carries no direction unless another record gives one (`dependency-map` Step 2 says how). The dependency results carry each project's status, target date and owner.
6. **Cross-team:** an upstream item is cross-team when it's in another Jira project, or another team owns it (its project's team in Projects, or its assignee's team from Step 7). Same-project upstream links count too, but say "in this release" rather than naming a team.

## Step 4: Code

At most 8 `getGraphContext` calls and 1 `getGraphObject` batch.

1. **Which items:** up to 8, leaving out release checks and items whose summary starts with "Explore", "Spike", "Investigate" or "Research", which rarely have code. Open items in In review first, then In progress and Blocked, most recently updated first, up to 6. Keep the last 2 for Done items resolved in the last 30 days, most recent first, so the check also shows whether finished work merged (use them for open items when nothing was resolved). To do items aren't checked, including Blocked items whose status sits in the To do category: their code usually hasn't started. Say how many items were checked and how many weren't.
2. **The walk:** for each, `getGraphContext` (`objectType: JiraWorkItem`, the key, `detailLevel: full`, `relationshipTypes: ["jira_work_item_links_external_pull_request"]`, `first: 20`). Each target carries a pull request ARI and its title.
3. **Shared pull requests:** when some of an item's pull requests name its key in their title, drop the ones that name no key or another item's key ("Merge master to hotfix") from that item's counts.
4. **Hydrate** up to 25 pull request ARIs in one `getGraphObject` batch, the most recent per item first. Pass the graph ARIs, not `bitbucket.org` URLs, which don't resolve. Take `pullRequestStatus` (OPEN, DRAFT, MERGED, DECLINED), `lastUpdatedAt`, the count of reviewers with `approvalStatus: APPROVED`, and whether the description has a Testing heading or a Rollback heading. The graph cuts descriptions at about 1,000 characters: when a description is cut before any such heading, count it as "couldn't be judged", not as missing one ("6 of 9 describe their testing; 2 couldn't be judged"). Never quote a description.
5. **Per item:** Merged (every non-declined pull request merged), Open (at least one OPEN or DRAFT), No pull requests found (none linked), or Not readable (`raw: {}`, or dropped from the batch). A GitHub pull request that comes back with `raw: {}` is read with the GitHub connector if the client has one, and is otherwise Not readable.
6. **What counts:** a Done item with an Open pull request is Unmerged code. An In review item with an Open pull request is waiting on review or merge. An In review item whose pull requests are all merged is noted in the Code area ("2 items in review have only merged pull requests"), not as a finding: Jira may simply lag. A Done item with no pull requests isn't a finding: not every item has code. Declined pull requests are ignored.

## Step 5: Testing and rollout

At most 3 `getGraphContext` calls, 1 `getGraphObject` batch, 3 `search` calls, 1 CQL query and 3 `getConfluenceContent` reads.

1. **The release's docs,** sent together:
   - the related work from Step 1, by category
   - `searchConfluence` with `type in (page, blogpost) AND title ~ "<distinctive term>" AND (title ~ "rollout" OR title ~ "release" OR title ~ "test plan" OR title ~ "spec" OR title ~ "runbook" OR title ~ "launch" OR title ~ "readiness" OR title ~ "go/no-go" OR title ~ "DACI")`, `limit: 25`, with `AND space = "<Jira project key>"` first, since teams often name the space after the project. If that returns nothing or fails, run it once site-wide inside the same cap and mark those results Found by search
   - `search` (`mode: STANDARD`, `targetApp: CONFLUENCE`, `limit: 20`) with the release name plus "rollout plan"
   Read up to 3 with `getConfluenceContent` (`detail: outline` first, `full` only for a rollout plan or test plan whose outline has a checklist, status or sign-off table): related work items first, then pages a record links, then search results whose title names the release. From a read, take the page's status, its sign-offs or checklist state, the date, and any decision table. Docs found only by search are marked Found by search.
2. **Deployments:** for up to 3 Done or In review items with merged pull requests, `getGraphContext` with `relationshipTypes: ["jira_work_item_links_external_deployment"]`, `detailLevel: full` and `first: 50`, paging with `after` while `hasNextPage` is true, up to 5 deployment calls in all (each page counts). A work item's deployment edges include deployments of other items' pull requests that went out in the same pipeline run, and come back oldest first. So keep only deployments whose title names one of the item's own pull request numbers ("pull request #128") or the item's key, then hydrate up to 25 of those, newest first (the end of the list), in one `getGraphObject` batch, spread across the items. Each deployment carries `environment.type` (DEVELOPMENT, TESTING, STAGING, PRODUCTION), `state` (SUCCESSFUL, FAILED, IN_PROGRESS, ROLLED_BACK), `createdAt`, `lastUpdatedAt` and the pipeline. Per item, report the furthest environment type with a SUCCESSFUL deployment, and any FAILED or ROLLED_BACK one newer than it, naming its environment ("prod-west: failed Oct 14"). That newer failure is a Failed deployment finding and a Rollout condition. An IN_PROGRESS deployment more than a day old whose `lastUpdatedAt` equals its `createdAt` is stuck reporting, not running: ignore it. If none of an item's deployments name its own pull requests, say "No deployments of this item's own pull requests found" rather than using the others. This is a sample: say so ("Deployments checked for 3 items"), and say when `hasNextPage` was true.
3. **Testing evidence,** any of: a Testing release check that's Done (a task to write a test plan is a plan, not a test: it counts only with the plan itself); related work in a testing category; a test plan doc that a record links, or that names the release, an in-scope key or an in-scope epic (one found by search that doesn't is listed as Found by search and not counted); merged pull requests whose descriptions have a Testing section ("6 of 8 checked pull requests describe their testing"); a SUCCESSFUL deployment to a TESTING or STAGING environment; a project update (Step 2) that reports testing done or under way. With none, say "No test evidence found" in the Testing area. Never infer that testing happened from a status name.
4. **Rollout evidence,** any of: Rollout release checks and their status; a rollout plan or runbook doc and its status; related work in a rollout or documentation category; the furthest environment from item 2; the version's approvers and their status.
5. **Unrecorded blockers:** 2 `search` calls (`mode: STANDARD`, `targetApp: THIRD_PARTY`, `limit: 20`): "[release name] blocked", and "[top blocker's key] [its summary's distinctive words]" when there's a blocker, or "[release name] go no-go" when there isn't. When the release name is only a number, a code or acronyms ("2.4", "ABC - XYZ"), use the summary words of the in-scope epic with the most items, with the release name taken out, in place of the release name, since acronyms match unrelated teams and customers. If nothing is left, use the top blocker's summary words. Keep a result only if its `lastModified` is in the last 14 days and its snippet says something is blocked, waiting, prevented or not ready, and names the release, an in-scope key, the release's distinctive term (two or more words of its name, leaving out version numbers and product or company words, such as "Ledger search" for "Ledger 2.4: search cutover"), or the top blocker's subject. Results that don't name the release or a key are marked Found by search. It's a Blocker with the source label "from Slack, not recorded in Jira". Drop sensitive results by title and snippet first, as `teamwork-graph-context` says. Comment links from Step 3 to Slack threads are read the same way, by snippet, when search returns them.

**Reviews by security, privacy or legal** (a security review ticket, a privacy assessment, a counsel sign-off) are shown as a check with its status, its owner as the record names them and its link. Never quote or summarise what the review found or asked for. When a blocker links a review page on this site, read it once with `getConfluenceContent` (`detail: summary`) for its status only, outside the 3-read cap. With no status on the page, show "Status not recorded on the page". Saying that an item waits on a review is allowed: that's the item's status, not the review's content. A review ticket on another site gets the one try that "Jira keys in text" in `teamwork-graph-context` allows, and is otherwise listed as unreadable.

## Step 6: Open work

One JQL query, only if the Step 2 result isn't already enough to list: the open items in scope, ordered as the page shows them. Up to 25 rows on the page: Blocked first, then In review, In progress and To do, then by most recent update. The rest are counted and linked as one JQL search ("12 more open items"). Show each item's own status name, its assignee's name and its due date if any.

## Step 7: People

Skip this step when every person on the page is already named by a record and no team is needed for the cross-team check. Otherwise one `getPeopleInfo` batch of up to 10 account IDs: the approvers, the assignees of blockers, and the owners of upstream items and projects. The version's driver comes back as a display name only, with no account ID: show the name as the version records it, with no team, and don't look it up. Use only the name and team. Never show emails, job titles or locations, and don't call with `manager: true`: a release decision goes to the people the records name, not up a reporting line.

## Step 8: Assess

### Areas

Give each of the five areas one state: **Ready**, **Conditions**, **Not ready**, **Not checked** or **Not used**.

First establish applicability. **Not used** requires the release scope, a record or the user to explicitly confirm that this area does not apply. State that reason and its source. No linked pull requests, an empty search, an unavailable app or a missing Projects project does not establish non-applicability. Assess each area independently: Code being Not used does not make Testing or Rollout Not used.

| Area | Not ready | Conditions | Ready | Not used |
| --- | --- | --- | --- | --- |
| **Work** | Any Blocked item, or any open item in To do or In progress that isn't a release check | Only In review items and release checks are open | No open items | Never: no release items means Can't assess |
| **Code** | Any Done item with an Open pull request | Any In review item with an Open pull request, 1 or more checked items Not readable, or fewer than 2 checked items with any pull request (a Gap for insufficient evidence) | Every checked item with pull requests is Merged, and at least 2 checked items have pull requests | Explicit confirmation that the release has no implementation changes requiring a code check |
| **Testing** | An open Testing check that's Blocked | An open Testing check, or no test evidence found | Test evidence found and no open Testing checks | Explicit confirmation that testing does not apply to this release |
| **Dependencies** | Any open upstream item or project that's Blocked, or whose due or target date is after the release date | Any other open upstream item or project, any upstream item that couldn't be read, or a Gap in applicable dependency coverage | No open upstream items or projects, and applicable dependency sources were checked | Explicit confirmation that this release has no applicable dependency area |
| **Rollout** | An open Rollout check that's Blocked, or an approver who declined | An open Rollout check, a Failed deployment, an approver still pending, no rollout doc found, or no deployment beyond development for the checked items | Rollout checks done, approvals given (or none set), and applicable rollout evidence checked with no outstanding condition | Explicit confirmation that rollout does not apply to this release |

For an applicable area, confirmed Not ready evidence wins. Otherwise, an area whose required records couldn't be read at all is **Not checked**, with a Gap condition explaining why. An empty successful read is not a failed read: missing evidence produces Conditions, rather than Not used. Where some evidence was checked, use Conditions for the remaining gaps. Missing Projects coverage remains a Gap condition even when the Jira links are clear; it makes Dependencies Conditions, unless the area is explicitly confirmed Not used. With no Not ready evidence, unreadable required records or outstanding conditions, use Ready.

### Findings

One row each, from this fixed set:

- **Blocker** (danger): a Blocked or flagged item; an open item with an open upstream item; or a record that says the release or an item is blocked (Step 5 item 5).
- **Unmerged code** (warning): a Done item with an open pull request, or an In review item whose pull request has had no update in 5 or more working days.
- **Open check** (warning): open Testing or Rollout checks, one row per kind ("6 rollout checks are open, all in Needs Triage"), with the count, the first two as links and the rest as a count. Checks under one readiness epic link the epic too.
- **Stalled** (warning): an In progress or In review item with no update in 10 or more working days.
- **Dependency** (warning): an open upstream item or project that isn't a Blocker.
- **Failed deployment** (warning): an item's newest deployment to an environment failed or was rolled back after an earlier success, named with the environment and date.
- **Date passed** (warning): the release date has passed and the version isn't released.
- **Gap** (neutral): evidence that couldn't be read or wasn't found (no test evidence, pull requests not readable, upstream items on another site, no rollout doc, no project found).

**Ranking.** Blockers first, by how many in-scope items wait on each (counting downstream links inside the scope), then by how long the item has been Blocked. Only a changelog gives that reliably: a Blocked status can sit in the To do category, so `statuscategorychangedate` may date a different move. For up to 2 blockers, read `listJiraIssueChangelogs` (through `discover`, within the `getJiraIssue` cap) for the date the status became Blocked, and show "Blocked since [date]". Otherwise leave the date out, and rank by downstream count, then by key. Then the other findings in the order above. Never by priority field, issue type or age alone. An open Critical item is open work like any other.

### The verdict

First build one explicit list of **outstanding conditions** from the evidence and the Areas table. Reuse that same list in the answer and any later report:

- One condition per open In review item, open Testing or Rollout check, pending approval, unresolved Failed deployment, open upstream dependency that isn't already a Blocker, or evidence Gap. Include every reason that makes an area Conditions, including insufficient code evidence, missing test or rollout evidence, unavailable deployment evidence and missing Projects coverage. Every applicable Not checked area contributes a Gap condition.
- Give each underlying condition one stable local `id`, its affected `areas`, a type, a plain-language explanation and source links. A condition affecting Work and Code is one entry naming both areas. An open check that is also In review is one entry. Separate genuinely different requirements, such as completing a check and obtaining an approval.
- Grouping findings does not change the count: six open checks shown in one Open check finding still require six condition entries. A Gap describing the same missing evidence as another condition is not an extra condition. Stalled and Date passed findings do not add conditions on their own.
- Every Conditions area must have at least one listed condition; every applicable Not checked area must have a listed Gap. Ready and Not used areas cannot have outstanding conditions attached. Not ready areas can still have other outstanding conditions, but the Not ready state takes precedence. Check these relationships before giving the answer. Never label an area Conditions while listing zero reasons.

Count the distinct entries, then decide the verdict in this order and say which rule decided it:

1. **Can't assess:** the scope has no items, or Work is Not checked.
2. **Not ready:** 1 or more Blockers, any area is Not ready, or more than 5 outstanding conditions.
3. **Ready:** zero outstanding conditions, and every area is Ready or explicitly confirmed Not used. The summary explains any unused area.
4. **Ready with conditions:** otherwise, 1 to 5 outstanding conditions, with none of the earlier rules applying. Name and count those conditions in the answer; the count cannot be zero.

Consistency examples, with other areas Ready and no blockers unless stated:

| Evidence | Area and conditions | Verdict |
| --- | --- | --- |
| All applicable areas Ready | No conditions | Ready |
| An unresolved failed deployment | Rollout Conditions; one Failed deployment condition | Ready with conditions |
| Jira links are clear, but no Projects project was found | Dependencies Conditions; one coverage Gap | Ready with conditions |
| The user confirms this release has no implementation changes requiring code review | Code Not used, with the user's reason; other areas assessed independently | Ready if no conditions remain |
| No pull requests were found in the code sample, with no confirmation that code is unused | Code Conditions; a Gap for insufficient code evidence | Ready with conditions |
| Six open checks are grouped into one finding | Six distinct condition entries | Not ready |

What never changes the verdict: a priority field, the number of done items, a status name that sounds finished, a title, or how close the release date is. The verdict is about now. With weeks left, Not ready is normal, and the summary says how much is open without forecasting when it will close.

### Decisions needed

Up to 4, most urgent first, each one sentence in plain words, labelled "Suggested", with who holds it:

- **Holder, in this order:** an approver on the version (for sign-off), the version's driver (for scope and date), the driver or approver on a linked decision page, the owner a record names for the item (the upstream project's owner, the blocker's assignee for its own work). Otherwise "No owner recorded".
- **Typical decisions,** each only when the findings support it: whether to move open items out of the release ("Move the 8 open rollout checks, or keep them in"), whether to ship without a check that has no evidence, whether to wait for an upstream team, whether the release date stands when it has passed, and any open decision page in scope. A decision page is in scope when a record in scope links it, or its title or body names the release, an in-scope key or an in-scope epic. One found by search that doesn't is left out.
- Never suggest a new date, an estimate or an assignee.

### Stop condition

Stop when the scope is known, every open item has a status group, each area has a state, and each Blocker has its evidence link. One extra call is fine if it could change the verdict.

## Writes

One offer, after the conversational result, never without a yes: link docs found in Step 5 (a rollout plan, a test plan) to the version's related work with `manageJiraProjectVersionRelatedWork` (`action: create`, `versionId`, `url`, `title`, `category`). Show each link first as a numbered list with its category and a total ("2 related work links on Ledger 2.4"), mark the category as "Proposed", wait for a yes, create them one call each, and read the related work back to check the count. Everything else (moving items, changing the date, releasing) is the team's call: point to it, don't do it.

## Answer and offer an export

- Lead with the verdict, the Step 8 rule that decided it, the top blocker and who or what it waits on. Include the recorded release date and scope without forecasting a new date.
- Present readiness by area, named blockers with source links, the explicit outstanding-condition list and its count, open work and decisions needed with the people the records name. Retain the assessment's rules, rankings, caps and uncertainty, and distinguish missing evidence from a failed check. Explain every Not used area with the record or explicit user confirmation that establishes it.
- Before answering, check that every area has a state and the third-party pass ran. In Sources and limitations, name any that did not run and why, and retain the sampled work, deployment coverage, graph gaps and caps required by the report's sources footer.
- After the answer, offer the related-work link write if Step 5 found eligible docs, following Writes, and `/dependency-map` when the full dependency picture would help. Neither action requires an HTML export.

Ask whether the user wants this exported to an HTML report. If they have already explicitly requested an export, HTML report or publication, proceed with that requested build without asking again. Otherwise stop here until they answer; a normal invocation of this skill does not request a report. Follow the shared availability and confirmation checks before offering or performing publication.

## Step 9: Build the page (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in this folder:

```bash
python3 <this skill's folder>/render.py readiness.json release-<name>.html
```

- **The data** has the shape of `example.json` in this folder (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **Conditions are explicit.** Supply `conditions` as the same deduplicated list used for the verdict, or `[]` when none remain. Each entry has `id`, `areas` (the affected area names), `type`, `text` and its source links, using the shared row format. One entry represents one underlying condition; do not replace several with a grouped count. The renderer displays the entries and their count, while the skill supplies the assessed verdict. For a Not used area, put its positive applicability reason in the area's `text` and cite its evidence, or state that the user explicitly confirmed it.
- **Optional keys** left out of the example: `meta.datePassed: true` (adds "passed" to the release date), `noBlockers` (the line when there are no blockers, "No blockers recorded." by default) and `sourceLabel` on a blocker (the words before its source, "Evidence: " by default).
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `references/hand-built.md` in this folder.

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
