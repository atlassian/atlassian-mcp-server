import { validateHeaderName, validateHeaderValue } from "node:http";
import path from "node:path";
import {
  addError,
  isPlainObject,
  isSafeRelativePath,
  readJsonFile,
  validateAllowedKeys,
} from "./common.mjs";
import { validateAgentSkills } from "./agent-skills.mjs";

const agentPluginNamePattern = /^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/;
const agentPluginSchema = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json";
const agentMcpSchema = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json";

export function validateRemoteMcpServer(validation, server, context) {
  validateAllowedKeys(validation, server, ["type", "url", "headers"], context);

  if (server.type !== "streamable-http" && server.type !== "sse") {
    addError(validation, `${context}.type must be "streamable-http" or "sse".`);
  }
  if (typeof server.url !== "string" || server.url.length === 0) {
    addError(validation, `${context}.url must be a non-empty string.`);
  } else {
    try {
      const parsedUrl = new URL(server.url);
      const isLoopback =
        parsedUrl.hostname === "localhost" ||
        parsedUrl.hostname.startsWith("127.") ||
        parsedUrl.hostname === "[::1]";
      if (
        (parsedUrl.protocol !== "https:" && !(parsedUrl.protocol === "http:" && isLoopback)) ||
        parsedUrl.username ||
        parsedUrl.password ||
        parsedUrl.hash
      ) {
        addError(validation, `${context}.url does not satisfy Agent Plugins remote URL requirements.`);
      }
    } catch {
      addError(validation, `${context}.url must be an absolute HTTP or HTTPS URL.`);
    }
  }

  if (server.headers !== undefined) {
    if (!isPlainObject(server.headers)) {
      addError(validation, `${context}.headers must be an object of strings.`);
    } else {
      const normalizedHeaderNames = new Set();
      for (const [headerName, headerValue] of Object.entries(server.headers)) {
        let headerNameIsValid = true;
        const normalizedName = headerName.toLowerCase();
        if (normalizedHeaderNames.has(normalizedName)) {
          addError(
            validation,
            `${context}.headers contains duplicate header "${headerName}" with different casing.`
          );
        }
        normalizedHeaderNames.add(normalizedName);

        try {
          validateHeaderName(headerName);
        } catch {
          headerNameIsValid = false;
          addError(validation, `${context}.headers contains invalid HTTP header name "${headerName}".`);
        }

        if (typeof headerValue !== "string") {
          addError(validation, `${context}.headers.${headerName} must be a string.`);
        } else if (headerNameIsValid) {
          try {
            validateHeaderValue(headerName, headerValue);
          } catch {
            addError(validation, `${context}.headers.${headerName} contains an invalid HTTP header value.`);
          }
        }
      }
    }
  }
}

export function validateStdioMcpServer(validation, server, context) {
  validateAllowedKeys(validation, server, ["type", "command", "args", "env", "cwd"], context);

  if (typeof server.command !== "string" || server.command.length === 0) {
    addError(validation, `${context}.command must be a non-empty string.`);
  } else if (!server.command.startsWith("./") && /\s/.test(server.command)) {
    addError(validation, `${context}.command must be a single executable token; put arguments in .args.`);
  } else if (server.command.includes("/") && !server.command.startsWith("./")) {
    addError(validation, `${context}.command must be a bare executable name or a path beginning with "./".`);
  } else if (server.command.startsWith("./") && !isSafeRelativePath(server.command)) {
    addError(validation, `${context}.command must remain within the plugin root.`);
  }

  if (
    server.args !== undefined &&
    (!Array.isArray(server.args) || server.args.some((arg) => typeof arg !== "string"))
  ) {
    addError(validation, `${context}.args must be an array of strings.`);
  }

  if (server.env !== undefined) {
    if (!isPlainObject(server.env) || Object.values(server.env).some((value) => typeof value !== "string")) {
      addError(validation, `${context}.env must be an object of strings.`);
    } else if (Object.hasOwn(server.env, "PLUGIN_ROOT") || Object.hasOwn(server.env, "PLUGIN_DATA")) {
      addError(validation, `${context}.env must not override PLUGIN_ROOT or PLUGIN_DATA.`);
    }
  }

  if (server.cwd !== undefined) {
    const normalizedCwd =
      typeof server.cwd === "string" ? server.cwd.replace(/\\/g, "/") : null;
    const validPrefix =
      normalizedCwd !== null &&
      /^(?:\.\/|\$\{PLUGIN_ROOT\}(?:\/|$)|\$\{PLUGIN_DATA\}(?:\/|$))/.test(normalizedCwd);
    const escapesRoot =
      normalizedCwd !== null && normalizedCwd.split("/").some((segment) => segment === "..");
    if (!validPrefix || escapesRoot) {
      addError(validation, `${context}.cwd must remain within the plugin root or plugin data directory.`);
    }
  }
}

export async function validateAgentPluginPackage(validation, pluginDir) {
  const manifest = await readJsonFile(
    validation,
    path.join(pluginDir, "plugin.json"),
    "Agent Plugins manifest"
  );
  if (manifest !== undefined) {
    if (!isPlainObject(manifest)) {
      addError(validation, "Agent Plugins manifest must contain a JSON object.");
    } else {
      validateAllowedKeys(
        validation,
        manifest,
        [
          "$schema",
          "name",
          "version",
          "description",
          "author",
          "homepage",
          "repository",
          "license",
          "keywords",
          "extensions",
        ],
        "Agent Plugins manifest"
      );
      if (manifest.$schema !== agentPluginSchema) {
        addError(validation, `Agent Plugins manifest.$schema must be "${agentPluginSchema}".`);
      }
      if (
        typeof manifest.name !== "string" ||
        manifest.name.length > 64 ||
        !agentPluginNamePattern.test(manifest.name)
      ) {
        addError(validation, "Agent Plugins manifest.name does not meet the Agent Plugins v1 naming constraints.");
      }
      for (const field of ["version", "description", "homepage", "repository", "license"]) {
        if (manifest[field] !== undefined && typeof manifest[field] !== "string") {
          addError(validation, `Agent Plugins manifest.${field} must be a string.`);
        }
      }
      if (manifest.author !== undefined) {
        if (!isPlainObject(manifest.author)) {
          addError(validation, "Agent Plugins manifest.author must be an object.");
        } else {
          validateAllowedKeys(
            validation,
            manifest.author,
            ["name", "email", "url"],
            "Agent Plugins manifest.author"
          );
          for (const [field, value] of Object.entries(manifest.author)) {
            if (typeof value !== "string") {
              addError(validation, `Agent Plugins manifest.author.${field} must be a string.`);
            }
          }
        }
      }
      if (
        manifest.keywords !== undefined &&
        (!Array.isArray(manifest.keywords) ||
          manifest.keywords.some((keyword) => typeof keyword !== "string"))
      ) {
        addError(validation, "Agent Plugins manifest.keywords must be an array of strings.");
      }
      if (
        manifest.extensions !== undefined &&
        (!isPlainObject(manifest.extensions) ||
          Object.values(manifest.extensions).some((value) => !isPlainObject(value)))
      ) {
        addError(validation, "Agent Plugins manifest.extensions must be an object whose values are objects.");
      }
    }
  }

  const mcpConfig = await readJsonFile(
    validation,
    path.join(pluginDir, "mcp.json"),
    "Agent Plugins MCP configuration"
  );
  if (mcpConfig !== undefined) {
    if (!isPlainObject(mcpConfig)) {
      addError(validation, "Agent Plugins mcp.json must contain a JSON object.");
    } else {
      validateAllowedKeys(validation, mcpConfig, ["$schema", "mcpServers"], "Agent Plugins mcp.json");
      if (mcpConfig.$schema !== agentMcpSchema) {
        addError(validation, `Agent Plugins mcp.json.$schema must be "${agentMcpSchema}".`);
      }
      if (!isPlainObject(mcpConfig.mcpServers)) {
        addError(validation, "Agent Plugins mcp.json.mcpServers must be an object.");
      } else {
        for (const [serverName, server] of Object.entries(mcpConfig.mcpServers)) {
          const context = `Agent Plugins mcp.json.mcpServers.${serverName}`;
          if (!isPlainObject(server)) {
            addError(validation, `${context} must be an object.`);
          } else if (server.type === "stdio") {
            validateStdioMcpServer(validation, server, context);
          } else {
            validateRemoteMcpServer(validation, server, context);
          }
        }
      }
    }
  }

  await validateAgentSkills(validation, pluginDir);
  return { manifest, mcpConfig };
}
