import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { promises as fs } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import test from "node:test";

const execFileAsync = promisify(execFile);
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const validatorPath = path.join(repoRoot, "scripts", "validate-template.mjs");
const fixtureEntries = [
  ".claude-plugin",
  ".cursor-plugin",
  ".mcp.json",
  "assets",
  "gemini-extension.json",
  "mcp.json",
  "plugin.json",
  "skills",
];

async function createFixture(t) {
  const fixtureRoot = await fs.mkdtemp(path.join(os.tmpdir(), "atlassian-mcp-validator-"));
  t.after(() => fs.rm(fixtureRoot, { recursive: true, force: true }));

  for (const entry of fixtureEntries) {
    await fs.cp(path.join(repoRoot, entry), path.join(fixtureRoot, entry), { recursive: true });
  }

  return fixtureRoot;
}

async function runValidator(cwd) {
  try {
    const result = await execFileAsync(process.execPath, [validatorPath], { cwd });
    return { ...result, exitCode: 0 };
  } catch (error) {
    return {
      stdout: error.stdout ?? "",
      stderr: error.stderr ?? "",
      exitCode: error.code,
    };
  }
}

async function writeSkill(fixtureRoot, frontmatter) {
  const skillPath = path.join(
    fixtureRoot,
    "skills",
    "capture-tasks-from-meeting-notes",
    "SKILL.md"
  );
  await fs.writeFile(skillPath, `${frontmatter}\n\n# Test skill\n`, "utf8");
}

async function writeMcpConfig(fixtureRoot, server) {
  const config = {
    $schema: "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
    mcpServers: { atlassian: server },
  };
  await fs.writeFile(path.join(fixtureRoot, "mcp.json"), `${JSON.stringify(config, null, 2)}\n`, "utf8");
}

test("the repository package passes validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  const result = await runValidator(fixtureRoot);

  assert.equal(result.exitCode, 0, result.stderr);
  assert.match(result.stdout, /Validation passed\./);
});

test("malformed Agent Skill YAML fails validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeSkill(
    fixtureRoot,
    `---
name: capture-tasks-from-meeting-notes
description: Test description
metadata: [unterminated
---`
  );

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /contains invalid YAML frontmatter/);
});

test("non-mapping Agent Skill frontmatter fails validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeSkill(fixtureRoot, `---
- name
- description
---`);

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /YAML frontmatter that must be a mapping/);
});

test("non-string Agent Skill fields fail validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeSkill(
    fixtureRoot,
    `---
name:
  - capture-tasks-from-meeting-notes
description: true
---`
  );

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /invalid Agent Skill name/);
  assert.match(result.stderr, /skill description must be 1-1024 characters/);
});

test("quoted, folded, and literal YAML strings pass validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeSkill(
    fixtureRoot,
    `---
name: "capture-tasks-from-meeting-notes"
description: >
  Find action items in meeting notes
  and create Jira tasks.
metadata:
  usage: |
    meeting notes
    action items
---`
  );

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 0, result.stderr);
});

test("invalid HTTP header names fail validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeMcpConfig(fixtureRoot, {
    type: "streamable-http",
    url: "https://mcp.atlassian.com/v1/mcp/authv2",
    headers: { "Bad Header": "value" },
  });

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /invalid HTTP header name "Bad Header"/);
});

test("invalid HTTP header values fail validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeMcpConfig(fixtureRoot, {
    type: "streamable-http",
    url: "https://mcp.atlassian.com/v1/mcp/authv2",
    headers: { "X-Test": "first line\nsecond line" },
  });

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /X-Test contains an invalid HTTP header value/);
});

test("header names remain case-insensitively unique", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeMcpConfig(fixtureRoot, {
    type: "streamable-http",
    url: "https://mcp.atlassian.com/v1/mcp/authv2",
    headers: { "X-Test": "first", "x-test": "second" },
  });

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /duplicate header "x-test" with different casing/);
});

test("shell-style stdio commands fail validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeMcpConfig(fixtureRoot, { type: "stdio", command: "node --inspect" });

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /command must be a single executable token/);
});

test("stdio arguments pass when separated from the executable", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeMcpConfig(fixtureRoot, {
    type: "stdio",
    command: "node",
    args: ["--inspect"],
  });

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 0, result.stderr);
});
