# Atlassian Rovo MCP Server skills

The skills in this directory target the **Atlassian Rovo MCP v2** endpoint,
`https://mcp.atlassian.com/v2/mcp`. They are what every packaged plugin installs, and each one
lives at `skills/<name>/SKILL.md` per the [Agent Skills](https://agent-plugins.org/) convention.

## Teamwork Graph workflows

These workflows answer in the conversation first. They offer an HTML report when requested,
and check whether Atlassian Artifacts is available before offering publication. Results depend
on the user's permissions, available Atlassian apps, and connected sources.

| Skill | Use it to |
| --- | --- |
| [`assess-release`](assess-release/SKILL.md) | Assess release readiness, blockers, and outstanding conditions. |
| [`before-you-start`](before-you-start/SKILL.md) | Find similar efforts and their recorded owners before starting work. |
| [`catch-up`](catch-up/SKILL.md) | Review decisions, changes, and work needing attention during a specified period. |
| [`decision-trace`](decision-trace/SKILL.md) | Trace a decision, its alternatives, and later changes to source records. |
| [`dependency-map`](dependency-map/SKILL.md) | Map dependencies, their direction, and blocked or at-risk work. |
| [`how-it-works`](how-it-works/SKILL.md) | Explain product behavior from connected source code and supporting records. |

The workflows share [`teamwork-graph-context`](teamwork-graph-context/SKILL.md) for context
gathering and [`atlassian-design`](atlassian-design/SKILL.md) for optional report exports.
Both dependencies are included in the package, along with the report renderers, examples,
and design assets. The included live-artifact adapter applies only to its named host;
other hosts use their documented capabilities or the static report fallback.

## Archived v1 skills

The previous generation is archived in [`v1/`](v1/), unchanged, for anyone still pointed at a v1
endpoint (`/v1/mcp/authv2` or `/v1/mcp`). **No plugin installs the archived skills** — plugin
discovery only looks one level deep for a `SKILL.md`, so `v1/` is skipped. Set them up manually if
you need them.

## What changed between v1 and v2

A skill written for one generation will fail against the other. The most consequential differences:

* **Not every tool is directly callable.** v2 exposes a small set of *primary* tools in the
  client's tool list; the rest are reached through the `discover` and `execute` meta-tools. Each
  skill that needs one explains the convention in its **Calling non-primary tools** section.
* **Confluence tools were renamed** from `*Page` to `*Content` — `getConfluencePage` →
  `getConfluenceContent`, `createConfluencePage` → `createConfluenceContent`,
  `updateConfluencePage` → `updateConfluenceContent`, and `searchConfluenceUsingCql` →
  `searchConfluence`. The v1 names survive only as search-recall synonyms, not callable operations.
* **Confluence read and write contracts changed.** Reads default to a summary and need
  `detail="full"` for the body; document edits require a `snapshotToken` from the preceding read;
  writes must honor space instructions via `getConfluenceSpace`; and create/update take a `parent`
  object plus a required `contentType`, with `body` as `{format, value}`.
* **Some Jira tools were renamed** — `getVisibleJiraProjects` → `listJiraProjects`,
  `getJiraProjectIssueTypesMetadata` → `listJiraProjectIssueTypesMetadata`, `addCommentToJiraIssue` → `addOrEditJiraIssueComment`.
* **Jira create parameters differ** — `createJiraIssue` takes `issueType` and `assignee`, not
  `issueTypeName` and `assignee_account_id`.

For the current tool reference, see
[Supported tools](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/).
