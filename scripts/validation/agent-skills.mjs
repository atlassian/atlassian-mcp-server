import { promises as fs } from "node:fs";
import path from "node:path";
import { parseDocument } from "yaml";
import { addError, isPlainObject, pathExists, walkFiles } from "./common.mjs";

const agentSkillNamePattern = /^(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;

function normalizeNewlines(content) {
  return content.replace(/\r\n/g, "\n");
}

export function parseFrontmatter(content) {
  const normalized = normalizeNewlines(content);
  if (!normalized.startsWith("---\n")) {
    return { fields: null, error: "is missing YAML frontmatter" };
  }

  const lines = normalized.split("\n");
  const closingIndex = lines.findIndex((line, index) => index > 0 && /^---[\t ]*$/.test(line));
  if (closingIndex < 0) {
    return { fields: null, error: "has unterminated YAML frontmatter" };
  }

  const document = parseDocument(lines.slice(1, closingIndex).join("\n"), {
    uniqueKeys: true,
  });
  if (document.errors.length > 0) {
    const detail = document.errors[0].message.replace(/\s+/g, " ").trim();
    return { fields: null, error: `contains invalid YAML frontmatter (${detail})` };
  }

  let fields;
  try {
    fields = document.toJS();
  } catch (error) {
    return { fields: null, error: `contains invalid YAML frontmatter (${error.message})` };
  }
  if (!isPlainObject(fields)) {
    return { fields: null, error: "has YAML frontmatter that must be a mapping" };
  }

  return { fields, error: null };
}

async function validateFrontmatterFile(
  validation,
  filePath,
  componentName,
  requiredKeys,
  pluginName
) {
  const content = await fs.readFile(filePath, "utf8");
  const { fields, error } = parseFrontmatter(content);
  const relativeFile = path.relative(validation.repoRoot, filePath);

  if (error) {
    addError(validation, `${pluginName}: ${componentName} file ${error}: ${relativeFile}`);
    return;
  }

  for (const key of requiredKeys) {
    if (typeof fields[key] !== "string" || fields[key].length === 0) {
      addError(
        validation,
        `${pluginName}: ${componentName} file missing "${key}" in frontmatter: ${relativeFile}`
      );
    }
  }
}

export async function validateComponentFrontmatter(validation, pluginDir, pluginName) {
  const componentRules = [
    { directory: "rules", extensions: [".md", ".mdc", ".markdown"], requiredKeys: ["description"] },
    {
      directory: "agents",
      extensions: [".md", ".mdc", ".markdown"],
      requiredKeys: ["name", "description"],
    },
    {
      directory: "commands",
      extensions: [".md", ".mdc", ".markdown", ".txt"],
      requiredKeys: ["name", "description"],
    },
  ];

  for (const rule of componentRules) {
    const componentDir = path.join(pluginDir, rule.directory);
    if (!(await pathExists(componentDir))) {
      continue;
    }

    const files = await walkFiles(componentDir);
    for (const file of files) {
      if (rule.extensions.includes(path.extname(file).toLowerCase())) {
        await validateFrontmatterFile(
          validation,
          file,
          rule.directory.slice(0, -1),
          rule.requiredKeys,
          pluginName
        );
      }
    }
  }
}

export async function validateAgentSkills(validation, pluginDir) {
  const skillsDir = path.join(pluginDir, "skills");
  if (!(await pathExists(skillsDir))) {
    return;
  }
  if (validation.validatedAgentSkillDirectories.has(skillsDir)) {
    return;
  }
  validation.validatedAgentSkillDirectories.add(skillsDir);

  let entries;
  try {
    entries = await fs.readdir(skillsDir, { withFileTypes: true });
  } catch (error) {
    addError(validation, `Agent Plugins: unable to read skills directory: ${error.message}`);
    return;
  }

  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }

    const skillPath = path.join(skillsDir, entry.name, "SKILL.md");
    if (!(await pathExists(skillPath))) {
      continue;
    }

    const skillStat = await fs.stat(skillPath);
    if (!skillStat.isFile()) {
      addError(
        validation,
        `Agent Plugins: skill path is not a regular file: ${path.relative(validation.repoRoot, skillPath)}`
      );
      continue;
    }

    const content = await fs.readFile(skillPath, "utf8");
    const relativeSkill = path.relative(validation.repoRoot, skillPath);
    const { fields, error } = parseFrontmatter(content);

    if (error) {
      addError(validation, `Agent Plugins: skill ${error} in ${relativeSkill}.`);
      continue;
    }

    const { name, description } = fields;
    if (typeof name !== "string" || name.length > 64 || !agentSkillNamePattern.test(name)) {
      addError(validation, `Agent Plugins: invalid Agent Skill name in ${relativeSkill}.`);
    } else if (name !== entry.name) {
      addError(
        validation,
        `Agent Plugins: skill name "${name}" must match its parent directory "${entry.name}" in ${relativeSkill}.`
      );
    }

    if (typeof description !== "string" || description.length === 0 || description.length > 1024) {
      addError(
        validation,
        `Agent Plugins: skill description must be 1-1024 characters in ${relativeSkill}.`
      );
    }
  }
}
