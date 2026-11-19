import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { promises as fs } from "node:fs";
import path from "node:path";
import test from "node:test";
import { promisify } from "node:util";
import { parseFrontmatter } from "./validation/agent-skills.mjs";
import { repoRoot } from "./validation/test-helpers.mjs";

const execFileAsync = promisify(execFile);

test("Gemini overrides have valid skill metadata and produce runnable offline reports", async () => {
  const manifest = JSON.parse(await fs.readFile(path.join(repoRoot, ".gemini-plugin/plugin.json"), "utf8"));
  for (const source of manifest.skills) {
    const name = source.split("/")[2];
    const content = await fs.readFile(path.join(repoRoot, "gemini/overrides", name, "SKILL.md"), "utf8");
    const { fields, error } = parseFrontmatter(content);
    assert.equal(error, null, name);
    assert.equal(fields.name, name);
    assert.ok(fields.description.length > 0 && fields.description.length <= 1024, name);
  }
  const { stdout } = await execFileAsync("python3", ["-B", "scripts/test_gemini_package.py"], { cwd: repoRoot });
  assert.match(stdout, /Gemini package checks passed/);
});
