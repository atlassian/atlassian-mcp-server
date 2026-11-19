# discovery

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

## Budget

Unless the user asks for a deeper pass, stay within these, and say in the footer if one was reached:

| Tool | Cap | Where |
| --- | --- | --- |
| `searchProjects` | 4 | 2 in Step 2, 2 in Step 4 |
| `search` | 6 | 4 in Step 2, 2 in Step 4 |
| JQL (`searchJiraIssuesUsingJql`) | 2 | 1 in Step 2, 1 in Step 5 |
| `getGraphContext` | 4 | Step 5, one `full` call per top effort |
| Product reads | 8 calls | Step 5: `getProject`, `getConfluenceContent`, `getLoomVideo`, a code or README read, and `getGraphObject` (one batched call counts as one) |
| `getPeopleInfo` | 2 | Step 6, batches of up to 10 account IDs |
| `listArtifacts` | 1 | Step 1, the user's own Artifacts |

`search`, `getGraphContext` and `getPeopleInfo` use Rovo credits. A typical run makes 22 to 30 calls, including one `discover` for each operation reached through `executeRead`.

Calls in the same step that don't depend on each other go out together, as "Fetch in parallel" in `teamwork-graph-context` describes: the whole sweep in Step 2, the echo pass in Step 4, and the reads in Step 5. Send at most 4 `getProject` calls at once: on real data a read straight after a batch of 7 returned 429.

## Step 1: Frame the idea

1. Call `getAccessibleAtlassianResources` once for the `cloudId` and any returned `products` metadata (absence means unknown availability), and `atlassianUserInfo` once for the user's account ID. If `listArtifacts` is available and authorized, run it with `limit: 100`, and keep the IDs and titles: search returns an Artifact's author as a third-party identity, not an account ID, so this is the only way to recognise the user's own.
2. **If the user gave a record** (a page, a project, a Jira work item or a doc), read it first: `getConfluenceContent` (`content_format: markdown`, `detail: full`), `getProject` with `include: ["description"]`, or `getJiraIssue`. Use it to frame the idea and take the terms from it; supplying a record doesn't establish that the user owns it. Keep that record as the idea's anchor rather than a separate result. Assess its linked records individually in Step 3. This initial read doesn't count towards the product-read budget.
3. **Restate the idea** in one sentence, the way the user would explain it to another team ("a daily summary of what changed in my work, delivered each morning"). Then write down its three **facets**:
   - **Outcome:** what it produces, and what for ("a daily summary of changes, so nothing is missed")
   - **Audience:** who it's for ("individual knowledge workers")
   - **Mechanism:** how it works and how it's delivered, if the user said ("an agent reading their Jira, Confluence and chat, posted in Slack"). It can have two parts.
   A facet the user didn't give stays blank. Don't invent one. Assess compares only the facets that aren't blank.
4. **Build the term set,** 5 short terms:
   - the **user's own name** for the idea, exactly as given ("Beacon AI search tips"), if they gave one. Keep product and AI words in it: other teams often use the same name.
   - the **core name**: the shortest phrase that names the thing, usually two words taken from the user's own words ("daily brief" from "daily morning brief", "overlap detector", "agent skills"). Use a single word ("overlays") only when it's distinctive on its own: a common word such as "brief", "overlap", "report" or "agent" matches hundreds of unrelated things
   - a **"what it does" phrase** in plain words ("summary of my day")
   - **2 synonyms**: names another team would give it. Make one of them name the thing as a tool or actor ("overlap agent", "brief bot", "readiness checker"), because internal efforts are often named that way.
   Product, company, version and team words ("Rovo", "Jira", "v2", "AI") never count as terms on their own, and you don't add them to terms you make up. The exception: when the idea is built on or for a product ("skills for Teamwork Graph"), that product's name is part of the core name ("Teamwork Graph skills"), because without it the term matches every effort of that kind.
5. If the idea is too vague to have an outcome ("something with AI"), ask for one sentence on what it would produce. Don't search on a vague idea.

## Step 2: Sweep

Send all of these together, at most 2 `searchProjects`, 4 `search` and 1 JQL:

- **`searchProjects`** x2, with `query` set to the core name and then the user's own name (or, if they gave none, the actor synonym), and `limit: 20`. It matches the words of project names closely, and plurals and longer phrases often miss: on real data "daily brief" found 7 projects, "morning brief" found none, and "video overlay" missed two projects named "Overlays". Don't filter by status: done, paused and cancelled projects are part of the answer.
- **`search`** (`targetApp: ALL`, `limit: 20`) x2, with the user's own name (or the core name) and the "what it does" phrase. `search` finds project records that `searchProjects` misses: a hit whose URL is a project (`/project/`) counts as a project record, the same as one from `searchProjects`.
- **`search`** (`targetApp: THIRD_PARTY`, `limit: 20`) with the actor synonym.
- **`search`** (`targetApp: CONFLUENCE`, `limit: 20`) with the core name plus "plan" or "design" ("daily brief design").
- **JQL**: `issuetype = Epic AND (summary ~ "\"<core name>\"" OR summary ~ "\"<synonym 1>\"" OR summary ~ "\"<synonym 2>\"") ORDER BY updated DESC`, with `fields: ["summary", "status", "project", "assignee", "resolution", "resolutiondate"]` and `maxResults: 20`. Without the epic filter, it returns pages of unrelated tasks that share a word.

If `search` warns that some sources couldn't be queried, say so in the footer.

## Step 3: Filter and cluster

Work through every hit in this order.

1. **Drop sensitive results first,** as "Sensitive content" in `teamwork-graph-context` says, before reading anything else about them. This idea search reaches far, and on real data every sweep surfaced some. Leave out, without listing, counting in the card or describing them:
   - direct messages and group messages (a Slack title with no channel, a URL with `/archives/D`, a channel starting `mpdm-`)
   - calendar events, including their descriptions: they carry review feedback and one-to-one notes
   - performance, review, feedback, calibration and promotion material, even when the work it describes matches. This means people's promotions: a marketing "promo" project is ordinary work. Judge it from the search result's own snippet or description, without reading further, and drop it only if that is about people. A Loom transcript or page that mentions someone's level or review is used for what the work does, without that part
   - deal, contract, pricing and customer commercial documents (an order form, a quote, a renewal, a success plan), customer account or agreement channels, and anything else carrying customer financials
   - HR, legal, security-incident, board and exec-only material (a leadership or leaders channel, a board paper, an exec briefing). An "internal only" marking on ordinary work isn't sensitive: most work is internal
   If any result was left out for these reasons, the footer says "Some results weren't used", and nothing more.
2. **Exclude the idea's anchor and confirmed own items.** Leave the supplied record from Step 1.2 out as the idea being compared. Separately drop items the records identify as the user's own: a project they own, a work item assigned to or reported by them, a page or doc they wrote, an Artifact from the Step 1 list, a Slack message they posted, or a channel they started. A link from the anchor, or a matching channel name, isn't ownership evidence: keep other teams' efforts and candidates whose ownership is unconfirmed. Count only confirmed own items in the footer ("4 of your own items were left out"); an anchor with unconfirmed ownership doesn't enter that count. Never spend the echo pass on an excluded item.
3. **Efforts the user is already part of** stay, owned by someone else: the user contributes to the project, is a contributor on the page, or is mentioned in its updates. Mark the effort "You're already connected", and don't write the first message as an introduction.
4. **Cluster the rest into efforts.** One effort is one piece of work, however many records it has: a project and its epic, the epic's design page, the channel where it's discussed and its repository are one effort. Hits belong together when:
   - one links to another, or names the other's key, title or channel, or
   - they share the effort's distinctive name, and the author of one is the owner or a contributor of the other, or they share a team or a Confluence space.
   Don't merge two efforts because they use the same generic words. A newer plan with its own scope (a new feature on top of shipped work) stays a separate candidate, even when the same people wrote it.
5. **A line of work** is two or more projects for the same thing, such as a beta and a GA, or one product after another, that share a team, an owner or PM, or a project link. Show it as one effort, with one main record:
   - the In progress record (a page can be the main record), or if there's none, the newest active one. A new Pending record goes in the row as "Next phase". A project named for one discipline ("… Design", "… Eng") is a workstream of the main record, not the main record
   - the others go in the row as "Earlier phases", with their status. A shipped earlier phase keeps its own Reuse line in the row ("Reuse: Ledger digest, Done")
   - when a Done project's latest update names the work that continues it, or an active effort's own record says it carries on a done one ("builds on X", "continues X"), they're one line of work. Read the successor as the main record, if it's on the site
   When several projects match, pick the one whose description names the idea's outcome, not the newest.
6. **An effort needs a record or an artifact:** a project, an epic, a page, a doc, a repository, a Compass component or a Loom. A chat message on its own is not an effort, unless it names one ("we're building X in #channel"), in which case keep it as a candidate for the echo pass.
7. **Linked and found stay separate.** For each effort, note which items are linked to its main record (a graph edge, a project link, an issue link, a URL in its description) and which were only found by search. Keep that label on every item from here to the card.
8. Keep up to **8 candidates**: at most 5 whose main record is a project or epic, and the rest pages, docs, repositories or chat-named efforts, so the page-only efforts aren't crowded out. Within each group, prefer those whose snippet or description names the idea's outcome, then the most recently updated.

## Step 4: Echo pass

Efforts are often named differently from the idea, so a search with the idea's words finds a doc or a chat message about an effort but misses its record. An echo search reuses the effort's own vocabulary. On real data, this is what found the project record, owner and team of the hardest overlap, and the real names of efforts that the first sweep's generic words missed.

- Pick up to **2 candidates** with no project or epic yet (found through a page, doc, repo or chat only, or named in another record's text), ranked as Assess describes from what the snippets say. Skip pages that already cluster with an effort that has a project. For each, send together:
  - one `searchProjects` with the effort's own distinctive word plus its short form if it has one ("SM checker" for "Search migration checker"), as it appears in its title or snippet. If that's a term the sweep already searched, use another name the effort goes by, or spend the call on a `search` with `targetApp: CONFLUENCE` and the effort's name instead
  - one `search` (`targetApp: ALL`, `limit: 20`) with the effort's own name plus one distinctive word from its snippet
- Apply Step 3 to the results. A new record for the same effort joins it. A different effort that turns up joins the candidates, if there's room.
- If every top candidate already has a record, skip this step and say "Not run: every effort had a record" in the footer.

## Step 5: Confirm the top efforts

Rank the candidates as Assess describes, using what you have so far, and read the top **4**, or fewer if fewer could overlap. Send the reads together.

- **Project:** `getProject` with `identifier` set to the ARI or key, `include: ["description", "updates", "teams", "contributors", "goals", "links", "dependencies"]` and `limits: {updates: 3, teams: 5, contributors: 10, goals: 5, links: 10, dependencies: 10}`. The owner, status, phase, teams, goal, and the latest user update. When the description is only a URL to a page or doc, read that page as the description: it counts as one product read.
- **Epic:** one JQL for all of them together (this is the second JQL): `key in (...)`, with `fields: ["summary", "description", "status", "assignee", "reporter", "resolution", "resolutiondate", "issuelinks"]`. Read descriptions only for these.
- **Page:** `getConfluenceContent` with `content_format: markdown` and `detail: full`, for an effort whose only record is a page. Use the body to say what it does, and take its status line and its named owners from it.
- **Loom:** `getLoomVideo` without the transcript, for its title, description and owner. Read the transcript only when the description doesn't say what was built, and apply "Sensitive content" to it.
- **Compass component:** its owner team (resolve the team ARI with `getTeam`), shown as "Owned by [team]", and its state as its status. Use the description and links to say what it does.
- **Repository:** the owner, as "Code and repositories" in `teamwork-graph-context` describes (finding and reading a `CODEOWNERS`, manifest or README counts as one product read; brace globs in a path return a 400). Read a README to say what it does. A page that documents a repository clusters with it: its writer is "Wrote", and the owner comes from the repository.
- **Doc or other third-party object:** `getGraphObject`, batched. For a GitHub object that returns `raw: {}`, use the vendor connector or keep the snippet.
- **Graph,** one call per top effort's main record, with `detailLevel: full` and `relationshipTypes` for its type:
  - project: `atlassian_user_owns_atlassian_project`, `atlassian_user_contributes_to_atlassian_project`, `atlassian_project_contributes_to_atlassian_goal`, `atlassian_project_links_atlassian_project`, `jira_work_item_tracks_atlassian_project`. Atlas keys don't resolve here, so pass the project's ARI.
  - page: `atlassian_user_owns_confluence_page`, `atlassian_user_created_confluence_page`, `atlassian_user_contributed_to_confluence_page`
  - epic: skip the graph, because the JQL already gives its assignee and links
  Items it returns are linked evidence. If it shows a link between the effort and the user's own work, mark the effort "You're already connected".
- **Description, from the effort's own records:** what the main record says, plus the descriptions of work items that track it and pages its owner wrote that are linked to it. When the main record's description is empty or describes something other than its name, use the tracked items and linked pages, and say on the card which one you used.
- The product record wins over the graph for owners, teams and status, as "What the graph doesn't tell you" says. Don't trust a project update's `updateType`: on real data a bot's cancellation update was marked `USER`. Read the creator's name and the text instead.

**Stop gathering** when each of the top 4 has an owner and a status, and you can say what it does from its own records. One extra read is fine if it could change the top effort's class.

## Step 6: Bring in people

- `getPeopleInfo` with up to 10 account IDs per call, at most 2 calls: the owner of each effort, up to 2 contributors each, and the people who posted each project's latest updates, so an inactive owner's fallback needs no second call. No `manager` or `directReports`. Use only the name. It returns no team: take the team from the project's teams, and otherwise show none. Ignore job title, department, email and location, and never show them.
- **Owner** means a person a record names in a role that covers the whole effort: a project's owner field, an epic's assignee, a page owner, or a person named in the body as Owner, DRI, Driver, Lead, Accountable or PM. Page markdown gives names but not account IDs for mentions: match a name to an account ID already found, and otherwise show the name without checking whether the account is active. Say "Owner". A role that covers only a part ("Design driver", "Eng lead for the API") is a contributor.
- If no record names one, the person who created the record or wrote the page is shown as "Created by" or "Wrote". A person seen only in chat is shown as "[Name] in Slack" with the snippet's channel, never as owner.
- **Inactive accounts:** drop them without saying why. If the owner's account is inactive, show "Owner not available", and name up to 2 active contributors who posted the latest updates or edits. If nobody active is left, point to the record and its channel.
- **No owner at all** (a repository with blank authors and no `CODEOWNERS`): show "Owner not recorded", and give the channel or page to ask in, if there is one.
- The user is never shown, even as a contributor.
