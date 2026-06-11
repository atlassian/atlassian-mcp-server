# Cloning Patterns & Field Preservation Rules

## Label Format

Every cloned issue receives a **label** that tracks the source and timestamp of the clone operation.

**Format:** `clonedFrom<SOURCE_KEY>@<YYYY_MM_DD:HH:MM>`

**Example:** `clonedFromABC-2026@2026_04_22:16:40`

This label serves as a searchable reference. Use it to find all issues created from a single cloning operation.

---

## Field Preservation Rules

### Always Copied (Feature → Feature Clone)
- **Summary** (with `[TEMPLATE]` prefix removed, if present)
- **Description**
- **Acceptance Criteria** (customfield_11028)
- **Components**
- **Labels** (all existing labels preserved, cloning label added)
- **Fix Versions** (fixVersions)
- **Size/Story Points** (customfield_10042 for Features; customfield_10060 for Stories)

### Never Copied
- **Status** (Jira assigns default: "Created" for Features, "To Do" for Stories)
- **Assignee** (clone has no assignee; teams assign post-creation)
- **Reporter** (automatically the cloning user)
- **Comments** (fresh issues have no historical comments)
- **Worklogs** (time tracking resets)
- **Subtasks** (if using subtask hierarchy; use Parent-Child links instead)

### Conditional (Project-Specific)
- **Custom Fields:** Only copied if the target project has the same custom field IDs
  - If field IDs differ, use JQL to look up the correct IDs in the target project
  - Example: ABC project has customfield_11028 for AC; XYZ project may use a different ID
- **Components:** Only if target project has matching component names
  - If names differ, the API call fails; retry without components or update component names

---

## Link Direction Rules

All parent-child links use the **Parent-Child** link type (ID: 10402).

### Capability → Feature (Parent-Child)
- **Inward issue:** Capability (parent)
- **Outward issue:** Feature (child)
- **Example:** ABC-1909 (Capability) is the parent of ABC-2211 (Feature clone)
- **Direction:** inward_issue_key=ABC-1909, outward_issue_key=ABC-2211

### Feature → Story (Parent-Child)
- **Inward issue:** Feature (parent)
- **Outward issue:** Story (child)
- **Example:** ABC-2211 (Feature) is the parent of ABC-717 through ABC-723 (Story clones)
- **Direction:** inward_issue_key=ABC-2211, outward_issue_key=ABC-717 (and so on)

### Cross-Project Links
- Parent-child links work across projects
- **Example:** ABC-2211 (ABC project Feature) → XYZ-717 (XYZ project Story)
- Jira preserves the link regardless of project distribution

---

## Multi-Project Preservation

When cloning a Feature with child Stories distributed across multiple projects:

1. **Feature clone stays in source project** (e.g., ABC-2026 → ABC-2211)
2. **Story clones remain in their original projects**
   - If source story is in ABC, clone is in ABC
   - If source story is in XYZ, clone is in XYZ
   - If source story is in a third project, clone is in that project
3. **Parent-child links cross project boundaries** seamlessly
   - ABC-2211 Feature → ABC-717, ABC-718 Stories (in ABC)
   - ABC-2211 Feature → XYZ-719, XYZ-720 Stories (in XYZ)
4. **All clones share the same cloning label** for easy discovery
   - Search: `labels = clonedFromABC-2026@2026_04_22:16:40` returns all 8 clones

---

## Field ID Quick Reference

| Field | Type | ID | Used For |
|-------|------|-----|----------|
| Acceptance Criteria | Custom | customfield_11028 | Features & Stories |
| Size | Custom | customfield_10042 | Features |
| Story Points | Custom | customfield_10060 | Stories |
| Fix Versions | Built-in | fixVersions | Any issue |
| Components | Built-in | components | Any issue |
| Labels | Built-in | labels | Any issue |

---

## Why Certain Fields Are Excluded

- **Status:** New issues must start in a default state. Copying "Done" status would bypass workflow validation.
- **Assignee:** Clones are unassigned by design; let teams choose who implements.
- **Comments:** Historical discussions don't apply to new work; keep clones clean.
- **Worklogs:** Time tracking is specific to the original execution; don't carry over.

