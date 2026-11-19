---
name: "decision-trace"
description: "Trace a decision to its records: what was decided, when, who decided, the options considered, and whether it was revisited or reversed. Uses Teamwork Graph to find decision pages, DACIs, registers, meeting decisions, Jira work items, project and goal highlights, Loom summaries and public chat, then reads records and version history. Answers in the conversation first with source wording, a dated timeline, deciders and gaps. Offers the existing HTML report on request and publication only when Atlassian Artifacts is available and requested. Use for why did we decide, who decided or signed off, what was decided, is it still current, or /decision-trace. For a period's changes, use catch-up. For behaviour in code, use how-it-works. For an expert, use whos-the-expert."
---

# Decision trace

Answer "why did we decide X?", "who decided?" or "what did we decide about X?" in the conversation for someone who wasn't there: a new team member, a stakeholder who's been asked to defend the decision, or a lead deciding whether to reopen it. In a few minutes they get what was decided in the record's own words, when, who the record names as the decider, the options it weighed, and whether anything since has reopened it.

Decisions are scattered. The record might be a decision page, a DACI table, one row in a register, a list in meeting notes, a Jira work item or a highlight on a project, and the discussion that led to it is somewhere else again. The value of this skill is the judgement a search results page can't make. It tells a recorded decision apart from a proposal and from talk, takes the decider only from a field that names one, dates when a status or the decision text actually changed, keeps a chain of related decisions apart instead of merging them, and says plainly when no record exists.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. Its "Content lost in markdown" and "Loom lists come back short" notes under "Product tools" matter most here. This file adds what's specific to tracing decisions.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## What this skill will and won't do

- **It reports what the records say.** The decision, its reasons and its options appear only as a record states them, quoted or closely paraphrased, with a link. It never fills a gap with what the decision probably was, and never quotes a decision from a search snippet: snippets can carry text that no version of the page holds.
- **It never infers who decided.** The decider comes only from an Approver, Decider or Accountable field, a register's approvers column, or a record that names who decides. Never from the page's author or owner, the person who edited the status or moved the work item, the most senior person in a meeting, or the exec sponsor. A process page that says "the approver moves it to Decision Made" doesn't make whoever moved it the approver. When no record names one, say "No decider recorded".
- **It doesn't judge the decision.** No view on whether it was right, and no recommendation to reopen it.
- **Sensitive decisions stay out.** Decisions about people (hiring, levels, reorgs, performance) and anything "Sensitive content" in `teamwork-graph-context` covers are never traced, even when the user names one. Say that this skill doesn't cover that kind of decision, and stop.

## Sensitive content for decisions

These add to "Sensitive content" in `teamwork-graph-context`.

- **Where decisions happen privately.** Real decisions are often made in direct messages, group messages and leadership channels. Leave them all out, even when they hold the answer: a Slack direct message (URL contains `/archives/D`, or a title with no channel name), a group message (channel name starts with `mpdm-`), and a channel whose name says leadership, exec, staff or board, or uses a word or abbreviation for them (`leaders`, `leads`, `lt`, `elt`, `slt`, `exec`), whether or not it shows as private: search results don't say. A Slack URL with `/archives/G` is a private channel, so its name needs the check too. Don't read, quote or count them. When any were left out, the footer says "Some results weren't used", and nothing more.
- **Documents written for leadership** (a leadership-team DACI, an exec review page) are usable decision records, unless they're marked confidential or restricted, or hold a category "Sensitive content" lists. The exec-only rule covers restricted channels and material marked as such, not every page a leader reads.
- **Comments and meeting notes** on a decision often carry customer revenue, deal sizes, headcount or named customers' staff. Drop those parts and keep the rest.
- **Calendar events** found by search are pointers to a meeting. Their snippets can hold dial-in passcodes, and their links encode an email address. Use the meeting's recording or notes if there are any. Otherwise name the event and its date in plain text, with no link or snippet.
- **One-to-one recordings:** a Loom meeting recording between two people counts as a private conversation, like a direct message. Leave it out. The list doesn't return participants, so judge by the title: "1:1", "1-1", "one on one", "mentorship", "coaching", or two names joined by "/", "|", "&", ",", "<>" or "and". The leadership words above apply to recording and event titles too.
- **Account labels:** drop "(Deactivated)" and similar suffixes from names.
- **Rejected options can name people** ("move Sam's team to…"). Describe the option by what it does, not by who it affects.

## Tool access and coverage

Load `teamwork-graph-context` first. Call tools directly when exposed. If a needed operation is not exposed and discovery is available, discover it and use the matching runner with its returned schema. Skip an operation only after checking the session's capabilities. Missing `products` metadata means unknown availability, not no access.

Use the full workflow when its tools are available. With Jira, Confluence and Rovo Search only, gather those records and use the fallbacks below. Keep unavailable, permission denied, successful empty results and checks not run distinct. List the impact of each gap in Sources and limitations. A Jira project is not an Atlassian Project.

## Find and read the decision records

Read [the records and history procedures](references/records-and-history.md) before searching or dating changes. Resolve the question, option or supplied record and any time bounds. Ask only when the intended decision is ambiguous. Use the bounded searches in the reference, following explicit links before broader search.

1. Find decision pages, Jira records, Projects/Goals updates and relevant discussion using the tools available in this session. If graph, Projects, Goals or Loom tools are unavailable, use Jira/Confluence/Search and report the missing coverage. Use Rovo `search` without a `mode` argument; use JQL and CQL for structured constraints.
2. Read the main records in full, with status, decision tables, named driver/approvers, alternatives, reasons, dates, explicit links and any superseding record. `getConfluenceContent` defaults to a summary; request `detail: "full"`. When `lostFeatures` or missing tables/panels hides decision evidence, re-read `content_format: "html"`. Confirm a classic page's approval/status separately from a live doc; do not assume the two provide the same approval metadata.
3. Date changes from actual evidence: decision log entries, version content and history, timestamped comments or recorded highlights. Follow the reference's bounded version probes and range rules. A page's last-modified date is not its decision date, and current live-doc version metadata may reflect the read time. If the precise change cannot be dated, show a range or Unknown.
4. Use the newest actual decision event as the main decision. Keep the initial decision, amendments, reversals and reopened proposals distinct. A later document edit does not itself supersede an earlier decision. AI meeting notes and discussion do not establish Decided without a recorded decider and decision.

## Expand and verify

Read [the related-evidence procedures](references/related-evidence.md) when following graph links, project/goal highlights or discussion. Use summary graph context first, then filtered full context for relevant relationships. Preserve the specified 90-day related-content bound and bounded sweeps. Read Projects/Goals highlights and updates with their DECISION filters when available; read Loom records around the decision date and recent period, with at most five transcripts when needed. Skip only the unavailable capabilities and disclose their impact.

For a Jira/Confluence-only session, follow explicit links, search the decision's distinctive terms and involved Jira keys, and use readable comment/history evidence. If `listConfluenceComments` is absent, use the CQL comment fallback in shared context and disclose incomplete coverage. A search hit can identify a possible discussion; it cannot prove a recorded connection, owner or decision.

## Assess

Read [the assessment rules](references/assessment.md) before assigning the decision state. Keep the exact state vocabulary, evidence requirements and conflict handling. State what was decided, by whom, when and why only when the record supports each part. Distinguish recorded alternatives and reasons from your inference. Show Unknown or No owner recorded for gaps.

Give a chronological trace with linked evidence for the original decision and each meaningful change. Explain conflicting records and whether a later event superseded or merely revisited the decision. Include unresolved questions and suggested follow-up, without contacting people or reopening work. In Sources and limitations, state queries, bounds, caps, inaccessible records, missing history and unavailable discussion sources. Answer in the conversation first.

## Writes

None. The skill is read-only. If no record exists, suggest in the reply that the decision be written down, and offer nothing more.

## Answer

- Lead with the verdict and the answer to the question as asked, using the record's words. State the newest decision, when it was decided, who is explicitly recorded as decider or that no decider is recorded, and whether it was reopened.
- Keep each decision in a chain separate. For each, show the source wording, date and how it is known, decider and how that is known, and other records of the same decision. Retain the later-wording, approval-date, revisit and newer-proposal qualifications from the report export reference's answer section.
- Present recorded reasons, options and their recorded dispositions when available, plus the dated timeline. Keep proposals and discussion separate from decisions and mark inferred relationships found by search.
- Include Not in the records and Sources and limitations: contradictions, missing deciders or dates, record/discussion counts, version ranges left open, search windows, HTML re-reads, Loom date coverage and caps. If no decision record was found, say so and suggest recording the decision; offer no write.


## Optional report

Answer in the conversation first. For a requested HTML report, read [the report export instructions](references/report-export.md) and run this skill's existing `render.py` with the bundled design assets. Preserve the same findings and limitations. Offer publication only after confirming the required tools and permission; a static export remains available when publication is unavailable.
