import assert from "node:assert/strict";
import { promises as fs } from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  validateAgentPluginPackage,
  validateRemoteMcpServer,
  validateStdioMcpServer,
} from "./agent-plugin.mjs";
import { createValidationContext } from "./common.mjs";
import { createEmptyFixture } from "./test-helpers.mjs";

const serverContext = "Agent Plugins mcp.json.mcpServers.test";

function validateRemote(server) {
  const validation = createValidationContext(process.cwd());
  validateRemoteMcpServer(validation, server, serverContext);
  return validation;
}

function validateStdio(server) {
  const validation = createValidationContext(process.cwd());
  validateStdioMcpServer(validation, server, serverContext);
  return validation;
}

test("invalid HTTP header names are rejected", () => {
  const validation = validateRemote({
    type: "streamable-http",
    url: "https://example.com/mcp",
    headers: { "Bad Header": "value" },
  });

  assert.ok(validation.errors.some((error) => error.includes('invalid HTTP header name "Bad Header"')));
});

test("invalid HTTP header values are rejected", () => {
  const validation = validateRemote({
    type: "streamable-http",
    url: "https://example.com/mcp",
    headers: { "X-Test": "first line\nsecond line" },
  });

  assert.ok(validation.errors.some((error) => error.includes("invalid HTTP header value")));
});

test("header names remain case-insensitively unique", () => {
  const validation = validateRemote({
    type: "streamable-http",
    url: "https://example.com/mcp",
    headers: { "X-Test": "first", "x-test": "second" },
  });

  assert.ok(validation.errors.some((error) => error.includes('duplicate header "x-test"')));
});

test("shell-style stdio commands are rejected", () => {
  const validation = validateStdio({ type: "stdio", command: "node --inspect" });

  assert.ok(validation.errors.some((error) => error.includes("single executable token")));
});

test("stdio arguments pass when separated from the executable", () => {
  const validation = validateStdio({ type: "stdio", command: "node", args: ["--inspect"] });

  assert.deepEqual(validation.errors, []);
});

test("Windows-style cwd traversal is rejected", () => {
  const validation = validateStdio({
    type: "stdio",
    command: "node",
    cwd: "${PLUGIN_ROOT}/..\\outside",
  });

  assert.ok(validation.errors.some((error) => error.includes("cwd must remain within")));
});

test("contained Windows-style cwd paths pass validation", () => {
  const validation = validateStdio({
    type: "stdio",
    command: "node",
    cwd: "${PLUGIN_ROOT}\\server",
  });

  assert.deepEqual(validation.errors, []);
});

const invalidRootValues = [null, false, true, 0, 1, "", "value", []];
for (const [fileName, expectedError] of [
  ["plugin.json", "Agent Plugins manifest must contain a JSON object."],
  ["mcp.json", "Agent Plugins mcp.json must contain a JSON object."],
]) {
  test(`${fileName} rejects every non-object root value`, async (t) => {
    const fixtureRoot = await createEmptyFixture(t);
    const filePath = path.join(fixtureRoot, fileName);

    for (const value of invalidRootValues) {
      await fs.writeFile(filePath, JSON.stringify(value), "utf8");
      const validation = createValidationContext(fixtureRoot);

      await validateAgentPluginPackage(validation, fixtureRoot);

      assert.ok(
        validation.errors.includes(expectedError),
        `${fileName} unexpectedly accepted ${JSON.stringify(value)}`
      );
    }
  });
}
