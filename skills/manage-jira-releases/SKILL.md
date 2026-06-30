---
name: manage-jira-releases
description: "Create and manage Jira project versions (releases) to organize work into shippable increments. When an agent needs to: (1) Create a new version/release in a Jira project, (2) Update an existing version's details such as description or dates, (3) Mark a version as released, or (4) List versions for a project. Handles version creation with name, description, start/release dates, and manages the version lifecycle from planning through release."
---

# Manage Jira Releases

## Keywords
create version, create release, new version, new release, jira version, jira release, project version, fix version, release version, manage versions, manage releases, ship release, mark released, update version, update release, list versions, list releases, version management, release management, set fix version, plan release

## Overview

Create and manage Jira project versions (releases) to organize issues into shippable increments. This skill enables creating new versions, updating version details (description, dates), listing existing versions, and marking versions as released—eliminating the need to switch to Jira's UI for version management.

**Use this skill when:** Users need to create, update, list, or release Jira project versions/releases.

---

## Core Workflow

**CRITICAL: Always follow this sequence for version creation:**

1. **Identify Project** → Determine target Jira project
2. **Gather Version Details** → Collect name, description, dates
3. **Present Plan** → Show user what will be created
4. **Create Version** → Execute the API call
5. **Confirm & Summarize** → Present result with next steps

---

## Step 1: Identify Project

Determine the target Jira project for the version.

### If user provides a project key:

Use it directly (e.g., "PROJ", "ENG", "MOBILE").

### If user is unsure:

Call `getVisibleJiraProjects` to show available projects:
```
getVisibleJiraProjects(
  cloudId="...",
  action="create"
)
```

Present: "I found these projects you can manage versions for: PROJ (Project Alpha), ENG (Engineering), MOBILE (Mobile Apps). Which one?"

### Get Cloud ID:

If not already known, call `getAccessibleAtlassianResources` to determine the cloudId for the user's Atlassian site.

---

## Step 2: Gather Version Details

Collect the necessary information for the version.

### Required:

- **Name** — The version name (e.g., "v1.2.0", "2025-Q1", "Sprint 23 Release")

### Optional:

- **Description** — What this version delivers or its scope
- **Start date** — When work on this version begins (format: `YYYY-MM-DD`)
- **Release date** — Target release/ship date (format: `YYYY-MM-DD`)

### Naming Conventions:

Help users follow their project's conventions:

**Semantic versioning:**
- `v1.0.0`, `v1.2.0`, `v2.0.0-beta`

**Date-based:**
- `2025-Q1`, `2025-W12`, `March 2025`

**Sprint-based:**
- `Sprint 23`, `Sprint 23 Release`

**Product-based:**
- `Launch MVP`, `Phase 2`, `GA Release`

### If Details Are Incomplete:

Ask for what's missing:
```
I'll create a version in [PROJECT]. I need a few details:

1. **Version name** (required): e.g., "v1.2.0" or "Sprint 23 Release"
2. **Description** (optional): What does this version deliver?
3. **Start date** (optional): When does work begin? (YYYY-MM-DD)
4. **Release date** (optional): Target ship date? (YYYY-MM-DD)
```

---

## Step 3: Present Plan

**Before creating**, confirm with the user:

```
I'll create this version in [PROJECT KEY]:

**Version:** [Name]
**Description:** [Description or "None"]
**Start date:** [Date or "Not set"]
**Release date:** [Date or "Not set"]

Shall I proceed?
```

Wait for user confirmation before proceeding.

---

## Step 4: Create Version

Once confirmed, create the version.

### Create the version:

```
createJiraVersion(
  cloudId="...",
  projectKey="PROJ",
  name="v1.2.0",
  description="Bug fixes and performance improvements for the dashboard module",
  startDate="2025-01-15",
  releaseDate="2025-02-01"
)
```

**Parameters:**
- `cloudId` (required) — The Atlassian Cloud site ID
- `projectKey` (required) — The Jira project key
- `name` (required) — Version name; must be unique within the project
- `description` (optional) — Description of what this version includes
- `startDate` (optional) — Start date in `YYYY-MM-DD` format
- `releaseDate` (optional) — Target release date in `YYYY-MM-DD` format

### Handle Errors:

**Duplicate name:**
```
A version named "v1.2.0" already exists in PROJ.

Would you like me to:
1. Use a different name (e.g., "v1.2.1" or "v1.3.0")
2. Update the existing version instead
3. List existing versions so you can choose
```

**Permission error:**
```
You don't have permission to create versions in PROJ.
Version management typically requires the "Administer Projects" permission.
Please ask your Jira admin for access.
```

---

## Step 5: Confirm & Summarize

After successful creation, confirm:

```
✅ Version created successfully!

**Project:** PROJ (Project Alpha)
**Version:** v1.2.0
**Description:** Bug fixes and performance improvements for the dashboard module
**Start date:** 2025-01-15
**Release date:** 2025-02-01
**Status:** Unreleased

**Next Steps:**
- Set fix version on issues: use "Fix Version" = "v1.2.0" when creating or editing issues
- View in Jira: https://yoursite.atlassian.net/projects/PROJ/versions
- When ready to ship, ask me to mark this version as released
```

---

## Additional Operations

### List Versions

When a user wants to see existing versions:

```
getJiraProjectVersions(
  cloudId="...",
  projectKey="PROJ"
)
```

**Present results:**
```
📋 **Versions in PROJ:**

| # | Name | Status | Release Date |
|---|------|--------|--------------|
| 1 | v1.0.0 | Released (2024-12-01) | 2024-12-01 |
| 2 | v1.1.0 | Released (2025-01-10) | 2025-01-10 |
| 3 | v1.2.0 | Unreleased | 2025-02-01 |
| 4 | v2.0.0-beta | Unreleased | — |

Would you like me to create a new version, update an existing one, or mark one as released?
```

### Update a Version

When a user wants to modify an existing version:

```
updateJiraVersion(
  cloudId="...",
  versionId="10001",
  name="v1.2.0",
  description="Updated description with new scope",
  startDate="2025-01-20",
  releaseDate="2025-02-15"
)
```

**Workflow:**
1. List versions to find the target (or ask for name)
2. Show current details
3. Ask what to change
4. Present update plan
5. Execute update
6. Confirm changes

**Example interaction:**
```
Current version details:
- **Name:** v1.2.0
- **Description:** Bug fixes and performance improvements
- **Start date:** 2025-01-15
- **Release date:** 2025-02-01

What would you like to update?
```

### Release a Version

When a user wants to mark a version as released:

```
updateJiraVersion(
  cloudId="...",
  versionId="10001",
  released=true,
  releaseDate="2025-02-01"
)
```

**Workflow:**
1. Confirm which version to release
2. Optionally set the release date to today if not specified
3. Ask about unreleased issues (move to next version or remove fix version)
4. Execute the release
5. Confirm

**Example interaction:**
```
I'll mark **v1.2.0** as released in PROJ.

**Release date:** 2025-02-01 (today)

⚠️ If there are unresolved issues with fix version "v1.2.0", they will remain
associated with this version unless you move them.

Shall I proceed with the release?
```

**After releasing:**
```
✅ Version released!

**Project:** PROJ
**Version:** v1.2.0
**Released:** 2025-02-01
**Status:** Released

**Next Steps:**
- Review the release notes in Jira
- Communicate the release to stakeholders
- Create the next version if needed
```

---

## Edge Cases & Troubleshooting

### Version Name Already Exists

If the version name conflicts:
1. Inform the user
2. Suggest alternatives (increment patch, add suffix)
3. Offer to list existing versions for context

### No Permission to Manage Versions

Version management requires "Administer Projects" permission in Jira. If the user lacks access:
1. Explain the permission requirement
2. Suggest they contact their Jira admin
3. Offer alternative actions (e.g., creating issues with a label instead)

### Project Has No Versions Feature

Some Jira project types (e.g., team-managed with versions disabled) may not support versions:
1. Explain that versions need to be enabled for the project
2. Guide: "Your Jira admin can enable versions in Project Settings → Features"

### Bulk Version Creation

If the user wants to create multiple versions at once:
```
I'll create these versions in PROJ:

1. v1.2.0 — Bug fixes (Release: 2025-02-01)
2. v1.3.0 — Feature additions (Release: 2025-03-01)
3. v2.0.0 — Major release (Release: 2025-06-01)

Shall I create all 3?
```

Create sequentially and report results for each.

---

## Integration with Other Skills

### With spec-to-backlog:
After creating tickets from a spec, suggest creating a version to group them:
"Would you like me to create a version for this work and set it as the fix version on the new tickets?"

### With capture-tasks-from-meeting-notes:
If meeting notes reference a release target, offer to create the version:
"The notes mention a 'v2.0 release'. Would you like me to create that version in Jira?"

### With generate-status-report:
When generating reports, reference version progress:
"Of 15 issues targeted for v1.2.0, 10 are Done, 3 are In Progress, and 2 are To Do."

---

## Examples

### Example 1: Simple Version Creation

**User:** "Create version v1.2.0 in project MOBILE with release date Feb 1"

**Process:**
1. Project: MOBILE (provided)
2. Details: name="v1.2.0", releaseDate="2025-02-01"
3. Present plan → User confirms
4. Create version
5. Confirm creation

**Output:**
```
✅ Version created successfully!

**Project:** MOBILE
**Version:** v1.2.0
**Release date:** 2025-02-01
**Status:** Unreleased
```

### Example 2: Version with Full Details

**User:** "Create a new release for the Q1 dashboard improvements in ENG"

**Process:**
1. Project: ENG (provided)
2. Ask for details: name, description, dates
3. User provides: "Dashboard Q1 Release", desc, dates
4. Present plan → User confirms
5. Create version
6. Confirm

**Output:**
```
✅ Version created successfully!

**Project:** ENG
**Version:** Dashboard Q1 Release
**Description:** Q1 dashboard improvements including new widgets, performance fixes, and dark mode support
**Start date:** 2025-01-06
**Release date:** 2025-03-31
**Status:** Unreleased
```

### Example 3: Release a Version

**User:** "Mark v1.1.0 as released in PROJ"

**Process:**
1. Find version "v1.1.0" in PROJ
2. Confirm: "Mark v1.1.0 as released with today's date?"
3. User confirms
4. Update version with released=true
5. Confirm

**Output:**
```
✅ Version released!

**Project:** PROJ
**Version:** v1.1.0
**Released:** 2025-01-15
**Status:** Released
```

### Example 4: List and Create

**User:** "What versions exist in BACKEND? I need to create the next one."

**Process:**
1. List versions in BACKEND
2. Show table of existing versions
3. Suggest next version name based on pattern
4. User confirms details
5. Create version
6. Confirm

**Output:**
```
📋 **Existing versions in BACKEND:**
- v3.0.0 (Released: 2024-11-01)
- v3.1.0 (Released: 2025-01-05)
- v3.2.0 (Unreleased, target: 2025-02-01)

Based on the pattern, the next version would be **v3.3.0**.

Would you like me to create v3.3.0? If so, what's the target release date?
```

---

## When NOT to Use This Skill

This skill is for **managing Jira project versions/releases only**.

**Don't use for:**
❌ Creating Jira issues or tickets (use spec-to-backlog or capture-tasks)
❌ Setting the fix version field on existing issues (use issue editing directly)
❌ Generating release notes content (use search + Confluence publishing)
❌ Managing sprints (sprints are different from versions)
❌ Creating Confluence release documentation pages

**Use only when:**
✅ "Create a version in Jira"
✅ "Add a release to project X"
✅ "Mark version Y as released"
✅ "What versions exist in project Z?"
✅ "Update the release date for version X"

---

## Quick Reference

**Primary tools:**
- `createJiraVersion(cloudId, projectKey, name, description?, startDate?, releaseDate?)` — Create a new version
- `getJiraProjectVersions(cloudId, projectKey)` — List all versions in a project
- `updateJiraVersion(cloudId, versionId, name?, description?, startDate?, releaseDate?, released?)` — Update or release a version

**Always:**
- Confirm with user before creating or modifying
- Use project-consistent naming conventions
- Include release dates when available
- Suggest next steps after creation

**Remember:**
- Version names must be unique within a project
- Releasing a version doesn't automatically move unresolved issues
- Version management requires "Administer Projects" permission
- Dates must be in `YYYY-MM-DD` format
