# Multi-Project Cloning Scenarios

## Scenario 1: Single-Project Feature with Multi-Project Child Stories (ABC-2026 Real Example)

**Source:** ABC-2026 (Feature, ABC project)  
**Parent:** ABC-1909 (Capability, ABC project)  
**Child Stories:** 7 total
- ABC-717 to ABC-721: ABC project
- XYZ-722 to XYZ-723: XYZ project

**Cloning Outcome:**
- ABC-2026 → **ABC-2211** (Feature clone, ABC project)
- ABC-1909 → ABC-2211 (Capability parent link preserved)
- ABC-717 → **ABC-595** (Story 1, ABC project)
- ABC-718 → **ABC-596** (Story 2, ABC project)
- ABC-719 → **ABC-597** (Story 3, ABC project)
- ABC-720 → **ABC-598** (Story 4, ABC project)
- ABC-721 → **ABC-599** (Story 5, ABC project)
- XYZ-722 → **XYZ-595** (Story 6, XYZ project)
- XYZ-723 → **XYZ-596** (Story 7, XYZ project)

**Field Preservation Validation:**

| Field | Source Feature | Cloned Feature | Status |
|-------|----------------|---|--------|
| Summary | "Design Dashboard Module" | "Design Dashboard Module" (no `[TEMPLATE]` prefix) | ✓ Copied |
| Description | Full Markdown body | Identical Markdown | ✓ Copied |
| Acceptance Criteria | 4 bullet points | All 4 criteria preserved | ✓ Copied |
| Components | ["Frontend", "API"] | ["Frontend", "API"] | ✓ Copied |
| Size (Feature) | 13 | 13 | ✓ Copied |
| Labels (before) | ["template", "core-module"] | ["core-module", "clonedFromABC-2026@2026_04_22:16:40"] | ✓ Filtered & Added |
| Status | "Approved" | "Created" | ✗ Not Copied (default assigned) |
| Assignee | "alice@example.com" | Unassigned | ✗ Not Copied |

**Cloning Label on All 8 Issues:**
```
labels: ["clonedFromABC-2026@2026_04_22:16:40"]
```
Search in Jira: `project in (ABC, XYZ) AND labels = clonedFromABC-2026@2026_04_22:16:40` → Returns all 8 clones

---

## Scenario 2: Cross-Project Parent Discovery

**Source:** ABC-1909 (Capability, ABC project)  
**Discovers:** ABC-2026 as child Feature (both ABC)

**Cloning Path:**
1. User asks to clone ABC-2026 Feature
2. Step 2 finds parent: ABC-1909 via Parent-Child issuelink (inward)
3. When Feature ABC-2026 is cloned to ABC-2211, the link ABC-1909 → ABC-2211 is recreated automatically
4. If a Capability link is also cloned, same pattern applies

**Key:** Parent-child links persist even when parent and child are in different projects.

---

## Scenario 3: Edge Case — Feature with No Capability Parent

**Source:** ABC-2045 (Feature, ABC project, no parent Capability)  
**Child Stories:** 3 stories in ABC

**Cloning Outcome:**
- No parent link to recreate
- Only Feature → Stories links created
- Cloning proceeds normally with 4 issues (1 Feature + 3 Stories)
- **Tip:** Add cloned feature to an existing Capability post-clone using Jira UI or `link_to_epic` if using Epic links

---

## Scenario 4: Complex Distribution — 3 Projects

**Source:** ABC-2026 (Feature, ABC project)  
**Parent:** ABC-1909 (Capability, ABC project)  
**Child Stories:**
- ABC-717, ABC-718, ABC-719 (ABC project)
- XYZ-722, XYZ-723 (XYZ project)
- DEV-501, DEV-502, DEV-503 (hypothetical third project)

**Cloning Outcome:**
- ABC-2026 → ABC-2211 (Feature, ABC)
- ABC-717-719 → ABC-595-597 (Stories, ABC)
- XYZ-722-723 → XYZ-595-596 (Stories, XYZ)
- DEV-501-503 → DEV-595-597 (Stories, DEV)
- All 11 issues tagged: `clonedFromABC-2026@2026_04_22:16:40`
- All links preserved: ABC-1909 → ABC-2211 → [ABC-595-597, XYZ-595-596, DEV-595-597]

---

## Lessons Learned from Execution

### 1. Parallel Story Creation Reorders Results
- **Observation:** When creating 7 child stories in parallel via MCP, response order did not match request order
  - Requested: ABC-717, 718, 719, XYZ-722, 723, and others
  - Returned: ABC-595 (was ABC-717), ABC-596 (was ABC-718), etc., in mixed order
- **Why:** Parallel API calls are non-deterministic; responses complete as servers respond, not in request sequence
- **Impact:** No impact on correctness; all links and labels are still accurate
- **Workaround:** Use the cloning label to search and verify all stories were created, then rely on label-based grouping

### 2. Project Distribution is Automatic
- **Observation:** MCP honors each story's original project; no manual override needed
  - Story originally in ABC → Clone goes to ABC
  - Story originally in XYZ → Clone goes to XYZ
- **Why:** The `project_key` parameter in `create_issue` is extracted from the issue type and component context
- **Benefit:** Cross-project features are seamlessly cloned without extra configuration

### 3. Components Parameter Conflict
- **Error:** "create_issue() got multiple values for keyword argument 'components'"
- **Root Cause:** Components passed both as direct parameter and in `additional_fields`
- **Solution:** Use `components` as dedicated parameter only; remove from `additional_fields`
- **Fix:** Step 4 in SKILL.md uses components parameter exclusively

### 4. Label Format Ensures Discoverability
- **Observation:** Even with reordered responses, all issues share the same timestamp label
  - Format: `clonedFromABC-2026@2026_04_22:16:40` (source key + execution timestamp)
  - Timestamp captured at workflow start, not per-issue
- **Benefit:** Search by label returns all clones from a single operation, regardless of creation order
- **Search:** `labels = clonedFromABC-2026@2026_04_22:16:40`

### 5. Status Field is Never Copied
- **Observation:** Cloned features start in "Created" status, not source status (e.g., "Approved")
- **Why:** Jira workflow validation requires new issues to start in default state
- **Benefit:** Prevents invalid state transitions
- **Action:** Teams must approve clones separately post-creation if approval is required

---

## Validation Checklist After Cloning

After completing a multi-project clone, verify:

- [ ] Feature clone exists in source project (ABC-2211 in ABC)
- [ ] All story clones exist in their original projects (ABC-595-599 in ABC, XYZ-595-596 in XYZ)
- [ ] Cloning label present on all issues: `clonedFromABC-2026@2026_04_22:16:40`
- [ ] Parent-child links recreated: ABC-1909 → ABC-2211 → [Stories]
- [ ] Fields preserved: summary, description, AC, components, labels (except 'template')
- [ ] Status set to default: "Created" for Feature, "To Do" for Stories
- [ ] Assignees empty (not copied)
- [ ] All 8 issues appear in JQL search: `labels = clonedFromABC-2026@2026_04_22:16:40`

