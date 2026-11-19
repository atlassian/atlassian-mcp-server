---
name: "teamwork-graph-context"
description: "Gather context for a skill from Teamwork Graph through the Atlassian Rovo MCP server, across Atlassian and connected third-party tools such as Slack, Google Drive, GitHub, Zendesk and Salesforce. Falls back on vendor connectors (such as Google Calendar, Gmail or Slack) where the graph has gaps. Labels every source, states every gap, keeps sensitive content out, and confirms structured relationships against product records. Load it from another skill before gathering context, follow that skill's delivery mode, and use its publishing guidance only when publication is requested."
---

# Teamwork Graph context

This is the shared method every skill in this repo uses to gather context and deliver its result. A skill loads it first, then adds what's specific to its job: the anchor, the sources it needs, what the artifact shows and when to stop. Where a skill and this file disagree, the skill wins.

Skill authors can use the [author checklist](references/author-checklist.md) when adding a workflow.

Companion skills mentioned as alternatives or next steps are optional. Check that a suggested skill is installed before offering its slash command. If it is unavailable, describe the next step in ordinary language and use the current host's available capabilities.

## Tool access

Read the session's tool list before planning calls. A v2 client can expose primary tools plus discovery/execution, or a flat list of direct operations (for example, a connection configured with `?tools=all`). These are presentation modes of the same operation schemas.

- Call an operation directly when exposed. Otherwise, if `discover` and execution tools exist, discover the needed operation and use its returned schema and matching read/write/destructive runner. Never send a flat direct call through an absent wrapper or assume an operation is unavailable just because it is not primary.
- Call `getAccessibleAtlassianResources` once and reuse the selected site's `cloudId`. Read `products` when returned; its absence means unknown availability. An app listing does not guarantee connector scope. Check exposed/discoverable tools and actual access. A permission denial is final; do not use another connector to bypass it.
- Use `atlassianUserInfo` once when the user identity is needed. Resolve account IDs with `lookupJiraAccountId(query=...)` or available people tools; never invent IDs or display emails.
- Rovo `search` uses `cloudId`, `query` and optional `targetApp`/`limit`. It has no `mode` argument. Use JQL/CQL for structured constraints and date windows. Read [the tool reference](references/tool-reference.md) when choosing operations, queries or graph relationship types.
- Jira creates use `issueType`, top-level `priority` and account-ID `assignee`; use `additional_fields` for supported native/custom fields. Jira read `view: "evidence"` is valid, but explicit `fields` avoids large custom-field payloads. Custom values can be under `fields.customFields`. Read Jira comment bodies with `listJiraIssueComments`; an issue read may only report their count.
- Confluence reads use `content_id` or `content_url`, `detail: "full"` and `content_format`; `include_metadata` is not supported. Re-read HTML when markdown loses panels, dates or tables. Read space instructions before writes. For `getContentFormatGuide`, content-specific keys remain `createConfluencePage`/`updateConfluencePage`; do not replace those guide keys with operation names. Document updates need the current `snapshotToken` and `body: {format, value}`.
- When `listConfluenceComments` is absent, use `searchConfluence` with CQL `type = comment AND container = <contentId>` and read returned IDs with `getConfluenceComment` if available. Paginate within budget and disclose incomplete comment coverage; the fallback does not establish a complete thread.

## Gather context

Resolve the anchor, read its product record, follow relevant explicit links, then search to fill specific gaps. Parallelize independent reads and stop when another call would not change a finding, owner, decision or action. Unless the calling skill sets a budget, cap search and graph-context calls at ten each. Record a repeated error and move on; never route around access denial.

Load [the graph procedures](references/graph-context.md) when graph tools are available. They retain relationship direction, hydration, product cross-checks and bounded context expansion. Prefer the graph for connected context when available; use an authorized standalone connector only for a known gap, including an unavailable graph operation. Keep its source and coverage visible.

For Jira dependencies, graph edges are candidates. Confirm with Jira's `type.inward`/`type.outward` wording: "is blocked by"/"depends on" is upstream, "blocks"/"is depended on by" downstream. Other relationships do not imply waiting. Project-to-project links come from `getProject`; `listJiraProjects` is a different entity and cannot replace it.

With Jira/Confluence/Search only, use those sources and linked records rather than stopping the skill. Preserve the broad workflow when more capabilities are available. Missing applicable PR, deployment, Projects or other evidence remains a gap, not proof of readiness or non-applicability. Never infer that a user saw an event from assignee, author or contributor metadata; that needs a confirmed timestamped user action after the event.

## Connector coverage

Report apps and operations actually checked. Distinguish unavailable on connector, not connected, permission denied, successful no results and not run with its reason. Omitted `products` metadata is unknown, not an unavailable app. A successful search with no hits describes only that scope. A tool failure or skipped check cannot support a no-results claim. Cite search warnings, caps, truncated results and unhydrated snippets, and state how each affects the answer.

## Optional reports and publication

Calling skills keep their delivery mode. Answer-first workflows give the conversational result before offering an HTML export. For an authorized report, load `atlassian-design` and use the bundled renderers and both design kits offline with Python's standard library. Do not install packages or fetch remote assets in an offline host.

Before publication or a live report, read [the publication procedures](references/publication.md). Confirm tools and site access without a test upload. Missing `products` metadata needs capability discovery, not an assumption. An export request does not authorize publication or sharing. If publication or the host's live APIs are unavailable, return the requested static report. Load host adapters only for their actual host.

## Principles

1. **Use the graph to discover and the records to confirm.** Start from one object in Teamwork Graph and walk its relationships. That's how you find connected work, docs and conversations across tools. For structured facts (dependencies and their direction, linked projects, owners, teams, statuses, dates), the product record is the source of truth. Cross-check, and say when the graph and the record disagree. "What the graph doesn't tell you" lists the known gaps.
2. **Keep sensitive content out.** Search can return HR, performance, legal and other confidential documents even for unrelated queries. Never quote, summarise, cite or title them anywhere. See "Sensitive content".
3. **Third-party sources are first-class.** A Slack thread, a Google Doc or a Zendesk ticket counts as much as a Confluence page or a Jira work item. Never call them fallbacks or rank them below Atlassian sources. Label where each fact came from; don't rank sources by vendor.
4. **Linked and found are different.** A relationship stored in the graph or a product record is confirmed. A search hit that looks related is inferred. Keep them apart in the reasoning and in the artifact.
5. **Never invent.** No made-up titles, owners, dates, statuses, quotes or numbers. If something can't be confirmed, say so.
6. **Say what's missing.** A source that wasn't connected, a search that returned nothing, a record that doesn't exist and a check you couldn't run are all results. Show them.
7. **Read-only by default.** Only write (create, edit, link, comment, post) when the skill's job is the write or the user asks, and confirm first.
8. **Fall back on vendor connectors for what the graph can't do.** When Teamwork Graph and the Atlassian product tools can't answer something a skill needs (a day's meetings, recent email, a full Slack thread), use the vendor's own connector if the client has one. See "Vendor connectors". This is about which tool to call, not how much a source counts: a fact read through a vendor connector counts the same as one from the graph.

## Sensitive content

Searches surface whatever the user can see, and that includes documents nobody wants in a status report. This rule overrides every skill.

- **Never use these, even when they match:** promotion, calibration or performance review material; training, certification or knowledge-check results that name people; compensation, salary, equity or offer details; disciplinary, PIP or termination records; medical, leave or other personal circumstances; legal holds, privileged advice or litigation; security incidents not yet disclosed; M&A, layoffs or other restricted plans.
- **Never use these either, unless the user asks for them:** private and group direct messages, and board or exec-only material. A Slack direct message's title has no channel name ("[Name] in #") and its URL contains `/archives/D`. A group message's channel name starts with `mpdm-`. A channel whose name says leadership, exec, staff or board, or uses a word or abbreviation for them (`leaders`, `leads`, `lt`, `elt`, `slt`), counts as exec-only material whether or not it's private, since search results don't show a channel's privacy.
- **Spot them early.** Titles and snippets often give them away: "calibration", "promo panel", "promotion packet", "level panel", level codes ("P50 to P60", "L4>L5"), "impact bar", "comp review", "PIP", "Knowledge Check" or "Responses" sheets with scores, "offer letter", "legal privileged", "confidential: do not forward". Don't hydrate a result that looks like one. A page that's otherwise ordinary (a runbook, a design doc) can end in a section that is its author's review or promotion evidence (a closing section headed "… evidence" that isn't test evidence, or one that maps the work to a competency or review criteria): drop that section silently and use the rest.
- **Linked records count too.** A legal or HR project linked to the work can be shown with its status, owner and dates, but never quote its advice or the reasons in its updates. A legal or HR record that's only found by search, such as a counsel review work item that matches the product's name, is left out.
- **When the work is itself a people programme** (a development programme, hiring, a reorg), nearly every result sits next to these categories. Use the programme's design, schedule, owners and actions. Never use participant or candidate lists, who was selected or removed, assessments, ratings, or anyone's level or role move. A notes doc, recording or chat message that mixes the two is usable: drop the sensitive items silently and keep the rest. Results whose titles name the programme (a participant page, a ratings sheet) need the check too. In a footer, say only "Some results weren't used".
- **Leave and absence:** never mention anyone's leave, sickness or time off, even when a work record states it. If it affects delivery, say "reduced capacity until [date]" without the reason.
- **Titles can leak too.** If an object's title contains a financial figure, personal data or an internal identifier (an org ID, an account number), cut that part with an ellipsis everywhere the title appears, including `title=""` attributes.
- **If you read one by accident,** drop it. Don't quote it, cite it, list its title, count it, or mention that it exists, in the artifact, your reply or any log. The one exception is a pilot run's log, which gives a count and how they were spotted, never titles, authors or content.
- **Personal data:** never include email addresses, phone numbers or home locations. Refer to end customers' individual staff by account and role ("Admin at Northwind"), not by name.
- **Customer financials** (revenue, ARR, deal size, renewal dates) appear only if they come from a connected CRM, and only when the skill's job needs them. Figures mentioned in chat or tickets stay out.

## Dating events in a window

For a skill that covers a window ("since the last update", "while I was away"), each item gets one **event time**, the moment the thing happened, from this table. An item is in the window only if its event time is.

| Source | Event time |
| --- | --- |
| Jira status, assignee, due date or priority change | The changelog entry's `created` |
| Jira work item created or resolved | `created` or `resolutiondate` |
| Comment (Jira, Confluence, Loom) | The comment's created time |
| Confluence page edit | The `createdAt` of the version that made the change. When a diff spans many versions and the change can't be pinned to one, show the range ("edited Oct 7 to Oct 21") |
| Project or goal update, or highlight | Its `creationDate` |
| Pull request | `mergedAt`, or `createdAt` for a new one |
| Meeting | Its start time |
| Loom recording | Its creation time |
| Third-party search result | `lastModified`, which is the last edit, so it can say "updated" but never "new" |

- **Jira's `updated` and a page's last-modified date are not events.** A bot, a resync or a later edit moves them. Use them only to pick candidates, then read the history for the event.
- **"New" needs a creation date inside the window.** A page created before the window and edited during it is Updated.
- **Date a page from its versions** (`listConfluenceContentVersions`), never from `getConfluenceContent` metadata: on a live doc, `version.createdAt` came back as the time of the read.
- **Items with no date** (a project with no update, a result with `lastModified: null`) aren't windowed. Judge them by their own record, and never present them as new.

## Labelling sources

- Every fact in the artifact links to the object it came from, as a smart link chip with the object's real title and, for third-party objects, the app's name ("Slack", "Google Docs", "GitHub"). Atlassian and third-party chips look the same. Icons follow `atlassian-design`. ADS has no third-party logos, so use the object-type icon (`comment` for a chat message, `hashtag` for a channel, `page` for a doc, `pull-request` for a PR, `calendar` for an event, `globe` for anything else).
- **Found by search** marks an item whose relationship to the anchor is inferred: it has a dashed border and a "Found by search" label inside the chip. When nearly everything in an artifact comes from search by design (a feedback explorer, for example), don't label every chip. Say once in the footer that items were found by search, and mark the few that are linked instead.
- When a work fact comes from chat, email or a call rather than a record, say so in the text ("according to Marco in Slack"). Colleagues can be named this way. End customers' individual staff can't (see "Sensitive content").
- The "Generated from" line under a summary lists the apps actually used, not a fixed list.
- Project and goal updates have no title. Show them as "[KEY] update, [date]" ("ATLAS-123 update, Oct 16, 2026").
- Every artifact ends with a sources footer showing:
  - the apps searched, as tags
  - apps or scopes confirmed unavailable, with the actual reason; omitted `products` metadata stays unknown
  - apps known not to be connected, as muted tags labelled "Not connected", and apps with no results, as "No results from"
  - a search or check you chose not to run, or couldn't, as "Not run: [reason]". Never write "weren't searched" without saying why. A skipped check is not a successful empty read; retain an applicable readiness gap with its reason
  - gaps from "What the graph doesn't tell you" that affected the result, checks that couldn't be run, and search warnings
  - the window searched, and how far the walk went
  - when the artifact was prepared, as a relative time plus the absolute date, time and timezone

## Copy

- No em dashes or en dashes in your own copy, and sentence case everywhere. Quotes and object titles are exempt: keep them as written, or trim with an ellipsis. The title trimming rule in "Sensitive content" still applies.

## Writes

- Read the current state first, then tell the user exactly what will change (which object, which fields, what text), and wait for a yes unless the request was explicitly to make that change.
- Prefer linking to duplicating. Use `addGraphContext` to connect work to projects and goals, and remote links to point Jira at third-party sources, instead of copying content across.
- After creating something, link it back to the sources that justified it.
- Resolve people to account IDs with `getPeopleInfo` or `lookupJiraAccountId`. Never guess an account ID.

## Mockups and sample data

When the user asks for a mockup, or gives sample data:

- Skip the context loop and use only what was given, filling plausible gaps.
- Add a small discovery-coloured note at the top: "Mockup with sample data. People, work and pages are made up."
- Use `#` for every link unless told otherwise.
