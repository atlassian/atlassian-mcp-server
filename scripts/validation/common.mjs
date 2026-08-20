import { promises as fs } from "node:fs";
import path from "node:path";

export function createValidationContext(repoRoot) {
  return {
    repoRoot,
    errors: [],
    warnings: [],
    validatedAgentSkillDirectories: new Set(),
  };
}

export function addError(validation, message) {
  validation.errors.push(message);
}

export function addWarning(validation, message) {
  validation.warnings.push(message);
}

export function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function validateAllowedKeys(validation, value, allowedKeys, context) {
  for (const key of Object.keys(value)) {
    if (!allowedKeys.includes(key)) {
      addError(validation, `${context} contains unsupported field "${key}".`);
    }
  }
}

export async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

export async function ensureDirectory(validation, targetPath, context) {
  try {
    const stat = await fs.stat(targetPath);
    if (!stat.isDirectory()) {
      addError(validation, `${context} exists but is not a directory: ${targetPath}`);
      return false;
    }
    return true;
  } catch {
    addError(validation, `${context} directory is missing: ${targetPath}`);
    return false;
  }
}

export async function readJsonFile(validation, filePath, context) {
  let raw;
  try {
    raw = await fs.readFile(filePath, "utf8");
  } catch {
    addError(validation, `${context} is missing: ${filePath}`);
    return undefined;
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    addError(validation, `${context} contains invalid JSON (${filePath}): ${error.message}`);
    return undefined;
  }
}

export async function walkFiles(dirPath) {
  const files = [];
  const stack = [dirPath];

  while (stack.length > 0) {
    const current = stack.pop();
    const entries = await fs.readdir(current, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(entryPath);
      } else if (entry.isFile()) {
        files.push(entryPath);
      }
    }
  }

  return files;
}

export function isSafeRelativePath(value) {
  if (typeof value !== "string" || value.length === 0) {
    return false;
  }
  if (value.startsWith("http://") || value.startsWith("https://")) {
    return true;
  }
  if (path.isAbsolute(value)) {
    return false;
  }
  const normalized = path.posix.normalize(value.replace(/\\/g, "/"));
  return !normalized.startsWith("../") && normalized !== "..";
}

export function extractPathValues(value) {
  if (typeof value === "string") {
    return [value];
  }

  if (Array.isArray(value)) {
    return value.flatMap((entry) => extractPathValues(entry));
  }

  if (value && typeof value === "object") {
    const candidates = [];
    if (typeof value.path === "string") {
      candidates.push(value.path);
    }
    if (typeof value.file === "string") {
      candidates.push(value.file);
    }
    return candidates;
  }

  return [];
}

export async function validateReferencedPath(
  validation,
  pluginDir,
  fieldName,
  pathValue,
  pluginName
) {
  if (pathValue.startsWith("http://") || pathValue.startsWith("https://")) {
    return;
  }

  if (!isSafeRelativePath(pathValue)) {
    addError(
      validation,
      `${pluginName}: field "${fieldName}" has invalid path "${pathValue}". Use a relative path without ".." or absolute prefixes.`
    );
    return;
  }

  const resolved = path.resolve(pluginDir, pathValue);
  if (!(await pathExists(resolved))) {
    addError(
      validation,
      `${pluginName}: field "${fieldName}" references missing path "${pathValue}".`
    );
  }
}
