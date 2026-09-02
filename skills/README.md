# Atlassian Rovo MCP Server skills

The skills in this directory target the **Atlassian Rovo MCP v2** endpoint,
`https://mcp.atlassian.com/v2/mcp`. They are what every packaged plugin installs, and each one
lives at `skills/<name>/SKILL.md` per the [Agent Skills](https://agent-plugins.org/) convention.

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
