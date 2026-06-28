<p align="center">
  <img src="images/atlassian_logo_brand_RGB.svg" alt="Atlassian" width="320">
</p>

<h1 align="center">Atlassian Rovo MCP Server</h1>

<p align="center">
  <b>The official Model Context Protocol (MCP) server for Atlassian: a cloud-hosted bridge that gives your AI tools secure, real-time access to Jira, Confluence, Jira Service Management, Bitbucket, and Compass.</b>
</p>

<!-- Line 1 · Project -->
<p align="center">
  <img src="https://img.shields.io/badge/Official-Atlassian-0052CC?logo=atlassian&logoColor=white" alt="Official Atlassian Server">
  <a href="https://github.com/atlassian/atlassian-mcp-server/stargazers"><img src="https://img.shields.io/github/stars/atlassian/atlassian-mcp-server?style=flat&logo=github&label=Stars&color=0052CC" alt="GitHub stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/atlassian/atlassian-mcp-server?label=License&color=0052CC" alt="License: Apache 2.0"></a>
  <img src="https://img.shields.io/badge/Status-Generally_Available-2EBC4F" alt="Status: Generally Available">
</p>

<!-- Line 2 · Protocol & access -->
<p align="center">
  <img src="https://img.shields.io/badge/Model_Context_Protocol-compatible-000000?logo=modelcontextprotocol&logoColor=white" alt="Model Context Protocol compatible">
  <a href="server.json"><img src="https://img.shields.io/badge/MCP_Registry-com.atlassian-000000?logo=modelcontextprotocol&logoColor=white" alt="MCP Registry: com.atlassian"></a>
  <img src="https://img.shields.io/badge/Auth-OAuth_2.1%20%7C%20API%20token-2EBC4F" alt="Auth: OAuth 2.1 or API token">
  <img src="https://img.shields.io/badge/Hosting-Atlassian_Cloud-0052CC?logo=atlassian&logoColor=white" alt="Hosting: Atlassian Cloud">
</p>

<!-- Line 3 · Supported products. Compass & Rovo have no simple-icons slug, so they use the official @atlaskit/logo (v20) tile glyphs embedded as SVG data URIs. -->
<p align="center">
  <img src="https://img.shields.io/badge/Jira-0052CC?logo=jira&logoColor=white" alt="Jira">
  <img src="https://img.shields.io/badge/Confluence-172B4D?logo=confluence&logoColor=white" alt="Confluence">
  <img src="https://img.shields.io/badge/Jira_Service_Management-0052CC?logo=jirasoftware&logoColor=white" alt="Jira Service Management">
  <img src="https://img.shields.io/badge/Bitbucket-0052CC?logo=bitbucket&logoColor=white" alt="Bitbucket">
  <img src="https://img.shields.io/badge/Compass-94C748?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzk0Yzc0OCIgZD0iTTAgNmE2IDYgMCAwIDEgNi02aDEyYTYgNiAwIDAgMSA2IDZ2MTJhNiA2IDAgMCAxLTYgNkg2YTYgNiAwIDAgMS02LTZ6Ii8+PHBhdGggZmlsbD0iIzEwMTIxNCIgZD0iTTEyLjc1IDcuODc3di0zLjM3bDYuMTYtLjAwN2guMDA3YS41OS41OSAwIDAgMSAuNTgzLjU5OHY2LjE0N2gtMy4zNjZWNy44Nzd6Ii8+PHBhdGggZmlsbD0iIzEwMTIxNCIgZD0iTTEyLjc1IDE0LjYxNXYtMy4zN2gzLjM2OHY2LjE2NWEuNTkuNTkgMCAwIDEtLjU5MS41OUg2LjU4M0EuNTkuNTkgMCAwIDEgNiAxNy40MDJWOC40NjdhLjU5LjU5IDAgMCAxIC41OTEtLjU5aDYuMTZ2My4zNjhIOS4zNzN2My4zN3oiLz48L3N2Zz4=" alt="Compass">
  <img src="https://img.shields.io/badge/Rovo-1868DB?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzE4NjhkYiIgZD0iTTAgNmE2IDYgMCAwIDEgNi02aDEyYTYgNiAwIDAgMSA2IDZ2MTJhNiA2IDAgMCAxLTYgNkg2YTYgNiAwIDAgMS02LTZ6Ii8+PHBhdGggZmlsbD0iI2ZmZmZmZiIgZD0iTTExLjA1NyA1LjI1N2ExLjU3IDEuNTcgMCAwIDEgMS41MzkuMDE1bDQuNjIxIDIuNjY4Yy40ODQuMjc5Ljc4My43OTcuNzgzIDEuMzU0djUuMzM2YTEuNTYgMS41NiAwIDAgMS0uNzgyIDEuMzU1bC0zLjQ3NCAyLjAwNWEyIDIgMCAwIDAgLjEyLS42OTF2LTUuMzM3YzAtLjczMy0uMzktMS40MDktMS4wMjYtMS43NzRsLTIuNTktMS40OTVWNi42MjZxLjAwMS0uMjQ2LjA3NC0uNDczYy4xMTctLjM2NC4zNjYtLjY4LjcwNy0uODc3eiIvPjxwYXRoIGZpbGw9IiNmZmZmZmYiIGQ9Ik05Ljg4MSA1Ljk0IDYuNDA4IDcuOTQ1QTEuNTYgMS41NiAwIDAgMCA1LjYyNSA5LjN2NS4zMzdjMCAuNTU3LjMgMS4wNzUuNzgzIDEuMzU0bDQuNjIxIDIuNjY4Yy40NzUuMjc0IDEuMDYuMjc5IDEuNTM5LjAxNWwuMDI3LS4wMTlhMS41NyAxLjU3IDAgMCAwIC43ODEtMS4zNXYtMi4wNjdsLTIuNTg5LTEuNDk1YTIuMDUgMi4wNSAwIDAgMS0xLjAyNi0xLjc3NVY2LjYzMWEyIDIgMCAwIDEgLjEyLS42OTEiLz48L3N2Zz4=&amp;logoColor=white" alt="Rovo">
</p>

<p align="center">
  <a href="https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/"><b>Getting started</b></a> ·
  <a href="https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/"><b>Supported tools</b></a> ·
  <a href="https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/"><b>Security &amp; admin</b></a> ·
  <a href="https://community.atlassian.com/"><b>Community</b></a>
</p>

---

The **official Atlassian Rovo MCP Server** is a cloud-based bridge between your Atlassian Cloud site and compatible external tools. Once configured, it enables those tools to interact with **Jira, Confluence, Jira Service Management, Bitbucket, and Compass** data in real time. Authentication uses **OAuth 2.1** or **API tokens**, so every action respects the user's existing access controls.

With the Atlassian Rovo MCP Server, you can:

* **Summarize and search** Jira, Confluence, Jira Service Management, and Bitbucket content without switching tools.
* **Create and update** issues or pages based on natural language commands.
* **Automate repetitive work**, like generating tickets from meeting notes or specs.

It's built for developers, content creators, and project teams who work in IDEs or AI tools and want to use Atlassian data without constantly switching context.

## Contents

* [Supported clients](#supported-clients)
* [Supported products and tools](#supported-products-and-tools)
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
| Claude (Claude.ai, Desktop, and Code) | [Claude MCP docs](https://code.claude.com/docs/en/mcp) |
| Cursor | [Atlassian on the Cursor marketplace](https://cursor.com/marketplace/atlassian) |
| Visual Studio Code (GitHub Copilot) | [VS Code MCP docs](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) |
| GitHub Copilot CLI | [About Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli) |
| Google Gemini CLI | [Gemini CLI MCP docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md) |
| Amazon Quick Suite | [MCP integration guide](https://docs.aws.amazon.com/quicksuite/latest/userguide/mcp-integration.html) |

The Atlassian Rovo MCP Server also supports any **local MCP-compatible client** that can run on `localhost` and connect to the server via the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) proxy. This enables custom or third-party integrations that follow the MCP specification.

> [!TIP]
> For the current, canonical list of supported clients and step-by-step setup, see [Getting started with the Atlassian Rovo MCP Server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/). You can also refer to your client's own MCP documentation or built-in assistant.

---

## Supported products and tools

Tools are organized by product and intent (read, write, or search). Organization admins grant or revoke access at the permission-group level, and each tool inherits the access of its parent group.

| Product | Permission groups | OAuth 2.1 | API token |
| --- | --- | :---: | :---: |
| **Jira** | `read` · `write` · `search` | ✅ | ✅ |
| **Confluence** | `read` · `write` · `search` | ✅ | ✅ |
| **Jira Service Management** | `read` · `write` | — | ✅ (only) |
| **Bitbucket Cloud** | `read` · `write` | — | ✅ (scoped, only) |
| **Compass** | `read` · `write` | ✅ (only) | — |
| **Atlassian platform** | `read_teamwork_graph` · `search_atlassian` | ✅ | ✅ |

> [!NOTE]
> Jira Service Management and Bitbucket Cloud tools are available **only via API token authentication**, while Compass tools are available **only via OAuth 2.1**. For the complete, current tool reference, see [Supported tools](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/).

---

## Before you start

Check that your environment meets these requirements before you set up the server.

### Prerequisites

The requirements depend on how you connect:

#### For supported clients

* An **Atlassian Cloud site** with one or more of Jira, Confluence, Jira Service Management, Bitbucket, or Compass
* Access to **the client of choice**
* A modern browser to complete the OAuth 2.1 authorization flow, or API token credentials for headless authentication

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
* Data access respects Jira, Confluence, Jira Service Management, Bitbucket, and Compass user permissions.
* If your organization uses IP allowlisting for Atlassian Cloud products, tool calls made through the Atlassian Rovo MCP Server also honor those IP rules.

For a deeper overview of the security model and admin controls, see:

* [Understand Atlassian Rovo MCP Server](https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/)
* [Control Atlassian Rovo MCP Server settings](https://support.atlassian.com/security-and-access-policies/docs/control-atlassian-rovo-mcp-server-settings/)

---

## How it works

### Architecture and communication

1. A supported client connects to the server endpoint. The recommended endpoint for most clients is:

   ```
   https://mcp.atlassian.com/v1/mcp/authv2
   ```

   The `https://mcp.atlassian.com/v1/mcp` endpoint is also supported (for example, for API token configurations).
2. Depending on your setup, a secure browser-based OAuth 2.1 flow is triggered, or API token authentication is used.
3. Once authorized, the client streams contextual data and receives real-time responses from your connected Atlassian products.

> [!NOTE]
> The legacy Server-Sent Events endpoint (`https://mcp.atlassian.com/v1/sse`) is still supported, but we recommend updating any custom clients configured to use `/sse` so they now point to `/mcp` (or `/mcp/authv2`).

### Permission management

Access is granted only to data that the user already has permission to view in Atlassian Cloud. All actions respect existing project or space-level roles. OAuth and API token authentication both honor configured scopes and Atlassian permissions.

### API token authentication (headless)

API token authentication is available for headless, service-style, or non-interactive client setups (for example, backend systems or automations). It is also **required** for Jira Service Management and Bitbucket Cloud tools.

* **Admin enablement required:** An organization admin must enable API token authentication for the Rovo MCP Server (**Atlassian Administration → Rovo → Rovo MCP server → Authentication**).
* **Scoped token required:** Create a personal API token with the scopes required for the tools and data you need to access.
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

### Combined tasks

* **Link content**: "Link these three Jira tickets to the 'Release Plan' page."
* **Find documentation**: "Fetch the Confluence documentation page linked to this Compass component."

> [!NOTE]
> Actual capabilities vary depending on your permission level and client platform.

---

## ❓ FAQ

### What is the Atlassian Rovo MCP Server?

The Atlassian Rovo MCP Server is a **cloud-based bridge** between your Atlassian Cloud site (Jira, Compass, Confluence) and compatible external AI tools. It enables AI agents to interact with your Atlassian data in real-time using **OAuth 2.1** or **API token authentication**.

### What can I do with it?

- **Search**: "Find all open bugs in Project Alpha" (Jira)
- **Create/Update**: "Create a story titled 'Redesign onboarding'" (Jira)
- **Summarize**: "Summarize the Q2 planning page" (Confluence)
- **Link content**: "Link these Jira tickets to the Release Plan page" (Confluence)
- **Component management**: "Create a service component from this repo" (Compass)
- **Query dependencies**: "What depends on the `api-gateway` service?" (Compass)

### Which clients are supported?

- **OpenAI ChatGPT** — via Tools & Connectors MCP
- **Claude Desktop / Claude Code** — MCP integration
- **GitHub Copilot CLI** — Copilot agent tools
- **Gemini CLI** — MCP server tools
- **Amazon Quick Suite** — MCP integration
- **Visual Studio Code** — MCP client
- **Any local MCP-compatible client** — via `mcp-remote` proxy

### How does authentication work?

Two options:
1. **OAuth 2.1** — Browser-based consent flow, secure and user-friendly
2. **API Token** — Headless/long-running setups (admin must enable, requires scoped token)

### Do I need admin approval?

**For OAuth 2.1**: Yes — a site admin must complete the first 3LO consent flow. After that, users with access to at least one Atlassian app (Jira or Confluence) can also connect.

**For API Token**: An organization admin must enable API token authentication for Rovo MCP Server.

### What permissions does the MCP use?

All actions respect your **existing Atlassian permissions**:
- Project-level roles in Jira
- Space-level permissions in Confluence
- Compass component access

The MCP cannot access data you don't already have permission to view.

### How do I set up for local clients (Claude Desktop, VS Code)?

1. Ensure Node.js v18+ is installed
2. Configure your client to connect via `mcp-remote` proxy
3. Complete OAuth 2.1 login in browser, or use API token credentials
4. Refer to your client's MCP documentation for specific setup

### What is the MCP endpoint?

```
https://mcp.atlassian.com/v1/mcp
```

> Note: `/sse` endpoint is deprecated. Update custom clients to use `/mcp`.

### Can I use skills with MCP?

**Yes.** If using Claude Desktop, create or reuse skills for repeated tasks. Default Rovo MCP skills are available at [github.com/atlassian/atlassian-mcp-server/tree/main/skills](https://github.com/atlassian/atlassian-mcp-server/tree/main/skills).

For Cursor, skills are part of the marketplace plugin.

### How can I reduce tool calls and save tokens?

Add defaults to your `AGENTS.md`:
```markdown
## Atlassian Rovo MCP

When connected to atlassian-rovo-mcp:
- MUST use Jira project key = YOURPROJ
- MUST use Confluence spaceId = "123456"
- MUST use cloudId = "https://yoursite.atlassian.net"
- MUST use maxResults: 10 for all searches
```

### What if my IP is blocked?

If your organization uses **IP allowlisting**, requests must come from an allowed IP. Ask your admin to:
- Review IP allowlist configuration
- Add relevant network/VPN IP ranges

### How do admins manage access?

- **Connected apps**: Manage/revoke access in Atlassian Administration
- **Domain controls**: Configure which external domains can connect
- **Audit logging**: Monitor MCP activity in organization audit log

### What security measures are in place?

- HTTPS with TLS 1.2+ encryption
- OAuth 2.1 + scoped API tokens
- Permission-based access control
- IP allowlisting support
- Audit logging for all actions

### What are MCP security risks?

MCP clients can perform actions on your behalf. Risks include:
- **Prompt injection** — malicious prompts can instruct agents
- **Indirect prompt injection** — compromised data sources
- **Tool poisoning** — malicious MCP servers

**Mitigation**:
- Use trusted MCP clients/servers
- Apply least privilege (scoped tokens, minimal access)
- Require human confirmation for high-impact actions
- Monitor audit logs for unusual activity

See: [MCP Clients: Understanding the potential security risks](https://www.atlassian.com/blog/artificial-intelligence/mcp-risk-awareness)

### Where can I get help?

- **Support**: [Atlassian Support Portal](https://support.atlassian.com/)
- **Community**: [Atlassian Community](https://community.atlassian.com/)
- **Developer Portal**: [ecosystem.atlassian.net](https://ecosystem.atlassian.net/servicedesk/customer/portal/14)
- **Troubleshooting**: See [Troubleshooting common issues](#troubleshooting-common-issues) section above

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

### Installation and access

* **Not a Marketplace app:**
  The Atlassian Rovo MCP Server is _not_ installed via the Atlassian Marketplace or the **Manage apps** screen. Instead, it is installed automatically the first time a user completes the OAuth 2.1 (3LO) consent flow (just-in-time, or "lazy loading," installation).
* **First-time installation requirements:**
  The first user to complete the 3LO consent flow for your site must have access to the Atlassian apps requested by the MCP scopes (for example, Jira and/or Confluence). This ensures the MCP app is registered with the correct permissions for your site.
* **Subsequent user access:**
  After the initial install, users with access to only one Atlassian app (for example, just Jira or just Confluence) can also complete the 3LO flow to access that app through MCP.

### Manage, monitor, and revoke access

* **Admin controls:**
  Site and organization admins can manage, review, or revoke the MCP app's access from [Manage your organization's Marketplace and third-party apps](https://support.atlassian.com/security-and-access-policies/docs/manage-your-users-third-party-apps/). The app appears in your site's **Connected apps** list after the first successful 3LO consent.
* **Domain controls:**
  Use the **Rovo MCP server** settings page in Atlassian Administration to control which external AI tools and domains are allowed to connect. By default, Atlassian-supported domains are allowed; you can add trusted domains or block supported ones. Domain controls apply to OAuth 2.1 connections. For details, see [Available Atlassian Rovo MCP server domains](https://support.atlassian.com/security-and-access-policies/docs/available-atlassian-rovo-mcp-server-domains/).
* **IP controls:**
  If your organization uses IP allowlisting for Atlassian Cloud apps, requests made through the Atlassian Rovo MCP Server must originate from an IP address allowed by your organization's IP allowlist for the relevant app. For configuration details, see [Specify IP addresses for product access](https://support.atlassian.com/security-and-access-policies/docs/specify-ip-addresses-for-product-access/).
* **End-user controls:**
  Individual users can revoke their own app authorizations from their profile settings.
* **Audit logging:**
  Every time a tool is used through the Atlassian Rovo MCP Server, an event is recorded in your organization's audit log. Admins can review these in Atlassian Administration under **Insights → Audit log** (filter for _Rovo MCP User Actions_ or search _MCP_). For more information, see [Monitor Atlassian Rovo MCP server activity](https://support.atlassian.com/security-and-access-policies/docs/monitor-atlassian-rovo-mcp-server-activity/).

### Troubleshooting common issues

* **"Your site admin must authorize this app" error:**
  A site admin must complete the 3LO consent flow before anyone else can use the MCP app. See ["Your site admin must authorize this app" error in Atlassian Cloud apps](https://support.atlassian.com/atlassian-cloud/kb/your-site-admin-must-authorize-this-app-error-in-atlassian-cloud-apps/) for more details.
* **"You don't have permission to connect from this IP address. Please ask your admin for access."**
  This usually indicates that IP allowlisting is enabled and the user's current IP address isn't allowed to access Jira, Confluence, Jira Service Management, Bitbucket, or Compass via the Atlassian Rovo MCP Server. Ask your site or organization admin to review the IP allowlist configuration and add the relevant network or VPN IP ranges if appropriate.
* **App not appearing in Connected apps:**
  Ensure the user is using the correct Atlassian account and site, and confirm the app is requesting the correct Atlassian app scopes (for example, Jira scopes). If issues persist, check [Manage your organization's Marketplace and third-party apps](https://support.atlassian.com/security-and-access-policies/docs/manage-your-users-third-party-apps/) or contact Atlassian Support. Also verify the user's product permissions in Atlassian Administration.

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

MCP clients can perform actions in Jira, Confluence, Jira Service Management, Bitbucket, and Compass with your existing permissions. Use least privilege, review high-impact changes before confirming, and monitor audit logs for unusual activity.

Learn more: [MCP Clients: Understanding the potential security risks](https://www.atlassian.com/blog/artificial-intelligence/mcp-risk-awareness).
