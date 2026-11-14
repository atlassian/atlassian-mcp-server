# Building a live artifact

Read this with "Live artifact" in `SKILL.md`. These checks apply to any host; runtime APIs, connector declarations, consent, caching, errors, storage and sharing rules come from that host's own adapter.

## Choose a supported runtime

- Confirm the actual host and that it supports connector calls from page code. Agent-side MCP tools alone do not establish that capability.
- Load only the matching adapter from `adapters/`. The included [runtime adapter](adapters/claude.md) identifies the host it supports. Do not apply it to another host.
- Prefer the host's current runtime documentation or capability skill over a stored adapter. If no matching adapter or documented contract is available, do not invent one. Keep the conversational answer or requested static HTML report and state the live limitation.
- For an answer-first skill, build a live version only after an explicit request for a report or live export. A live capability does not override that skill's delivery choice.

## Preserve the output contract

- Refresh only the sections the calling skill lists under "When live"; keep the rest as the build-time snapshot.
- Render a labelled snapshot before any live call, and retain it if the runtime or connector is unavailable.
- Declare only the connectors and tools the page needs, using the actual host's syntax and identifiers. Verify schemas and result shapes from the session rather than translating another adapter's examples.
- Confirm the viewer access and consent model, recovery actions, sharing limits and any storage requirements against the matching adapter. Never bypass a denied permission.
- Use fixed reads and rule-based sensitive-content filters only. Drop private messages, personal calendar events and other excluded content as `SKILL.md` requires. Open-ended search and sensitive-content judgement stay at build time. If the host can call a model to rank or summarise live results, include the "Sensitive content" rules word for word and keep the same rule-based filters.
- Never watch or poll tools that use Rovo credits. Refreshes stay within the calling skill's budget.
- Make only the writes listed by the calling skill. Preview each exact change, wait for a confirm click, call once, and re-read after an ambiguous error before offering it again.
- Publishing a static copy to Atlassian Artifacts follows the separate availability and confirmation checks in "Publishing". A live artifact does not grant permission to publish or share another copy.
