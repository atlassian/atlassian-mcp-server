import assert from "node:assert/strict";
import test from "node:test";
import { validateRemoteMcpServer, validateStdioMcpServer } from "./agent-plugin.mjs";
import { createValidationContext } from "./common.mjs";

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
