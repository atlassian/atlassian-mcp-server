import { execFile } from "node:child_process";
import { promises as fs } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
export const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
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

export async function createFixture(t) {
  const fixtureRoot = await fs.mkdtemp(path.join(os.tmpdir(), "atlassian-mcp-validator-"));
  t.after(() => fs.rm(fixtureRoot, { recursive: true, force: true }));

  for (const entry of fixtureEntries) {
    await fs.cp(path.join(repoRoot, entry), path.join(fixtureRoot, entry), { recursive: true });
  }
  return fixtureRoot;
}

export async function createEmptyFixture(t) {
  const fixtureRoot = await fs.mkdtemp(path.join(os.tmpdir(), "atlassian-mcp-validator-unit-"));
  t.after(() => fs.rm(fixtureRoot, { recursive: true, force: true }));
  return fixtureRoot;
}

export async function runValidator(cwd) {
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

export async function writeSkill(fixtureRoot, directoryName, frontmatter) {
  const skillDir = path.join(fixtureRoot, "skills", directoryName);
  await fs.mkdir(skillDir, { recursive: true });
  await fs.writeFile(path.join(skillDir, "SKILL.md"), `${frontmatter}\n\n# Test skill\n`, "utf8");
}
