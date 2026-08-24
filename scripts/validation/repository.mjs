import { validateAgentPluginPackage } from "./agent-plugin.mjs";
import { validateCursorFormats, validateOtherClientManifests } from "./client-formats.mjs";
import { addError, createValidationContext } from "./common.mjs";

export async function validateRepository(repoRoot) {
  const validation = createValidationContext(repoRoot);
  const portablePackage = await validateAgentPluginPackage(validation, repoRoot);
  const clientManifests = await validateOtherClientManifests(validation, repoRoot);

  const portableName = portablePackage.manifest?.name;
  const claudeName = clientManifests.claudeManifest?.name;
  if (typeof portableName === "string" && typeof claudeName === "string" && portableName !== claudeName) {
    addError(
      validation,
      `Agent Plugins and Claude plugin names must match ("${portableName}" !== "${claudeName}").`
    );
  }

  const portableEndpoint = portablePackage.mcpConfig?.mcpServers?.atlassian?.url;
  const nativeEndpoint = clientManifests.nativeMcpConfig?.mcpServers?.atlassian?.url;
  if (
    typeof portableEndpoint === "string" &&
    typeof nativeEndpoint === "string" &&
    portableEndpoint !== nativeEndpoint
  ) {
    addError(validation, "Agent Plugins mcp.json and native .mcp.json endpoints must match.");
  }

  await validateCursorFormats(validation, repoRoot, portableName);
  return {
    errors: [...validation.errors],
    warnings: [...validation.warnings],
  };
}
