## Action Item Pattern Examples

### Pattern 1: @Mentions (Most Explicit)

```
@john to update documentation
@sarah will create the report
@mike should review PR #123
```

**Parsed:**
- Assignee: john/sarah/mike
- Task: update documentation / create the report / review PR #123

---

### Pattern 2: Name + Action Verb

```
John to update documentation
Sarah will create the report
Mike should review PR #123
Lisa needs to test the feature
```

**Parsed:**
- Assignee: name before action verb
- Task: text after "to/will/should/needs to"

---

### Pattern 3: Structured Action Format

```
Action: John - update documentation
Action Item: Sarah - create the report
AI: Mike - review PR #123
```

**Parsed:**
- Assignee: name after "Action:" and before "-"
- Task: text after "-"

---

### Pattern 4: TODO Format

```
TODO: Update documentation (John)
TODO: Create report - Sarah
[ ] Mike: review PR #123
```

**Parsed:**
- Assignee: name in parentheses or after ":"
- Task: text between TODO and assignee

---

### Pattern 5: Bullet Lists

```
- John: update documentation
- Sarah - create the report
* Mike will review PR #123
```

**Parsed:**
- Assignee: name before ":" or "-" or action verb
- Task: remaining text

---

## Handling Edge Cases

### No Action Items Found

If no action items with assignees are detected:

```
I analyzed the meeting notes but couldn't find any action items with clear assignees.

Action items typically follow patterns like:
- @Name to do X
- Name will do X
- Action: Name - do X
- TODO: X (Name)

Options:
1. I can search for TODO items without assignees
2. You can point out specific action items to create
3. I can create tasks for bullet points you specify

What would you like to do?
```

---

### Mixed Formats

If some action items have assignees and some don't:

```
I found [N] action items:
- [X] with clear assignees
- [Y] without assignees

Should I:
1. Create all [N] tasks ([X] assigned, [Y] unassigned)
2. Only create the [X] tasks with assignees
3. Ask you to assign the [Y] unassigned tasks

Which option would you prefer?
```

---

### Assignee Name Variations

If the same person is mentioned different ways:

```
Notes mention: @sarah, Sarah, Sarah J.

These likely refer to the same person. I'll look up "Sarah" once and use
that account ID for all three mentions. Is that correct?
```

---

### Duplicate Action Items

If the same task appears multiple times:

```
I found what appears to be the same action item twice:
1. "@Sarah to create user stories" (line 15)
2. "Action: Sarah - create user stories" (line 42)

Should I:
1. Create one task (combine duplicates)
2. Create two separate tasks
3. Skip the duplicate

What would you prefer?
```

---

### Long Task Descriptions

If action item text is very long (>200 characters):

```
The task "[long text...]" is quite detailed.

Should I:
1. Use first sentence as summary, rest in description
2. Use full text as summary
3. Let you edit it to be more concise

Which would you prefer?
```

---

## Tips for High-Quality Results

### Do:
✅ Use consistent @mention format in notes
✅ Include full names when possible
✅ Be specific in action item descriptions
✅ Add context (why/what/when)
✅ Review parsed tasks before confirming

### Don't:
❌ Mix multiple tasks for one person in one bullet
❌ Use ambiguous names (just "John" if you have 5 Johns)
❌ Skip action verbs (unclear what to do)
❌ Forget to specify project

### Best Meeting Notes Format

```
# Meeting Title - Date

Attendees: [Names]

## Decisions
[What was decided]

## Action Items
- @FullName to [specific task with context]
- @AnotherPerson will [specific task with context]
- etc.
```

---


## Examples

### Example 1: Simple @Mentions

**Input:**
```
Team Sync - Dec 3, 2025

Action Items:
- @Sarah to create user stories for chat feature
- @Mike will update the architecture doc
- @Lisa should review design mockups
```

**Process:**
1. Parse → 3 action items found
2. Project → "PROJ"
3. Lookup → Sarah (123), Mike (456), Lisa (789)
4. Present → User confirms
5. Create → PROJ-100, PROJ-101, PROJ-102

**Output:**
```
✅ Created 3 tasks in PROJ:

1. PROJ-100 - Create user stories for chat feature
   Assigned to: Sarah Johnson

2. PROJ-101 - Update the architecture doc
   Assigned to: Mike Chen

3. PROJ-102 - Review design mockups
   Assigned to: Lisa Park
```

---

### Example 2: Mixed Formats

**Input:**
```
Product Review Meeting

Discussed new features and priorities.

Follow-ups:
- Sarah will draft the PRD
- Mike: implement API changes
- TODO: Review security audit (Lisa)
- Update stakeholders on timeline
```

**Process:**
1. Parse → Found 4 items (3 with assignees, 1 without)
2. Ask → "Found 3 with assignees, 1 without. Create all or only assigned?"
3. User → "All, make the last one unassigned"
4. Create → 4 tasks (3 assigned, 1 unassigned)

---

### Example 3: Name Lookup Issue

**Input:**
```
Sprint Planning

Action Items:
- @John to update tests
- @Sarah to refactor code
```

**Process:**
1. Parse → 2 action items
2. Lookup "John" → Found 3 Johns!
3. Ask → "Which John? (John Smith, John Doe, John Wilson)"
4. User → "John Smith"
5. Create → Both tasks assigned correctly

---
