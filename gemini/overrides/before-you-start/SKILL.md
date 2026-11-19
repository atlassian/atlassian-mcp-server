---
name: "before-you-start"
description: "Before starting an idea, plan, or initiative, search Jira epics and issues, Confluence specs and docs, and Rovo Search to find who in the organization is already doing, or has previously done, something similar. Delivers a structured conversational readout with up to 4 overlapping efforts: what each record says it does, overlap class (Same, Partial overlap, Done before, Cancelled, Adjacent), recorded Jira/Confluence status and owner/author, linked vs search-found evidence kept separate, and a suggested move (Join, Differentiate, Reuse, or Talk) with a draft outreach message. Use for duplication checks, prior-art checks, or /before-you-start. For dependency mapping, use dependency-map."
---

# Before You Start

Give someone a crisp readout in the conversation before committing time to an idea: which other efforts in Jira and Confluence already do (or previously did) something similar, who owns or authored each one, how closely each overlaps, and what move makes sense next (talk to the owner, join existing work, differentiate scope, or reuse what was already built).

Two teams can build the same thing under different names for months, and a cancelled epic leaves no trace in the next team's plan. The value of this skill is finding efforts named differently from the idea, reading what their Jira and Confluence records actually say they do rather than judging by title alone, sorting them into explicit overlap classes, and turning each into a concrete suggested move with a contact from the records.

Load the `teamwork-graph-context` skill first and follow it for direct v2 tool usage, schema verification, source labeling, sensitive-content filtering, and conversational delivery. This file adds what is specific to finding overlapping efforts.

## What this skill will and won't do

- **It answers "is anyone already doing this?"** The input is always an idea, plan, or project. People appear only as recorded owners, assignees, or authors of an effort.
- **It never judges an effort or its people.** Classes describe overlap, not quality. Never claim an effort "failed" or was "abandoned" unless a person explicitly wrote that in a record. Never rank or describe people by seniority.
- **It excludes the user's own work.** Call `atlassianUserInfo` once solely to recognize and drop the user's own epics, issues, and pages (Step 3). Never show the user as an effort's owner or contributor.
- **It does not decide for the user.** Every move and draft outreach message is labelled **Suggested**; this skill is strictly read-only.
- **Unavailable scopes are reported transparently.** This Atlassian connector exposes Jira, Confluence, and Rovo Search only — it does **not** expose Atlassian Projects (Atlas), Goals, Loom videos, Bitbucket/code repositories, Compass components, Teams, reporting-line directories, or Atlassian Artifacts. Always state in Sources and limitations that those systems were not checked (unless a separate standalone session connector such as GitHub or Slack was used).

## Tool Access & Coverage

- **Needed:** Jira (`searchJiraIssuesUsingJql`, `getJiraIssue`, `listJiraIssueRemoteIssueLinks`, `getJiraUser`) and Confluence (`searchConfluence`, `getConfluenceContent`), plus Rovo `search` and `getAccessibleAtlassianResources` / `atlassianUserInfo`. Call `getAccessibleAtlassianResources` once for `cloudId` and the site base URL, then call Jira and Confluence tools directly (do not block on a `products` field).
- **Unavailable on this connector:** Atlassian Projects (Atlas), Goals, Loom, Bitbucket/GitHub code search, Compass, Teams, org-chart people directories, and Artifacts. Never attempt to call tools for these scopes; rely on Jira epics/issues, Confluence plans/specs/retros, and Rovo Search, and state those coverage gaps clearly in Sources and limitations.
- **Optional standalone session connectors:** If the user's session also exposes Slack, Teams, Google Drive, or GitHub connectors, you may optionally check them read-only for unrecorded discussions or repos (never reading DMs or private channels), labeling those hits by app.
- **Direct calls & live schema check:** Call every tool directly by name. If a tool is not in your tool list, it is not available on this connector; say so and use the closest available tool. Always check live tool schemas before passing parameters (especially cloudId/query/targetApp/limit for search (without mode), content_id/content_format/detail for Confluence reads, and explicit fields or view for Jira reads).

## Budget

Unless the user asks for a deeper pass, stay within these caps and report any cap reached in Sources and limitations:

| Tool | Cap | Where |
| --- | --- | --- |
| `search` (Rovo) | 6 | 4 in Step 2, 2 in Step 4 (echo pass) |
| `searchJiraIssuesUsingJql` | 4 | 2 in Step 2 (epics + general issues), 1 in Step 4 (echo pass), 1 in Step 5 (`key in (...)` batch for top epics) |
| `searchConfluence` (CQL) | 3 | 2 in Step 2 (plans/designs/specs/retros), 1 in Step 4 (echo pass) |
| `getConfluenceContent` | 6 (+2 HTML re-reads) | Step 5 (and Step 1 anchor read if user supplied a Confluence URL) |
| `getJiraIssue` / `listJiraIssueRemoteIssueLinks` | 4 | Step 5: linked specs/docs on top Jira epics |
| `getJiraUser` | Up to 6 | Step 6: only if an assignee/author is returned only as an account ID |

Send independent calls within each step in parallel.

## Step 1: Frame the idea

1. Call `getAccessibleAtlassianResources` once for `cloudId` and the site base URL, and `atlassianUserInfo` once for the current user's account ID and display name.
2. **If the user supplied a record** (a Confluence URL or Jira key), read it first with `getConfluenceContent` (`content_format="markdown"`, `detail="full"`) or `getJiraIssue` (using explicit `fields: ["summary", "description", "status", "assignee", "reporter", "issuelinks"]`). Use it to frame the idea and extract terms; keep that record as the idea's anchor rather than listing it as an overlapping result.
3. **Restate the idea** in one sentence as the user would explain it to another team, and extract up to three **facets**:
   - **Outcome:** what it produces and for what purpose ("a daily summary of work changes so nothing is missed")
   - **Audience:** who it is for ("individual knowledge workers")
   - **Mechanism:** how it works and is delivered, if stated ("an agent reading Jira and Confluence and posting a summary")
   Leave unstated facets blank; do not invent them. Step 7 compares only non-blank facets.
4. **Build 5 short search terms:**
   - The **user's own name** for the idea if given (keeping product/AI terms if part of the name)
   - The **core name**: the shortest distinctive 2-word phrase ("daily brief", "overlap detector", "agent skills"; avoid generic single words like "brief" or "report")
   - A **"what it does" phrase** in plain words ("summary of my day")
   - **2 synonyms** another team might use, including one tool/actor phrasing ("brief bot", "readiness checker")
   Do not use bare company, product-family, or version words ("Jira", "Rovo", "v2", "AI") as standalone terms unless the idea is specifically built for that product.
5. If the idea is too vague to have an outcome ("something with AI"), ask for one sentence on what it would produce before searching.

## Step 2: Sweep

Send these in parallel (using cloudId and query, with optional targetApp and limit, without mode):

- **`search`** x2: user's own name (or core name), and the "what it does" phrase.
- **`search`** x2: actor synonym, and `"<core name> design plan spec"`.
- **`searchJiraIssuesUsingJql`** (Epics): `issuetype = Epic AND (summary ~ "\"<core name>\"" OR summary ~ "\"<synonym 1>\"" OR summary ~ "\"<synonym 2>\"") ORDER BY updated DESC`, with `fields: ["summary", "status", "project", "assignee", "reporter", "resolution", "resolutiondate", "updated"]`, `maxResults: 20`.
- **`searchJiraIssuesUsingJql`** (Broad fallback if epics are sparse): `(summary ~ "\"<core name>\"" OR description ~ "\"<core name>\"") AND issuetype != Sub-task ORDER BY updated DESC`, same fields, `maxResults: 20`.
- **`searchConfluence`** (CQL) x2:
  - `type in (page, blogpost) AND (title ~ "<core name>" OR title ~ "<synonym 1>") ORDER BY lastmodified DESC` (`limit: 20`)
  - `type in (page, blogpost) AND text ~ "\"<core name>\"" AND (title ~ "plan" OR title ~ "design" OR title ~ "spec" OR title ~ "RFC" OR title ~ "PRD" OR title ~ "proposal" OR title ~ "retro") ORDER BY lastmodified DESC` (`limit: 20`)

Report any search warnings in Sources and limitations.

## Step 3: Filter and cluster

Work through all hits in this order:

1. **Drop sensitive results first** per "Sensitive content" in `teamwork-graph-context` before reading full bodies (calibration, promo/review packets, comp, PIP, HR/legal, customer financials/contracts, exec-only/DM snippets). If any were dropped, add only "Some results were not used" to Sources and limitations.
2. **Exclude the anchor and confirmed own items.** Drop the user's supplied anchor record, plus Jira items where the user is assignee or reporter and Confluence pages created/owned by the user (matched against `atlassianUserInfo`). Count confirmed own items dropped in Sources and limitations ("N of your own items were left out").
3. **Keep efforts where the user is merely a contributor/mentioned** under another owner, marking them **"You are already connected"** (so the draft message reads as a follow-up, not a cold intro).
4. **Cluster hits into distinct efforts.** Group records that link to each other (Jira epic + children + remote Confluence links, or Confluence pages sharing a distinctive name and space/author) into a single effort. Do not merge unrelated efforts that merely share generic words; keep a newer distinct phase separate unless records explicitly show a continuous line of work ("builds on X", "Phase 2 of X"), in which case show the active record as primary and older shipped phases under "Earlier phases".
5. **Keep Linked vs Found by search separate** for every item attached to an effort.
6. Keep up to **8 candidates** (prioritizing Jira epics and Confluence specs/plans whose snippets match the idea's outcome, then recency).

## Step 4: Echo pass

Because other teams often use different names, pick up to **2 promising candidates** found only via a page or snippet (with no Jira epic yet, or hinting at another internal codename) and run targeted follow-ups using *their* distinctive vocabulary:
- One `search` with the candidate's own name plus a distinctive word from its snippet.
- One `searchJiraIssuesUsingJql` (`issuetype = Epic AND summary ~ "\"<candidate name>\""`) or `searchConfluence` (`title ~ "<candidate name>"`).

Apply Step 3 to the new hits. If every top candidate already has clear Jira and Confluence records, skip this step and note `"Echo pass: Not run (every candidate already had a clear record)"` in Sources and limitations.

## Step 5: Confirm the top efforts

Rank candidates using available snippets (per Step 7), then read full records for the **top 4** in parallel:

- **Jira Epics / Issues:** Batch `searchJiraIssuesUsingJql` with `key in (...)` and `fields: ["summary", "description", "status", "assignee", "reporter", "resolution", "resolutiondate", "issuelinks", "project", "updated"]`. Also call `listJiraIssueRemoteIssueLinks` on top epics to find linked Confluence design docs or specs (linked evidence!).
- **Confluence Pages:** Call `getConfluenceContent` (`content_format="markdown"`, `detail="full"`, checking live schema for `content_id` vs `contentId`). Re-read with `content_format="html"` if `lostFeatures` lists `time` or `ac:structured-macro` / `ac:adf-extension` and key content is missing. Capture what the effort actually does, any in-body Status line, and named owners/DRIs.
- **Stop gathering** once each of the top 4 efforts has a confirmed description of what it does from its own records, a recorded status, and an owner/author (or confirmed absence of one).

## Step 6: Identify owners and authors

- **Owner:** Use the epic assignee, or a person explicitly named in a Confluence page as Owner, DRI, Driver, Lead, Accountable, or PM. Label them **Owner**.
- **Fallback:** If no owner is recorded, use the Jira reporter or Confluence page creator/author, labelled **Created by** or **Wrote**.
- If a record returns only an account ID without a display name, resolve the display name via `getJiraUser` (up to 6 calls). Never show email addresses, job titles, departments, or locations.
- If an account is marked inactive/deactivated, drop it silently and list up to 2 active recent editors/contributors instead, or state **"Owner not available"** / **"Owner not recorded"** and point to the Jira project or Confluence space.
- Never show the requesting user as an owner or contributor.

## Step 7: Assess

### Overlap evaluation

An effort overlaps **only when its own records say so** — never from a title match alone. Compare its documented behavior against the non-blank facets from Step 1:
- **Outcome:** full match (1) = same deliverable for same purpose; partial match (0.5) = same deliverable for another purpose, same purpose via different deliverable, or same capability for a different consumer.
- **Audience:** full match (1) = same users or teams.
- **Mechanism:** full match (1) = same approach and delivery; partial match (0.5) = one part matches.

Record the **main difference** in one short phrase (or "none found"). Any candidate whose description could not be read or that matched only on title goes into **"Names that matched, not checked"** (up to 3, with no overlap class).

### Status

- **Jira:** Use the issue's workflow status and resolution.
- **Confluence page:** Use any explicit status line in the page ("Status: In progress"); otherwise treat pages edited in the last 90 days as active ("Page · edited [date]") and older pages as inactive. A page documenting a shipped feature ("User Guide", "Getting Started", "Release Notes") counts as shipped (**Done before**).

### Overlap classes (pick the first match)

| Class | Criteria |
| --- | --- |
| **Cancelled** | Jira resolution is Won't Do, Declined, or Duplicate (or status Cancelled), and outcome matches fully or in part |
| **Done before** | Jira status is Done/Resolved (not cancelled), or a page says it shipped, outcome matches fully or in part, and no active successor exists |
| **Same** | Outcome matches fully, every other stated facet matches fully, and no conflicting audience is recorded |
| **Partial overlap** | Outcome matches in part, or fully with a different audience, scope, or delivery |
| **Adjacent** | Outcome differs, but mechanism or audience matches so parts or users could overlap |

Drop anything that fits none of these classes. Never assume a Cancelled item "failed" unless a person recorded why in a comment or page.

### Ranking

Rank only efforts confirmed in Step 5:
1. Most matched facets (full = 1, partial = 0.5)
2. Active before paused/inactive, paused before Done/Cancelled
3. Class order: Same -> Partial overlap -> Done before -> Cancelled -> Adjacent
4. Efforts with a recorded owner/author before those without
5. Most recently updated first

Show at most **4** efforts (ensuring the closest active effort is included if any exist; mention any additional qualifying efforts as "and N more" in Sources and limitations).

### Suggested move (one per effort, with evidence-based reason)

| Class | Move | Exception |
| --- | --- | --- |
| Same (active, with owner) | **Join** — work is already moving; offer to contribute | If paused, inactive, or unowned -> **Talk** |
| Partial overlap | **Differentiate** — align on scope boundary using the main difference | If in progress and covers most of the outcome for the same audience -> **Join**; if inactive with a written design -> **Reuse** |
| Done before | **Reuse** — build on what shipped or was learned | If no reusable page/doc/artifact is recorded -> **Talk** |
| Cancelled | **Talk** — ask the owner what happened before repeating it | — |
| Adjacent | **Reuse** if a shipped component fits | Otherwise **Talk** |

### Headline & Verdict

- Headline: **"Before you start: N efforts to know about"**
- Verdict:
  - **Someone is already on this:** at least one active **Same** effort, or any effort with move **Join**
  - **Related work exists:** efforts found, but none is an active Same or a Join
  - **Nothing close found:** zero overlapping efforts found (never claim nothing exists — list the exact terms searched and suggest 1–2 alternative names to try)

## Writes

None. This skill is strictly read-only. Do not create tickets, post comments, or message anyone.

## Conversational Answer Structure

Deliver the complete readout directly in Markdown:

1. **Header & Verdict:** Headline, verdict, and the restated idea in one sentence.
2. **Overlapping efforts (up to 4, ranked):** For each effort:
   - Main record Markdown link, **Overlap class**, and recorded **Status**
   - One sentence on what its records say it does, matched facets, and **Main difference**
   - **Owner / Author** label (and up to 2 contributors if relevant; plus "You are already connected" if applicable)
   - **Suggested move** (`Join` / `Differentiate` / `Reuse` / `Talk`) with a 1-line reason grounded in records
   - **Linked evidence** and **Found by search** lists kept clearly separate with Markdown links
   - **Earlier phases / Next phase** if part of a line of work
3. **Suggested first message** (omit if Nothing close found): One short, natural draft message labelled **Suggested** addressed to the top effort's owner/author (written as a colleague follow-up if already connected). Do not send it.
4. **Names that matched, not checked** (only if any): Up to 3 title-only or unread candidates with links and statuses.
5. **Sources and limitations:** Exact Atlassian tools and search terms used (including echo pass), candidate/shown counts, user's own items excluded, any caps reached, "Some results were not used" if sensitive hits were dropped, and the explicit statement that **Atlassian Projects (Atlas), Goals, Loom, Compass, Teams, and code repositories are not exposed on this connector** and were not checked. Mention `dependency-map` if mapping Jira dependencies would help next.
## Optional offline report

Answer in the conversation first. When the user requests an HTML report, read [the report export instructions](references/report-export.md), load atlassian-design, and run the bundled render.py from this skill directory using its example.json and data-format reference. Preserve the same facts, verdict, condition count and coverage gaps in the report. Both design kits run offline with Python's standard library; do not install packages or download assets. Export does not authorize publication or sharing. Return static HTML when publication tools are unavailable.
