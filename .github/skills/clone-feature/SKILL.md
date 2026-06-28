---
name: clone-feature
description: "Clone a Jira Feature and all its child User Stories while preserving each item's original Jira project. Automatically handles multi-project scenarios, maintains parent-child relationships, and applies consistent labeling. Useful when duplicating feature templates for new initiatives, creating feature variations for different teams, or re-running a feature blueprint in a different project."
---

**Keywords:** clone-feature, copy-feature, duplicate-feature, clone-story, feature-template, reuse-feature

## Overview

This skill helps you duplicate a Jira Feature and all its child User Stories into new issues while preserving:
- Each item's original Jira project (stories stay in their project, feature stays in its project)
- Parent-child relationships (cloned stories link to cloned feature)
- Key fields: summary, description, acceptance criteria, components, labels (except `template`), fix versions
- Feature Size and Story Points
- Multi-project distribution (if your feature spans multiple projects, the clone will too)

Use this skill when you want to:
1. Create a new feature initiative from an existing template
2. Duplicate a feature for a different team or product line
3. Re-run a proven feature blueprint with updated context
4. Preserve feature structure across multiple Jira projects

## Workflow

### Step 1: Accept Source Feature Key

Greet the user and ask for the feature key to clone.

```
I can help you clone a Jira Feature and all its child User Stories while preserving each item's original project.

What Feature would you like to clone? Provide the Jira key (e.g., ACV2-101, ABC-1774).
```

Save the provided key as `source_feature_key`.

### Step 2: Fetch Source Feature & Parent Capability

```
Call: mcp_aptiv-atlassi_jira_get_issue
Parameters:
- issue_key: <source_feature_key>
- fields: "summary,description,customfield_11028,components,labels,fixVersions,customfield_10042,issuelinks,project"
```

Extract: `source_summary`, `source_description`, `source_ac`, `source_components`, `source_labels` (filter `template`), `source_fix_versions`, `source_size`, `source_project_key`

Discover parent Capability:
- Check `parent` field if issue type is Capability
- Else search `issuelinks` for Parent-Child link where `inward_issue` is Capability
- Store as `parent_capability_key` (null if not found)

If feature not found, stop.

### Step 3: Fetch All Child Stories

From Step 2 `issuelinks`, find all `outward_issue` entries with link type `Parent-Child` and issue type `Story`. For each:

```
Call: mcp_aptiv-atlassi_jira_get_issue
Parameters:
- issue_key: <child_story_key>
- fields: "summary,description,customfield_11028,components,labels,fixVersions,customfield_10060,project"
```

Extract per story: `story_key`, `story_summary`, `story_description`, `story_ac`, `story_components`, `story_labels` (filter `template`), `story_fix_versions`, `story_story_points`, `story_project_key`

**Fallback:** If no Parent-Child links exist, use JQL: `parent = <source_feature_key> AND type = Story`

Store all in list: `child_stories`

Continue if none found.

### Step 4: Build Cloning Summary & Get Approval

Count items per project: `projects_distribution = {<project_key>: {"features": 1/0, "stories": N}, ...}`

Present approval summary:

```
**Cloning Plan**
Source Feature: <key> – <summary>
Total: 1 feature + N stories

Per-project breakdown:
- <PROJECT>: M items

Cloning label: clonedFrom<sourceKey>@<timestamp>

Preserved fields: summary, description, AC, components, labels (except 'template'), 
fix versions, Size (feature), Story Points (stories)

Links: Capability → Feature, Feature → Stories

Proceed?
```

Wait for explicit user confirmation before continuing.

### Step 5: Generate Cloning Label

```
timestamp_format = YYYY_MM_DD:HH:MM (e.g., 2026_04_22:14:35)
cloning_label = f"clonedFrom{source_feature_key}@{timestamp_format}"
```

### Step 6: Create Cloned Feature

```
Call: mcp_aptiv-atlassi_jira_create_issue
Parameters:
- projectKey: <source_project_key>
- issueTypeName: "Features"
- summary: <source_summary with [TEMPLATE] removed, whitespace stripped>
- description: <source_description>
- additional_fields: {
    "customfield_11028": <source_ac>,
    "components": <source_components>,
    "labels": <source_labels (exclude 'template') + cloning_label>,
    "fixVersions": <source_fix_versions>,
    "customfield_10042": <source_size>
  }
```

Store `cloned_feature_key` from response.

### Step 7: Link Cloned Feature to Capability (if parent exists)

If `parent_capability_key` is not null:

```
Call: mcp_aptiv-atlassi_jira_create_issue_link
Parameters:
- inward_issue_key: <parent_capability_key>
- outward_issue_key: <cloned_feature_key>
- link_type: "Parent-Child"
```

If linking fails, continue (feature is created; link is secondary).

### Step 8: Create Cloned Stories & Link Each to Feature

For each story in `child_stories`:

```
Call: mcp_aptiv-atlassi_jira_create_issue
Parameters:
- projectKey: <story_project_key>
- issueTypeName: "Story"
- summary: <summary with [TEMPLATE] removed, whitespace stripped>
- description: <story_description>
- additional_fields: {
    "customfield_11028": <story_ac>,
    "components": <story_components>,
    "labels": <story_labels (exclude 'template') + cloning_label>,
    "fixVersions": <story_fix_versions>,
    "customfield_10060": <story_story_points>
  }
```

Store each `cloned_story_key`. Then link to cloned feature:

```
Call: mcp_aptiv-atlassi_jira_create_issue_link
Parameters:
- inward_issue_key: <cloned_feature_key>
- outward_issue_key: <cloned_story_key>
- link_type: "Parent-Child"
```

If any creation/link fails, log and continue with remaining stories.

### Step 9: Report Results

After all creations complete, present the final report:

```
✅ **Cloning Complete**

**Cloned Feature:** [ABC-2045](https://yoursite.atlassian.net/browse/ABC-2045)

**Issues Created:**
- PROJECT-ABC: 4 (1 feature + 3 stories)
- PROJECT-DEV: 2 (2 stories)

**Total:** 6 new issues created

All items labeled: clonedFromABC-1774@2026_04_22:14:35
```

If there were any failures, clearly separate successful creations from failures.

---

## Edge Cases & Troubleshooting

**Feature not found**
- Inform user and stop: "Feature <key> not found. Verify and try again."

**Feature has no parent Capability**
- Proceed with cloning; note: "Source has no parent. Cloned feature will not be linked."

**Feature has no child stories**
- Proceed with cloning feature only. Confirm: "No child stories found. Clone feature alone?"

**User lacks permission to create in target project**
- Stop and inform: "No permission to create in <project>. Contact Jira admin."

**Custom field IDs don't match**
- Use metadata discovery to find correct field IDs; adjust and retry.
- Inform user of any adjustments made.

**Stories span multiple projects with different permissions**
- Create stories where user has permission; report successes/failures separately.

**Labeling fails after creation**
- Attempt to add label via update call as fallback.
- If both fail, inform user and provide manual instruction.

**Child stories created in different order than source**
- Expected behavior with parallel creation; all stories linked correctly regardless of order.
- Cloning label `clonedFrom<featureKey>@<timestamp>` groups all clones from one operation.
- If sequential order is critical, create stories one at a time.

---

## Tips for High-Quality Results

1. **Verify source feature exists** before showing approval summary.
2. **Remove [TEMPLATE] prefix** from summaries and strip whitespace.
3. **Filter labels:** Exclude `template` label; add `cloning_label` to all clones.
4. **Preserve field values** verbatim—don't modify descriptions, components, etc.
5. **Discover custom field IDs** via metadata if standard IDs don't match.
6. **Label grouping:** Format `clonedFrom<featureKey>@<timestamp>` enables searchability for all clones from one operation.
7. **Test incrementally:** Clone small features (1-2 stories) before complex multi-project scenarios.

---

## Examples

### Single-Project Cloning
**Request:** Clone ABC-1774
**Source:** ABC-1774 (Feature) → 3 stories in ABC → parent Capability ABC-100
**Result:** ABC-2045 + ABC-2046, 2047, 2048 (all linked, all labeled)

### Multi-Project Cloning
**Request:** Clone ABC-2026  
**Source:** ABC-2026 (Feature) → 5 stories in ABC, 2 stories in XYZ → parent Capability ABC-1909  
**Result:** ABC-2211 + ABC-595-599 (ABC) + XYZ-595-596 (XYZ) (all linked, all labeled)

### Prefix Removal
**Source:** "[TEMPLATE] Enable bulk-edit on case list"  
**Clone:** "Enable bulk-edit on case list"

---

## Quick Reference

| Aspect | Value |
|--------|-------|
| Cloning Label Format | `clonedFrom<sourceKey>@YYYY_MM_DD:HH:MM` |
| Excluded Label | `template` |
| Excluded Prefix | `[TEMPLATE] ` |
| Fields Cloned | summary, description, AC, components, labels, fix versions |
| Feature Size Field | customfield_10042 |
| Story Points Field | customfield_10060 |
| Acceptance Criteria Field | customfield_11028 |
| Capability → Feature Link | Parent-Child with inward=Capability, outward=Feature |
| Feature → Story Link | Parent-Child with inward=Feature, outward=Story |
| Issue Types | Features, Story, Capability |

---

## When NOT to Use This Skill

- **Cloning a single User Story** — use Jira's built-in duplicate feature instead
- **Cloning across different Jira instances** — this skill works within one cloud instance
- **Cloning archived or deleted features** — verify the feature exists first
- **Cloning with heavily customized field mappings** — if your Jira has non-standard field IDs, you may need manual adjustment
