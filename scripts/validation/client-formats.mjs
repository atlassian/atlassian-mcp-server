import path from "node:path";
import { validateAgentSkills, validateComponentFrontmatter } from "./agent-skills.mjs";
import {
  addError,
  addWarning,
  ensureDirectory,
  extractPathValues,
  isPlainObject,
  isSafeRelativePath,
  pathExists,
  readJsonFile,
  validateReferencedPath,
} from "./common.mjs";

const pluginNamePattern = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/;
const marketplaceNamePattern = /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;

export async function validateOtherClientManifests(validation, pluginDir) {
  const claudeManifest = await readJsonFile(
    validation,
    path.join(pluginDir, ".claude-plugin", "plugin.json"),
    "Claude plugin manifest"
  );
  if (claudeManifest) {
    if (typeof claudeManifest.name !== "string" || !pluginNamePattern.test(claudeManifest.name)) {
      addError(validation, "Claude plugin manifest.name is invalid.");
    }
    for (const field of ["mcpServers", "skills"]) {
      if (typeof claudeManifest[field] !== "string") {
        addError(validation, `Claude plugin manifest.${field} must be a relative path string.`);
      } else {
        await validateReferencedPath(
          validation,
          pluginDir,
          field,
          claudeManifest[field],
          "Claude plugin"
        );
      }
    }
  }

  const claudeMarketplace = await readJsonFile(
    validation,
    path.join(pluginDir, ".claude-plugin", "marketplace.json"),
    "Claude marketplace manifest"
  );
  if (
    claudeMarketplace &&
    (!Array.isArray(claudeMarketplace.plugins) || claudeMarketplace.plugins.length === 0)
  ) {
    addError(validation, "Claude marketplace manifest.plugins must be a non-empty array.");
  }

  const geminiManifest = await readJsonFile(
    validation,
    path.join(pluginDir, "gemini-extension.json"),
    "Gemini extension manifest"
  );
  if (geminiManifest) {
    if (typeof geminiManifest.name !== "string" || geminiManifest.name.length === 0) {
      addError(validation, "Gemini extension manifest.name must be a non-empty string.");
    }
    if (!isPlainObject(geminiManifest.mcpServers)) {
      addError(validation, "Gemini extension manifest.mcpServers must be an object.");
    }
  }

  const nativeMcpConfig = await readJsonFile(
    validation,
    path.join(pluginDir, ".mcp.json"),
    "Native MCP client configuration"
  );
  if (nativeMcpConfig && !isPlainObject(nativeMcpConfig.mcpServers)) {
    addError(validation, "Native .mcp.json.mcpServers must be an object.");
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

async function validateOnePlugin(validation, pluginDir, pluginName) {
  const manifestPath = path.join(pluginDir, ".cursor-plugin", "plugin.json");
  const pluginManifest = await readJsonFile(validation, manifestPath, `${pluginName} plugin manifest`);
  if (!pluginManifest) {
    return;
  }

  if (typeof pluginManifest.name !== "string" || !pluginNamePattern.test(pluginManifest.name)) {
    addError(
      validation,
      `${pluginName}: "name" in plugin.json must be lowercase and use only alphanumerics, hyphens, and periods.`
    );
  }

  const manifestFields = ["logo", "rules", "skills", "agents", "commands", "hooks", "mcp", "mcpServers"];
  for (const field of manifestFields) {
    const values = extractPathValues(pluginManifest[field]);
    for (const value of values) {
      await validateReferencedPath(validation, pluginDir, field, value, pluginName);
    }
  }

  await validateComponentFrontmatter(validation, pluginDir, pluginName);
  await validateAgentSkills(validation, pluginDir);

  const hooksPath = path.join(pluginDir, "hooks", "hooks.json");
  if (!(await pathExists(hooksPath))) {
    addWarning(validation, `${pluginName}: no hooks/hooks.json file found (only needed when using hooks).`);
  }

  const mcpPath = path.join(pluginDir, ".mcp.json");
  const mcpLegacyPath = path.join(pluginDir, "mcp.json");
  if (!(await pathExists(mcpPath)) && !(await pathExists(mcpLegacyPath))) {
    addWarning(
      validation,
      `${pluginName}: no .mcp.json or mcp.json file found (only needed when using MCP servers).`
    );
  }
}

export async function validateCursorFormats(validation, repoRoot, portableName) {
  const marketplacePath = path.join(repoRoot, ".cursor-plugin", "marketplace.json");
  const rootManifestPath = path.join(repoRoot, ".cursor-plugin", "plugin.json");
  const hasMarketplace = await pathExists(marketplacePath);
  const hasRootPlugin = await pathExists(rootManifestPath);

  if (!hasMarketplace && hasRootPlugin) {
    const pluginManifest = await readJsonFile(validation, rootManifestPath, "Plugin manifest");
    if (!pluginManifest) {
      return;
    }
    const pluginName = pluginManifest.name || "plugin";
    if (typeof pluginName !== "string" || !pluginNamePattern.test(pluginName)) {
      addError(
        validation,
        '"name" in plugin.json must be lowercase and use only alphanumerics, hyphens, and periods.'
      );
    }
    if (typeof portableName === "string" && typeof pluginName === "string" && portableName !== pluginName) {
      addError(
        validation,
        `Agent Plugins and Cursor plugin names must match ("${portableName}" !== "${pluginName}").`
      );
    }
    await validateOnePlugin(validation, repoRoot, pluginName);
    return;
  }

  const marketplace = await readJsonFile(validation, marketplacePath, "Marketplace manifest");
  if (!marketplace) {
    if (!hasRootPlugin) {
      addError(validation, "No .cursor-plugin/marketplace.json and no .cursor-plugin/plugin.json found.");
    }
    return;
  }

  if (typeof marketplace.name !== "string" || !marketplaceNamePattern.test(marketplace.name)) {
    addError(
      validation,
      'Marketplace "name" must be lowercase kebab-case and start/end with an alphanumeric character.'
    );
  }

  if (!marketplace.owner || typeof marketplace.owner.name !== "string" || marketplace.owner.name.length === 0) {
    addError(validation, 'Marketplace "owner.name" is required.');
  }

  if (!Array.isArray(marketplace.plugins) || marketplace.plugins.length === 0) {
    addError(validation, 'Marketplace "plugins" must be a non-empty array.');
    return;
  }

  const pluginRoot = marketplace.metadata?.pluginRoot;
  if (pluginRoot !== undefined) {
    if (typeof pluginRoot !== "string" || !isSafeRelativePath(pluginRoot)) {
      addError(validation, 'Marketplace "metadata.pluginRoot" must be a safe relative path.');
    } else {
      await ensureDirectory(
        validation,
        path.join(repoRoot, pluginRoot),
        'Marketplace "metadata.pluginRoot"'
      );
    }
  }

  const seenNames = new Set();
  for (const [index, entry] of marketplace.plugins.entries()) {
    const label = `plugins[${index}]`;

    if (!entry || typeof entry !== "object") {
      addError(validation, `${label} must be an object.`);
      continue;
    }
    if (typeof entry.name !== "string" || !pluginNamePattern.test(entry.name)) {
      addError(validation, `${label}.name must be lowercase and use only alphanumerics, hyphens, and periods.`);
      continue;
    }
    if (seenNames.has(entry.name)) {
      addError(validation, `Duplicate plugin name in marketplace manifest: "${entry.name}"`);
    }
    seenNames.add(entry.name);

    const sourcePath = resolveMarketplaceSource(entry.source, pluginRoot ?? "");
    if (!sourcePath) {
      addError(validation, `${label}.source must be a string path.`);
      continue;
    }
    if (!isSafeRelativePath(sourcePath)) {
      addError(validation, `${label}.source is not a safe relative path: "${sourcePath}"`);
      continue;
    }

    const pluginDir = path.join(repoRoot, sourcePath);
    if (!(await ensureDirectory(validation, pluginDir, `${label}.source`))) {
      continue;
    }

    const manifestPath = path.join(pluginDir, ".cursor-plugin", "plugin.json");
    const pluginManifest = await readJsonFile(validation, manifestPath, `${entry.name} plugin manifest`);
    if (!pluginManifest) {
      continue;
    }
    if (typeof pluginManifest.name !== "string" || !pluginNamePattern.test(pluginManifest.name)) {
      addError(
        validation,
        `${entry.name}: "name" in plugin.json must be lowercase and use only alphanumerics, hyphens, and periods.`
      );
    }
    if (pluginManifest.name && pluginManifest.name !== entry.name) {
      addError(
        validation,
        `${entry.name}: marketplace entry name does not match plugin.json name ("${pluginManifest.name}").`
      );
    }

    await validateOnePlugin(validation, pluginDir, entry.name);
  }
}
