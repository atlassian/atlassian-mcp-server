<p align="center">
  <img src="images/atlassian_logo_brand_RGB.svg" alt="Atlassian" width="320">
</p>

<h1 align="center">Atlassian Rovo MCP Server</h1>

<p align="center">
  <b>The official Model Context Protocol (MCP) server for Atlassian: a cloud-hosted bridge that gives your AI tools secure, real-time access to Jira, Confluence, Jira Service Management, Bitbucket, Compass, Loom, and the wider Atlassian platform — powered by your Teamwork Graph.</b>
</p>

<!-- Line 1 · Project -->
<p align="center">
  <a href="https://github.com/atlassian/atlassian-mcp-server"><img src="https://img.shields.io/badge/Official-Atlassian-0052CC?logo=atlassian&logoColor=white" alt="Official Atlassian Server"></a>
  <a href="https://github.com/atlassian/atlassian-mcp-server/stargazers"><img src="https://img.shields.io/github/stars/atlassian/atlassian-mcp-server?style=flat&logo=github&label=Stars&color=0052CC" alt="GitHub stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/atlassian/atlassian-mcp-server?label=License&color=0052CC" alt="License: Apache 2.0"></a>
  <a href="https://www.atlassian.com/blog/announcements/remote-mcp-server"><img src="https://img.shields.io/badge/Status-Generally_Available-2EBC4F" alt="Status: Generally Available"></a>
</p>

<!-- Line 2 · Protocol & access -->
<p align="center">
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/Model_Context_Protocol-compatible-000000?logo=modelcontextprotocol&logoColor=white" alt="Model Context Protocol compatible"></a>
  <a href="server.json"><img src="https://img.shields.io/badge/MCP_Registry-com.atlassian-000000?logo=modelcontextprotocol&logoColor=white" alt="MCP Registry: com.atlassian"></a>
  <a href="https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/"><img src="https://img.shields.io/badge/Auth-OAuth_2.1%20%7C%20API%20token-2EBC4F" alt="Auth: OAuth 2.1 or API token"></a>
  <a href="https://www.atlassian.com/cloud"><img src="https://img.shields.io/badge/Hosting-Atlassian_Cloud-0052CC?logo=atlassian&logoColor=white" alt="Hosting: Atlassian Cloud"></a>
</p>

<!-- Line 3 · Supported products. Two-tone shields: dark logo segment on the left (labelColor), brand-colored product name on the right. Jira Service Management, Compass & Rovo have no simple-icons slug, so they use the official @atlaskit/logo (v20) tile glyphs embedded as SVG data URIs. -->
<p align="center">
  <a href="https://www.atlassian.com/software/jira"><img src="https://img.shields.io/badge/Jira-0052CC?logo=jira&logoColor=white&labelColor=172B4D" alt="Jira"></a>
  <a href="https://www.atlassian.com/software/confluence"><img src="https://img.shields.io/badge/Confluence-0052CC?logo=confluence&logoColor=white&labelColor=172B4D" alt="Confluence"></a>
  <a href="https://www.atlassian.com/software/jira/service-management"><img src="https://img.shields.io/badge/Jira_Service_Management-0052CC?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZmZmZiI+PHBhdGggZD0iTTEyIDBhMTIgMTIgMCAxIDAgMCAyNEExMiAxMiAwIDAgMCAxMiAwem0wIDMuNmE1LjA0IDUuMDQgMCAwIDEgNS4wNCA1LjA0IDUuMDQgNS4wNCAwIDAgMS01LjA0IDUuMDQgNS4wNCA1LjA0IDAgMCAxLTUuMDQtNS4wNEE1LjA0IDUuMDQgMCAwIDEgMTIgMy42em0wIDE2LjhhOC4wNCA4LjA0IDAgMCAxLTUuOTQtMi42MmMuMDMtMS45OCA0LjAyLTMuMDYgNS45NC0zLjA2czUuOTEgMS4wOCA1Ljk0IDMuMDZBOC4wNCA4LjA0IDAgMCAxIDEyIDIwLjR6Ii8+PC9zdmc+&logoColor=white&labelColor=172B4D" alt="Jira Service Management"></a>
  <a href="https://www.atlassian.com/software/bitbucket"><img src="https://img.shields.io/badge/Bitbucket-0052CC?logo=bitbucket&logoColor=white&labelColor=172B4D" alt="Bitbucket"></a>
  <a href="https://www.loom.com/"><img src="https://img.shields.io/badge/Loom-625DF5?logo=loom&logoColor=white&labelColor=172B4D" alt="Loom"></a>
  <a href="https://www.atlassian.com/software/compass"><img src="https://img.shields.io/badge/Compass-94C748?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzk0Yzc0OCIgZD0iTTAgNmE2IDYgMCAwIDEgNi02aDEyYTYgNiAwIDAgMSA2IDZ2MTJhNiA2IDAgMCAxLTYgNkg2YTYgNiAwIDAgMS02LTZ6Ii8+PHBhdGggZmlsbD0iIzEwMTIxNCIgZD0iTTEyLjc1IDcuODc3di0zLjM3bDYuMTYtLjAwN2guMDA3YS41OS41OSAwIDAgMSAuNTgzLjU5OHY2LjE0N2gtMy4zNjZWNy44Nzd6Ii8+PHBhdGggZmlsbD0iIzEwMTIxNCIgZD0iTTEyLjc1IDE0LjYxNXYtMy4zN2gzLjM2OHY2LjE2NWEuNTkuNTkgMCAwIDEtLjU5MS41OUg2LjU4M0EuNTkuNTkgMCAwIDEgNiAxNy40MDJWOC40NjdhLjU5LjU5IDAgMCAxIC41OTEtLjU5aDYuMTZ2My4zNjhIOS4zNzN2My4zN3oiLz48L3N2Zz4=&labelColor=101214" alt="Compass"></a>
  <a href="https://www.atlassian.com/software/rovo"><img src="https://img.shields.io/badge/Rovo-1868DB?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzE4NjhkYiIgZD0iTTAgNmE2IDYgMCAwIDEgNi02aDEyYTYgNiAwIDAgMSA2IDZ2MTJhNiA2IDAgMCAxLTYgNkg2YTYgNiAwIDAgMS02LTZ6Ii8+PHBhdGggZmlsbD0iI2ZmZmZmZiIgZD0iTTExLjA1NyA1LjI1N2ExLjU3IDEuNTcgMCAwIDEgMS41MzkuMDE1bDQuNjIxIDIuNjY4Yy40ODQuMjc5Ljc4My43OTcuNzgzIDEuMzU0djUuMzM2YTEuNTYgMS41NiAwIDAgMS0uNzgyIDEuMzU1bC0zLjQ3NCAyLjAwNWEyIDIgMCAwIDAgLjEyLS42OTF2LTUuMzM3YzAtLjczMy0uMzktMS40MDktMS4wMjYtMS43NzRsLTIuNTktMS40OTVWNi42MjZxLjAwMS0uMjQ2LjA3NC0uNDczYy4xMTctLjM2NC4zNjYtLjY4LjcwNy0uODc3eiIvPjxwYXRoIGZpbGw9IiNmZmZmZmYiIGQ9Ik05Ljg4MSA1Ljk0IDYuNDA4IDcuOTQ1QTEuNTYgMS41NiAwIDAgMCA1LjYyNSA5LjN2NS4zMzdjMCAuNTU3LjMgMS4wNzUuNzgzIDEuMzU0bDQuNjIxIDIuNjY4Yy40NzUuMjc0IDEuMDYuMjc5IDEuNTM5LjAxNWwuMDI3LS4wMTlhMS41NyAxLjU3IDAgMCAwIC43ODEtMS4zNXYtMi4wNjdsLTIuNTg5LTEuNDk1YTIuMDUgMi4wNSAwIDAgMS0xLjAyNi0xLjc3NVY2LjYzMWEyIDIgMCAwIDEgLjEyLS42OTEiLz48L3N2Zz4=&amp;logoColor=white&labelColor=101214" alt="Rovo"></a>
</p>

<p align="center">
  <a href="https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/"><b>Getting started</b></a> ·
  <a href="https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/"><b>Supported tools</b></a> ·
  <a href="https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/"><b>Security &amp; admin</b></a> ·
  <a href="https://community.atlassian.com/"><b>Community</b></a>
</p>

---

The **official Atlassian Rovo MCP Server** is a cloud-based bridge between your Atlassian Cloud site and compatible external tools. Once configured, it enables those tools to interact with **Jira, Confluence, Jira Service Management, Bitbucket, Compass, Loom, and Atlassian platform data (Projects, Goals, Teams, Focus, Talent, and the Teamwork Graph)** in real time. Authentication uses **OAuth 2.1** or **API tokens**, so every action respects the user's existing access controls.

With the Atlassian Rovo MCP Server, you can:

* **Summarize and search** Jira, Jira Service Management, Confluence, Bitbucket, Projects, Goals, and more without switching tools.
* **Retrieve and review** recordings of videos and meetings from Loom.
* **Create and update** work items or pages based on natural language commands.
* **Automate repetitive work**, like generating work items from meeting notes or specs.

Connect once, then describe what you want — no tab switching and no copy-pasting. Your AI selects and runs the right actions.

It's built for developers, content creators, and project teams who work in IDEs or AI tools and want to use Atlassian data without constantly switching context.

> [!IMPORTANT]
> **v2 is now the recommended version.** New setups should use `https://mcp.atlassian.com/v2/mcp`, which exposes more tools and more products. Existing v1 connections automatically start to expose and use v2 tools; incompatible clients may need to clear cached client IDs or `.well-known` credentials to keep authenticating. For setup steps, see [Getting started with the Atlassian Rovo MCP Server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/).

## One-click setup

Pick your AI client below to install the official Atlassian Rovo MCP Server. Each button uses your client's native install link, so you don't need to edit any JSON config by hand.

<table align="center">
  <tr>
    <td align="center" width="180">
      <a href="https://cursor.com/en/install-mcp?name=Atlassian-Rovo-MCP&config=eyJ1cmwiOiJodHRwczovL21jcC5hdGxhc3NpYW4uY29tL3YyL21jcCJ9">
        <img src="https://img.shields.io/badge/Cursor-000000?style=for-the-badge&logo=cursor&logoColor=white" alt="Add to Cursor"><br>
        <b>Add to Cursor</b>
      </a>
      <br><sub>Reference issues and log work in your codebase.</sub>
    </td>
    <td align="center" width="180">
      <a href="https://vscode.dev/redirect/mcp/install?name=Atlassian-Rovo-MCP&config=%7B%22url%22%3A%22https%3A%2F%2Fmcp.atlassian.com%2Fv2%2Fmcp%22%2C%22type%22%3A%22http%22%7D">
        <img src="https://img.shields.io/badge/VS_Code-0098FF?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZmZmZiI+PHBhdGggZD0iTTE3LjUgMiA5LjIgOS42IDQuNiA2LjEgMyA2Ljl2MTAuMmwxLjYuOCA0LjYtMy41IDguMyA3LjZMMjEgMjFWM3pNNi40IDEybDIuOS0yLjJ2NC40em0xMS4xIDQuOS01LjQtNC45IDUuNC00Ljl6Ii8+PC9zdmc+&logoColor=white" alt="Add to VS Code"><br>
        <b>Add to VS Code</b>
      </a>
      <br><sub>Search and create Jira issues via GitHub Copilot.</sub>
    </td>
    <td align="center" width="180">
      <a href="https://chatgpt.com/apps/atlassian-rovo/connector_692de805e3ec8191834719067174a384">
        <img src="https://img.shields.io/badge/ChatGPT-10A37F?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZmZmZiI+PHBhdGggZD0iTTEyIDIgMyA3djEwbDkgNSA5LTVWN3ptMCAyLjMgNi41IDMuNkwxMiAxMS41IDUuNSA3Ljl6TTUgOS42bDYgMy4zdjYuOGwtNi0zLjN6bTE0IDB2Ni44bC02IDMuM3YtNi44eiIvPjwvc3ZnPg==&logoColor=white" alt="Add to ChatGPT"><br>
        <b>Add to ChatGPT</b>
      </a>
      <br><sub>Search, summarize, and create right from ChatGPT.</sub>
    </td>
    <td align="center" width="180">
      <a href="https://claude.ai/directory/connectors/atlassian">
        <img src="https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=claude&logoColor=white" alt="Add to Claude"><br>
        <b>Add to Claude</b>
      </a>
      <br><sub>Bring Jira and Confluence into Claude workflows.</sub>
    </td>
  </tr>
</table>

### Let your agent do the setup

Most AI coding agents can install, authenticate, and configure the server themselves. Copy and paste this prompt into your agent:

```
Set up Atlassian Rovo MCP for this agent using the official setup guide at
https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/
and the MCP server URL https://mcp.atlassian.com/v2/mcp. Then start the Atlassian MCP
authentication flow so I can sign in.
```

Or add the server manually with your client's own command:

| Client | Command or configuration |
| --- | --- |
| Claude Code | `claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp`, then run `/mcp` in a session to authenticate |
| Codex | `codex mcp add atlassian --url https://mcp.atlassian.com/v2/mcp` |
| Claude Desktop | **Settings → Extensions → Browse extensions → Plugins**, then search for **Atlassian** |
| Codex Desktop | **Plugins** or **Connectors**, then install **Atlassian Rovo** |
| VS Code / GitHub Copilot | Extensions view → search `@mcp Atlassian` → **Install** |
| Cursor | [Atlassian plugin for Cursor with MCP](https://cursor.com/marketplace/atlassian) → **Add to Cursor** |
| Windsurf | **Cascade → MCP servers → Add Server → Add custom server**, with `serverUrl` set to `https://mcp.atlassian.com/v2/mcp` |
| Any other MCP client | Use the server URL `https://mcp.atlassian.com/v2/mcp` |

## Contents

* [One-click setup](#one-click-setup)
* [Supported clients](#supported-clients)
* [Plugin packaging and compatibility](#plugin-packaging-and-compatibility)
* [Supported products and tools](#supported-products-and-tools)
* [How the server exposes tools](#how-the-server-exposes-tools)
* [MCP gateways](#mcp-gateways)
* [Before you start](#before-you-start)
* [Data and security](#data-and-security)
* [How it works](#how-it-works)
* [Example workflows](#example-workflows)
* [Tips and tricks](#tips-and-tricks)
* [Admin notes: managing access](#admin-notes-managing-access)
* [Security](#security)
* [Support and feedback](#support-and-feedback)
* [Disclaimer](#disclaimer)

---

## Supported clients

The Atlassian Rovo MCP Server works with a growing list of MCP-compatible clients:

| Client | Setup reference |
| --- | --- |
| OpenAI ChatGPT | [Connectors / MCP guide](https://platform.openai.com/docs/guides/tools-connectors-mcp) |
| OpenAI Codex (CLI and Desktop) | [Codex MCP docs](https://developers.openai.com/codex/mcp/) |
| Claude (Claude.ai, Desktop, and Code) | [Claude MCP docs](https://code.claude.com/docs/en/mcp) |
| Cursor | [Atlassian on the Cursor marketplace](https://cursor.com/marketplace/atlassian) |
| Visual Studio Code (GitHub Copilot) | [VS Code MCP docs](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) |
| GitHub Copilot CLI | [About Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli) |
| Google Gemini CLI | [Gemini CLI MCP docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md) |
| Windsurf | [Windsurf MCP docs](https://docs.windsurf.com/windsurf/cascade/mcp) |
| Docker | [Docker MCP Catalog and Toolkit](https://docs.docker.com/ai/mcp-catalog-and-toolkit/) |
| Kiro and other Agent Plugins clients | [Kiro Powers documentation](https://kiro.dev/docs/powers/create/) |
| Amazon Quick Suite | [MCP integration guide](https://docs.aws.amazon.com/quicksuite/latest/userguide/mcp-integration.html) |

The Atlassian Rovo MCP Server also supports any **local MCP-compatible client** that can run on `localhost` and connect to the server via the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) proxy. This enables custom or third-party integrations that follow the MCP specification.

> [!TIP]
> For the current, canonical list of supported clients and step-by-step setup, see [Getting started with the Atlassian Rovo MCP Server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/). You can also refer to your client's own MCP documentation or built-in assistant.

---

## Plugin packaging and compatibility

This repository publishes the same MCP server and skills in several package formats so clients can use their native discovery and installation flows:

| Format | Manifest and configuration | Shared components |
| --- | --- | --- |
| [Agent Plugins v1](https://agent-plugins.org/) | [`plugin.json`](plugin.json) and [`mcp.json`](mcp.json) | [`skills/`](skills/) |
| Claude Code plugin | [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | [`.mcp.json`](.mcp.json) and [`skills/`](skills/) |
| Cursor plugin | [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) | [`.mcp.json`](.mcp.json) and [`skills/`](skills/) |
| Gemini extension | [`gemini-extension.json`](gemini-extension.json) | MCP server configuration embedded in the manifest |
| MCP Registry | [`server.json`](server.json) | Remote server metadata |

The skills in [`skills/`](skills/) target the `/v2/mcp` endpoint and are what every packaged plugin
installs. The previous generation is archived in [`skills/v1/`](skills/v1/) for anyone still on a v1
endpoint; it is not installed by any plugin and is set up manually. See
[`skills/README.md`](skills/README.md) for the differences.

Both `mcp.json` and `.mcp.json` are intentional. Agent Plugins requires the root `mcp.json` filename and its portable transport vocabulary; existing clients continue to use `.mcp.json` and their native configuration vocabulary. Keep their endpoint settings aligned when changing either file.

The root package can be imported by clients that implement Agent Plugins, including Kiro Powers. Client-specific manifests remain available and are not replaced by the portable package.

---

## Supported products and tools

Tools are organized by product and intent (read, write, search, delete, or manage). Organization admins grant or revoke access at the permission-group level, and each tool inherits the access of its parent group.

| Product | Permission groups | OAuth 2.1 | API token |
| --- | --- | :---: | :---: |
| **Jira** | `read_jira` · `write_jira` · `search_jira` | ✅ | ✅ |
| **Jira** (admin-enabled) | `delete_jira` · `manage_jira` | ✅ | ✅ |
| **Confluence** | `read_confluence` · `write_confluence` · `search_confluence` | ✅ | ✅ |
| **Bitbucket Cloud** | `read_bitbucket` · `write_bitbucket` | ✅ | ✅ |
| **Jira Service Management** | `read_jsm` · `write_jsm` | — | ✅ (only) |
| **Atlassian platform** | `read_teamwork_graph` · `write_teamwork_graph` · `search_atlassian` | ✅ | ✅ |
| **Loom** | `read_loom` · `write_loom` | ✅ | ✅ |
| **Goals** | `read_goals` · `write_goals` | ✅ | ✅ |
| **Projects** | `read_projects` · `write_projects` | ✅ | ✅ |
| **Teams** | `read_teams` · `write_teams` | ✅ | ✅ |
| **Focus** | `read_focus` · `write_focus` | ✅ | ✅ |
| **Talent** | `read_talent` · `write_talent` | ✅ | ✅ |
| **Compass** | `read_compass` · `write_compass` | ✅ (only) | — |

Product-specific conditions:

* **`delete_jira` and `manage_jira`** are **disabled by default** and must be enabled by an admin before they can be used.
* **Bitbucket Cloud** tools are only available if your Bitbucket workspace is linked to an organization. Workspaces that aren't linked to an organization can't be selected when authenticating.
* **Jira Service Management** tools only support authentication via API token, and are only available if an organization admin has enabled API token authentication.
* **Loom** tools are only available for Loom workspaces linked to an Atlassian site.
* **Teamwork Graph** tools can retrieve data from third-party services connected to Jira, such as linked pull requests, builds, and deployments. For **GitHub for Atlassian**, *full access* means tools retrieve GitHub data based on the user's GitHub permissions, while *limited access* means they retrieve data based on the user's Jira permissions. Azure DevOps, GitLab, Jenkins, and Spinnaker connectors follow the limited access model.

> [!NOTE]
> For the complete, current tool reference, including the required scope for each permission group, see [Supported tools](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/).

---

## How the server exposes tools

Rather than sending every tool definition to the AI client at connection time, the Atlassian Rovo MCP Server exposes a small set of the most-used tools and lets the client discover the rest on demand. Tools marked **Primary** are visible directly to agents.

This has two benefits:

* Your client's context stays free for the task at hand instead of being filled with tool definitions.
* New tools become available without the client needing to reconnect.

## MCP gateways

If you're using an MCP gateway, or otherwise need every tool available up front rather than using the discovery and execute methods, use the `tools=all` override to expose all tools as a paginated flat tool list:

```
https://mcp.atlassian.com/v2/mcp?tools=all
```

---

## Before you start

Check that your environment meets these requirements before you set up the server.

### Prerequisites

The requirements depend on how you connect:

#### For supported clients

* An **Atlassian Cloud site** with one or more of Jira, Confluence, Jira Service Management, Bitbucket, or Compass
* Access to **the client of choice**
* A modern browser to complete the OAuth 2.1 authorization flow, or API token credentials for headless authentication

If your organization admin has disabled authentication via API token, MCP clients can't connect with a token and need to use OAuth 2.1 instead.

#### For IDEs or local clients (desktop setup)

* An **Atlassian Cloud site** with one or more supported products
* A supported IDE (for example, **Claude Desktop, VS Code, or Cursor**) or a custom MCP-compatible client
* **Node.js v18+** installed to run the local MCP proxy ([`mcp-remote`](https://www.npmjs.com/package/mcp-remote))
* A modern browser for completing OAuth login, or API token credentials for headless authentication

---

## Data and security

The server enforces several security controls:

* All traffic is encrypted in transit over **HTTPS (TLS 1.2 or later)**, per [Atlassian's security practices](https://www.atlassian.com/trust/security/security-practices).
* **OAuth 2.1** and **API token** authentication provide secure access control.
* Data access respects user permissions across every connected Atlassian product, including Jira, Confluence, Jira Service Management, Bitbucket, Compass, and Loom.
* If your organization uses IP allowlisting for Atlassian Cloud products, tool calls made through the Atlassian Rovo MCP Server also honor those IP rules.

For a deeper overview of the security model and admin controls, see:

* [Understand Atlassian Rovo MCP Server](https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/)
* [Control Atlassian Rovo MCP Server settings](https://support.atlassian.com/security-and-access-policies/docs/control-atlassian-rovo-mcp-server-settings/)

---

## How it works

### Architecture and communication

1. A supported client connects to the server endpoint. The recommended endpoint for all clients is:

   ```
   https://mcp.atlassian.com/v2/mcp
   ```

   The v1 endpoints (`https://mcp.atlassian.com/v1/mcp/authv2` and `https://mcp.atlassian.com/v1/mcp`) remain supported, and existing v1 connections automatically start to expose and use v2 tools.
2. Depending on your setup, a secure browser-based OAuth 2.1 flow is triggered, or API token authentication is used.
3. Once authorized, the client streams contextual data and receives real-time responses from your connected Atlassian products.

> [!WARNING]
> **After 30 June 2026, the legacy Server-Sent Events endpoint (`https://mcp.atlassian.com/v1/sse`) will no longer be supported.** Update any custom clients configured to use `/sse` so they point to `/mcp` — preferably `https://mcp.atlassian.com/v2/mcp`.

> [!NOTE]
> Clients that can't complete authentication after the move to v2 tools may need to clear cached client IDs or `.well-known` credentials.

### Permission management

Access is granted only to data that the user already has permission to view in Atlassian Cloud. All actions respect existing project or space-level roles. OAuth and API token authentication both honor configured scopes and Atlassian permissions.

### API token authentication (headless)

API token authentication is available for headless, service-style, or non-interactive client setups (for example, backend systems or automations). It is also **required** for Jira Service Management tools.

Two mechanisms are supported:

| Mechanism | Header |
| --- | --- |
| Personal API token (Basic auth) | `Authorization: Basic <base64(email:api_token)>` |
| Service account API key (Bearer token) | `Authorization: Bearer <api_key>` |

* **Admin enablement required:** An organization admin must enable API token authentication for the Rovo MCP Server (**Atlassian Administration → Rovo → Rovo MCP server → Authentication**).
* **Scoped token required:** Create a personal API token, or ask your admin for a service account API key, with the scopes required for the tools and data you need to access.
* **Configuration guide:** [Configure authentication via API token](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/configuring-authentication-via-api-token/)
* **Admin setting reference:** [Control Atlassian Rovo MCP Server settings: Configure authentication](https://support.atlassian.com/security-and-access-policies/docs/control-atlassian-rovo-mcp-server-settings/#Configure-authentication)

---

## Example workflows

Once connected, you can run tasks like these from your client.

### Jira workflows

* **Search**: "Find all open bugs in Project Alpha."
* **Create/update**: "Create a story titled 'Redesign onboarding'."
* **Bulk create**: "Make five Jira issues from these notes."

### Confluence workflows

* **Summarize**: "Summarize the Q2 planning page."
* **Create**: "Create a page titled 'Team Goals Q3'."
* **Navigate**: "What spaces do I have access to?"

### Compass workflows

* **Create**: "Create a service component based on the current repository."
* **Bulk create**: "Import components and custom fields from this CSV/JSON."
* **Query**: "What depends on the `api-gateway` service?"

### Loom workflows

* **Retrieve**: "Find the Loom recording of last week's design review."
* **Summarize**: "Summarize this Loom walkthrough and list the action items."

### Projects and Goals workflows

* **Status**: "What's the current status of the Checkout Revamp project?"
* **Roll up**: "Which goals are at risk this quarter, and why?"

### Combined tasks

* **Link content**: "Link these three Jira work items to the 'Release Plan' page."
* **Find documentation**: "Fetch the Confluence documentation page linked to this Compass component."
* **Move work forward**: "Move PROJ-456 to 'In Review' and add a comment that the PR is up."

> [!NOTE]
> Actual capabilities vary depending on your permission level and client platform.

---

## Tips and tricks

### Set default CloudId, Jira project, and Confluence space

Update your [AGENTS.md](https://agents.md/) with the Markdown below to reduce discovery tool calls, save time and tokens, and set maximum search results.

```md
## Atlassian Rovo MCP

When connected to atlassian-rovo-mcp:
- **MUST** use Jira project key = YOURPROJ
- **MUST** use Confluence spaceId = "123456"
- **MUST** use cloudId = "https://yoursite.atlassian.net" (do NOT call getAccessibleAtlassianResources)
- **MUST** use `maxResults: 10` or `limit: 10` for ALL Jira JQL and Confluence CQL search operations.
```

### Use skills

If you're using a desktop client like Claude, you can create or reuse skills for repeated tasks. [See the default Rovo MCP skills](https://github.com/atlassian/atlassian-mcp-server/tree/main/skills).

For [Cursor](https://cursor.com/marketplace/atlassian), skills are part of the marketplace plugin.

---

## Admin notes: managing access

If you're an admin preparing your organization to use the Atlassian Rovo MCP Server, review the points below. For more detailed admin guidance, see:

* [Understand Atlassian Rovo MCP Server](https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/)
* [Control Atlassian Rovo MCP Server settings](https://support.atlassian.com/security-and-access-policies/docs/control-atlassian-rovo-mcp-server-settings/)
* [Manage Atlassian Rovo MCP Server](https://support.atlassian.com/security-and-access-policies/docs/manage-atlassian-rovo-mcp-server/)
* [Monitor Atlassian Rovo MCP Server activity](https://support.atlassian.com/security-and-access-policies/docs/monitor-atlassian-rovo-mcp-server-activity/)

### Manage, monitor, and revoke access

* **Admin controls:**
  Site and organization admins can manage, review, or revoke the MCP app's access from [Manage your organization's Marketplace and third-party apps](https://support.atlassian.com/security-and-access-policies/docs/manage-your-users-third-party-apps/).
* **Domain controls:**
  Use the **Rovo MCP server** settings page in Atlassian Administration to control which external AI tools and domains are allowed to connect. By default, Atlassian-supported domains are allowed; you can add trusted domains or block supported ones. Domain controls apply to OAuth 2.1 connections. For details, see [Available Atlassian Rovo MCP server domains](https://support.atlassian.com/security-and-access-policies/docs/available-atlassian-rovo-mcp-server-domains/).
* **IP controls:**
  If your organization uses IP allowlisting for Atlassian Cloud apps, requests made through the Atlassian Rovo MCP Server must originate from an IP address allowed by your organization's IP allowlist for the relevant app. For configuration details, see [Specify IP addresses for product access](https://support.atlassian.com/security-and-access-policies/docs/specify-ip-addresses-for-product-access/).
* **End-user controls:**
  Individual users can revoke their own app authorizations from their profile settings.
* **Audit logging:**
  Every time a tool is used through the Atlassian Rovo MCP Server, an event is recorded in your organization's audit log. Admins can review these in Atlassian Administration under **Insights → Audit log** (filter for _Rovo MCP User Actions_ or search _MCP_). For more information, see [Monitor Atlassian Rovo MCP server activity](https://support.atlassian.com/security-and-access-policies/docs/monitor-atlassian-rovo-mcp-server-activity/).

### Troubleshooting common issues

* **"You don't have permission to connect from this IP address. Please ask your admin for access."**
  This usually indicates that IP allowlisting is enabled and the user's current IP address isn't allowed to access Jira, Confluence, Jira Service Management, Bitbucket, or Compass via the Atlassian Rovo MCP Server. Ask your site or organization admin to review the IP allowlist configuration and add the relevant network or VPN IP ranges if appropriate.

---

## Security

Model Context Protocol (MCP) lets AI agents connect to tools and Atlassian data using your account's permissions, which creates powerful workflows but also structural risks. Any MCP client or server you enable (for example, IDE plugins, desktop apps, hosted MCP servers, or "one-click" integrations) can cause an AI agent to perform actions on your behalf.

Large language models (LLMs) are vulnerable to [prompt injection](https://owasp.org/www-community/attacks/PromptInjection) and related attacks (such as indirect prompt injection and [tool poisoning](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)). These attacks can instruct the agent to exfiltrate data or make unintended changes without explicit requests.

To reduce risk, only use trusted MCP clients and servers, carefully review which tools and data each agent can access, and apply least privilege (scoped tokens, minimal project/workspace access). For any high-impact or destructive action, require human confirmation and monitor audit logs for unusual activity. We strongly recommend reviewing Atlassian's guidance on MCP risks at [MCP Clients: Understanding the potential security risks](https://www.atlassian.com/blog/artificial-intelligence/mcp-risk-awareness).

---

## Support and feedback

We use your feedback to improve the Atlassian Rovo MCP Server. If you hit a bug or limitation, or have a suggestion:

* Visit the [Atlassian Support Portal](https://support.atlassian.com/) to report issues and feature requests.
* Share your experiences and questions on the [Atlassian Community](https://community.atlassian.com/), and developer-related asks on the [Atlassian Developer Community](https://community.developer.atlassian.com/).
* Go to our [Ecosystem Developer Portal](https://ecosystem.atlassian.net/servicedesk/customer/portal/14/user/login?destination=portal%2F14) if you are building an app and found a bug or issue, or have suggestions.

---

## Disclaimer

MCP clients can perform actions across Atlassian products with your existing permissions. Use least privilege, review high-impact changes before confirming, and monitor audit logs for unusual activity.

Learn more: [MCP Clients: Understanding the potential security risks](https://www.atlassian.com/blog/artificial-intelligence/mcp-risk-awareness).
