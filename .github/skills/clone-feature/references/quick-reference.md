# Quick Reference

## MCP Tools Required

| Tool | Purpose | Example |
|------|---------|---------|
| `mcp_aptiv-atlassi_jira_get_issue` | Fetch Feature + issuelinks | `issue_key="ABC-2026"`, `fields="*all"` |
| `mcp_aptiv-atlassi_jira_create_issue` | Create Feature clone | `project_key="ABC"`, `issue_type="Features"` |
| `mcp_aptiv-atlassi_jira_create_issue` | Create Story clone | `project_key="ABC"`, `issue_type="Story"` |
| `mcp_aptiv-atlassi_jira_create_issue_link` | Link parent-child | `link_type="Parent-Child"`, `inward_issue_key`, `outward_issue_key` |

---

## Field IDs & Custom Fields (ABC Instance)

| Field Name | Field ID | Used For | Example |
|------------|----------|----------|---------|
| Acceptance Criteria | customfield_11028 | Features, Stories | 4 bullet points |
| Size | customfield_10042 | Features | 13 (story points) |
| Story Points | customfield_10060 | Stories | 5 (story points) |
| Fix Versions | fixVersions | Any issue | v2.0 |
| Components | components | Any issue | ["Frontend", "API"] |
| Labels | labels | Any issue | ["core-module"] |

**Note:** Field IDs may differ in other Jira instances. Verify before cloning to a different project.

---

## Issue Type Names

| Issue Type | Display | API Name | Use For |
|------------|---------|----------|---------|
| Capability | Capability | Capability | Root of hierarchy |
| Feature | Features | Features | Cloning source; child of Capability |
| User Story | Story | Story | Child of Feature; implementable work |

**Critical:** Issue types are case-sensitive in Jira API. Use exact names: "Features" (not "Feature"), "Story" (not "User Story").

---

## Link Types & Directions

### Parent-Child Link (ID: 10402)

**For Capability → Feature:**
- Inward issue: Capability parent
- Outward issue: Feature child
- Example: ABC-1909 (inward) is parent of ABC-2211 (outward)

**For Feature → Story:**
- Inward issue: Feature parent
- Outward issue: Story child
- Example: ABC-2211 (inward) is parent of ABC-717 (outward)

**API Format:**
```
link_type="Parent-Child"
inward_issue_key="ABC-1909"   # Parent
outward_issue_key="ABC-2211"  # Child
```

---

## Cloning Workflow Steps (Quick Version)

1. **Discovery** — Confirm Feature exists, has children, parent is Capability
2. **Fetch Source** — Get all fields, issuelinks, custom fields
3. **Build Approval** — Show stakeholders what will be cloned
4. **Create Clones** — Create Feature + Stories in target projects
5. **Link Issues** — Recreate parent-child relationships
6. **Add Labels** — Apply cloning label to all issues
7. **Validate** — Confirm all fields copied, all links created
8. **Report** — Share summary: Feature key, Story keys, cloning label
9. **Cleanup** — Archive source if no longer needed (optional)

---

## Field Preservation Checklist

| Field | Copied? | Preserved From |
|-------|---------|---|
| Summary | ✓ Yes | Source issue |
| Description | ✓ Yes | Source issue |
| Acceptance Criteria (AC) | ✓ Yes | Source issue |
| Components | ✓ Yes | Source issue |
| Size (Features) | ✓ Yes | Source Feature |
| Story Points (Stories) | ✓ Yes | Source Story |
| Labels | ✓ Yes | Source issue (+ cloning label) |
| Fix Versions | ✓ Yes | Source issue |
| Status | ✗ No | Jira default (Created, To Do) |
| Assignee | ✗ No | None (unassigned) |
| Reporter | ✗ No | Current user |
| Comments | ✗ No | None (fresh issue) |
| Worklogs | ✗ No | None (time tracking resets) |

---

## Label Format

**Cloning Label Format:** `clonedFrom<SOURCE_KEY>@<YYYY_MM_DD:HH:MM>`

**Example:** `clonedFromABC-2026@2026_04_22:16:40`

- Source: ABC-2026
- Date: 2026-04-22 (April 22, 2026)
- Time: 16:40 (4:40 PM)

**Search All Clones:**
```jql
labels = clonedFromABC-2026@2026_04_22:16:40
```

---

## Permissions Required

| Action | Permission | Check How |
|--------|-----------|-----------|
| Fetch Feature + children | Browse | Visit issue in Jira |
| Create Feature clone | Create Issue | Try creating test issue in project |
| Create Story clones | Create Issue | Try creating test issue in project |
| Link issues | Link Issues | Jira Admin → Issue Linking → Permission |
| Add labels | Edit Issue | Try editing label on any issue |

**Insufficient Permission?** Contact project admin. Ask for "Create Issue" and "Link Issues" permissions.

---

## JQL Search Patterns

### Find All Clones from One Operation
```jql
labels = clonedFromABC-2026@2026_04_22:16:40
```

### Find Feature with Capability Parent
```jql
issuetype = Features AND issueLink = "is child of"
```

### Find Stories in a Feature
```jql
issuetype = Story AND parent = ABC-2211
```
*(Works if Feature uses field-based parent; ABC uses links instead)*

### Find All Issues with Parent-Child Links
```jql
issueLink = "is parent of" OR issueLink = "is child of"
```

### Find Custom Field Value
```jql
project = ABC AND customfield_11028 is not EMPTY
```
*(Confirms AC field exists in project ABC)*

---

## Troubleshooting Map

| Symptom | Likely Cause | Guide |
|---------|-------------|-------|
| Feature not found | Key typo or wrong project | Error 1 |
| No children detected | No Parent-Child links | Error 2 |
| components error | Passed twice (parameter + JSON) | Error 3 |
| Permission denied | Insufficient permissions | Error 4 |
| Custom field error | Field ID differs in target | Error 5 |
| Label invalid | Bad character in label | Error 6 |
| Stories out of order | Parallel API completion order | Error 7 |
| Linking failed | Wrong direction or bad IDs | Error 8 |
| Rate limit error | Too many parallel requests | Error 9 |

See [troubleshooting-guide.md](troubleshooting-guide.md) for detailed solutions.

---

## Workflow Decision Tree

**Start: Do you want to clone a Feature?**

- **Yes, with all children → Use SKILL.md Steps 1-9**
- **Yes, but manual selection of which children → Use Steps 1-2, then manually pick stories for Step 4**
- **No, just duplicate field values → Use copy-paste in Jira UI (no MCP needed)**

**Multi-Project Cloning?**

- **Yes (stories in different projects) → MCP handles automatically; just specify each story's source project in Step 2**
- **No (all in same project) → Standard cloning; no special handling needed**

**After Cloning, Do You Need:**

- **Approval from stakeholders → Use cloning label to show all created issues (8 total for ABC-2026)**
- **Linking to existing Epics → Manually add Epic link post-creation in Jira**
- **Approval workflow → Update Status of created Feature (not copied) in Jira**

