# Atlassian Rovo MCP Server skills

These skills are published in two versions, matching the two generations of the Atlassian Rovo
MCP Server. Pick the directory that matches the server endpoint your client is configured with.

| Directory | For server endpoint | Status |
| --- | --- | --- |
| [`v1/`](v1/) | `https://mcp.atlassian.com/v1/mcp/authv2` or `https://mcp.atlassian.com/v1/mcp` | Maintained for existing setups |
| [`v2/`](v2/) | `https://mcp.atlassian.com/v2/mcp` | Recommended |

Both directories contain the same six skills. They differ only in the tool names, parameters, and
call conventions they instruct the agent to use.

## Why the split

v2 renamed and reshaped a number of tools, and a skill written for one generation will fail
against the other. The most consequential differences:

* **Not every tool is directly callable.** v2 exposes a small set of *primary* tools in the
  client's tool list; the rest are reached through the `discover` and `execute` meta-tools. The
  v2 skills call those operations through `execute` and explain the convention.
* **Confluence tools were renamed** from `*Page` to `*Content` — `getConfluencePage` →
  `getConfluenceContent`, `createConfluencePage` → `createConfluenceContent`,
  `updateConfluencePage` → `updateConfluenceContent`, and `searchConfluenceUsingCql` →
  `searchConfluence`.
* **Some Jira tools were renamed** — `getVisibleJiraProjects` → `listJiraProjects`,
  `getJiraProjectIssueTypesMetadata` → `listJiraProjectIssueTypesMetadata`, `addCommentToJiraIssue` →
  `addOrEditJiraIssueComment`.

For the current tool reference, see
[Supported tools](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/).
