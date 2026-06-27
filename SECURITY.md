# Security policy

Thanks for helping keep the Atlassian Rovo MCP Server and the people who use it safe.

## Reporting a vulnerability

**Please don't open a public GitHub issue for a security problem.** Public issues are visible to everyone and can put users at risk before a fix is ready.

Report it privately to the Atlassian security team instead. If what you found matches Atlassian's [definition of a vulnerability](https://www.atlassian.com/trust/security/report-a-vulnerability#definition-of-vulnerability), submit it through one of the methods on the [Report a vulnerability](https://www.atlassian.com/trust/security/report-a-vulnerability) page. That gets it to the people who can triage and fix it, and eligible reports may qualify for Atlassian's bug bounty program.

A good report usually includes:

- What you found, and why you think it's a security issue
- Steps to reproduce, or a proof of concept
- The affected component (a file in this repo, a client manifest, or the hosted endpoint)
- The impact you think it could have

## What this repository covers

This repo holds the public pieces of the Atlassian Rovo MCP Server: the documentation, the client manifests (`.mcp.json` and the Claude, Cursor, and Gemini plugin manifests), the MCP registry entry (`server.json`), and the [skills](skills/).

The server itself is a hosted service at `mcp.atlassian.com`. Issues in the hosted service, in authentication, or in any Atlassian product go through the same [Report a vulnerability](https://www.atlassian.com/trust/security/report-a-vulnerability) process above. Atlassian maintains and updates the hosted server, so there's nothing for you to patch on your end. Just connect to the current endpoint documented in the [README](README.md).

## Using the MCP server safely

MCP lets an AI agent act in Jira, Confluence, and other products with your permissions. That's useful, and it carries real risk. Language models can be tricked by [prompt injection](https://owasp.org/www-community/attacks/PromptInjection) and [tool poisoning](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks), where hidden instructions push an agent to leak data or make changes you never asked for.

A few habits that lower the risk:

- Connect only to MCP clients and servers you trust.
- Use least privilege: scoped tokens and the smallest project or space access you need.
- Ask for human confirmation before any high-impact or destructive action.
- Watch your audit logs for anything that looks off.

For the wider picture, see [MCP clients: understanding the potential security risks](https://www.atlassian.com/blog/artificial-intelligence/mcp-risk-awareness) and [Atlassian's security practices](https://www.atlassian.com/trust/security/security-practices).

## Coordinated disclosure

Please give the security team a fair chance to investigate and ship a fix before you share details publicly. We're grateful to the researchers who report responsibly and work with us on timing.
