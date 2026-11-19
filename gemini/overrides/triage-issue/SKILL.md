---
name: triage-issue
description: "Intelligently triage bug reports and error messages by searching for duplicates in Jira and offering to create new issues or add comments to existing ones. When an agent needs to: (1) Triage a bug report or error message, (2) Check if an issue is a duplicate, (3) Find similar past issues, (4) Create a new bug ticket with proper context, or (5) Add information to an existing ticket. Searches Jira for similar issues, identifies duplicates, checks fix history, and helps create well-structured bug reports."
---

# Triage Issue

## Tool access

Call an operation directly when its exact name is in the current tool list. Otherwise, if discovery and execution tools are available, discover the operation when needed and use the returned read/write/destructive runner and schema. With a flat connector, an operation absent from the tool list is unavailable; report that gap instead of inventing a call. Examples below name operations directly; translate them to the available runner only when necessary. Use current input schemas and never change a parameter to a v1 spelling.


## Keywords
triage bug, check duplicate, is this a duplicate, search for similar issues, create bug ticket, file a bug, report this error, triage this error, bug report, error message, similar issues, duplicate bug, who fixed this, has this been reported, search bugs, find similar bugs, create issue, file issue

## Overview

Automatically triage bug reports and error messages by searching Jira for duplicates, identifying similar past issues, and helping create well-structured bug tickets or add context to existing issues. This skill eliminates manual duplicate checking and ensures bugs are properly documented with relevant historical context.

**Use this skill when:** Users need to triage error messages, bug reports, or issues to determine if they're duplicates and take appropriate action.

---

## Workflow

Follow this 6-step process to effectively triage issues:

### Step 1: Extract Key Information

Analyze the bug report or error message to identify search terms.

#### Extract These Elements:

**Error signature:**
- Error type or exception name (e.g., "NullPointerException", "TimeoutError")
- Error code or status (e.g., "500", "404", "ERR_CONNECTION_REFUSED")
- Specific error message text (key phrases, not full stack trace)

**Context:**
- Component or system affected (e.g., "authentication", "payment gateway", "API")
- Environment (e.g., "production", "staging", "mobile app")
- User actions leading to error (e.g., "during login", "when uploading file")

**Symptoms:**
- Observable behavior (e.g., "page blank", "infinite loading", "data not saving")
- Impact (e.g., "users can't login", "payments failing")

#### Example Extractions:

**Input:** "Users getting 'Connection timeout' error when trying to login on mobile app"
**Extracted:**
- Error: "Connection timeout"
- Component: "login", "mobile app"
- Symptom: "can't login"

**Input:** "NullPointerException in PaymentProcessor.processRefund() line 245"
**Extracted:**
- Error: "NullPointerException"
- Component: "PaymentProcessor", "refund"
- Location: "processRefund line 245"

---

### Step 2: Search for Duplicates

Search Jira using extracted keywords to find similar or duplicate issues.

#### Search Strategy:

Execute **multiple targeted searches** to catch duplicates that may use different wording:

**Search 1: Error-focused**
```
searchJiraIssuesUsingJql(
  cloudId="...",
  jql='project = "PROJ" AND (text ~ "error signature" OR summary ~ "error signature") AND type = Bug ORDER BY created DESC',
  fields=["summary", "description", "status", "resolution", "created", "updated", "assignee"],
  maxResults=20
)
```

**Search 2: Component-focused**
```
searchJiraIssuesUsingJql(
  cloudId="...",
  jql='project = "PROJ" AND text ~ "component keywords" AND type = Bug ORDER BY updated DESC',
  fields=["summary", "description", "status", "resolution", "created", "updated", "assignee"],
  maxResults=20
)
```

**Search 3: Symptom-focused**
```
searchJiraIssuesUsingJql(
  cloudId="...",
  jql='project = "PROJ" AND summary ~ "symptom keywords" AND type = Bug ORDER BY priority DESC, updated DESC',
  fields=["summary", "description", "status", "resolution", "created", "updated", "assignee"],
  maxResults=20
)
```

#### Search Tips:

**Use key terms only:**
- ✅ "timeout login mobile"
- ✅ "NullPointerException PaymentProcessor refund"
- ❌ "Users are getting a connection timeout error when..." (too verbose)

**Search recent first:**
- Order by `created DESC` or `updated DESC` to find recent similar issues
- Recent bugs are more likely to be relevant duplicates

**Don't over-filter:**
- Include resolved issues (might have been reopened or regression)
- Search across all bug statuses to find fix history

---

### Step 3: Analyze Search Results

Evaluate the search results to determine if this is a duplicate or a new issue.

#### Duplicate Detection:

**High confidence duplicate (>90%):**
- Exact same error message in summary or description
- Same component + same error type
- Recent issue (< 30 days) with identical symptoms
- **Action:** Strongly recommend adding comment to existing issue

**Likely duplicate (70-90%):**
- Similar error with slight variations
- Same component but different context
- Resolved issue with same root cause
- **Action:** Present as possible duplicate, let user decide

**Possibly related (40-70%):**
- Similar symptoms but different error
- Same component area but different specific error
- Old issue (> 6 months) that might be unrelated
- **Action:** Mention as potentially related

**Likely new issue (<40%):**
- No similar issues found
- Different error signature and component
- Unique symptom or context
- **Action:** Recommend creating new issue

#### Check Fix History:

If similar resolved issues are found:

**Extract relevant information:**
- Who fixed it? (assignee on resolved issues)
- How was it fixed? (resolution comment or linked PRs)
- When was it fixed? (resolution date)
- Has it regressed? (any reopened issues)

**Present this context** to help with triage decision.

---

### Step 4: Present Findings to User

**CRITICAL:** Always present findings and wait for user decision before taking any action.

Present the matching candidates, evidence, confidence and proposed next action. Do not call a write tool until the user has authorized that action. Read [the response examples](references/triage-examples.md) for output formats and [bug report templates](references/bug-report-templates.md) when composing a new issue.

### Step 5: Execute User Decision

Based on user's choice, either add a comment or create a new issue.

#### Option A: Add Comment to Existing Issue

If user wants to add to existing issue:

**Fetch the full issue first** to understand context:
```
getJiraIssue(
  cloudId="...",
  issueIdOrKey="PROJ-456"
)
```

**Then add the comment:**
```
addOrEditJiraIssueComment(
  cloudId="...",
  issueIdOrKey="PROJ-456",
  commentBody="[formatted comment - see below]"
)
```

**Comment Structure:**
```markdown
## Additional Instance Reported

**Reporter:** [User's name or context]
**Date:** [Current date]

**Error Details:**
[Paste relevant error message or stack trace]

**Context:**
- Environment: [e.g., Production, iOS 16.5]
- User Impact: [e.g., 50+ users affected in last hour]
- Steps to Reproduce: [if provided]

**Additional Notes:**
[Any unique aspects of this instance]

---
*Added via triage automation*
```

#### Option B: Create New Issue

If user wants to create new issue:

**First, check available issue types.** `listJiraProjectIssueTypesMetadata` uses the tool-access rules above:
```
listJiraProjectIssueTypesMetadata(
  cloudId="...",
  projectIdOrKey="PROJ"
)
```

**Determine appropriate issue type:**
- For bugs/errors → Use "Bug" (if available)
- For issues without errors → Use "Task" or "Issue"
- Fallback → First available non-Epic, non-Subtask type

**Create the issue:**
```
createJiraIssue(
  cloudId="...",
  projectKey="PROJ",
  issueType="Bug",
  summary="[Clear, specific summary - see below]",
  description="[Detailed description - see below]",
  priority="Medium"  # Adjust based on the severity assessment
)
```

**Summary Format:**
Use the pattern: `[Component] [Error Type] - [Brief Symptom]`

**Examples:**
- ✅ "Mobile Login: Connection timeout during authentication"
- ✅ "Payment API: NullPointerException in refund processing"
- ✅ "Dashboard: Infinite loading on reports page"
- ❌ "Error in production" (too vague)
- ❌ "Users experiencing issues" (not specific)

**Description Structure:**
```markdown
## Issue Description
[1-2 sentence summary of the problem]

## Error Details
```
[Error message or stack trace]
```

## Environment
- **Platform:** [e.g., Mobile iOS, Web, API]
- **Version:** [if known]
- **Environment:** [Production/Staging/etc]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## User Impact
- **Frequency:** [e.g., Every time, Intermittent]
- **Affected Users:** [e.g., All users, Mobile users only]
- **Severity:** [e.g., Users cannot complete checkout]

## Additional Context
[Any other relevant information]

## Related Issues
[If applicable, reference similar issues found during triage]
- See also: PROJ-123 (similar but resolved)

---
*Created via automated triage*
```

---

### Step 6: Provide Summary

After taking action, confirm what was done.

#### If Comment Added:

```
✅ **Comment Added Successfully**

Added details to existing issue: **PROJ-456**
https://yoursite.atlassian.net/browse/PROJ-456

**What I included:**
- Your error details
- Environment context
- User impact information

**Next Steps:**
- The assignee (@john.doe) will be notified
- Monitor PROJ-456 for updates
- If this turns out to be different, we can still create a separate ticket
```

#### If New Issue Created:

```
✅ **New Issue Created**

**PROJ-890** - Mobile Login: Connection timeout during authentication
https://yoursite.atlassian.net/browse/PROJ-890

Type: Bug | Priority: Medium | Status: Open

**What's Included:**
- Complete error details and stack trace
- Environment and reproduction steps
- User impact assessment
- References to related issues (PROJ-123, PROJ-789)

**Next Steps:**
- Issue will be reviewed during next triage meeting
- Consider setting priority based on user impact
- Assign to appropriate team member
```

---

## Troubleshooting

Read [the triage examples and troubleshooting guide](references/triage-examples.md) for ambiguous matches, missing project context, regressions and required-field errors. Ask for missing required values and retry only the failed operation. Reuse successfully created issue keys to prevent duplicate creation.

## Tips for Effective Triage

### For Search:

**Do:**
✅ Use multiple search queries with different angles
✅ Include both open and resolved issues in search
✅ Search for error signatures and symptoms separately
✅ Look at recent issues first (last 30-90 days)
✅ Check for patterns (multiple reports of same thing)

**Don't:**
❌ Search with entire error messages (too specific)
❌ Only search open issues (miss fix history)
❌ Ignore resolved issues (miss regressions)
❌ Use too many keywords (reduces matches)

### For Issue Creation:

**Do:**
✅ Write clear, specific summaries with component names
✅ Include complete error messages in code blocks
✅ Add environment and impact details
✅ Reference related issues found during search
✅ Use "Bug" issue type for actual bugs

**Don't:**
❌ Create vague summaries like "Error in production"
❌ Paste entire stack traces in summary (use description)
❌ Skip reproduction steps
❌ Forget to mention user impact
❌ Hard-code issue type without checking availability

### For Duplicate Assessment:

**High Confidence Duplicates:**
- Exact same error + same component + recent (< 30 days)
- Same root cause identified

**Likely Different Issues:**
- Different error signatures
- Different components/systems
- Significantly different contexts

**When Unsure:**
- Present both options to user
- Lean toward creating new issue (can be closed as duplicate later)
- Linking issues is better than hiding information

---

## Worked examples

Read [the triage examples](references/triage-examples.md) for duplicate, new-issue and regression scenarios.

## When NOT to Use This Skill

This skill is for **triaging bugs and errors only**. Do NOT use for:

❌ Feature requests (use spec-to-backlog)
❌ General task creation (use capture-tasks-from-meeting-notes)
❌ Searching for information (use search-company-knowledge)
❌ Generating status reports (use generate-status-report)

**Use this skill specifically for:**
✅ "Is this a duplicate bug?"
✅ "Triage this error message"
✅ "Has this been reported before?"
✅ "Create a bug ticket for this"

---

## Quick Reference

**Primary workflow:** Extract → Search → Analyze → Present → Execute → Confirm

**Search tool:** `searchJiraIssuesUsingJql(cloudId, jql, fields, maxResults)`

**Action tools:**
- `addOrEditJiraIssueComment(cloudId, issueIdOrKey, commentBody)` - Add to existing
- `createJiraIssue(cloudId, projectKey, issueType, summary, description)` - Create new

**Issue type:** Always prefer "Bug" for error reports, check with
`listJiraProjectIssueTypesMetadata` using the available direct tool or runner

**Remember:**
- Multiple searches catch more duplicates
- Present findings before acting
- Include error details and context
- Reference related issues
- Use "Bug" issue type when available

---
