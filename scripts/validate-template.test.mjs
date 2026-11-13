import assert from "node:assert/strict";
import { promises as fs } from "node:fs";
import path from "node:path";
import test from "node:test";
import { createFixture, runValidator, writeSkill } from "./validation/test-helpers.mjs";

test("the repository package passes validation", async (t) => {
  const fixtureRoot = await createFixture(t);
  const result = await runValidator(fixtureRoot);

  assert.equal(result.exitCode, 0, result.stderr);
  assert.match(result.stdout, /Validation passed\./);
});

test("the CLI reports validation failures and exits with status 1", async (t) => {
  const fixtureRoot = await createFixture(t);
  await writeSkill(
    fixtureRoot,
    "capture-tasks-from-meeting-notes",
    `---
name: capture-tasks-from-meeting-notes
description: Test description
metadata: [unterminated
---`
  );

  const result = await runValidator(fixtureRoot);
  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /^Validation failed:/);
  assert.match(result.stderr, /contains invalid YAML frontmatter/);
});

test("the CLI rejects falsy primitive Agent Plugin root documents", async (t) => {
  const fixtureRoot = await createFixture(t);
  await Promise.all([
    fs.writeFile(path.join(fixtureRoot, "plugin.json"), "false\n", "utf8"),
    fs.writeFile(path.join(fixtureRoot, "mcp.json"), "false\n", "utf8"),
  ]);

  const result = await runValidator(fixtureRoot);

  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /Agent Plugins manifest must contain a JSON object\./);
  assert.match(result.stderr, /Agent Plugins mcp\.json must contain a JSON object\./);
});

test("the CLI rejects Gemini Agent configuration drift and invalid skill paths", async (t) => {
  const fixtureRoot = await createFixture(t);
  const manifestPath = path.join(fixtureRoot, ".gemini-plugin", "plugin.json");
  const manifest = JSON.parse(await fs.readFile(manifestPath, "utf8"));
  manifest.name = "different-plugin";
  manifest.mcpServers = { atlassian: { url: "https://example.com/mcp" } };
  manifest.skills = ["../outside/SKILL.md", "./skills/not-present/SKILL.md"];
  await fs.writeFile(manifestPath, JSON.stringify(manifest), "utf8");

  const result = await runValidator(fixtureRoot);

  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /Gemini Agent and Claude plugin names must match/);
  assert.match(result.stderr, /mcpServers must reference/);
  assert.match(result.stderr, /Gemini Agent skills must reference root-level/);
  assert.match(result.stderr, /references missing path/);
});

test("the CLI rejects a non-object Gemini Agent manifest", async (t) => {
  const fixtureRoot = await createFixture(t);
  await fs.writeFile(path.join(fixtureRoot, ".gemini-plugin", "plugin.json"), "null\n", "utf8");

  const result = await runValidator(fixtureRoot);

  assert.equal(result.exitCode, 1);
  assert.match(result.stderr, /Gemini Agent plugin manifest must contain a JSON object/);
});
