#!/usr/bin/env node

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const errors = [];
const warnings = [];

const pluginNamePattern = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/;
const marketplaceNamePattern = /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
const agentPluginNamePattern = /^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/;
const agentSkillNamePattern = /^(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
const agentPluginSchema = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json";
const agentMcpSchema = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json";

function addError(message) {
  errors.push(message);
}

function addWarning(message) {
  warnings.push(message);
}

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validateAllowedKeys(value, allowedKeys, context) {
  for (const key of Object.keys(value)) {
    if (!allowedKeys.includes(key)) {
      addError(`${context} contains unsupported field "${key}".`);
    }
  }
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function ensureDirectory(targetPath, context) {
  try {
    const stat = await fs.stat(targetPath);
    if (!stat.isDirectory()) {
      addError(`${context} exists but is not a directory: ${targetPath}`);
      return false;
    }
    return true;
  } catch {
    addError(`${context} directory is missing: ${targetPath}`);
    return false;
  }
}

async function readJsonFile(filePath, context) {
  let raw;
  try {
    raw = await fs.readFile(filePath, "utf8");
  } catch {
    addError(`${context} is missing: ${filePath}`);
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    addError(`${context} contains invalid JSON (${filePath}): ${error.message}`);
    return null;
  }
}

function normalizeNewlines(content) {
  return content.replace(/\r\n/g, "\n");
}

function parseFrontmatter(content) {
  const normalized = normalizeNewlines(content);
  if (!normalized.startsWith("---\n")) {
    return null;
  }

  const closingIndex = normalized.indexOf("\n---\n", 4);
  if (closingIndex === -1) {
    return null;
  }

  const frontmatterBlock = normalized.slice(4, closingIndex);
  const fields = {};

  for (const line of frontmatterBlock.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const separator = line.indexOf(":");
    if (separator === -1) {
      continue;
    }
    const key = line.slice(0, separator).trim();
    const value = line.slice(separator + 1).trim();
    fields[key] = value;
  }

  return fields;
}

function parseFrontmatterString(content, targetKey) {
  const normalized = normalizeNewlines(content);
  if (!normalized.startsWith("---\n")) {
    return null;
  }

  const closingIndex = normalized.indexOf("\n---\n", 4);
  if (closingIndex === -1) {
    return null;
  }

  const lines = normalized.slice(4, closingIndex).split("\n");
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (/^\s/.test(line)) {
      continue;
    }
    const separator = line.indexOf(":");
    if (separator === -1 || line.slice(0, separator).trim() !== targetKey) {
      continue;
    }

    const rawValue = line.slice(separator + 1).trim();
    if (/^[>|][+-]?$/.test(rawValue)) {
      const blockLines = [];
      for (let childIndex = index + 1; childIndex < lines.length; childIndex += 1) {
        const childLine = lines[childIndex];
        if (childLine.length > 0 && !/^\s/.test(childLine)) {
          break;
        }
        blockLines.push(childLine.replace(/^\s+/, ""));
      }
      return rawValue.startsWith(">")
        ? blockLines.join(" ").replace(/\s+/g, " ").trim()
        : blockLines.join("\n").trim();
    }

    if (rawValue.startsWith('"') && rawValue.endsWith('"')) {
      try {
        return JSON.parse(rawValue);
      } catch {
        return null;
      }
    }
    if (rawValue.startsWith("'") && rawValue.endsWith("'")) {
      return rawValue.slice(1, -1).replace(/''/g, "'");
    }
    return rawValue;
  }

  return null;
}

async function walkFiles(dirPath) {
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

function isSafeRelativePath(value) {
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

function extractPathValues(value) {
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

async function validateReferencedPath(pluginDir, fieldName, pathValue, pluginName) {
  if (pathValue.startsWith("http://") || pathValue.startsWith("https://")) {
    return;
  }

  if (!isSafeRelativePath(pathValue)) {
    addError(
      `${pluginName}: field "${fieldName}" has invalid path "${pathValue}". Use a relative path without ".." or absolute prefixes.`
    );
    return;
  }

  const resolved = path.resolve(pluginDir, pathValue);
  const exists = await pathExists(resolved);
  if (!exists) {
    addError(`${pluginName}: field "${fieldName}" references missing path "${pathValue}".`);
  }
}

async function validateFrontmatterFile(filePath, componentName, requiredKeys, pluginName) {
  const content = await fs.readFile(filePath, "utf8");
  const parsed = parseFrontmatter(content);
  const relativeFile = path.relative(repoRoot, filePath);

  if (!parsed) {
    addError(`${pluginName}: ${componentName} file missing YAML frontmatter: ${relativeFile}`);
    return;
  }

  for (const key of requiredKeys) {
    if (!parsed[key] || parsed[key].length === 0) {
      addError(`${pluginName}: ${componentName} file missing "${key}" in frontmatter: ${relativeFile}`);
    }
  }
}

async function validateComponentFrontmatter(pluginDir, pluginName) {
  const rulesDir = path.join(pluginDir, "rules");
  if (await pathExists(rulesDir)) {
    const files = await walkFiles(rulesDir);
    for (const file of files) {
      const ext = path.extname(file).toLowerCase();
      if (ext === ".md" || ext === ".mdc" || ext === ".markdown") {
        await validateFrontmatterFile(file, "rule", ["description"], pluginName);
      }
    }
  }

  const skillsDir = path.join(pluginDir, "skills");
  if (await pathExists(skillsDir)) {
    const files = await walkFiles(skillsDir);
    for (const file of files) {
      if (path.basename(file) === "SKILL.md") {
        await validateFrontmatterFile(file, "skill", ["name", "description"], pluginName);
      }
    }
  }

  const agentsDir = path.join(pluginDir, "agents");
  if (await pathExists(agentsDir)) {
    const files = await walkFiles(agentsDir);
    for (const file of files) {
      const ext = path.extname(file).toLowerCase();
      if (ext === ".md" || ext === ".mdc" || ext === ".markdown") {
        await validateFrontmatterFile(file, "agent", ["name", "description"], pluginName);
      }
    }
  }

  const commandsDir = path.join(pluginDir, "commands");
  if (await pathExists(commandsDir)) {
    const files = await walkFiles(commandsDir);
    for (const file of files) {
      const ext = path.extname(file).toLowerCase();
      if (ext === ".md" || ext === ".mdc" || ext === ".markdown" || ext === ".txt") {
        await validateFrontmatterFile(file, "command", ["name", "description"], pluginName);
      }
    }
  }
}

async function validateAgentSkills(pluginDir) {
  const skillsDir = path.join(pluginDir, "skills");
  if (!(await pathExists(skillsDir))) {
    return;
  }

  let entries;
  try {
    entries = await fs.readdir(skillsDir, { withFileTypes: true });
  } catch (error) {
    addError(`Agent Plugins: unable to read skills directory: ${error.message}`);
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
      addError(`Agent Plugins: skill path is not a regular file: ${path.relative(repoRoot, skillPath)}`);
      continue;
    }

    const content = await fs.readFile(skillPath, "utf8");
    const name = parseFrontmatterString(content, "name");
    const description = parseFrontmatterString(content, "description");
    const relativeSkill = path.relative(repoRoot, skillPath);

    if (typeof name !== "string" || name.length > 64 || !agentSkillNamePattern.test(name)) {
      addError(`Agent Plugins: invalid Agent Skill name in ${relativeSkill}.`);
    } else if (name !== entry.name) {
      addError(
        `Agent Plugins: skill name "${name}" must match its parent directory "${entry.name}" in ${relativeSkill}.`
      );
    }

    if (typeof description !== "string" || description.length === 0 || description.length > 1024) {
      addError(`Agent Plugins: skill description must be 1-1024 characters in ${relativeSkill}.`);
    }
  }
}

function validateRemoteMcpServer(server, context) {
  validateAllowedKeys(server, ["type", "url", "headers"], context);

  if (server.type !== "streamable-http" && server.type !== "sse") {
    addError(`${context}.type must be "streamable-http" or "sse".`);
  }
  if (typeof server.url !== "string" || server.url.length === 0) {
    addError(`${context}.url must be a non-empty string.`);
  } else {
    try {
      const parsedUrl = new URL(server.url);
      const isLoopback =
        parsedUrl.hostname === "localhost" ||
        parsedUrl.hostname.startsWith("127.") ||
        parsedUrl.hostname === "[::1]";
      if ((parsedUrl.protocol !== "https:" && !(parsedUrl.protocol === "http:" && isLoopback)) || parsedUrl.username || parsedUrl.password || parsedUrl.hash) {
        addError(`${context}.url does not satisfy Agent Plugins remote URL requirements.`);
      }
    } catch {
      addError(`${context}.url must be an absolute HTTP or HTTPS URL.`);
    }
  }

  if (server.headers !== undefined) {
    if (!isPlainObject(server.headers)) {
      addError(`${context}.headers must be an object of strings.`);
    } else {
      const normalizedHeaderNames = new Set();
      for (const [headerName, headerValue] of Object.entries(server.headers)) {
        const normalizedName = headerName.toLowerCase();
        if (normalizedHeaderNames.has(normalizedName)) {
          addError(`${context}.headers contains duplicate header "${headerName}" with different casing.`);
        }
        normalizedHeaderNames.add(normalizedName);
        if (typeof headerValue !== "string") {
          addError(`${context}.headers.${headerName} must be a string.`);
        }
      }
    }
  }
}

function validateStdioMcpServer(server, context) {
  validateAllowedKeys(server, ["type", "command", "args", "env", "cwd"], context);

  if (typeof server.command !== "string" || server.command.length === 0) {
    addError(`${context}.command must be a non-empty string.`);
  } else if (server.command.includes("/") && !server.command.startsWith("./")) {
    addError(`${context}.command must be a bare executable name or a path beginning with "./".`);
  } else if (server.command.startsWith("./") && !isSafeRelativePath(server.command)) {
    addError(`${context}.command must remain within the plugin root.`);
  }

  if (server.args !== undefined && (!Array.isArray(server.args) || server.args.some((arg) => typeof arg !== "string"))) {
    addError(`${context}.args must be an array of strings.`);
  }

  if (server.env !== undefined) {
    if (!isPlainObject(server.env) || Object.values(server.env).some((value) => typeof value !== "string")) {
      addError(`${context}.env must be an object of strings.`);
    } else if (Object.hasOwn(server.env, "PLUGIN_ROOT") || Object.hasOwn(server.env, "PLUGIN_DATA")) {
      addError(`${context}.env must not override PLUGIN_ROOT or PLUGIN_DATA.`);
    }
  }

  if (server.cwd !== undefined) {
    const validPrefix =
      typeof server.cwd === "string" &&
      /^(?:\.\/|\$\{PLUGIN_ROOT\}(?:\/|$)|\$\{PLUGIN_DATA\}(?:\/|$))/.test(server.cwd);
    const escapesRoot =
      typeof server.cwd === "string" &&
      server.cwd.split("/").some((segment) => segment === "..");
    if (!validPrefix || escapesRoot) {
      addError(`${context}.cwd must remain within the plugin root or plugin data directory.`);
    }
  }
}

async function validateAgentPluginPackage(pluginDir) {
  const manifest = await readJsonFile(path.join(pluginDir, "plugin.json"), "Agent Plugins manifest");
  if (manifest) {
    if (!isPlainObject(manifest)) {
      addError("Agent Plugins manifest must contain a JSON object.");
    } else {
      validateAllowedKeys(
        manifest,
        ["$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"],
        "Agent Plugins manifest"
      );
      if (manifest.$schema !== agentPluginSchema) {
        addError(`Agent Plugins manifest.$schema must be "${agentPluginSchema}".`);
      }
      if (typeof manifest.name !== "string" || manifest.name.length > 64 || !agentPluginNamePattern.test(manifest.name)) {
        addError("Agent Plugins manifest.name does not meet the Agent Plugins v1 naming constraints.");
      }
      for (const field of ["version", "description", "homepage", "repository", "license"]) {
        if (manifest[field] !== undefined && typeof manifest[field] !== "string") {
          addError(`Agent Plugins manifest.${field} must be a string.`);
        }
      }
      if (manifest.author !== undefined) {
        if (!isPlainObject(manifest.author)) {
          addError("Agent Plugins manifest.author must be an object.");
        } else {
          validateAllowedKeys(manifest.author, ["name", "email", "url"], "Agent Plugins manifest.author");
          for (const [field, value] of Object.entries(manifest.author)) {
            if (typeof value !== "string") {
              addError(`Agent Plugins manifest.author.${field} must be a string.`);
            }
          }
        }
      }
      if (manifest.keywords !== undefined && (!Array.isArray(manifest.keywords) || manifest.keywords.some((keyword) => typeof keyword !== "string"))) {
        addError("Agent Plugins manifest.keywords must be an array of strings.");
      }
      if (manifest.extensions !== undefined && (!isPlainObject(manifest.extensions) || Object.values(manifest.extensions).some((value) => !isPlainObject(value)))) {
        addError("Agent Plugins manifest.extensions must be an object whose values are objects.");
      }
    }
  }

  const mcpConfig = await readJsonFile(path.join(pluginDir, "mcp.json"), "Agent Plugins MCP configuration");
  if (mcpConfig) {
    if (!isPlainObject(mcpConfig)) {
      addError("Agent Plugins mcp.json must contain a JSON object.");
    } else {
      validateAllowedKeys(mcpConfig, ["$schema", "mcpServers"], "Agent Plugins mcp.json");
      if (mcpConfig.$schema !== agentMcpSchema) {
        addError(`Agent Plugins mcp.json.$schema must be "${agentMcpSchema}".`);
      }
      if (!isPlainObject(mcpConfig.mcpServers)) {
        addError("Agent Plugins mcp.json.mcpServers must be an object.");
      } else {
        for (const [serverName, server] of Object.entries(mcpConfig.mcpServers)) {
          const context = `Agent Plugins mcp.json.mcpServers.${serverName}`;
          if (!isPlainObject(server)) {
            addError(`${context} must be an object.`);
          } else if (server.type === "stdio") {
            validateStdioMcpServer(server, context);
          } else {
            validateRemoteMcpServer(server, context);
          }
        }
      }
    }
  }

  await validateAgentSkills(pluginDir);
  return { manifest, mcpConfig };
}

async function validateOtherClientManifests(pluginDir) {
  const claudeManifest = await readJsonFile(
    path.join(pluginDir, ".claude-plugin", "plugin.json"),
    "Claude plugin manifest"
  );
  if (claudeManifest) {
    if (typeof claudeManifest.name !== "string" || !pluginNamePattern.test(claudeManifest.name)) {
      addError("Claude plugin manifest.name is invalid.");
    }
    for (const field of ["mcpServers", "skills"]) {
      if (typeof claudeManifest[field] !== "string") {
        addError(`Claude plugin manifest.${field} must be a relative path string.`);
      } else {
        await validateReferencedPath(pluginDir, field, claudeManifest[field], "Claude plugin");
      }
    }
  }

  const claudeMarketplace = await readJsonFile(
    path.join(pluginDir, ".claude-plugin", "marketplace.json"),
    "Claude marketplace manifest"
  );
  if (claudeMarketplace && (!Array.isArray(claudeMarketplace.plugins) || claudeMarketplace.plugins.length === 0)) {
    addError("Claude marketplace manifest.plugins must be a non-empty array.");
  }

  const geminiManifest = await readJsonFile(path.join(pluginDir, "gemini-extension.json"), "Gemini extension manifest");
  if (geminiManifest) {
    if (typeof geminiManifest.name !== "string" || geminiManifest.name.length === 0) {
      addError("Gemini extension manifest.name must be a non-empty string.");
    }
    if (!isPlainObject(geminiManifest.mcpServers)) {
      addError("Gemini extension manifest.mcpServers must be an object.");
    }
  }

  const nativeMcpConfig = await readJsonFile(path.join(pluginDir, ".mcp.json"), "Native MCP client configuration");
  if (nativeMcpConfig && !isPlainObject(nativeMcpConfig.mcpServers)) {
    addError("Native .mcp.json.mcpServers must be an object.");
  }

  return { claudeManifest, geminiManifest, nativeMcpConfig };
}

function resolveMarketplaceSource(source, pluginRoot) {
  if (typeof source !== "string" || source.length === 0) {
    return null;
  }
  if (!pluginRoot) {
    return source;
  }
  const normalizedRoot = pluginRoot.replace(/\\/g, "/").replace(/\/+$/, "");
  const normalizedSource = source.replace(/\\/g, "/");
  if (normalizedSource === normalizedRoot || normalizedSource.startsWith(`${normalizedRoot}/`)) {
    return normalizedSource;
  }
  return `${normalizedRoot}/${normalizedSource}`;
}

async function validateOnePlugin(pluginDir, pluginName) {
  const manifestPath = path.join(pluginDir, ".cursor-plugin", "plugin.json");
  const pluginManifest = await readJsonFile(manifestPath, `${pluginName} plugin manifest`);
  if (!pluginManifest) {
    return;
  }

  if (typeof pluginManifest.name !== "string" || !pluginNamePattern.test(pluginManifest.name)) {
    addError(
      `${pluginName}: "name" in plugin.json must be lowercase and use only alphanumerics, hyphens, and periods.`
    );
  }

  const manifestFields = ["logo", "rules", "skills", "agents", "commands", "hooks", "mcp", "mcpServers"];
  for (const field of manifestFields) {
    const values = extractPathValues(pluginManifest[field]);
    for (const value of values) {
      await validateReferencedPath(pluginDir, field, value, pluginName);
    }
  }

  await validateComponentFrontmatter(pluginDir, pluginName);

  const hooksPath = path.join(pluginDir, "hooks", "hooks.json");
  if (!(await pathExists(hooksPath))) {
    addWarning(`${pluginName}: no hooks/hooks.json file found (only needed when using hooks).`);
  }

  const mcpPath = path.join(pluginDir, ".mcp.json");
  const mcpLegacyPath = path.join(pluginDir, "mcp.json");
  if (!(await pathExists(mcpPath)) && !(await pathExists(mcpLegacyPath))) {
    addWarning(`${pluginName}: no .mcp.json or mcp.json file found (only needed when using MCP servers).`);
  }
}

async function main() {
  const portablePackage = await validateAgentPluginPackage(repoRoot);
  const clientManifests = await validateOtherClientManifests(repoRoot);

  const portableName = portablePackage.manifest?.name;
  const claudeName = clientManifests.claudeManifest?.name;
  if (typeof portableName === "string" && typeof claudeName === "string" && portableName !== claudeName) {
    addError(`Agent Plugins and Claude plugin names must match ("${portableName}" !== "${claudeName}").`);
  }

  const portableEndpoint = portablePackage.mcpConfig?.mcpServers?.atlassian?.url;
  const nativeEndpoint = clientManifests.nativeMcpConfig?.mcpServers?.atlassian?.url;
  if (
    typeof portableEndpoint === "string" &&
    typeof nativeEndpoint === "string" &&
    portableEndpoint !== nativeEndpoint
  ) {
    addError(`Agent Plugins mcp.json and native .mcp.json endpoints must match.`);
  }

  const marketplacePath = path.join(repoRoot, ".cursor-plugin", "marketplace.json");
  const rootManifestPath = path.join(repoRoot, ".cursor-plugin", "plugin.json");
  const hasMarketplace = await pathExists(marketplacePath);
  const hasRootPlugin = await pathExists(rootManifestPath);

  if (!hasMarketplace && hasRootPlugin) {
    // Single-plugin mode: validate .cursor-plugin/plugin.json at repo root
    const pluginManifest = await readJsonFile(rootManifestPath, "Plugin manifest");
    if (!pluginManifest) {
      summarizeAndExit();
      return;
    }
    const pluginName = pluginManifest.name || "plugin";
    if (typeof pluginName !== "string" || !pluginNamePattern.test(pluginName)) {
      addError(
        '"name" in plugin.json must be lowercase and use only alphanumerics, hyphens, and periods.'
      );
    }
    if (typeof portableName === "string" && typeof pluginName === "string" && portableName !== pluginName) {
      addError(`Agent Plugins and Cursor plugin names must match ("${portableName}" !== "${pluginName}").`);
    }
    await validateOnePlugin(repoRoot, pluginName);
    summarizeAndExit();
    return;
  }

  const marketplace = await readJsonFile(marketplacePath, "Marketplace manifest");
  if (!marketplace) {
    if (!hasRootPlugin) {
      addError("No .cursor-plugin/marketplace.json and no .cursor-plugin/plugin.json found.");
    }
    summarizeAndExit();
    return;
  }

  if (typeof marketplace.name !== "string" || !marketplaceNamePattern.test(marketplace.name)) {
    addError(
      'Marketplace "name" must be lowercase kebab-case and start/end with an alphanumeric character.'
    );
  }

  if (!marketplace.owner || typeof marketplace.owner.name !== "string" || marketplace.owner.name.length === 0) {
    addError('Marketplace "owner.name" is required.');
  }

  if (!Array.isArray(marketplace.plugins) || marketplace.plugins.length === 0) {
    addError('Marketplace "plugins" must be a non-empty array.');
    summarizeAndExit();
    return;
  }

  const pluginRoot = marketplace.metadata?.pluginRoot;
  if (pluginRoot !== undefined) {
    if (typeof pluginRoot !== "string" || !isSafeRelativePath(pluginRoot)) {
      addError('Marketplace "metadata.pluginRoot" must be a safe relative path.');
    } else {
      const pluginRootAbs = path.join(repoRoot, pluginRoot);
      await ensureDirectory(pluginRootAbs, 'Marketplace "metadata.pluginRoot"');
    }
  }

  const seenNames = new Set();
  for (const [index, entry] of marketplace.plugins.entries()) {
    const label = `plugins[${index}]`;

    if (!entry || typeof entry !== "object") {
      addError(`${label} must be an object.`);
      continue;
    }

    if (typeof entry.name !== "string" || !pluginNamePattern.test(entry.name)) {
      addError(`${label}.name must be lowercase and use only alphanumerics, hyphens, and periods.`);
      continue;
    }

    if (seenNames.has(entry.name)) {
      addError(`Duplicate plugin name in marketplace manifest: "${entry.name}"`);
    }
    seenNames.add(entry.name);

    const sourcePath = resolveMarketplaceSource(entry.source, pluginRoot ?? "");
    if (!sourcePath) {
      addError(`${label}.source must be a string path.`);
      continue;
    }
    if (!isSafeRelativePath(sourcePath)) {
      addError(`${label}.source is not a safe relative path: "${sourcePath}"`);
      continue;
    }

    const pluginDir = path.join(repoRoot, sourcePath);
    const pluginDirExists = await ensureDirectory(pluginDir, `${label}.source`);
    if (!pluginDirExists) {
      continue;
    }

    const manifestPath = path.join(pluginDir, ".cursor-plugin", "plugin.json");
    const pluginManifest = await readJsonFile(manifestPath, `${entry.name} plugin manifest`);
    if (!pluginManifest) {
      continue;
    }

    if (typeof pluginManifest.name !== "string" || !pluginNamePattern.test(pluginManifest.name)) {
      addError(
        `${entry.name}: "name" in plugin.json must be lowercase and use only alphanumerics, hyphens, and periods.`
      );
    }

    if (pluginManifest.name && pluginManifest.name !== entry.name) {
      addError(
        `${entry.name}: marketplace entry name does not match plugin.json name ("${pluginManifest.name}").`
      );
    }

    await validateOnePlugin(pluginDir, entry.name);
  }

  summarizeAndExit();
}

function summarizeAndExit() {
  if (warnings.length > 0) {
    console.log("Warnings:");
    for (const warning of warnings) {
      console.log(`- ${warning}`);
    }
    console.log("");
  }

  if (errors.length > 0) {
    console.error("Validation failed:");
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    process.exit(1);
  }

  console.log("Validation passed.");
}

await main();
