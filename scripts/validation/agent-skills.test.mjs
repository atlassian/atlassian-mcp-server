import assert from "node:assert/strict";
import test from "node:test";
import { parseFrontmatter, validateAgentSkills } from "./agent-skills.mjs";
import { createValidationContext } from "./common.mjs";
import { createEmptyFixture, writeSkill } from "./test-helpers.mjs";

test("malformed Agent Skill YAML is rejected", () => {
  const result = parseFrontmatter(`---
name: test-skill
description: Test description
metadata: [unterminated
---`);

  assert.match(result.error, /contains invalid YAML frontmatter/);
});

test("non-mapping Agent Skill frontmatter is rejected", () => {
  const result = parseFrontmatter(`---
- name
- description
---`);

  assert.match(result.error, /YAML frontmatter that must be a mapping/);
});

test("quoted, folded, and literal YAML strings are parsed", () => {
  const result = parseFrontmatter(`---
name: "test-skill"
description: >
  Find action items in meeting notes
  and create Jira tasks.
metadata:
  usage: |
    meeting notes
    action items
---`);

  assert.equal(result.error, null);
  assert.equal(result.fields.name, "test-skill");
  assert.match(result.fields.description, /Find action items.*create Jira tasks\./s);
  assert.equal(result.fields.metadata.usage, "meeting notes\naction items\n");
});

test("Agent Skill fields must use valid string values", async (t) => {
  const fixtureRoot = await createEmptyFixture(t);
  await writeSkill(
    fixtureRoot,
    "test-skill",
    `---
name:
  - test-skill
description: true
---`
  );
  const validation = createValidationContext(fixtureRoot);

  await validateAgentSkills(validation, fixtureRoot);

  assert.ok(validation.errors.some((error) => error.includes("invalid Agent Skill name")));
  assert.ok(validation.errors.some((error) => error.includes("description must be 1-1024 characters")));
});

test("Agent Skill names must match their parent directory", async (t) => {
  const fixtureRoot = await createEmptyFixture(t);
  await writeSkill(
    fixtureRoot,
    "test-skill",
    `---
name: different-skill
description: Test description
---`
  );
  const validation = createValidationContext(fixtureRoot);

  await validateAgentSkills(validation, fixtureRoot);

  assert.ok(validation.errors.some((error) => error.includes('must match its parent directory "test-skill"')));
});
