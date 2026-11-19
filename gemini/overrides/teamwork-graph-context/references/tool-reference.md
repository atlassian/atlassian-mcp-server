# Jira and Confluence tool reference

Consult this only when selecting an operation whose purpose is unclear. Exact inputs come from the live tool schema.

### Available Core Tools

#### Rovo Search & Common (Read-only)
| Tool | Use it to | Schema & Usage Notes |
| --- | --- | --- |
| `getAccessibleAtlassianResources` | Obtain the site's `cloudId` and base site URL once per session | Do not block on a `products` field if omitted from the response; call Jira and Confluence tools directly and report missing/denied capabilities transparently. |
| `atlassianUserInfo` | Get the signed-in user's Atlassian profile and account ID | Call once when a skill needs to identify or exclude the current user's work. |
| `getMyWork` | List the signed-in user's recently viewed or updated items on the site | Useful for catch-up and establishing recent activity context. |
| `search` | Rovo semantic search across Jira and Confluence (and any indexed content) | Check the live tool schema first: Use required cloudId and query, with optional targetApp and limit. Do not pass mode. Never pass raw JQL or CQL into `search`. |
| `getContentFormatGuide` | Get formatting guidance before authoring Confluence or Jira content | Check live schema for accepted `toolName` values and whether `cloudId` is omitted. |

#### Jira (Read-only)
| Tool | Use it to | Schema & Usage Notes |
| --- | --- | --- |
| `searchJiraIssuesUsingJql` | Query Jira work items by structured JQL criteria | Check live schema before using `view` or `searchResultMode`; prefer explicit `fields` lists (e.g., `["summary", "status", "assignee", "duedate", "priority", "issuelinks"]`) and `maxResults` (up to 100) with `nextPageToken` pagination. |
| `getJiraIssue` | Read full details and fields for a single Jira issue by key or ID | Check live schema before using `view`: if `view` is unsupported (or returns oversized custom fields), pass an explicit `fields` list (e.g., `["summary", "status", "description", "issuelinks", "assignee", "resolution", "resolutiondate"]`). |
| `listJiraIssueComments` | Read comment bodies, authors, and timestamps on a Jira issue | `getJiraIssue` may only return comment counts; call `listJiraIssueComments` directly when discussion matters. |
| `listJiraIssueChangelogs` | Read field change history (status transitions, assignee/date/priority changes) | Paginate from the end when checking recent transitions (`maxResults` / `startAt`). |
| `listJiraIssueRemoteIssueLinks` | Read Confluence pages and external web links attached to a Jira issue | Primary way to follow spec, decision, and rollout links from an epic or issue. |
| `listJiraIssueLinkTypes` | Inspect custom and standard Jira issue link type names and wording | Useful when confirming unfamiliar custom dependency link labels. |
| `getJiraProjectVersions` | List releases/versions in a Jira project or inspect a single version | Check live schema for `versionId`, `projectIdOrKey`, `query`, `status`, and `include` (driver/approvers). |
| `getJiraProjectVersionRelatedWork` | List related work links (designs, testing, docs, rollout) on a release version | Primary source of release-attached documentation. |
| `listJiraProjects` | List visible Jira projects and their keys/types | Use to resolve project names or verify project keys. |
| `listJiraBoards`, `getJiraBoardConfig`, `listJiraBoardSprints`, `getJiraBoardSprintData`, `getJiraBoardIssueData` | Read Jira boards, sprint lists, active sprint issues, and board columns | Use for board/sprint anchors; some boards do not support sprints; inspect their actual features. |
| `getJiraCurrentUser`, `getJiraUser`, `lookupJiraAccountId`, `listJiraIssueAssignableUsers` | Resolve Jira user display names, time zones (`getJiraCurrentUser`), and account IDs | lookupJiraAccountId takes cloudId and query. Never display email addresses. |

#### Confluence (Read-only)
| Tool | Use it to | Schema & Usage Notes |
| --- | --- | --- |
| `searchConfluence` | Search Confluence pages, blog posts, databases, or comments using CQL | Reliable for date filtering (`lastmodified >=`, `created >=`) and title/label/space scoping. |
| `getConfluenceContent` | Read a Confluence page, live doc, or blog post by ID or URL | Use content_id or content_url, content_format and detail="full" for full bodies. Do not pass include_metadata; metadata is returned by the operation. |
| `getConfluenceApproval` | Read approval status, reviewers, and approval history on a Confluence page | Applies to classic pages (not live docs). |
| `listConfluenceContentVersions`, `getConfluenceContentVersion`, `diffConfluenceContentVersions` | List historical versions, inspect a specific version, and diff two versions | Essential for dating edits and decisions accurately inside a time window. |
| Confluence comment retrieval (use `searchConfluence` with `type = comment AND container = <id>` when a dedicated comments tool is absent; report its coverage limits) | List footer and inline comments with authors and timestamps on a page | Use directly to read page discussions and timestamps. |
| `listConfluenceTasks` | List Confluence inline tasks filtered by assignee or status | Check live schema for exact assignee parameter name (`assigned-to` vs `assignedTo`), `status`, `limit`, and pagination cursor. |
| `listConfluenceSpaces`, `getConfluenceSpace` | List spaces and read space metadata / space instructions | Call `getConfluenceSpace` once before authoring in a space. |

#### Jira & Confluence Writes (Always Confirm First)
- `createJiraIssueLink` — link two Jira issues (e.g., Blocks)
- `createJiraIssueRemoteIssueLink` — attach a Confluence page or external URL to a Jira issue
- `manageJiraProjectVersionRelatedWork` — attach related work links to a Jira version (check live schema for exact parameter names)
- `addOrEditJiraIssueComment` — post a comment on a Jira issue
- `createConfluenceContent` / `updateConfluenceContent` — create or update a Confluence page if the user requests saving an output to Confluence
