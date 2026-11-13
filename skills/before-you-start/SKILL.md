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

## Connectors

- **Needed:** Projects or Jira, at least one, for efforts with owners and status. Confluence, for the plans, designs and retrospectives that say what an effort does. With neither Projects nor Jira on the site (see "Atlassian apps on the site" in `teamwork-graph-context`), say so before building: efforts can only come from docs and chat, and owners from authors.
- **Helpful, from Atlassian:** Loom, for demos of work already built. Bitbucket, for repositories and pull requests. Goals, for the goal an effort contributes to. Compass, for internal tools registered as components.
- **Helpful, from other tools:** Slack or Teams, where efforts are often announced or discussed before they have a record. Google Drive or SharePoint, for plans and decks. GitHub or GitLab, for prototypes and internal tools.
- **Vendor connectors,** as `teamwork-graph-context` describes: Slack or Teams, to read a public channel thread when an effort's only owner signal is a snippet. GitHub, to read a repository's README or pull request author when the graph returns it empty (`raw: {}`). Never read direct or group messages through them.

## Budget

Unless the user asks for a deeper pass, stay within these, and say in the footer if one was reached:

| Tool | Cap | Where |
| --- | --- | --- |
| `searchProjects` (through `discover` and `executeRead`) | 4 | 2 in Step 2, 2 in Step 4 |
| `search` | 6 | 4 in Step 2, 2 in Step 4 |
| JQL (`searchJiraIssuesUsingJql`) | 2 | 1 in Step 2, 1 in Step 5 |
| `getGraphContext` | 4 | Step 5, one `full` call per top effort |
| Product reads | 8 calls | Step 5: `getProject`, `getConfluenceContent`, `getLoomVideo`, a code or README read, and `getGraphObject` (one batched call counts as one) |
| `getPeopleInfo` | 2 | Step 6, batches of up to 10 account IDs |
| `listArtifacts` | 1 | Step 1, the user's own Artifacts |

`search`, `getGraphContext` and `getPeopleInfo` use Rovo credits. A typical run makes 22 to 30 calls, including one `discover` for each operation reached through `executeRead`.

Calls in the same step that don't depend on each other go out together, as "Fetch in parallel" in `teamwork-graph-context` describes: the whole sweep in Step 2, the echo pass in Step 4, and the reads in Step 5. Send at most 4 `getProject` calls at once: on real data a read straight after a batch of 7 returned 429.

## Step 1: Frame the idea

1. Call `getAccessibleAtlassianResources` once for the `cloudId` and the site's `products` list, and `atlassianUserInfo` once for the user's account ID. If `artifacts` is in the `products` list, run `listArtifacts` (through `discover` and `executeRead`) with `limit: 100`, and keep the IDs and titles: search returns an Artifact's author as a third-party identity, not an account ID, so this is the only way to recognise the user's own.
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

- **`searchProjects`** x2 (through `discover` and `executeRead`), with `query` set to the core name and then the user's own name (or, if they gave none, the actor synonym), and `limit: 20`. It matches the words of project names closely, and plurals and longer phrases often miss: on real data "daily brief" found 7 projects, "morning brief" found none, and "video overlay" missed two projects named "Overlays". Don't filter by status: done, paused and cancelled projects are part of the answer.
- **`search`** (STANDARD, `targetApp: ALL`, `limit: 20`) x2, with the user's own name (or the core name) and the "what it does" phrase. `search` finds project records that `searchProjects` misses: a hit whose URL is a project (`/project/`) counts as a project record, the same as one from `searchProjects`.
- **`search`** (STANDARD, `targetApp: THIRD_PARTY`, `limit: 20`) with the actor synonym.
- **`search`** (STANDARD, `targetApp: CONFLUENCE`, `limit: 20`) with the core name plus "plan" or "design" ("daily brief design").
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
  - one `search` (STANDARD, `targetApp: ALL`, `limit: 20`) with the effort's own name plus one distinctive word from its snippet
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

## Step 7: Assess

### Is it about the idea?

An effort overlaps the idea only when its **own records** say so, as Step 5 defines them: a project description or update, an epic description, a page or doc body, a README, a Loom description, or a search snippet of that body. Never infer an overlap from a title match alone. Compare what it does with the facets from Step 1 that aren't blank:

- **Outcome matches** when the effort produces the same kind of thing for the same purpose. It matches **in part** when only one of those holds: the same thing for another purpose, the same purpose served another way, or the same capability built for a different consumer (a merge pipeline that feeds another product).
- **Audience matches** when it's for the same users or teams.
- **Mechanism matches** when it works the same way and is delivered the same way (the same sources, the same kind of agent, the same channel). Compare delivery only when the user gave a mechanism. It matches in part when one of its two parts does ("AI-generated" but baked into a file, not "shown while it plays").

Count a full match as 1 and a match in part as a half, for ranking. Write down the **main difference** in one phrase ("runs once a week, not on every change", "for support leads, not every user"), or "none found". The card shows it.

A candidate whose description you couldn't read, or that matches only on its title, goes in "Names that matched, not checked" (up to 3), with its record's status and no class.

### Status

- **Projects** use Pending, On track, At risk, Off track, Paused, Done and Cancelled, with phases Pending, In progress, Paused and Done.
- **Jira** uses its workflow statuses and resolutions.
- **A page, doc, repository or Loom** has no status field. Use its status line if it has one ("Status: In progress"). Otherwise, it's **active** if it was edited, or the repository had a merged pull request, in the last 90 days, and shows as "Page · edited Oct 2026". Older than that, it shows its date and is inactive.
- **Active** means Pending, On track, At risk, Off track, In progress, To do, or the 90-day rule above. Paused is inactive but not finished.
- **A page that documents a shipped feature** (a guide, "getting started", help or release notes) means the work shipped: the effort is Done before, however recently the page was edited.
- **Dates on developer docs and Artifacts** found by search are often crawl dates: treat them as unknown.
- **An effort with several records** takes its status from its main record. With no project or epic, it takes the newest date among its records.

Show the record's own status beside the class, in plain text ("Projects · Paused").

### Classes

One per effort. Decide in this order, and take the first that fits:

| Class | When | Lozenge |
| --- | --- | --- |
| **Cancelled** | The record's status is Cancelled, or a Jira resolution of Won't Do, Declined or Duplicate, and the outcome matches fully or in part | neutral |
| **Done before** | The record is Done, Completed or Resolved as Done, or a page or update says it shipped, and the outcome matches fully or in part, and nothing in the same line of work is still active | success |
| **Same** | The outcome matches fully, every other facet the user gave matches fully, and its records name no different audience. It may be active, paused or inactive | warning |
| **Partial overlap** | The outcome matches in part, or fully with a different audience, scope or delivery, or it covers part of the idea | information |
| **Adjacent** | The outcome differs, but the mechanism or the audience matches, so it could share parts or users | discovery |

Anything that matches none of these isn't an effort to know about: drop it.

**Cancelled is not failed.** Read who cancelled it:
- If the cancelling update was posted by a bot or automation (a creator with "bot" or "automation" in its name, or text such as "deemed abandoned", "cleanup process" or "closed due to inactivity"), the label is "Closed as inactive" in small text beside the lozenge. The record says nothing about why the work stopped. Never say it was tried and failed, abandoned or rejected. This holds for a bot-cancelled project in "Names that matched, not checked" too.
- Only say why work stopped when a person wrote the reason in an update or comment, and link it.

### Ranking

Rank the efforts checked in Step 5 by how closely each matches the idea. Only those checked efforts are eligible for the main results:

1. The number of facets matched, most first.
2. Then active before paused, and paused before done and cancelled.
3. Then by class: Same, Partial overlap, Done before, Cancelled, Adjacent.
4. Then efforts with an owner from a record before those without.
5. Then by the latest update, newest first.

Don't rank by an effort's size, its team, its owner's seniority, its project status colour or how many hits it got. Show at most **4** efforts. If any checked effort is In progress, the closest one is among them. Otherwise, if any checked effort is active, at least one active effort is. If more qualify, say "and N more" in the footer with their names as plain text.

### The move

One move per effort, with a one-line reason that cites its evidence:

| Class | Move | Unless |
| --- | --- | --- |
| Same, active, with an owner | **Join**: the work is already moving, so offer to contribute rather than start a second one | It's Pending, Paused, inactive or has no owner: then **Talk** |
| Partial overlap | **Differentiate**: agree with the owner where one effort ends and the other starts, using the main difference | It covers most of the idea's outcome, for the same audience, and is in progress: then **Join**. It's inactive and its plan or design is written up: then **Reuse** |
| Done before | **Reuse**: use what was built, or what was learned, before building again | Nothing reusable is linked or recorded (no repo, page, demo, or an update recording a launch or GA): then **Talk** |
| Cancelled | **Talk**: ask the owner what happened before repeating it | |
| Adjacent | **Reuse** when it has a shipped part the idea could use | Otherwise **Talk** |

With no owner, the move stays, and the reason names the channel or page to go through. The moves are suggestions. Write each reason from the records ("Same outcome and audience, in progress, update 3 days ago"), never from a guess about the people.

### Headline

- **"Before you start: N efforts to know about"**, where N is the number of efforts shown.
- The verdict lozenge, decided by rule:
  - **"Someone's already on this"** (warning): at least one Same effort that's active, or any effort whose move is Join.
  - **"Related work exists"** (information): efforts were found, but none is an active Same or a Join.
  - **"Nothing close found"** (neutral): no efforts. Show the terms searched and the apps covered, and the "Names that matched, not checked", so the user can judge the search. Never say nothing like it exists: say nothing close was found with these words.

## Writes

None. The card suggests a move and a first message, but the user acts on it. Don't message, follow, join, link, comment or create anything for the user.

## Answer and offer an export

- Lead with Step 7's headline and verdict, and restate the idea in one sentence.
- Show up to 4 efforts checked in Step 5, in the established ranking. For each, retain what its records say it does, its overlap class and main difference, recorded status, owner label and contributors, and the suggested move with its evidence-based reason. Keep Linked evidence and Found by search evidence separate, with ordinary Markdown links.
- Include the suggested first message when there is a top effort, labelled Suggested. Keep it as draft text; do not send it. Include names that matched but could not be checked, if any.
- In Sources and limitations, retain the searched apps and terms, echo-pass coverage, candidate and result counts, own-item exclusions, caps and gaps required by the report's sources footer. For Nothing close found, say which words were searched and suggest one other name the work might go by; never claim that no similar effort exists.

Ask whether the user wants this exported to an HTML report. If they have already explicitly requested an export, HTML report or publication, proceed with that requested build without asking again. Otherwise stop here until they answer; a normal invocation of this skill does not request a report. Follow the shared availability and confirmation checks before offering or performing publication.

## Step 8: Build the card (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in this folder:

```bash
python3 <this skill's folder>/render.py card.json before-you-start-<idea>.html
```

- **The data** has the shape of `example.json` in this folder (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **The keys.** `headline` is the h1 ("3 efforts to know about"), `verdict` the verdict lozenge and `idea` the idea restated in one sentence. Each of `efforts`, ranked, is `{"link", "class", "status", "does", "facets", "owner", "contributors", "move", "linked", "found", "earlier", "next", "note", "connected"}`: `class` the class lozenge, `status` the record's status line ("Projects · On track"), `does` the line on what it does, `facets` the matched facets and main difference, `owner` `{"name", "label", "team"}` labelled as Step 6 says (just `{"label"}` for "Owner not available" or "Owner not recorded"), `contributors` up to 2 names, `move` `{"label", "why"}`, `linked` up to 4 links and `found` up to 3, `earlier` and `next` the other phases, `note` the line for a bot-cancelled effort, and `connected` "You're already connected" when Step 3 or Step 5 found it. `message` is the suggested first message, left out for "Nothing close found". `unchecked` lists the names that matched as `{"link"}`.
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `references/hand-built.md` in this folder.

The rules below say what the renderer builds, and what each part of the data must hold.

### Sections, in this order

1. **Header** (not a card): eyebrow "Before you start", the headline as the page's only `h1` ("3 efforts to know about"), the verdict lozenge on the right, and the idea restated in one sentence under it in subtle text. Then, in small subtlest text: "Based on what each effort's own records say it does. The moves are suggestions."
2. **Efforts** (icon `project`): one row per effort, ranked. Each row:
   - the effort's main record as a smart link, the class lozenge, and the record's status in small subtle text ("Projects · On track")
   - one line on what it does, from its own records, with the matched facets and the main difference in small subtlest text ("Same outcome and audience · Main difference: for support leads only"). If the description came from tracked items or linked pages, say so ("From its linked work items")
   - the owner as a 24px initials avatar, name and team, labelled as Step 6 says ("Owner", "Owned by [team]", "Created by", "[Name] in Slack", "Owner not available", "Owner not recorded"), and up to 2 contributors by name
   - the move as a bold label with the reason after it ("**Join** · In progress with an update this week, and the same outcome and audience")
   - **Linked** evidence: up to 4 smart links connected to the record. **Found by search**: up to 3 smart links, with the dashed "Found by search" chip. Always two separate lists, each with its label, and leave a list out when it's empty
   - "Earlier phases" and "Next phase", for a line of work: the other records as smart links with their status
   - for a bot-cancelled effort, "Closed as inactive. The record doesn't say why." in small subtlest text
   - "You're already connected" in small text, if Step 3 or Step 5 found it
3. **Suggested first message** (icon `comment`): one message about the top effort, to its Owner, or else the person who created it or wrote it, or else its channel, naming the effort and the user's idea ("I'm about to start a daily summary for support leads. I saw Morning digest in Projects. Could we compare scope before I begin?"), in a quote block with a "Copy" button. Labelled "Suggested". When the user is already connected, write it as a follow-up between colleagues, not an introduction. Leave it out for "Nothing close found".
4. **Names that matched, not checked** (icon `search`), only if any: one line each, a smart link and its status, with "Title matches only. We couldn't read what it does."
5. **Sources footer** (not a card), as `teamwork-graph-context` describes: the apps searched, the terms searched (including echo searches), how many candidates were considered and how many efforts were shown, "N of your own items were left out", "Some results weren't used" when Step 3.1 dropped anything, whether the echo pass ran, any budget cap reached, and gaps such as owners from chat only or GitHub authors not available.

## When live

Static only. Finding efforts depends on open-ended search and on the sensitive-content judgement, which page code can't make. To refresh, run the skill again.

## Step 9: Deliver the requested report

- Hand over the requested HTML report. Offer a private, read-only Atlassian Artifact only when availability is confirmed as described in `teamwork-graph-context`, and publish only if requested. Exporting the report does not authorise publication.
- The result is for the user. Do not offer to share it with the owners shown in it; share only if the user asks and names who.
- Keep the verdict, evidence separation, suggested message and limitations from the conversational answer.
