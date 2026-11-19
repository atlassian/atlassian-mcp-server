# collection

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

## Budget

A release can hold a hundred items, so every step states its cap. In total, unless the user asks for a deeper pass:

| Tool | Cap | Where |
| --- | --- | --- |
| `getJiraProjectVersions` | 2 | Step 1: the version, and one name lookup in its project |
| `getJiraProjectVersionRelatedWork` | 1 | Step 1 |
| JQL | 10 | 1 in Step 1 (name lookup), 4 in Step 2 (the release's items, flagged items, epics' children, unversioned siblings count), 1 in Step 3 (open items with links), up to 3 in Step 3 (other projects' upstream items, one per project key), 1 in Step 6 (open work shown) |
| `getJiraIssue` | 5 | Step 3: Blocked or flagged items |
| `listJiraIssueComments` | 5 | Step 3: blocker reasons; reuse each issue read |
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

1. **Setup:** `getAccessibleAtlassianResources`; call exposed version/Projects operations directly. If needed and discovery is available, discover "jira project version" (both version operations) or "get atlassian project" once. Skip unavailable Projects enrichment with a coverage condition.
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
6. **The project behind it,** if Projects tools are available. Find it from the work, not by name, because a release name is often too generic to search (on real data, a release name matched 20 projects):
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
4. **Blocked and flagged items:** for up to 5, ranked as Step 8 ranks blockers, read `getJiraIssue` with `fields: ["summary", "status", "issuelinks", "updated", "assignee"]` and read the reason with `listJiraIssueComments`. Take the reason only from the latest comments that say what it's waiting on, even when they predate the move to Blocked, and say when ("from a comment on Aug 14"). Paraphrase in at most 20 words, never quote, and keep any URL a comment gives (a ticket, a thread, a page) as the evidence link. Comment authors come with email addresses: never show them.
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
   - `search` (`targetApp: CONFLUENCE`, `limit: 20`) with the release name plus "rollout plan"
   Read up to 3 with `getConfluenceContent` (`detail: outline` first, `full` only for a rollout plan or test plan whose outline has a checklist, status or sign-off table): related work items first, then pages a record links, then search results whose title names the release. From a read, take the page's status, its sign-offs or checklist state, the date, and any decision table. Docs found only by search are marked Found by search.
2. **Deployments:** for up to 3 Done or In review items with merged pull requests, `getGraphContext` with `relationshipTypes: ["jira_work_item_links_external_deployment"]`, `detailLevel: full` and `first: 50`, paging with `after` while `hasNextPage` is true, up to 5 deployment calls in all (each page counts). A work item's deployment edges include deployments of other items' pull requests that went out in the same pipeline run, and come back oldest first. So keep only deployments whose title names one of the item's own pull request numbers ("pull request #128") or the item's key, then hydrate up to 25 of those, newest first (the end of the list), in one `getGraphObject` batch, spread across the items. Each deployment carries `environment.type` (DEVELOPMENT, TESTING, STAGING, PRODUCTION), `state` (SUCCESSFUL, FAILED, IN_PROGRESS, ROLLED_BACK), `createdAt`, `lastUpdatedAt` and the pipeline. Per item, report the furthest environment type with a SUCCESSFUL deployment, and any FAILED or ROLLED_BACK one newer than it, naming its environment ("prod-west: failed Oct 14"). That newer failure is a Failed deployment finding and a Rollout condition. An IN_PROGRESS deployment more than a day old whose `lastUpdatedAt` equals its `createdAt` is stuck reporting, not running: ignore it. If none of an item's deployments name its own pull requests, say "No deployments of this item's own pull requests found" rather than using the others. This is a sample: say so ("Deployments checked for 3 items"), and say when `hasNextPage` was true.
3. **Testing evidence,** any of: a Testing release check that's Done (a task to write a test plan is a plan, not a test: it counts only with the plan itself); related work in a testing category; a test plan doc that a record links, or that names the release, an in-scope key or an in-scope epic (one found by search that doesn't is listed as Found by search and not counted); merged pull requests whose descriptions have a Testing section ("6 of 8 checked pull requests describe their testing"); a SUCCESSFUL deployment to a TESTING or STAGING environment; a project update (Step 2) that reports testing done or under way. With none, say "No test evidence found" in the Testing area. Never infer that testing happened from a status name.
4. **Rollout evidence,** any of: Rollout release checks and their status; a rollout plan or runbook doc and its status; related work in a rollout or documentation category; the furthest environment from item 2; the version's approvers and their status.
5. **Unrecorded blockers:** 2 `search` calls (`targetApp: THIRD_PARTY`, `limit: 20`): "[release name] blocked", and "[top blocker's key] [its summary's distinctive words]" when there's a blocker, or "[release name] go no-go" when there isn't. When the release name is only a number, a code or acronyms ("2.4", "ABC - XYZ"), use the summary words of the in-scope epic with the most items, with the release name taken out, in place of the release name, since acronyms match unrelated teams and customers. If nothing is left, use the top blocker's summary words. Keep a result only if its `lastModified` is in the last 14 days and its snippet says something is blocked, waiting, prevented or not ready, and names the release, an in-scope key, the release's distinctive term (two or more words of its name, leaving out version numbers and product or company words, such as "Ledger search" for "Ledger 2.4: search cutover"), or the top blocker's subject. Results that don't name the release or a key are marked Found by search. It's a Blocker with the source label "from Slack, not recorded in Jira". Drop sensitive results by title and snippet first, as `teamwork-graph-context` says. Comment links from Step 3 to Slack threads are read the same way, by snippet, when search returns them.

**Reviews by security, privacy or legal** (a security review ticket, a privacy assessment, a counsel sign-off) are shown as a check with its status, its owner as the record names them and its link. Never quote or summarise what the review found or asked for. When a blocker links a review page on this site, read it once with `getConfluenceContent` (`detail: summary`) for its status only, outside the 3-read cap. With no status on the page, show "Status not recorded on the page". Saying that an item waits on a review is allowed: that's the item's status, not the review's content. A review ticket on another site gets the one try that "Jira keys in text" in `teamwork-graph-context` allows, and is otherwise listed as unreadable.

## Step 6: Open work

One JQL query, only if the Step 2 result isn't already enough to list: the open items in scope, ordered as the page shows them. Up to 25 rows on the page: Blocked first, then In review, In progress and To do, then by most recent update. The rest are counted and linked as one JQL search ("12 more open items"). Show each item's own status name, its assignee's name and its due date if any.

## Step 7: People

Skip this step when every person on the page is already named by a record and no team is needed for the cross-team check. Otherwise one `getPeopleInfo` batch of up to 10 account IDs: the approvers, the assignees of blockers, and the owners of upstream items and projects. The version's driver comes back as a display name only, with no account ID: show the name as the version records it, with no team, and don't look it up. Use only the name and team. Never show emails, job titles or locations, and don't call with `manager: true`: a release decision goes to the people the records name, not up a reporting line.
