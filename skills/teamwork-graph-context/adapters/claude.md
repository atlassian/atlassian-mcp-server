# Claude live-artifact adapter

Use this adapter only when the current host is Claude and connector-enabled artifacts are available. Read it with "Live artifact" in `../SKILL.md` and the checks in `../live-artifacts.md`, before building one. It condenses Claude's runtime contract for artifacts that call connectors (contract version 0.2.85, October 2026) and adds what's specific to these skills. If the session has Claude's own artifact capabilities skill or its type definitions, they're newer and authoritative: follow them where this file differs.

## 1. Decide what's live

- **Live sections** come from reads with fixed rules: the list in the skill's "When live" section.
- **Snapshot sections** are everything else, built at build time as in a static artifact.
- Every live section also has a snapshot or empty-state rendering, used whenever the live call can't run.

## 2. Declare the connectors when publishing

The page declares, at publish time, every connector and tool it will call:

```json
"capabilities": { "mcp": { "servers": [
  { "server": "Google Calendar", "tools": ["list_events"] },
  { "server": "Atlassian Rovo", "tools": ["searchJiraIssuesUsingJql", "getGraphObject", "executeRead"] }
] } }
```

- **`server` is the connector's display name** in claude.ai, never an ID. In the session, the tool `mcp__Google_Calendar__list_events` belongs to "Google Calendar". Copy the Atlassian connector's name exactly as the session shows it.
- **`tools` are the tool names the connector exposes,** with every tool the page calls listed. An empty list is refused; it never means "all".
- **Only claude.ai connectors work for every viewer.** A desktop extension or local server (`host:<name>`) answers only for the artifact's owner, inside the Claude desktop app, so always render a fallback for it.
- **The Atlassian connector is the Rovo MCP server, version 2, added to Claude as a web connector.** Its display name is whatever the account gave it ("Atlassian Rovo v2" in one account), so copy it exactly from the session, and expect a viewer whose connector has another name to get `server_not_connected`.
- **Primary tools are declared by name:** `searchJiraIssuesUsingJql`, `getJiraIssue`, `getGraphObject`, `getGraphContext`, `getWorkActivity`, `getConfluenceContent`, `search`, `getLoomVideo`, `getPeopleInfo` and so on. `getGraphObject` on a project ARI returns its state (`atlassianProjectState`), target date, owner and last update, which is often all a live section needs.
- **Operations found through `discover` run through `executeRead`** (or `executeWrite`), with the operation's `name`, `cloudId` and `inputs`. Declaring `executeRead` lets the page run any read operation, and `executeWrite` any write, so declare them only when the page needs one, and call only the operation names the building session found. Never declare `executeDestructive`.
- **Check a result's shape** with one safe read in the building session before relying on it.
- **Declare the minimum.** Any `mcp` declaration bars public sharing.
- **Argument names** come from the tool's input schema in the session. Learn the result shape from one read, and don't bake that read's data into the page as sample data.
- **Republishing:** leaving `capabilities` out keeps the stored set, `{}` clears it, and a new object replaces it.

## 3. Calling from the page

- Get the namespace with `const mcp = await claude.use("mcp")`. `null` means this view can't make live calls (not granted, not served, switched off, or not opened in Claude), so render the static experience. Render first, then light up live sections when the promise resolves. Never read `window.claude.mcp` directly.
- **Display uses `watchTool(server, tool, input, handler, options)`.** It replays the last cached result at once, refetches when it's stale, and delivers every newer result to the handler. Use one watch per section, not per item (64 watches per view at most).
- **Actions use `callTool(server, tool, input, options)`,** once per click.
- Read `result.payload`, the tool's JSON answer. Drive "Live, updated 9:02 AM" from `result.cache.storedAt` when present. A result without `cache` ran fresh, so stamp it when it arrives.
- **Rovo credits.** Tools whose description says they can use Rovo credits (`search`, graph context, work activity, people tools) never go in a watch or a poll. Call them only from a click. Plain reads such as JQL and the calendar can be watched. If you poll at all (`refetchInterval`), use 5 minutes or more: the runtime pauses polling while the page is hidden.
- **Refresh button:** call `invalidate(server, tool)` for watched reads, so the watches refetch, and `callTool(..., {cache: {refresh: true}})` for click-only reads.
- Inputs are plain JSON, so pass dates as ISO strings.
- `describeTool(server, tool)` returns a tool's schemas once the viewer has allowed that connector. Treat any rejection as "no schema".

## 4. Consent

- Viewers are asked per connector, on the page's first call to it. `claude.use("permissions")` reads and requests consent with scoped names, `"mcp:<server>"`.
- `state("mcp:Google Calendar")` never prompts. "prompt" means go ahead (the first call asks), so never gate a section on "granted". Catch rejections as "unavailable".
- `request(["mcp:<server>"])` asks once, from a click in the section that needs it. A "no" stays "denied" for that page load, so don't ask again.
- `manage()` opens the platform's Permissions panel, the way out of a denial. Call it only from a button, never on load.

## 5. Errors, section by section

Branch on `error.code`, never on message text. Contain each failure to its own section and keep the snapshot visible. Never collapse every failure into one generic banner: most codes have their own fix.

| Code | The section shows |
| --- | --- |
| `needs_reauth` | "Reconnect [server] in claude.ai Settings, then Connectors." Don't retry. |
| `server_not_connected`, `server_not_found` | "Add [server] in claude.ai Settings, then Connectors." For a `host:` server, the no-host fallback. Don't retry. |
| `selection_required` | "Choose which [server] connector to use." Same fallback as not connected. |
| `not_in_manifest`, `blocked_by_policy` | "[server] isn't allowed for this page." Don't ask again in a loop. |
| `approval_required` | "Needs your approval", with a button that makes the same call once with `callTool`. |
| `server_unavailable`, `rate_limited`, and an `upstream_error` marked `retryable` | Keep the last data, with "Couldn't refresh just now". Retry once after a short random delay, honouring `retryAfterMs`, and only for reads. |
| `tool_error` | The tool's own message, in that section. |
| `not_granted`, `capability_disabled`, `capability_removed` | The static experience. |
| Anything else | A short line naming the server, plus the snapshot. |

- In a watch, authorisation errors (`needs_reauth`, `server_not_connected`, `blocked_by_policy`, `approval_required`) withdraw the live data. Show the snapshot instead, labelled as the snapshot.
- If every section fails with the same code, show one page-level message with a reload button instead.

## 6. Writes

- Make only the writes the skill's "When live" section lists. Show exactly what will change, wait for a confirm click, then call `callTool` once. Never pass an `AbortSignal` to a write.
- `server_unavailable`, `upstream_error` and `cancelled` on a write leave the outcome unknown: the tool may have run. Re-read the object before offering the action again, and never retry on your own.
- After a write, `invalidate` the reads it affects so their sections refetch.
- Tool annotations (`readOnlyHint`, `destructiveHint`) are the connector's own claims. Use them to shape the UI, not as proof.
- Tools that need approval for every action can't be used from a page. Use a link or a copy-command button for those.

## 7. Sensitive content in page code

Page code can't make the judgement "Sensitive content" asks for, so live results pass only through rules that can be written down:

- Ask the calendar for `eventType: ["DEFAULT"]`. Drop declined events and events titled as personal, leave, travel or wellbeing. Never render attendees' comments.
- Drop Slack direct and group messages (`/archives/D` URLs, `mpdm-` channels).
- Show the viewer's own items (`currentUser()` in JQL) unless the skill's job is a shared view.
- Open-ended search stays at build time. If the page uses the `sample` capability to have Claude rank or summarise live results, put "Sensitive content" in that prompt word for word, and still apply the rules above.

## 8. One live section, sketched

```js
const section = document.querySelector("#commitments");
renderSnapshot(section);                        // the build-time content, labelled with its time

claude.use("mcp").then((mcp) => {
  if (!mcp) return;                             // static experience, nothing more to do
  const jql = 'assignee = currentUser() AND statusCategory != Done AND duedate <= endOfDay("+1d")';
  mcp.watchTool("Atlassian Rovo", "searchJiraIssuesUsingJql",       // the connector's display name
    { cloudId: SITE, jql, fields: ["summary", "status", "duedate"], maxResults: 25 },
    (ev) => {
      if (ev.type === "data") return renderLive(section, ev.result.payload, ev.result.cache?.storedAt);
      showError(section, ev.error);             // branches on ev.error.code, as in section 5
    });
});
```

`SITE` is the cloud ID, written into the page at build time. The connector's name and the payload's shape come from the building session, as section 2 describes.

## Host capabilities and limits

- **They run with the viewer's access.** Whoever opens the artifact uses their own connectors, and a part they can't access shows an error. Write every live call from the viewer's point of view (`scope: me`, `currentUser()`). Anything baked in at build time is the author's data, and everyone who opens the artifact sees it, just as with a shared static page. So only share a live artifact whose build-time content you'd share as a static page, and label which parts are the snapshot and which are live.
- **Viewers approve each connector.** The page declares every connector and tool it calls when it's published, and each viewer is asked per connector on the first call. Viewers can turn tools off. Declare only the tools the skill's "When live" section lists. Make every section work without its tool: keep the snapshot, and show the fix for that error code.
- **Only claude.ai connectors work for every viewer.** A desktop extension or local server answers only for the artifact's owner, in the Claude desktop app. Connectors are named by their display name, which can differ between viewers, so a viewer whose Atlassian connector has another name sees the "add the connector" fix.
- **No per-action approval.** Connector tools that need approval for each action aren't available to artifacts. Don't build a live action on one; use a link or a copy-command button instead.
- **Sharing stays inside the organisation.** Artifacts that use connectors can't be shared with "Anyone with the link".
- **Storage is text only, up to 20 MB, and either personal or shared.** Use personal storage for the viewer's own state, such as items ticked off or the last refresh time. Use shared storage only when the skill's job is shared, and never put anything "Sensitive content" covers there.
- **They can call Claude,** on each viewer's own plan.


A live artifact lives in Claude's Artifacts view. Publishing a static copy to Atlassian Artifacts is a separate action and needs the user's request and confirmed service availability.
