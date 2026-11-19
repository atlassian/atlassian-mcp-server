---
name: "teamwork-graph-context"
description: "Shared context-gathering, source-labeling, sensitive-content filtering, event-dating, and conversational delivery method for Atlassian Jira, Confluence, and Rovo Search workflows. Loads before sibling Atlassian analysis skills (assess-release, before-you-start, catch-up, decision-trace, dependency-map) to ensure structured Jira and Confluence records are confirmed directly, every source is cited, sensitive content is excluded, unavailable product scopes are reported transparently, and writes always require explicit confirmation."
---

# Atlassian MCP context gathering

Gather candidates through search, then verify structured facts against the relevant product records. Load this skill before assess-release, before-you-start, catch-up, decision-trace and dependency-map. Keep recorded relationships separate from things merely found by search. Never invent facts, owners, dates, counts or source links.

## Tool access and scope

1. Reuse a known site hostname/URL as cloudId, or call getAccessibleAtlassianResources once when the site is unknown. Reuse its site URL and product information, but an absent products field means unknown, not unavailable. Product presence does not prove that this connector exposes every tool for it.
2. Call an operation directly when its exact name is exposed. Otherwise, when discover and an execution runner exist, discover a needed non-primary operation and use the returned name, inputs and read/write/destructive runner. Do not rediscover a primary tool.
3. Runner calls take name and inputs, with cloudId beside them. Inputs is a flat object. Operations such as getContentFormatGuide omit cloudId. On flat connectors, do not call nonexistent wrappers. If an operation is neither directly exposed nor discoverable, report it as unavailable.
4. Match the current operation's schema. Rovo search takes cloudId, query, optional targetApp and limit, without mode. Jira create uses issueType, priority and assignee (account ID); account lookup uses query. Confluence reads use content_id/content_url and detail="full" for a body; updates use contentId/contentUrl and a current snapshotToken for document edits. Format guides still use content-specific createConfluencePage/updateConfluencePage keys for documents.
5. A missing tool, a denied call, an empty successful read and an unperformed check are different results. State which happened. Stop after the same error twice; never bypass access controls.
6. Jira project records and Atlassian Projects (Atlas) are different entities. Do not silently substitute one for the other. Resolve people from recorded account IDs/names with available Jira tools; without a directory, do not invent manager or reporting-line information.
7. When listConfluenceComments is absent, searchConfluence CQL with type = comment AND container = <id> can find comment candidates. Use returned IDs with getConfluenceComment when available to read bodies. Disclose incomplete inline/footer comment coverage; search results alone are not proof that all comments were read.

## Gather context

Resolve the anchor, read its recorded relationships and source records, sweep for unlinked evidence, and stop at the calling workflow's scope and budget. For an unfamiliar operation, consult [the tool reference](references/tool-reference.md); use the live schema for exact inputs. Standalone session connectors may fill a named gap with source attribution. Do not load a host-specific live adapter in an offline sandbox.

## The context loop

1. **Resolve the anchor:**
   - Jira work item, epic, version, project, or board -> `getJiraIssue`, `getJiraProjectVersions`, `listJiraProjects`, `listJiraBoards` / `getJiraBoardSprintData`
   - Confluence page, live doc, database, or space -> `getConfluenceContent`, `getConfluenceSpace`, `searchConfluence`
   - Current user ("my work", "catch me up") -> `atlassianUserInfo`, `getJiraCurrentUser`, `getMyWork`, JQL `assignee = currentUser()`, CQL `contributor = currentUser()`
   - Topic or name -> `search` + targeted JQL/CQL; if two candidates are equally plausible, ask rather than guessing or merging.
   - If the anchor cannot be found, stop and say so.
2. **Read structured records:** Fetch linked children (`parent in (...)`), `issuelinks`, `listJiraIssueRemoteIssueLinks`, version related work, page contents, approvals, changelogs, and version histories as needed by the calling skill. Go at most two hops from the anchor unless the skill says otherwise, and state where you stopped.
3. **Sweep for unlinked context:** Run 2 to 4 focused `search` / CQL / JQL queries to catch relevant pages or issues that are not explicitly linked. Mark hits kept only via search as **Found by search**.
4. **Resolve people:** Use names directly returned by Jira/Confluence records, or call `getJiraUser` / `lookupJiraAccountId` when only an account ID is available. Activity shows involvement, not ownership — say "worked on" unless a record names an owner or approver. Never judge performance from activity, and never display email addresses.
5. **Know when to stop:** Stop when the calling skill's required facts (owners, statuses, dates, links, evidence) are covered or confirmed missing. If a call returns the same error twice, record the gap and move on; never try to bypass denied permissions.


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

## Evidence and dates

Read each record before making a substantive claim from it. Quote only the wording actually returned. Separate a record naming an owner or approver from activity showing involvement. Never infer performance or ownership from activity volume.

Use actual event times: Jira changelog created timestamps, comment timestamps, explicit creation/resolution dates, or the version that made a Confluence change. updated and lastmodified identify candidates; they do not prove when a decision or event occurred. A page created earlier and edited in the window is Updated, not New. Date-only end bounds include that whole day in the user's timezone.

Confluence Markdown can lose time elements and panels. Re-read important missing content as HTML when lostFeatures identifies time or structured macros, a heading is empty, or a snippet quotes missing text. Use HTML version diffs for changes in panels or dates. Preserve rich content when editing.

Read Jira link direction from type.inward/type.outward wording on the current issue, not inwardIssue/outwardIssue alone. Generic relates-to and duplicate links are not dependency edges. Keep cross-site keys separate and record unreadable ones. Batch independent reads and paginate until the intended scope is covered or a documented cap is reached. State caps and partial results.

Do not mark an event seen solely because the user is its assignee, reporter, creator or contributor. Confirm a dated action by that user after the event, or state that seen-state coverage is incomplete.

## Answer, export and write

Deliver the structured answer in chat first. Cite evidence with normal Markdown links and label recorded/linked versus found-by-search facts. End with sources and limitations: actual tools/apps checked, missing scopes, unreadable records, time/hop bounds, caps and search warnings. Mention filtered sensitive hits only as "Some results were not used".

Keep unavailable evidence as a coverage gap. In release assessments, an applicable missing code/deployment/Projects check remains a deduplicated condition; it cannot silently become Ready or Not used.

On a report request, load the calling workflow's report-export reference and atlassian-design. Run its packaged renderer from that skill directory using its data-format reference. Preserve the same facts, verdict and conditions in the HTML. Offline hosts use the bundled render_kit, render_kit_next, tokens, icons and logos. Never run npm/pip installs or network downloads there; static report export remains available.

Before a write, read current state and show the exact proposed change. Act within the user's authorization; obtain confirmation for a write the user has not authorized. Export does not authorize publishing or sharing. Offer Atlassian Artifacts only if its operations are actually available; otherwise return the report file. Never run a presigned upload or host-specific live-artifact adapter in an offline host.
