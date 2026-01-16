<p align="center">
  <img src="images/atlassian_logo_brand_RGB.svg">
</p>

# Atlassian MCP Server

The Atlassian Rovo MCP Server is a cloud-based bridge between your Atlassian Cloud site and compatible external tools. Once configured, it enables those tools to interact with Jira, Compass, and Confluence data in real-time. This functionality is powered by secure **OAuth 2.1 authorization**, which ensures all actions respect the user's existing access controls.

With the Atlassian Rovo MCP Server, you can:

* **Summarize and search** Jira, Compass, and Confluence content without switching tools.
* **Create and update** issues or pages based on natural language commands.
* **Automate repetitive work**, like generating tickets from meeting notes or specs.

It's designed developers, content creators, and project teams who use IDEs or AI platforms and want to work with Atlassian data without constantly context switching.

---

## Supported clients

The Atlassian Rovo MCP Server supports several clients, including:

* [OpenAI ChatGPT](https://platform.openai.com/docs/guides/tools-connectors-mcp)
* [Claude](https://code.claude.com/docs/en/mcp)
* [Google Gemini](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md)
* [Amazon Quick Suite](https://docs.aws.amazon.com/quicksuite/latest/userguide/mcp-integration.html)

The Atlassian Rovo MCP Server also supports any **local MCP-compatible client** that can run on `localhost` and connect to the server via the `mcp-remote` proxy. This enables custom or third-party integrations that follow the MCP specification.

For detailed setup instructions, refer to your client's own MCP documentation or built-in assistant.

---

## Before you start

Ensure your environment meets the necessary requirements to successfully set up the Atlassian Rovo MCP Server. This section outlines the technical prerequisites and key access considerations.

### Prerequisites

Before connecting to the Atlassian Rovo MCP Server, review the setup requirements for your environment:

#### For supported clients

* An **Atlassian Cloud site** with Jira, Compass, and/or Confluence
* Access to **the client of choice**
* A modern browser to complete the OAuth 2.1 authorization flow

#### For IDEs or local clients (Desktop setup)

* An **Atlassian Cloud site** with Jira, Compass, and/or Confluence
* A supported IDE (for example, **Claude desktop, VS Code, or Cursor**) or a custom MCP-compatible client
* **Node.js v18+** installed to run the local MCP proxy (`mcp-remote`)
* A modern browser for completing the OAuth login

---

## Data and security

Security is a core focus of the Atlassian Rovo MCP Server:

* All traffic is encrypted via HTTPS using TLS 1.2 or later.
* OAuth 2.1 ensures secure authentication and access control.
* Data access respects Jira, Compass, and Confluence user permissions.
* If your organization uses IP allowlisting for Atlassian Cloud products, tool calls made through the Atlassian Rovo MCP Server also honor those IP rules.

For a deeper overview of the security model and admin controls, see:

* [Understand Atlassian Rovo MCP Server](https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/)
* [Control Atlassian Rovo MCP Server settings](https://support.atlassian.com/security-and-access-policies/docs/control-atlassian-rovo-mcp-server-settings/)

---

## How it works

### Architecture and communication

1. A supported client connects to the server endpoint:
```
https://mcp.atlassian.com/v1/mcp
```
2. A secure browser-based OAuth 2.1 flow is triggered.
3. Once authorized, the client streams contextual data and receives real-time responses from Jira, Compass, or Confluence.

> [!NOTE]
> While `/sse` as a server endpoint are supported, we recommend updating any custom clients configured to use `/sse` so they now point to `/mcp`.

### Permission management

Access is granted only to data that the user already has permission to view in Atlassian Cloud. All actions respect existing project or space-level roles. OAuth tokens are scoped and session-based.

---

## Example workflows

Once connected, you can perform a variety of useful tasks from within your supported client.

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
* **Bulk create**: "Import components and custom fields from this CSV/JSON"
* **Query**: "What depends on the `api-gateway` service?"

### Combined tasks

* **Link content**: "Link these three Jira tickets to the 'Release Plan' page."
* **Find documentation: "**Fetch the Confluence documentation page linked to this Compass component."

> [!NOTE]
> Actual capabilities vary, depending on your permission level and client platform.

---

## Admin notes: Managing access

If you're an admin preparing your organization to use the Atlassian Rovo MCP Server, review these key considerations. For more detailed admin guidance, see:

* [Understand Atlassian Rovo MCP server](https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-rovo-mcp-server/)
* [Control Atlassian Rovo MCP server settings](https://support.atlassian.com/security-and-access-policies/docs/control-atlassian-rovo-mcp-server-settings/)
* [Manage Atlassian Rovo MCP server](https://support.atlassian.com/security-and-access-policies/docs/manage-atlassian-rovo-mcp-server/)
* [Monitor Atlassian Rovo MCP server activity](https://support.atlassian.com/security-and-access-policies/docs/monitor-atlassian-rovo-mcp-server-activity/)

### Installation and access

* **Not a Marketplace App:**  
The Atlassian Rovo MCP Server is _not_ installed via the Atlassian Marketplace or the **Manage apps** screen. Instead, it is installed automatically the first time a user completes the OAuth 2.1 (3LO) consent flow (just-in-time or "lazy loading" installation).
* **First-time installation requirements:**  
The first user to complete the 3LO consent flow for your site must have access to the Atlassian apps requested by the MCP scopes (for example, Jira and/or Confluence). This ensures the MCP app is registered with the correct permissions for your site.
* **Subsequent user access:**  
After the initial install, users with access to only one Atlassian app (for example, just Jira or just Confluence) can also complete the 3LO flow to access that Atlassian app through MCP.

### Manage, monitor, and revoke access

* **Admin controls:**  
Site and organization admins can manage, review, or revoke the MCP app's access from [Manage your organization's Marketplace and third-party apps](https://support.atlassian.com/security-and-access-policies/docs/manage-your-users-third-party-apps/). The app appears in your site's **Connected apps** list after the first successful 3LO consent.
* **End-user controls:**  
Individual users can revoke their own app authorizations from their profile settings.
* **Domain and IP controls:**  
Use the **Rovo MCP server** settings page in Atlassian Administration to control which external AI tools and domains are allowed to connect. For details, see [Available Atlassian Rovo MCP server domains](https://support.atlassian.com/security-and-access-policies/docs/available-atlassian-rovo-mcp-server-domains/). If your organization uses IP allowlisting for Atlassian Cloud apps, requests made through the Atlassian Rovo MCP Server must originate from an IP address that is allowed by your organization's IP allowlist for the relevant Atlassian app. For configuration details, see [Specify IP addresses for app access](https://support.atlassian.com/security-and-access-policies/docs/specify-ip-addresses-for-product-access/).
* **Audit logging:** To support monitoring and compliance, key actions performed via the Atlassian Rovo MCP Server are logged in your organization's audit log. Admins can review these logs in Atlassian Administration. For more information, see [Monitor Atlassian Rovo MCP server activity](https://support.atlassian.com/security-and-access-policies/docs/monitor-atlassian-rovo-mcp-server-activity/).

### Troubleshooting common issues

* **"Your site admin must authorize this app" error:**  
A site admin must complete the 3LO consent flow before anyone else can use the MCP app. See ["Your site admin must authorize this app"](https://support.atlassian.com/atlassian-cloud/kb/your-site-admin-must-authorize-this-app-error-in-atlassian-cloud-apps/) error in Atlassian Cloud apps for more details.
* **"You don't have permission to connect from this IP address. Please ask your admin for access."**  
This usually indicates that IP allowlisting is enabled and the user's current IP address isn't allowed to access Jira, Confluence, Compass, or Rovo via the Atlassian Rovo MCP Server. Ask your site or organization admin to review the IP allowlist configuration and add the relevant network or VPN IP ranges if appropriate.
* **App not appearing in Connected apps:**  
Ensure the user is using the correct Atlassian account and site, and confirm the app is requesting the correct Atlassian app scopes (for example, Jira scopes). If issues persist, check [Manage your organization's Marketplace and third-party apps](https://support.atlassian.com/security-and-access-policies/docs/manage-your-users-third-party-apps/) or contact Atlassian Support. Also verify the user's Jira, Confluence, or Compass permissions in Atlassian Administration.

## Security
Model Context Protocol (MCP) lets AI agents connect to tools and Atlassian data using your account’s permissions, which creates powerful workflows but also structural risks. Any MCP client or server you enable (e.g., IDE plugins, desktop apps, hosted MCP servers, “one-click” integrations) can cause an AI agent to perform actions on your behalf.

Large Language models (LLMs) are vulnerable to [prompt injection](https://owasp.org/www-community/attacks/PromptInjection) and related attacks (such as [indirect prompt injection](https://owasp.org/www-community/attacks/PromptInjection) and [tool poisoning](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)). These attacks can instruct the agent to exfiltrate data or make unintended changes without explicit requests.

To reduce risk, only use trusted MCP clients and servers, carefully review which tools and data each agent can access, and apply least privilege (scoped tokens, minimal project/workspace access). For any high‑impact or destructive action, require human confirmation and monitor audit logs for unusual activity. We strongly recommend reviewing Atlassian’s guidance on MCP risks at [MCP Clients: Understanding the potential security risks](https://www.atlassian.com/blog/artificial-intelligence/mcp-risk-awareness)

## Support and feedback
Your feedback plays a crucial role in shaping the Atlassian Rovo MCP Server. If you encounter bugs, limitations, or have suggestions:
- Visit the [Atlassian Support Portal](https://support.atlassian.com/) to report issues.
- Share your experiences and feature requests on the [Atlassian Community](https://community.atlassian.com/).

## Disclaimer

MCP clients can perform actions in Jira, Confluence, and Compass with your existing permissions. Use least privilege, review high‑impact changes before confirming, and monitor audit logs for unusual activity.

Learn more: MCP Clients - (Understanding the potential security risks)[https://www.atlassian.com/blog/artificial-intelligence/mcp-risk-awareness]
