# Atlassian Open Plugin

A host-agnostic [open-plugin](https://open-plugins.com/plugin-builders/specification) that connects any compatible AI assistant to [Atlassian](https://atlassian.com) Cloud products (Jira, Confluence, Compass) via the Atlassian Rovo MCP Server.

## Overview

This plugin is a self-contained, vendor-neutral package conforming to the [Open Plugins Specification v1.0.0](https://open-plugins.com/plugin-builders/specification). It can be installed by any host that implements the spec; vendor-specific hosts (e.g. Cursor, Claude) may also load it via their prefixed manifest locations.

The plugin bundles an MCP server configuration that points at `https://mcp.atlassian.com/v1/mcp`. Authentication is handled by the server via OAuth 2.1.

## Structure

```
plugins/atlassian/
├── .plugin/
│   └── plugin.json     # Vendor-neutral manifest
├── .mcp.json           # MCP server configuration
├── assets/
│   └── logo.svg
├── LICENSE
└── README.md
```

## Installation

Refer to your host's documentation for installing an open-plugin. Most hosts accept either a path to this directory or a reference to this repository with `plugins/atlassian` as the plugin root.

## Support

- Report issues at the [Atlassian Support Portal](https://support.atlassian.com/).
- Share feedback in the [Atlassian Community](https://community.atlassian.com/).
