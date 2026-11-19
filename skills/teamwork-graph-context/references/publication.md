# publication

Follow the tool-access and coverage rules in the shared skill entrypoint. Examples name operations; use direct calls when available, otherwise the discovered runner and schema.

## Publishing

Follow the calling skill's delivery mode. A skill that explicitly selects "Answer-first delivery" uses the flow below. Other skills keep their existing artifact flow: build the static artifact unless a live one is available and the skill's "When live" section says what it adds. Load `atlassian-design` only when building a report or artifact.

### Answer-first delivery (only when the calling skill selects it)

1. **Give the result in the conversation first.** Use the calling skill's assessment, ranking, row limits and content requirements. Cite evidence with ordinary Markdown links, retain Recorded, Proposed and Found by search labels as plain text where required, and include coverage, dates, caps and gaps in a Sources and limitations section. Do not load design guidance, write report data, run a renderer or create an artifact for this initial answer.
2. **Offer the existing HTML report as an optional export.** Ask whether the user wants it and wait for their answer. An ordinary invocation of the skill is not a request for a file. An explicit request for an HTML report, file export or publication already authorises the corresponding report build; do not ask again. Reuse the findings already gathered, and keep all evidence labels and limitations. If new evidence is needed, stay within the skill's budgets and explain what changed.
3. **Check Atlassian Artifacts availability before offering publication.** Reuse the selected site's `products` list from `getAccessibleAtlassianResources`; do not choose another site silently. Treat omitted `products` metadata as unknown. Confirm that `createArtifactsUpload` and `publishArtifact` are exposed or discoverable and permitted on the selected site, without creating an upload as a test. Skip publication tools and offers when unavailable. If availability cannot be confirmed, say so when relevant and hand over the report file.
4. **Keep export and publication separate.** Agreement to export is not agreement to publish. When the service is confirmed available, offer a private, read-only Atlassian Artifact with the calling skill's name and description. Publish only on an explicit request, using the static publishing steps below. If the user already requested export and publication, complete both without asking again. An unavailable publishing service never blocks the answer or local HTML export.
5. **Keep other writes independent.** Skipping export does not authorise or cancel other writes the calling skill offers. Follow its conditions and confirmations. Share a published artifact only on request, with the people the user approves.

### Static artifact (the default)

Don't publish by default. Publishing is a write, so hand over the file and offer to publish a private, read-only copy as an Atlassian Artifact. Publish only when the user says yes, or has already asked for it in this request.

1. **Build one self-contained HTML file.** Inline all CSS, JavaScript and images, and use no external files. Don't use `localStorage`, `sessionStorage` or IndexedDB, which the artifact viewer may block. Inline only the icons you use, and don't embed raw tool output, so the file stays small.
2. **Hand it over and offer to publish.** Give the user the file, and offer a private, read-only Atlassian Artifact: nobody else can open it until it's shared, and people it's shared with can view it but not edit it. Say what the name and description would be. If they'd rather have a Confluence page, confirm first and create it with `createConfluenceContent`.

When the user agrees:

3. **Measure it exactly.** Byte length: `wc -c < file.html`. Checksum, as base64 SHA-256, not hex: `openssl dgst -sha256 -binary file.html | openssl base64 -A`.
4. **Upload.** Run `createArtifactsUpload` with `length` and `checksum`, then send the exact bytes to the pre-signed URL as its instructions say.
5. **Publish.** Run `publishArtifact` with the `contentId` from step 4, a `name`, `contentType: text/html`, and a `description` that summarises what the artifact actually contains (up to 1000 characters, used for search). To update an artifact you published earlier, pass its `id`. Each publish is a new version that can't be changed.
6. **Share only on request.** `publishArtifact` returns a link that grants nobody access. Offer to share it with the people it's for (attendees, a leader, a team) and, if the user agrees, call `shareArtifact` with `ari:cloud:identity::user/<accountId>` or team ARIs. It only grants view access to named people, never to everyone with the link.

If the client can't upload over HTTP, hand over the HTML file and say why it wasn't published.

A static artifact can't call tools, so it shows what was true when it was built. To keep one fresh, run the skill again and publish with the same `id`, for example from a scheduled task the user set up to publish. Actions are links, or buttons that copy a command such as `/meeting-prep [title]`.

### Live artifact (when the host supports connector access)

A live artifact runs inside a host that explicitly supports tool calls from page code. Having an MCP connection in the agent conversation is not enough. Build one only when the host's documented runtime and permissions are available, the skill has a "When live" section, and the user requests it or that skill explicitly makes it the default. A skill using answer-first delivery still requires a report or live-export request first.

Read `../live-artifacts.md` before building one, then load only the adapter for the actual host. Use the host's current documentation when it differs from an included adapter. Do not rename one host's APIs, capability declarations, connector identifiers or error codes to make them look universal. If the host or its capabilities cannot be confirmed, retain the conversational answer or requested static report and explain why live refresh is unavailable.

- **Render the snapshot first.** Label build-time and live data separately, including their times. A missing connector or denied permission must leave the snapshot usable.
- **Respect viewer access.** Do not assume the host uses the author's credentials or the viewer's. Confirm the host's access model in its adapter before building or sharing, and use the viewer's own access for live sections. Build-time data is visible to everyone who can open the artifact.
- **Keep calls narrow and rule-based.** Refresh only the objects and fixed queries the skill lists. Keep open-ended search and sensitive-content judgement at build time. Tools that use Rovo credits run only from a click, never a watch or poll. Each refresh stays inside the skill's budget.
- **Confirm writes.** Show the exact change and wait for a confirm click. A failed write may have run, so re-read before offering it again. If a host cannot support the required consent or action, keep the offer in the conversation.
- **Use host-specific recovery.** Read actual error codes and connector setup instructions from the matching adapter. Keep failures in their own sections and retain a clearly labelled snapshot.
- **Keep the same source labels and design rules.** Show apps actually used, Found by search labels and coverage gaps. The host's actual sharing, storage and permission limits come from its adapter.

A live artifact belongs to its host. Publishing an HTML snapshot to Atlassian Artifacts is a separate, static export, offered only when that service is available and the user requests publication.
