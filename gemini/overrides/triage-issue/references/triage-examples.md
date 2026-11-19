## Examples

### Example 1: Clear Duplicate Found

**User Input:**
```
Triage this error: "Connection timeout error when users try to login on iOS app"
```

**Process:**
1. Extract: "Connection timeout", "login", "iOS"
2. Search: Find PROJ-456 (open, 2 days ago) with exact same error
3. Analyze: 95% match - same error, component, symptom
4. Present: Show PROJ-456 as duplicate, recommend adding comment
5. Execute: User confirms, add comment with iOS-specific details
6. Confirm: Comment added to PROJ-456

**Output:**
```
✅ Comment added to PROJ-456

Your iOS-specific error details have been added to the existing issue.
The assignee will be notified.
```

### Example 2: New Issue with Related Context

**User Input:**
```
Error: NullPointerException in PaymentProcessor.processRefund() at line 245
Stack trace: [full stack trace]
```

**Process:**
1. Extract: "NullPointerException", "PaymentProcessor", "processRefund", "line 245"
2. Search: Find PROJ-789 (resolved, 3 weeks ago) about payment errors, but different line
3. Analyze: Related component but different specific error
4. Present: No duplicates, found related issue, recommend new ticket
5. Execute: User confirms, create new Bug with context
6. Confirm: PROJ-890 created

**Output:**
```
✅ New Issue Created

PROJ-890 - Payment API: NullPointerException in refund processing
https://yoursite.atlassian.net/browse/PROJ-890

References related issue PROJ-789 for context.
```

### Example 3: Possible Regression

**User Input:**
```
Users can't upload files larger than 5MB, getting "Upload failed" error
```

**Process:**
1. Extract: "Upload failed", "5MB", "file upload"
2. Search: Find PROJ-234 (resolved 2 months ago) - exact same issue
3. Analyze: Was fixed but now happening again
4. Present: Possible regression, recommend new issue linked to old one
5. Execute: Create new issue, link to PROJ-234 as "may be caused by"
6. Confirm: PROJ-891 created with regression context

**Output:**
```
✅ New Issue Created (Possible Regression)

PROJ-891 - File Upload: Upload failed for files >5MB (Regression?)
https://yoursite.atlassian.net/browse/PROJ-891

This may be a regression of PROJ-234, which was resolved 2 months ago.
Issue includes reference to original fix for investigation.
```

---


#### Format for Likely Duplicate:

```
🔍 **Triage Results: Likely Duplicate**

I found a very similar issue already reported:

**PROJ-456** - Connection timeout during mobile login
Status: Open | Priority: High | Created: 3 days ago
Assignee: @john.doe
https://yoursite.atlassian.net/browse/PROJ-456

**Similarity:**
- Same error: "Connection timeout"
- Same component: Mobile app login
- Same symptoms: Users unable to login

**Difference:**
- Original report mentioned iOS specifically, this report doesn't specify platform

**Recommendation:** Add your details as a comment to PROJ-456

Would you like me to:
1. Add a comment to PROJ-456 with your error details
2. Create a new issue anyway (if you think this is different)
3. Show me more details about PROJ-456 first
```

#### Format for Possibly Related:

```
🔍 **Triage Results: Possibly Related Issues Found**

I found 2 potentially related issues:

**1. PROJ-789** - Mobile app authentication failures
Status: Resolved | Fixed: 2 weeks ago | Fixed by: @jane.smith
https://yoursite.atlassian.net/browse/PROJ-789

**2. PROJ-234** - Login timeout on slow connections
Status: Open | Priority: Medium | Created: 1 month ago
https://yoursite.atlassian.net/browse/PROJ-234

**Assessment:** Your error seems related but has unique aspects

**Recommendation:** Create a new issue, but reference these related tickets

Would you like me to create a new bug ticket?
```

#### Format for No Duplicates:

```
🔍 **Triage Results: No Duplicates Found**

I searched Jira for:
- "Connection timeout" errors
- Mobile login issues
- Authentication failures

No similar open or recent issues found.

**Recommendation:** Create a new bug ticket

**Note:** I found 1 old resolved issue (PROJ-123 from 8 months ago) about login timeouts, but it was for web, not mobile, and was resolved as "configuration error."

Would you like me to create a new bug ticket for this issue?
```

---

## Edge Cases & Troubleshooting

### Multiple Potential Duplicates

If you find 3+ very similar issues:

```
🔍 **Triage Results: Multiple Possible Duplicates**

I found 3 issues that might be related:

**Most Likely Duplicate:**
**PROJ-456** - [summary] (Open, 2 days ago)
Match: 95% - Same error and component

**Also Possibly Related:**
**PROJ-234** - [summary] (Open, 1 month ago)
Match: 70% - Similar symptoms, different error

**PROJ-123** - [summary] (Resolved, 8 months ago)
Match: 60% - Related component, but was fixed

**Recommendation:**
1. Add to PROJ-456 (most similar)
2. Reference PROJ-234 in your comment (might be related)
3. Note PROJ-123 was previously fixed (possible regression)

Which issue should I add your details to? (Or create new)
```

### Unclear Project Context

If user doesn't specify which project:

```
Which Jira project should I search for similar issues?

Available projects:
- BACKEND (Backend Services)
- MOBILE (Mobile Apps)
- WEB (Web Platform)
- INFRA (Infrastructure)

Or tell me the project key directly (e.g., BACKEND, MOBILE)
```

### Insufficient Information

If the bug report lacks critical details:

```
I need more information to effectively triage this issue:

**What I have:**
- Error: "Something went wrong"

**What would help:**
- Specific error message or code
- Which part of the system (login, payment, etc.)
- What the user was trying to do
- Which environment (production, staging, mobile, web)

Can you provide any of these details?
```

### Resolved Regression

If you find a resolved issue that matches:

```
🔍 **Triage Results: Possible Regression**

This looks like it might be a regression of a previously fixed issue:

**PROJ-567** - [Same issue description]
Status: Resolved (Fixed) | Fixed: 3 months ago | Fixed by: @jane.smith
Resolution: [Brief description of fix]
https://yoursite.atlassian.net/browse/PROJ-567

**This suggests:**
- The original fix may not have fully addressed the root cause
- OR there's been a regression in recent changes
- OR this is a different issue with similar symptoms

**Recommendation:** Create a new issue and link it to PROJ-567 as "may be related to" or "regression of"

Should I create a new issue with this context?
```

### Custom Required Fields

If creating an issue fails due to required fields:

1. **Check what fields are required.** `getJiraIssueTypeMetaWithFields` is not a primary tool, so
   run it through `execute`:
```
getJiraIssueTypeMetaWithFields(
  cloudId="...",
  projectIdOrKey="PROJ", issueTypeId="10001"
)
```

2. **Ask user for values:**
```
This project requires additional fields to create a Bug:
- Severity: [High/Medium/Low]
- Affected Version: [Version number]

Please provide these values so I can create the issue.
```

3. **Retry with additional fields:**
```
createJiraIssue(
  ...existing parameters...,
  priority="High",
  additional_fields={
    "customfield_10001": {"value": "Production"}
  }
)
```

---
