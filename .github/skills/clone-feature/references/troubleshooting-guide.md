# Troubleshooting Guide

## Common Errors & Solutions

### Error 1: Feature Not Found

**Message:**
```
Error: Issue key ABC-2026 not found in project ABC
```

**Causes:**
- Issue key is incorrect (typo: ABC-202 vs ABC-2026)
- Issue belongs to a different project (you're checking XYZ-2026, not ABC-2026)
- Issue was deleted or archived
- Insufficient permissions to view the issue

**Solution:**
1. Verify the issue key in Jira URL or search results
2. Check the project name matches: ABC vs XYZ vs other projects
3. If issue exists but is archived, contact Jira admin
4. Confirm your Jira user has "Browse" permission for the project

**Prevention:**
- Copy issue keys directly from Jira UI rather than typing manually
- Confirm project key before starting cloning workflow

---

### Error 2: No Parent-Child Links Detected

**Message:**
```
No Parent-Child links found for ABC-2026. The feature may not have a parent Capability or discoverable hierarchy.
```

**Causes:**
- Feature is a standalone issue with no Capability parent
- Parent-child links use a different link type (not "Parent-Child" with ID 10402)
- Jira instance uses field-based hierarchy (parent field) instead of link-based
- Insufficient permissions to view parent issues

**Solution:**
1. Check Jira: does ABC-2026 have a parent Capability?
2. If yes, verify the link type:
   - Open ABC-2026 → Link section
   - Look for "child of ABC-1909" (or similar parent key)
   - Confirm link type is "Parent-Child"
3. If using field-based hierarchy:
   - Open ABC-2026 → Parent field
   - Copy the parent key (e.g., ABC-1909)
   - Use that in Step 2 of the workflow manually

**Prevention:**
- In Step 1 Discovery, confirm the parent Capability exists before proceeding
- Document your Jira hierarchy model (link-based vs field-based) upfront

---

### Error 3: Components Parameter Conflict

**Message:**
```
TypeError: create_issue() got multiple values for keyword argument 'components'
```

**Causes:**
- Components passed both as direct parameter AND in additional_fields JSON
- Example mistake: `components=["Frontend"]` and `additional_fields='{"components": ["Frontend"]}'`

**Solution:**
1. Use components ONLY as the dedicated parameter: `components=["Frontend", "API"]`
2. Remove components from additional_fields
3. Retry creation

**Prevention:**
- In Step 4, keep components separate from additional_fields
- Use the exact format in SKILL.md: `components="Frontend,API"` (not JSON in additional_fields)

---

### Error 4: Permission Denied

**Message:**
```
Error 403 Forbidden: You do not have permission to create issues in project ABC
```

**Causes:**
- Jira user lacks "Create" permission in the target project
- Jira user is not a member of the project
- Project requires special role (e.g., "Developer") to create issues

**Solution:**
1. Contact project admin to grant "Create Issue" permission
2. Confirm your user account is added to the project team
3. Ask admin what role is required (e.g., Developer, Contributor)

**Prevention:**
- Before cloning, confirm you can manually create an issue in the target project
- If you can't, you don't have sufficient permissions for automated cloning

---

### Error 5: Custom Field Not Found

**Message:**
```
Error: Field customfield_11028 not found in project ABC
```

**Causes:**
- Custom field IDs differ between projects (ABC uses customfield_11028, XYZ uses customfield_11050)
- Custom field was deleted or removed from the project
- Custom field is not part of the Issue Create screen for your issue type

**Solution:**
1. Look up correct field ID in target project:
   - Jira Admin → Custom Fields → search "Acceptance Criteria"
   - Note the field ID (e.g., customfield_11050)
2. Update Step 2 in the workflow to use the correct ID
3. Retry cloning

**Prevention:**
- In Step 1 Discovery, run the field lookup JQL for the target project:
  ```
  project = ABC AND customfield_11028 is not EMPTY
  ```
  If this returns no results, the field ID is different in ABC

---

### Error 6: Labeling Fails / Label Format Mismatch

**Message:**
```
Error: Label 'clonedFromABC-2026@2026_04_22:16:40' is invalid
```

**Causes:**
- Label contains characters not allowed by Jira (e.g., spaces, `@`, colons)
- Jira label restrictions: labels must match `^[a-zA-Z0-9_-]+$` (letters, numbers, dash, underscore only)
- Timestamp format includes `:` which is not allowed

**Solution:**
1. Reformat label to remove `:` and `@`:
   - Instead: `clonedFromABC-2026@2026_04_22:16:40`
   - Use: `clonedFromABC-2026-2026_04_22_16_40` (replace `:` with `_`, remove `@`)
2. Re-run labeling step

**Prevention:**
- Test label format in SKILL.md Step 2 on one issue first
- If error occurs, update the label format for all subsequent clones

---

### Error 7: Child Stories Created Out of Order

**Message:**
```
Requested: ABC-717, ABC-718, ABC-719, XYZ-722, XYZ-723
Returned: ABC-595, ABC-596, ABC-597, XYZ-595, XYZ-596 (different order)
```

**Causes:**
- Parallel API calls to create stories complete in non-deterministic order
- Responses depend on server processing time, not request order

**Solution:**
- This is expected behavior and is NOT an error
- Verify using the cloning label (all clones share the same label)
- Search: `labels = clonedFromABC-2026@2026_04_22:16:40` → Returns all created stories
- Use the label to group and verify completeness

**Prevention:**
- Document cloning label in your notes immediately after Step 2
- Use label-based searches to validate all clones were created

---

### Error 8: Issue Linking Failed

**Message:**
```
Error: Cannot link ABC-2211 to ABC-1909 with link type 'Parent-Child'
```

**Causes:**
- Link direction is reversed (outward vs inward)
- Link type ID is incorrect (use 10402 for Parent-Child)
- One or both issues don't exist yet
- Circular linking detected (would create a loop)

**Solution:**
1. Verify link direction:
   - Parent (Capability) → Child (Feature): `inward_issue_key=ABC-1909`, `outward_issue_key=ABC-2211`
   - Not reversed: `inward_issue_key=ABC-2211`, `outward_issue_key=ABC-1909` (wrong!)
2. Confirm both issues exist before linking
3. Use link type ID 10402 exactly
4. Retry linking

**Prevention:**
- In Step 5, double-check the link direction before executing
- Use SKILL.md Step 5 format exactly (inward/outward are clearly labeled)

---

### Error 9: Timeout / Rate Limiting

**Message:**
```
Error 429 Too Many Requests: Rate limit exceeded
```

**Causes:**
- Too many parallel API calls in Step 4 (creating all stories simultaneously)
- Jira instance has strict rate limits
- MCP server is throttling requests

**Solution:**
1. Reduce parallelism: create stories sequentially instead of in parallel (slower but more reliable)
2. Wait 60 seconds and retry
3. If persistent, contact Jira admin about rate limit policy

**Prevention:**
- For large features (10+ stories), create in batches: 3-4 stories at a time, wait 30s, continue
- Monitor MCP server logs for throttling warnings

---

## Diagnostic Commands

### Find Your Custom Field IDs
```jql
project = ABC AND customfield_11028 is not EMPTY
```
If this returns issues, customfield_11028 exists in ABC.  
If no results, the field ID is different; find it via Jira Admin → Custom Fields.

### List All Clones from a Cloning Operation
```jql
labels = clonedFromABC-2026@2026_04_22:16:40
```
Returns all issues (Feature + Stories) created from cloning ABC-2026.

### Find Issues with Parent-Child Links
```jql
issueLink = "is parent of" AND project = ABC
```
Returns all Features in ABC that have child Stories.

### Find Capability Parents
```jql
issuetype = Capability AND issueLink = "is parent of" AND project = ABC
```
Returns all Capabilities in ABC that have child Features.

