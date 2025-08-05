<p align="center">
  <img src="images/atlassian_logo_brand_RGB.svg">
</p>

>[!NOTE]
> This feature is currently in public beta, which means: 
> - Core functionality is available, but some advanced features are still under development.
> - The experience may vary across different clients—Claude, for instance, works best on the Team or Enterprise plan.
> - We’re actively gathering feedback to improve the product before its general availability (GA) release.  
> 
> For more information, read our blog post - [Introducing Atlassian's Remote Model Context Protocol (MCP) Server - Work Life by Atlassian](https://www.atlassian.com/blog/announcements/remote-mcp-server)

# Atlassian MCP Server
The Model Context Protocol (MCP) is a new, standardized protocol designed by Anthropic to manage context between large language models (LLMs) and external systems. This repository offers an MCP Server for Atlassian.

The Remote MCP Server is a cloud-based bridge between your Atlassian Cloud site and compatible external tools. Once configured, it enables those tools to interact with Jira and Confluence data in real-time. This functionality is powered by secure **OAuth 2.1 authorization**, which ensures all actions respect the user’s existing access controls.

The Remote MCP Server helps bring Atlassian data into your existing workflows:
- **Summarize and search** Jira and Confluence content without switching tools.
- **Create and update** issues or pages based on natural language commands.
- **Bulk process tasks** like generating tickets from meeting notes or specs.
It’s designed to support developers, content creators, and project managers working within IDEs or AI platforms.

## Before you start
Ensure your environment meets the necessary requirements to successfully set up the Remote MCP Server. This section outlines the technical prerequisites, access considerations, and security details.

### Prerequisites
Before connecting to the Remote MCP Server, review the setup requirements for your environment:

#### Cloud-based Setup
- An Atlassian Cloud site with Jira and/or Confluence
- Access to an AI Client (Claude for Teams for example)
- A modern browser to complete the OAuth 2.0 authorization flow

#### Desktop Setup for Local Clients
- An Atlassian Cloud site with Jira and/or Confluence
- A supported IDE (for example, Claude desktop, VS Code, or Cursor) or a custom MCP-compatible client
- Node.js v18+ installed to run the local MCP proxy (mcp-remote). Download from [nodejs.org](https://nodejs.org/en)
- A modern browser for completing the OAuth login

### Beta access and limits
The beta is open to all Atlassian Cloud customers. No special sign-up is required. However, usage is subject to rate limits:
- **Standard plan**: Moderate usage thresholds.
- **Premium/Enterprise plans**: Higher usage quotas (1,000 requests/hour plus per-user limits).

### Data and security
Security is a core focus of the Remote MCP Server:
1. All traffic is encrypted via HTTPS using TLS 1.2 or later.
2. OAuth 2.0 ensures secure authentication and access control.
3. Data access respects Jira and Confluence user permissions.

## How It Works
### Architecture and Communication
1. A supported client connects to the server endpoint:
```
https://mcp.atlassian.com/v1/sse
```
2. A secure browser-based OAuth 2.0 flow is triggered.
3. Once authorized, the client streams contextual data and receives real-time responses from Jira or Confluence.

### Permission Management
Access is granted only to data that the user already has permission to view in Atlassian Cloud. All actions respect existing project or space-level roles. OAuth tokens are scoped and session-based.
Once connected, you can perform a variety of useful tasks from within your supported client.

### Example Workflows
#### Jira workflows
Use these examples to understand how to interact with Jira:

- **Search**: “Find all open bugs in Project Alpha.”
- **Create/update**: “Create a story titled ‘Redesign onboarding’.”
- **Bulk create**: “Make five Jira issues from these notes.”

#### Confluence workflows
Access and manage documentation content directly:

- **Summarize**: “Summarize the Q2 planning page.”
- **Create**: “Create a page titled ‘Team Goals Q3’.”
- **Navigate**: “What spaces do I have access to?”

#### Combined Tasks
Integrate actions across Jira and Confluence:

- **Link content**: “Link these three Jira tickets to the ‘Release Plan’ page.”

>[!Note]
> Actual capabilities vary depending on your permission level and client platform.

### Managing access
If you're an admin preparing your team to use the Remote MCP Server, keep the following considerations in mind:
- Ensure users have product access to Jira and/or Confluence via Atlassian Admin.
- Authorization tokens are tied to the user’s current product permissions—check these if data isn’t accessible.
- App authorizations can be revoked by end users through their profile settings or by admins in the [Connect apps section of Atlassian Admin](https://support.atlassian.com/security-and-access-policies/docs/manage-your-users-third-party-apps/) for site-level control.
- Consider establishing usage guidelines or policies for teams leveraging AI-driven content generation.
- Reach out to your Atlassian account representative for advice on OAuth scope control and long-term support planning.

## Setting up Atlassian MCP Server
### Cloud-based Clients
Depending on the tool you're using, the setup process may vary. We recommend you navigate to the exact instructions for connecting to an MCP client through the tool's documentation. Here is an example for [setting up Claude.ai](https://support.atlassian.com/rovo/docs/setting-up-claude-ai/)

### Desktop/Local Clients
>[!NOTE]
> If you’re using VSCode, you can also install it directly by browsing their [curated list of MCP servers](https://code.visualstudio.com/mcp).

1. Open your terminal
2. Run the following command to start the proxy and begin authentication:
```bash
npx -y mcp-remote https://mcp.atlassian.com/v1/sse
```
>[!NOTE]
> If this command doesn't work due to a version-related issue, try specifying an older version of mcp-remote. The example below uses version 0.1.13, but you may use another version if needed:
```bash
npx -y mcp-remote@0.1.13 https://mcp.atlassian.com/v1/sse
```
3. A browser window will open. Log in using your Atlassian credentials and approve the required permissions.
4. Once authorized, return to your IDE and configure the MCP server settings by adding the following atlassian entry to the server configuration file (e.g. `mcp.json`, `mcp_config.json`):
```json
"mcp.servers": {
  "atlassian": {
    "command": "npx",
    "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"]
  }
}
```
4. Save and reload your client's MCP extension or plugin.

## Support and feedback
Your feedback plays a crucial role in shaping the Remote MCP Server. If you encounter bugs, limitations, or have suggestions:
- Visit the [Atlassian Support Portal](https://customerfeedback.atlassian.net/servicedesk/customer/portal/1701/group/1762/create/11360) to report issues.
- Share your experiences and feature requests on the [Atlassian Community](https://community.atlassian.com/).
- Enterprise customers can contact their Atlassian Customer Success Manager for advanced support and roadmap discussions.
- We’re excited to collaborate with you to improve this capability before its general availability.

## Guides
- [Introducing Atlassian's MCP server](https://www.atlassian.com/blog/announcements/remote-mcp-server)
- [Setting up Claude.ai](https://support.atlassian.com/rovo/docs/setting-up-claude-ai/)
- [Setting up IDEs (like VS Code or Cursor)](https://support.atlassian.com/rovo/docs/setting-up-ides/)
- [Understanding Authentication & OAuth](https://support.atlassian.com/rovo/docs/authentication-and-authorization/)
- [Troubleshooting and verifying your setup](https://support.atlassian.com/rovo/docs/troubleshooting-and-verifying-your-setup/)

