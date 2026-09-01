---
name: generate-status-report
description: "Generate project status reports from Jira issues and publish to Confluence. When an agent needs to: (1) Create a status report for a project, (2) Summarize project progress or updates, (3) Generate weekly/daily reports from Jira, (4) Publish status summaries to Confluence, or (5) Analyze project blockers and completion. Queries Jira issues, categorizes by status/priority, and creates formatted reports for delivery managers and executives."
---

# Generate Status Report

## Keywords
status report, project status, weekly update, daily standup, Jira report, project summary, blockers, progress update, Confluence report, sprint report, project update, publish to Confluence, write to Confluence, post report

Automatically query Jira for project status, analyze issues, and generate formatted status reports published to Confluence.

**CRITICAL**: This skill should be **interactive**. Always clarify scope (time period, audience, Confluence destination) with the user before or after generating the report. Do not silently skip Confluence publishing—always offer it.

## Workflow

Generating a status report follows these steps:

1. **Identify scope** - Determine project, time period, and target audience
2. **Query Jira** - Fetch relevant issues using JQL queries
3. **Analyze data** - Categorize issues and identify key insights
4. **Format report** - Structure content based on audience and purpose
5. **Publish to Confluence** - Create or update a page with the report

## Step 1: Identify Scope

**IMPORTANT**: If the user's request is missing key information, ASK before proceeding with queries. Do not assume defaults without confirmation for Confluence publishing.

Clarify these details:

**Project identification:**
- Which Jira project key? (e.g., "PROJ", "ENG", "MKTG")
- If the user mentions a project by name but not key, search Jira to find the project key

**Time period:**
- If not specified, ask: "What time period should this report cover? (default: last 7 days)"
- Options: Weekly (7 days), Daily (24 hours), Sprint-based (2 weeks), Custom period

**Target audience:**
- If not specified, ask: "Who is this report for? (Executives/Delivery Managers, Team-level, or Daily standup)"
- **Executives/Delivery Managers**: High-level summary with key metrics and blockers
- **Team-level**: Detailed breakdown with issue-by-issue status  
- **Daily standup**: Brief update on yesterday/today/blockers

**Report destination:**
- **ALWAYS ASK** if not specified: "Would you like me to publish this report to Confluence? If so, which space should I use?"
- If user says yes: Ask for space name or offer to list available spaces
- Determine: New page or update existing page?
- Ask about parent page if creating under a specific section

## Step 2: Query Jira

Use the `searchJiraIssuesUsingJql` tool to fetch issues. Build JQL queries based on report needs.

### Common Query Patterns

For comprehensive queries, use the `scripts/jql_builder.py` utility to programmatically build JQL strings. For quick queries, reference `references/jql-patterns.md` for examples.

**All open issues in project:**
```jql
project = "PROJECT_KEY" AND status != Done ORDER BY priority DESC, updated DESC
```

**Issues updated in last week:**
```jql
project = "PROJECT_KEY" AND updated >= -7d ORDER BY priority DESC
```

**High priority and blocked issues:**
```jql
project = "PROJECT_KEY" AND (priority IN (Highest, High) OR status = Blocked) AND status != Done ORDER BY priority DESC
```

**Completed in reporting period:**
```jql
project = "PROJECT_KEY" AND status = Done AND resolved >= -7d ORDER BY resolved DESC
```

### Query Strategy

For most reports, execute multiple targeted queries rather than one large query:

1. **Completed issues**: Get recently resolved tickets
2. **In-progress issues**: Get active work items
3. **Blocked issues**: Get blockers requiring attention
4. **High priority open**: Get critical upcoming work

Use `maxResults: 100` for initial queries. If pagination is needed, use `nextPageToken` from results.

### Data to Extract

For each issue, capture:
- `key` (e.g., "PROJ-123")
- `summary` (issue title)
- `status` (current state)
- `priority` (importance level)
- `assignee` (who's working on it)
- `created` / `updated` / `resolved` dates
- `description` (if needed for context on blockers)

## Step 3: Analyze Data

Process the retrieved issues to identify:

**Metrics:**
- Total issues by status (Done, In Progress, Blocked, etc.)
- Completion rate (if historical data available)
- Number of high priority items
- Unassigned issue count

**Key insights:**
- Major accomplishments (recently completed high-value items)
- Critical blockers (blocked high priority issues)
- At-risk items (overdue or stuck in progress)
- Resource bottlenecks (one assignee with many issues)

**Categorization:**
Group issues logically:
- By status (Done, In Progress, Blocked)
- By priority (Highest → Low)
- By assignee or team
- By component or epic (if relevant)

## Step 4: Format Report

Select the appropriate template based on audience. Templates are in `references/report-templates.md`.

### For Executives and Delivery Managers

Use **Executive Summary Format**:
- Brief overall status (🟢 On Track / 🟡 At Risk / 🔴 Blocked)
- Key metrics (total, completed, in progress, blocked)
- Top 3 highlights (major accomplishments)
- Critical blockers with impact
- Upcoming priorities

**Keep it concise** - 1-2 pages maximum. Focus on what matters to decision-makers.

### For Team-Level Reports

Use **Detailed Technical Format**:
- Completed issues listed with keys
- In-progress issues with assignee and priority
- Blocked issues with blocker description and action needed
- Risks and dependencies
- Next period priorities

**Include more detail** - Team needs issue-level visibility.

### For Daily Updates

Use **Daily Standup Format**:
- What was completed yesterday
- What's planned for today
- Current blockers
- Brief notes

**Keep it brief** - This is a quick sync, not comprehensive analysis.

## Step 5: Publish to Confluence

**After generating the report, ALWAYS offer to publish to Confluence** (unless user explicitly said not to).

If user hasn't specified Confluence details yet, ask:
- "Would you like me to publish this report to Confluence?"
- "Which Confluence space should I use?"
- "Should this be nested under a specific parent page?"

Use the `createConfluenceContent` tool to publish the report.

**Before authoring the body**, load the authoring guidance. `getContentFormatGuide` is not a
primary tool, so run it through `execute` (see [Calling non-primary tools](#calling-non-primary-tools)).
Note that `toolName` takes the
content key `createConfluencePage`, **not** the name of the tool you are about to call:

```
executeRead(   # or execute(...) if your client exposes a single execute tool
    name="getContentFormatGuide",
    inputs={"toolName": "createConfluencePage"}
)
```

Never skip the body because the guidance failed to load — load it first, then build a real body.

**Page creation:**
```
createConfluenceContent(
    cloudId="[obtained from listConfluenceSpaces or URL]",
    parent={"spaceId": "[numerical space ID]"},
    contentType="page",
    title="[Project Name] - Status Report - [Date]",
    body={"format": "markdown", "value": "[formatted report]"}
)
```

To nest the report under an existing page, add `parentContentId` to `parent`:

```
    parent={"spaceId": "[numerical space ID]", "parentContentId": "[parent page ID]"},
```

**Title format examples:**
- "Project Phoenix - Weekly Status - Dec 3, 2025"
- "Engineering Sprint 23 - Status Report"
- "Q4 Initiatives - Status Update - Week 49"

**Body formatting:**
Write the report content in Markdown and pass it as `body={"format": "markdown", "value": ...}`,
following the spec returned by `getContentFormatGuide`. Use:
- Headers (`#`, `##`, `###`) for structure
- Bullet points for lists
- Bold (`**text**`) for emphasis
- Tables for metrics if needed
- Links to Jira issues: `[PROJ-123](https://yourinstance.atlassian.net/browse/PROJ-123)`

**Best practices:**
- Include the report date prominently
- Link directly to relevant Jira issues
- Use consistent naming conventions for recurring reports
- Consider creating under a "Status Reports" parent page for organization

### Finding the Right Space

If the user doesn't specify a Confluence space:

1. Use `listConfluenceSpaces` to list available spaces. This is not a primary tool, so run it
   through `execute`: `executeRead(name="listConfluenceSpaces", cloudId="...")`
2. Look for spaces related to the project (matching project name or key)
3. If unsure, ask the user which space to use
4. Default to creating in the most relevant team or project space

### Updating Existing Reports

If updating an existing page instead of creating new:

1. Get the current page content:
```
getConfluenceContent(
    cloudId="...",
    content_id="123456",
    content_format="markdown"
)
```

2. Load the authoring guidance for the edit (`toolName` is the content key, not the tool you call):
```
executeRead(   # or execute(...) if your client exposes a single execute tool
    name="getContentFormatGuide",
    inputs={"toolName": "updateConfluencePage"}
)
```

3. Update the page with new content:
```
updateConfluenceContent(
    cloudId="...",
    contentId="123456",
    body={"format": "markdown", "value": "[updated report content]"},
    versionMessage="Updated with latest status - Dec 8, 2025"
)
```

## Complete Example Workflow

**User request:** "Generate a status report for Project Phoenix and publish it to Confluence"

**Step 1 - Identify scope:**
- Project: Phoenix (need to find project key)
- Time period: Last week (default)
- Audience: Not specified, assume executive level
- Destination: Confluence, need to find appropriate space

**Step 2 - Query Jira:**
```python
# Find project key first
searchJiraIssuesUsingJql(
    cloudId="...",
    jql='project = "PHOENIX" OR project = "PHX"',
    maxResults=1
)

# Query completed issues
searchJiraIssuesUsingJql(
    cloudId="...",
    jql='project = "PHX" AND status = Done AND resolved >= -7d',
    maxResults=50
)

# Query blocked issues
searchJiraIssuesUsingJql(
    cloudId="...",
    jql='project = "PHX" AND status = Blocked',
    maxResults=50
)

# Query in-progress high priority
searchJiraIssuesUsingJql(
    cloudId="...",
    jql='project = "PHX" AND status IN ("In Progress", "In Review") AND priority IN (Highest, High)',
    maxResults=50
)
```

**Step 3 - Analyze:**
- 15 issues completed (metrics)
- 3 critical blockers (key insight)
- Major accomplishment: API integration completed (highlight)

**Step 4 - Format:**
Use Executive Summary Format from templates. Create concise report with metrics, highlights, and blockers.

**Step 5 - Publish:**
```python
# Find appropriate space (not a primary tool - run it through execute)
executeRead(name="listConfluenceSpaces", cloudId="...")

# Load authoring guidance before composing the body
executeRead(name="getContentFormatGuide", inputs={"toolName": "createConfluencePage"})

# Create page
createConfluenceContent(
    cloudId="...",
    parent={"spaceId": "12345"},
    contentType="page",
    title="Project Phoenix - Weekly Status - Dec 3, 2025",
    body={"format": "markdown", "value": "[formatted markdown report]"}
)
```

## Tips for Quality Reports

**Be data-driven:**
- Include specific numbers and metrics
- Reference issue keys directly
- Show trends when possible (e.g., "completed 15 vs 12 last week")

**Highlight what matters:**
- Lead with the most important information
- Flag blockers prominently
- Celebrate significant wins

**Make it actionable:**
- For blockers, state what action is needed and from whom
- For risks, provide mitigation options
- For priorities, be specific about next steps

**Keep it consistent:**
- Use the same format for recurring reports
- Maintain predictable structure
- Include comparable metrics week-over-week

**Provide context:**
- Link to Jira for details
- Explain the impact of blockers
- Connect work to business objectives when possible

## Resources

### scripts/jql_builder.py
Python utility for programmatically building JQL queries. Use this when you need to construct complex or dynamic queries. Import and use the helper functions rather than manually concatenating JQL strings.

### references/jql-patterns.md
Quick reference of common JQL query patterns for status reports. Use this for standard queries or as a starting point for custom queries.

### references/report-templates.md
Detailed templates for different report types and audiences. Reference this to select the appropriate format and structure for your report.

---

## Calling non-primary tools

The Atlassian Rovo MCP server exposes only a small set of **primary** tools directly in your tool
list. Everything else lives in the catalog and is reached through meta-tools:

- **`discover`** — describe the goal in natural language when you do not know an operation's name.
  It returns the exact `name` and `inputs` to use. Do not call `discover` for an operation you
  already have as a primary tool.
- **An execute-family tool** — run a catalog operation by name. Check your tool list: some clients
  expose a single **`execute`**, others expose **`executeRead`** / **`executeWrite`** /
  **`executeDestructive`** and expect the tier matching the operation. The arguments are identical:

```
executeRead(   # or execute(...) if your client exposes a single execute tool
  name="<operationName>",
  cloudId="...",
  inputs={"param": "value"}
)
```

Rules that matter:

- **`cloudId` is a top-level argument**, a sibling of `name` and `inputs` — never put it inside
  `inputs`. Operations declared `omitCloudId` (such as `getContentFormatGuide`) take no `cloudId`.
- **`inputs` is a flat object.** The server routes each parameter to path, query, or body itself.
- **Use the exact parameter names from the live tool schema.** Unrecognized parameters are dropped
  rather than reported as an error, so a wrong name fails silently — the call succeeds and your
  value is simply ignored. When in doubt, read the schema or `discover` result first.
- If the call reports an unknown operation, run `discover` with different keywords and use the
  name it returns rather than guessing.
