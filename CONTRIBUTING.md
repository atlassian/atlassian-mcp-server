# Contributing to the Atlassian Rovo MCP Server

Thanks for your interest in contributing. Pull requests, issues, and comments are all welcome.

It helps to know what lives in this repo: the documentation, the client manifests (`.mcp.json` and the Claude, Cursor, and Gemini plugin manifests), the MCP registry entry (`server.json`), and the [skills](skills/). The server itself runs as a hosted service at `mcp.atlassian.com` and isn't part of this repo, so changes here are about those public-facing pieces.

## Opening an issue

Use one of the [issue forms](https://github.com/atlassian/atlassian-mcp-server/issues/new/choose). If your report is really about the hosted server, authentication, or an Atlassian product rather than this repo, the forms will point you to faster support channels.

## Sending a pull request

A few things that make review easier:

- Keep each pull request focused on one change. Split unrelated work into separate PRs.
- Match the existing style and structure of the file you're editing.
- If you touch a manifest (`.mcp.json`, `server.json`, or a plugin file), check that it's still valid and renders the way you expect.
- For a larger change, open an issue first so we can talk it through before you put in the work.

## Contributor License Agreement

Atlassian asks contributors to sign a Contributor License Agreement (CLA). It's a record that you have the right to contribute your code, documentation, or other work, and that you're willing to have it used in the project and any derivative works.

Please sign the CLA before we accept your contribution:

- [CLA for corporate contributors](https://opensource.atlassian.com/corporate), if you're contributing on behalf of an organization
- [CLA for individuals](https://opensource.atlassian.com/individual), if you're contributing on your own
