---
name: atlassian-mcp-code-search
description: >
  Find source, callers, and API consumers outside the local workspace using the
  Atlassian MCP code search operations (searchCode, getCodeFile, scanCodeRepo,
  listCodeDirectory). Use whenever an answer needs code that is not checked out
  locally, even without an explicit search request or a known repository.
---

# Code Search And Navigation With The Atlassian MCP

Adapted from the TWG CLI `code-search.md` reference, for agents that reach code
search through the Atlassian MCP server instead of `twg search-code`.

## When To Use

Use this when an answer needs source unavailable locally, including follow-up
questions without an explicit search request. Start from the known service,
behavior, error, API, or symbol; discover the repository if unknown. Verify
implementation claims against source. Skip when local code, supplied context,
or general knowledge answers the question.

The Atlassian MCP covers code as well as Jira and Confluence. In the default v2
tool list, code search is reached through `discover` and `execute`. This skill
teaches that workflow; it does not register additional MCP tools.

## Operations

- `searchCode`: `query` plus optional `mode` (`hybrid` default, `semantic`,
  `lexical`), `namespace` (GitHub organization or Bitbucket workspace), `repo`
  (slug only, not `owner/repo`), `language`, `extension`, `path`, `maxResults`.
  Alternates are separated with `|`. Hits carry `workspace`, `repo`, `path`,
  `version` (a commit) and the matched spans.
- `getCodeFile`: `workspace`, `repo`, `path`, `commitHash`. Pass the hit's
  `workspace`, `repo`, `path` and `version`; do not infer the workspace from the
  search filter.
- `listCodeDirectory`: `workspace`, `repo`, `commitHash`, optional `path`,
  `maxDepth`, `page`.
- `scanCodeRepo`: `workspace`, `repo`, `commitHash` (a branch name works), optional
  `filter` (glob), `root` (directory prefix), `limit`, `cursor`. Paths only.

Use exact parameter names from the live schema. Treat the descriptions above as
a navigation guide when the live contract differs. Use `responseFields` only
when the advertised schema supports it.

## Search And Navigate

Choose the route from anchor precision:

- Known repository, exact path and commit: read it with `getCodeFile`.
- Known repository and exact path without a commit: search within that repository
  for the file or a known symbol. Use a matching hit's `version` as `commitHash`.
  `listCodeDirectory` also requires a commit, so it cannot supply the initial one.
- Known repository and symbol or class: run one repository-scoped `lexical` or
  `hybrid` `searchCode`, then read only the selected files.
- Unknown repository or conceptual behavior: begin with one unscoped `hybrid`
  `searchCode` using the concrete topic, symbol, or behavior.
- Cross-repository or reverse-dependency question: search without a
  `namespace` or `repo` filter so every indexed repository participates, unless
  the user limits the scope.

Honor an explicitly named repository or code host as the requested scope. Widen
beyond it only when the user asks for cross-repository coverage, the repository
identity is ambiguous, or scoped evidence is demonstrably incomplete.

### When a scoped search returns no matches

An empty result does not establish whether a repository is indexed or the code
is absent. Check the repository slug, filters and query before widening the search.
When the requested scope permits it, remove filters incrementally and stop when
the next search cannot resolve a specific gap. Look for candidate mirrors or
forks among the results. Verify their relationship to the requested repository
before using them as evidence. Identify the source repository and commit, and
note that its contents may differ from the original. Report an indexing gap only
when confirmed; otherwise report that the search found no matches.

## Reverse Dependencies

Search the exact API or symbol first. If that does not establish direct
consumption, search the package or import anchor, group candidates by
repository, and inspect the manifest or import plus the call site needed to
verify selected consumers. Prefer stable literal anchors; do not invent
delimiter-heavy code fragments merely to vary the query. Keep each search to a
compact result set and use the returned repository and path metadata for
selection; a result cap is not a reason to claim completeness.

## Efficiency

Treat search results as a batch. Do not rerun the same symbol separately for each
repository or usage pattern. Select a small, diverse set of direct consumers,
read the call-site files needed to establish each integration role, and fetch a
manifest only when the call-site evidence does not establish the package. Stop
when another result would repeat an already verified integration role, not while
a material role is unverified.

After discovery establishes repository, path and commit, read independent files
concurrently in one tool round. Do not wait for one file before requesting another
unless its result determines the next path.

## Reporting

Rank a bounded set of source-backed implementation locations. If the anchored
search is incomplete, returns only generated documentation, or exposes only one
part of the requested capability, widen while the next result can close that gap.
Fetch only the source files needed for symbol and behavior context. Cite
`workspace/repo` and path, and the commit when you read a file. Deduplicate mirror
results only when the retrieved code establishes equivalence. Say which source
appears canonical only when the evidence supports it. Never infer behavior from a filename, or completeness
from one repository's empty result. Use the fewest calls that establish the
answer; for a single known repository and symbol, one search and one read round
are the normal starting point.
