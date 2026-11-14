---
name: "how-it-works"
description: "Explain how a product behaviour works in plain language from the code that decides it. Searches connected Bitbucket and GitHub code, checks Confluence, Jira, chat and docs, and finds ownership from repository metadata and Compass. Answers in the conversation first with a short answer, a code-linked trace, settings and unknowns, documentation disagreements and owners; adds an account checklist and proposed reply for a customer question or ticket. Offers the existing HTML report on request and publication only when Atlassian Artifacts is available and requested. Use when support, customer success, product or docs asks how something works, why the product behaves that way, what happens when, or /how-it-works. For an expert, use whos-the-expert. For an active incident, use incident-brief."
---

# How it works

Answer a question in the conversation about how the product behaves ("Which people does the user picker suggest first?", "What happens to a trial site's data when the trial ends?") for someone who doesn't read code: a support engineer working a ticket, a customer success manager, a product manager or a docs writer. In a few minutes they get a plain answer, the behaviour step by step, what can change it, whether the docs are right, and who to ask if they need more.

Today that question goes into an engineering channel and waits. The docs may be out of date, and the person who knows may be busy. The value of this skill is the judgement a code search results page can't make. It reads the code that decides the behaviour and explains it in the product's words. It keeps what the code shows apart from what it can't show: a service whose code isn't indexed, whether a feature flag is on, a customer's own settings. And it checks the docs and chat against the code, so a wrong answer that keeps getting repeated gets caught.

Load the `teamwork-graph-context` skill first and follow it for gathering context, labelling sources, keeping sensitive content out and optional publishing. This file adds what's specific to explaining behaviour from code.

This skill selects "Answer-first delivery" in `teamwork-graph-context`: gather and assess, answer in the conversation, then ask whether the user wants an HTML report. Do not write report data, run a renderer or create an artifact unless the user requests an export, HTML report or publication. Use the existing report layout only for that optional export. Offer Atlassian Artifacts publication only after confirming availability; exporting does not authorise publishing.

## What this skill will and won't do

- **It explains what the code it read does.** Every step of the answer links to the lines it came from. It never fills a gap with how such things usually work, and it never says "probably".
- **It can't see a running system.** Code shows the rules, not their inputs. Whether a flag is on for a site, how a customer has configured something, and what data an account holds are outside it. For "why did this happen to this customer", answer the general rule, and list what someone would need to check on the account. Never name a cause for one customer's case.
- **It doesn't review or change code.** No bugs, quality judgements or fixes. If the code looks wrong, say only what it does, and suggest the owning team.
- **Security controls get explained, not worked around.** For a permission or access check, say what it allows and blocks. If the question is how to get around a permission, licence or security check, say what the check is and who owns it, and stop there.

## Sensitive content in code

These rules add to "Sensitive content" in `teamwork-graph-context`, and apply to the artifact, excerpts, your reply and any log.

- **Never reproduce secrets** found in code or config: keys, tokens, passwords, private keys, connection strings, signed URLs. Cut them with an ellipsis in any excerpt. Don't say what kind of secret was there.
- **Never reproduce internal endpoints** (internal hostnames, IP addresses, admin URLs) in a suggested customer reply. Describe them as "the user search service", not by address.
- **Test fixtures and sample data** can hold real-looking names, emails, account IDs or customer names. Never quote them.
- **Support chat** about the behaviour often carries customer names, site and cloud IDs, account IDs and links to support tickets. Never copy them. Refer to "a customer on Jira Cloud" and count the threads instead.
- **Same access only.** Code search returns only what the user can see. Never try to reach a repository it doesn't return.

## Connectors

- **Needed:** code search with at least one connected Bitbucket or GitHub source. Check that `code-search` is in the site's `products` list (see "Atlassian apps on the site" in `teamwork-graph-context`). If it isn't, say so before building: this skill can't answer without code. Offer `/whos-the-expert` to find who to ask instead.
- **Helpful, from Atlassian:** Confluence, for docs, runbooks and support articles to check against the code. Jira, for the ticket that raised the question and the work that changed the behaviour. Compass, for the component that owns the repository. Teams, to resolve the owning team. Bitbucket, for merged pull requests that changed the behaviour.
- **Helpful, from other tools:** Slack or Teams, where the question has been asked and answered before. GitHub, for pull requests and issues. Google Drive or SharePoint, for design docs. A public docs connector, for what customers are told.
- **Vendor connectors,** as `teamwork-graph-context` describes: GitHub, to read a pull request's body when the graph returns it empty (`raw: {}`). Slack, to read an answer in a thread when only the question shows in the snippet.

## Budget

Unless the user asks for a deeper pass, stay within these, and say in the footer if one was reached:

| Tool | Cap | Where |
| --- | --- | --- |
| `searchCode` | 9 | Up to 3 in Step 2: 2 initial searches and 1 reserved retry or follow-up. Up to 3 in Step 3 to follow an identifier, and up to 3 in Step 3 to pin line numbers |
| `getCodeFile` | 8 files | Step 3, including a manifest and a changelog |
| `scanCodeRepo` | 1 | Step 3, the home directory |
| `search` | 4 | 3 in Step 5, 1 in Step 6 for the Compass component |
| Product reads | 5 objects | The ticket in Step 1, up to 3 docs in Step 5 (`getConfluenceContent` or `getGraphObject`, each doc counts), 1 pull request list in Step 4 |
| `getGraphContext` | 1 | Step 6, the Compass component |
| `getTeam` or `searchTeams` | 1 | Step 6 |

`searchCode`, `getCodeFile` and `scanCodeRepo` are reached through `discover` and run with `executeRead`. `search`, `getGraphContext` and `searchTeams` can use Rovo credits. A typical run makes 20 to 30 calls. Send calls that don't depend on each other together, as "Fetch in parallel" in `teamwork-graph-context` describes: the code searches in Step 2, the file reads in Step 3, and the sweep in Step 5 alongside Step 3.

## Step 1: Pin down the question

1. Call `getAccessibleAtlassianResources` once for the `cloudId` and the site's `products` list, and check for `code-search`.
2. **If the user gave a ticket** (a Jira or Jira Service Management key or URL), read it with `getJiraIssue` (default view), and take the question from its summary and description. **If they gave a Slack or Teams thread,** take the question from what they pasted or from the search snippet. Keep the exact text of any error message or label the customer saw. Drop customer names, IDs and links as "Sensitive content in code" says.
3. Restate the question as **one behaviour**: a trigger and the outcome asked about ("When someone types a name in the user picker, which people are suggested, and in what order?"). Write down:
   - the product and feature, in the user's words, also as "[feature] in [product]" in sentence case for the header in Step 8 ("Invoice search in Ledger")
   - the **trigger** and the **outcome**, with the trigger also as a short phrase for the map in Step 8 ("Someone typing in the user picker")
   - **code hooks:** the exact strings a user sees (an error message, a button label, a setting name), which often appear word for word in code or translation files, plus 2 or 3 likely identifiers ("UserPicker", "suggest", "idle timeout")
4. **Too broad** ("How does Jira search work?"): ask for one behaviour, offering 2 or 3 that fit. If the user can't be asked, pick the one closest to their words and say so in the short answer's first sentence. **Two behaviours in one question:** if the same code is likely to decide both (who is suggested, and in what order), treat them as one behaviour with two outcomes. Otherwise answer the first, and list the second under "Not answered here".
5. **About one customer:** a question that names a customer, comes from a ticket, or reports what a customer saw ("A customer says…", "Why was this customer's user logged out?"). Answer the general rule, and add "What to check on the account" and the suggested reply in Step 7. A question with no customer in it gets neither.

## Step 2: Find where the behaviour lives

Send at most 2 initial `searchCode` calls together, each with `maxResults: 10`, and reserve the third Step 2 slot until their results have been filtered:

- `mode: hybrid` with the behaviour in plain words ("which users the user picker suggests first").
- `mode: lexical` with the most distinctive user-visible string, if there is one ("No matches found"); otherwise `mode: hybrid` with the feature plus the mechanism in code words ("user picker suggestions sort").

If the user named a repository, organisation or workspace, pass it as `repo` or `namespace` on every call.

**Drop noise before anything else.** On real data, unfiltered searches return mostly copies of open-source code and files that aren't code. Drop a result when:

- its workspace or namespace is a forks or mirror-of-open-source organisation (its name contains `fork`), or the repository is a copy of a well-known open-source project (tomcat, hibernate, moby), unless the question is about that project
- its path is vendored, built or generated: `vendor/`, `node_modules/`, `third_party/`, `dist/`, `build/`, `*.min.js`, lockfiles, `*.generated.*`
- it isn't code or config: dictionaries, word lists, `CHANGES` or release logs (Step 4 reads changelogs for history, not behaviour), licence files
- it's test data: `test-data/`, `fixtures/`, `__fixtures__/`, recorded API responses
- it's from a different product that uses the same words (an IDE extension's own user picker when the question is about the web app), unless the question is about that product

Keep tests (`*.test.*`, `*.spec.*`, `__tests__/`): their names often state the rule in plain words. Keep examples and docs inside the repository too, but as supporting, not as the behaviour itself. Count what you dropped for the footer, by reason ("18 results from forks and vendored code, and 6 from other products, left out").

**If more than half the first round was noise, or nothing was kept,** use the reserved third slot for one `searchCode` with `mode: hybrid`, the behaviour in code words, and `namespace` set to the kept workspaces, joined with `|`. **If nothing was kept,** set `namespace` to the organisation's own workspaces seen in any result instead: the non-fork workspace beside a forks one (`acme` beside `acme-forks`), or any workspace that isn't a fork. If the kept results cluster in one repository of a large shared workspace, add that repository as `repo` too. Run this retry before "Nothing kept" below; Step 2 still makes at most 3 calls. When no retry is needed, the reserved slot may instead fund the feature-and-mechanism search if it wasn't already run and could change the choice of home. Otherwise leave it unused.

**The same file can come back at two commits.** Read it once, at the commit most other kept results from that repository carry, and say in the footer that another version was indexed.

**Pick the home:** the repository and directory where most kept results cluster, usually one package or service ("packages/session in beacon-web"). Prefer the package that decides the outcome over one that only displays it: a component that fetches and filters suggestions, not the one that draws the list. If kept results split between two products with the same words, use the product the user named, or ask. Don't merge them.

**Only shared code found:** if the product the user named has no code in the results, but a shared component it may use does (a design-system or platform package), use the shared component as the home. Say in the short answer's first sentence that this is the shared component, and that how the product sets it up isn't in the code we can search. The verdict can be no better than "Partly answered". If a doc or record suggests the product doesn't use the component everywhere (some fields call the service another way), say so in the short answer: "This may not apply to every [product] field."

**Nothing kept after the retry:** the verdict is "Not in the code we can search" (Step 7). Skip Steps 3 and 4, and still run Steps 5 and 6, so the user gets the docs and an owner. Don't widen the search to generic words to find something.

## Step 3: Read the code and trace the behaviour

1. **List the home directory** with one `scanCodeRepo` call: `workspace` and `repo` from the result, `commitHash` from its `version`, `root` set to the home directory, `limit: 200`. This shows the manifest (`package.json`, `pom.xml`, `catalog-info.yaml`, `compass.yml`, `CODEOWNERS`), any `CHANGELOG.md`, and how the code is laid out.
2. **Read up to 8 files** with `getCodeFile`, together where you can, passing each result's `workspace`, `repo`, `path` and `version` (as `commitHash`). In this order:
   - the file whose matched lines handle the trigger (the component, handler or endpoint)
   - the files it calls that decide the outcome (sorting, filtering, checks, defaults)
   - the manifest, for the owner (Step 6)
   - the changelog, if there is one (Step 4)

   **Take line numbers from code search, not by counting.** `getCodeFile` returns the file as one string with no line numbers, and counting by eye drifts. `searchCode` results carry each chunk's `lineRange`, and lexical results add `matchedLineNumbers`. Cite those. Counting a few lines inside a returned chunk, from its `lineRange` start, is fine: chunks are short. Counting from the top of a whole file isn't. To cite lines no search has returned, run a lexical `searchCode` for a distinctive line in that code (an identifier or a string on it) with the file's `path`, up to 3 of these. If the client can save a tool result straight to a file, numbering that file (`nl -ba`) works too. Never retype a file to number it. If a range can't be pinned this way, cite the function by name with no line numbers.
3. **Follow an identifier** when the deciding logic calls a function, class or service defined somewhere you haven't read: one `searchCode` with `mode: lexical`, the identifier as the query, and the home's `namespace`. Up to 3 of these, apart from the pinning searches. Spend them on the hand-offs that decide the outcome first. For a service known only by its URL or endpoint, run one `mode: hybrid` search with the service's name and the endpoint path. If it returns only callers, stop: more searches won't find the service. If none finds where it's defined, the step is a hand-off (below).
4. **Write the trace:** the behaviour as an ordered list of 3 to 10 steps, from trigger to outcome. Each step has:
   - one plain sentence in the product's words, with the code name after it in monospace when it helps someone talking to an engineer ("It sorts people it already knows to the top (`sortByRecent`)")
   - the file, line range and commit it came from
   - one kind, from this table:

| Kind | Use it when |
| --- | --- |
| Shown in code | The cited lines do this whenever the step is reached |
| Depends on a setting | A feature flag, experiment, config value, permission, plan or edition check decides what happens, or an option the product using a shared component passes in |
| Hand-off | The code passes the decision to something whose code you didn't read: a service call, an API, a library you couldn't find |
| Default or limit | A fixed value shapes the result: a timeout, a maximum, a page size, a default choice |

   The page doesn't show the kind. It decides what the reply, the checklist and the settings table can use, so the sentence says it in words: the setting by name, the number with its unit, and the service a hand-off goes to.

5. **Rules for the trace:**
   - **Every sentence must be checkable in the lines it cites.** If you can't point to the lines, leave the sentence out.
   - **Numbers come from the code,** exactly, with units ("shows up to 50 people", "30 minutes"). Don't round. If a number comes from config you can't see, it's "Depends on a setting".
   - **Flags and settings are named, never resolved.** Name the flag or setting key, and say what each value does. Never say which value is live: code can't show rollout state.
   - **"Why" needs a source.** Only explain intent if a code comment, a linked doc or a pull request says it, and say which ("The code comment says this avoids…").
   - **A hand-off says what it hands to,** in plain words ("asks the people search service for matches"), naming the service as the map in Step 8 will show it ("People search service"). If a follow-up search found no code for it, add "We couldn't find this service's code." If no search was run for it because the cap was reached, say "We didn't search for this service's code" and name the cap in the footer. A code comment's claim about what the service does can be stated in the step as "A code comment says…", and never as a fact.
   - **One kind per step.** If a step mixes a setting and a fallback ("the site's timeout, or 30 minutes if none is set"), split it into two steps. Keep what always happens in its own "Shown in code" step, apart from what a setting changes.
   - **Tests support a step,** they don't make one. A test name that states the rule ("shows external users with a lozenge") can be cited beside the code, never instead of it.
   - **Name each file the trace cites** for the map in Step 8: one to three plain words in the product's words, for what the file does in this behaviour ("Idle timer" for `idleTimer.ts`, "Suggestion order" for `sortByRecent.ts`), not its code name. A file that several steps cite keeps one name.
   - **Link the files the cited lines connect,** for the map in Step 8: when a file's cited lines call, read, start, show or restart another cited file, record a link from the one that acts to the one acted on, with a verb of one or two words ("reads", "restarts", "calls") and the step whose cited lines show it. Only link what a cited line shows. Two steps in a row aren't a link, and a file nothing links can be left unlinked.
6. **Stop tracing** when the trace reaches the outcome asked about, reaches a hand-off that decides the outcome, or uses the file budget. Say in the footer where it stopped.

## Step 4: When it last changed

Code search has no history for a file, so use what the repository records. One of these, the first that applies:

- **A changelog in the home directory** (read in Step 3): keep entries about a trace step's subject (the field, setting, limit or check it describes), not every entry that names the package, from the last 12 months if the changelog has dates, or the 5 newest such entries if it doesn't. Take the version, the date if given, and the line. Link the pull request or commit it names, and say in the footer if those links point to a repository the reader may not be able to open (a private source behind a public mirror).
- **A Bitbucket home that isn't a mirror:** `listBitbucketRepoPullRequests` (through `discover`) with `workspaceId`, `repoId`, `state: MERGED`, a `q` filter on the title (`title ~ "<hook>"`) and `pagelen: 10`. Keep pull requests whose title is about the behaviour.
- **A GitHub home:** the Step 5 third-party search can return its pull requests. Keep those about the behaviour.

If none applies, show "Not checked: no change history for this code" in the footer. Never date a change from a commit hash alone.

## Step 5: What the docs, tickets and chat say

Run these together with Step 3, each `search` with `mode: STANDARD` and `limit: 20`:

- `targetApp: CONFLUENCE`, with the behaviour in the user's words
- `targetApp: THIRD_PARTY`, with the same, for Slack, GitHub, Google Drive and public docs
- `targetApp: JIRA`, with the user-visible string or the feature plus "bug", for work items and support tickets about it

Then:

- Keep a hit only if it's about the same behaviour (same feature and trigger). Drop sensitive results as `teamwork-graph-context` says, and drop direct and group messages.
- **Read up to 3 docs in full**: those that make a claim about the behaviour. Support articles and customer-facing docs come first, then runbooks, then design pages. Read Confluence pages with `getConfluenceContent` (`content_format: markdown`, `detail: full`), and third-party docs (a public developer site, a Google Doc) with `getGraphObject`. If one won't hydrate, its snippet is the citable text, as `teamwork-graph-context` says.
- **Compare every claim with the trace.** Each claim in a kept doc, ticket or message about how the behaviour works gets one row, so a doc with two claims gets two. Each row gets one of:

| Finding | When | Lozenge |
| --- | --- | --- |
| Disagrees with the code | It states something a "Shown in code" or "Default or limit" step contradicts: a different number, order, condition or outcome | Disagrees (danger) |
| Matches the code | What it states, the trace shows | Matches (success) |
| Can't check | It's about a hand-off, a setting's live value, or something the trace didn't reach | Can't check (default) |

  The code wins for what the code does. A doc can still be right about a service whose code wasn't read, so a claim about a hand-off is "Can't check", never "Disagrees". A plan, proposal or RFC describes what someone meant to build, not how it works: it's "Can't check", noted as "a plan from [Mon YYYY]" using its created date, or "a plan, last edited [Mon YYYY]" when only `lastModified` is known, never "Disagrees".
- **Questions count too.** Messages and tickets asking about this behaviour show it's a recurring question. Count them for the last 90 days by `lastModified` ("Asked 4 times in Slack in the last 90 days"). One question posted in several channels counts once. If none fall inside the window but some are older, say when it was last asked instead ("Last asked in Slack in Jul 2026, 2 times this year"). Never list who asked, and don't link the questions: a chat title names the person. A message that answers the question can be linked as a finding, with its author named as `teamwork-graph-context` allows.
- A Jira bug about the behaviour that's open goes in "What the docs and chat say" with its status, as "Open bug". Don't say whether it's the cause of anything.

## Step 6: Who owns it

Take the owner from the first source that names one, and say which:

1. **Declared in the code.** The manifest's team field (for example `"team": "..."` in a `package.json`), a `CODEOWNERS` entry for the home path, or the owner in `catalog-info.yaml` or `compass.yml`.
   - **Resolve the team.** If the file gives a team ARI or ID (`compass.yml`'s `ownerId` does), read it with one `getTeam` call (through `discover`), passing it as `teamId`. Otherwise use one `searchTeams` call on the exact declared name. Link it only if a returned name matches exactly, or if the ARI resolved. A team whose name differs but whose description names this component can be shown as "Possible match", labelled found by search. Otherwise show the declared name as plain text.
   - **The channel to ask in** is a help or support channel (`compass.yml` links often have one). A channel for pull request or build notifications isn't one: show it, if at all, as "Code notifications". Never name a person from these files as the owner.
2. **Compass.** One `search` (`targetApp: ALL`) for the repository's name. If a Compass component's snippet or links name this repository, read its owner with `getGraphContext` (`objectType: CompassComponent`, the component URL, `relationshipTypes: ["atlassian_team_owns_compass_component"]`, `detailLevel: full`).
3. **Docs.** A named contact or owner on a doc read in Step 5, for this behaviour.

The graph holds nothing useful for a repository here. A GitHub repository resolves with no relationships, and a Bitbucket repository URL doesn't resolve. So don't spend a call on it. If no source names an owner, say "No owner recorded", and suggest `/whos-the-expert` with the feature as the topic. Never name a person from commit or pull request activity as the owner.

**Each service a hand-off goes to** gets its owner for the map in Step 8 too: the team a source above or a doc from Step 5 names for that service, or "No owner recorded". It matches the service's row in Who owns it. Don't spend calls looking for it.

## Step 7: Assess

**Verdict,** one of these. The page doesn't show it, so the short answer says in plain words anything it leaves open:

- **Answered from the code** (success): the trace reaches the outcome asked about, and every step is "Shown in code", "Default or limit" or "Depends on a setting" with the setting named.
- **Partly answered** (warning): the trace reaches a hand-off before the outcome, or the file budget ran out before it. Say in the short answer where the code stops and what happens after it is unknown.
- **Not in the code we can search** (default): Step 2 kept nothing, after the retry. The short answer says we couldn't find the code for it, and the page shows what the docs say, marked as unchecked, and who owns it.

Never: claim a flag or setting's live value, name a cause for one customer's case, guess what a hand-off does, or call the code a bug.

**Docs that disagree:** if a finding is "Disagrees with the code" about something the answer says, add one plain sentence to the short answer with the doc's smart link and what it still says ("The help article [link] still says 60 minutes, which changed to 30 in version 3.0.0."). The step it contradicts is in What the docs and chat say. Rank disagreements by audience: customer-facing docs first, then support articles and runbooks, then internal pages, then chat. Within each, newest first.

**The short answer:** 2 to 4 plain sentences, the first answering the question as asked. Every sentence must be backed by a trace step, or for a doc that disagrees, by its finding. Name any setting that changes the answer. For "Partly answered", the last sentence says where the code we can see stops.

**What to check on the account,** for a question about one customer: the settings and inputs from "Depends on a setting" steps, as a checklist in plain words ("Is the site on the new user management?"). When only shared code was found, add where it happened ("Which field or screen was it?"), since the product may set the component up differently in each place. Never answer them.

**Suggested reply,** when the anchor is a ticket or the user says it's for a customer: 2 to 5 sentences the user could send, labelled "Proposed". It uses only "Shown in code" and "Default or limit" steps, in customer language. Leave out a default the product or site can change ("up to 100 people" when the product sets its own maximum). If little is left, a short reply that says what's known and asks the customer for the facts on the checklist is fine. It names no flags, internal services, endpoints, repositories or people, and no "Depends on a setting" step unless it's a setting the customer controls.

**Stop condition:** stop gathering when the trace reaches the outcome and the owner is found, or when the budgets for Steps 2 and 3 are spent. One extra `getCodeFile` is fine if it could change the verdict.

## Writes

The skill reads by default. It offers one write only when the user gave a Jira or Jira Service Management ticket and the report has actually been published. Without a published report, do not offer the comment or publish a report just to enable it:

- **A comment on that ticket** with the short answer and a link to the published explainer. Show the full comment text first, labelled "Proposed". Say whether it's internal or public (on a service desk, offer it as an internal note, never a public reply), and wait for a yes. Create it with `addOrEditJiraIssueComment`. On an error, say what happened and re-read the ticket's comments before offering again.

Never edit a doc that disagrees with the code. The explainer shows the disagreement, and the user takes it to the doc's owner.

## Answer and offer an export

- Lead with the short answer and what is Shown in code, depends on a setting, or happens beyond the code that can be read. Keep Step 7's assessment and wording rules.
- Explain the behaviour step by step, with ordinary Markdown links to the code lines and tests that support each step. Include the repository and commit, relevant defaults and settings, hand-offs and where the trace stops. Do not create the report's diagram or HTML to answer in chat.
- Include documentation or chat disagreements, recent changes when found, recorded owners and channels, and anything set aside or not answered. For a customer question or ticket, retain What to check on the account and the Proposed suggested reply, with all of Step 7's exclusions.
- In Sources and limitations, retain the repositories and commits read, file and search counts, excluded-result reasons, missing change history, caps and coverage gaps required by the report's sources footer.
- A suggested reply is draft text only. Offer the ticket-comment write only once a report has actually been published, as Writes requires. Skipping export or publication leaves that write unavailable.

Ask whether the user wants this exported to an HTML report. If they have already explicitly requested an export, HTML report or publication, proceed with that requested build without asking again. Otherwise stop here until they answer; a normal invocation of this skill does not request a report. Follow the shared availability and confirmation checks before offering or performing publication.

## Step 8: Build the explainer (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in this folder:

```bash
python3 <this skill's folder>/render.py explainer.json how-it-works-<topic>.html
```

- **The data** has the shape of `example.json` in this folder (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **The keys.** `question` and `about` head the page, `about` the "[feature] in [product]" phrase from Step 1, and `readFrom` is `{"repository", "commit", "date"}` for the header's date, the map and the trace (the date you read it, never the commit's date). `askedOn` is the ticket's link with its status, when the anchor was a ticket, shown in Suggested reply. `answer` is the 2 to 4 sentences, as paragraphs, each a text field, with a doc that disagrees as a link in it. Each of `steps` is `{"text", "code", "test", "excerpt"}`: `code` and `test` `{"path", "lines", "url", "name"}` with `lines` as `[first, last]` and `name` the test's name, and `excerpt` up to 12 lines as `{"n", "code"}`, with `{"gap": true}` between runs that aren't next to each other, secrets cut. `map` is `{"trigger", "parts", "links", "outside"}` for Where it happens: `trigger` the short phrase from Step 1, `parts` a `{"path", "name"}` for every file a step's `code` cites, with `path` exactly as in `code` and `name` its plain name from Step 3, `links` a `{"from", "to", "verb", "step"}` for each link from Step 3, with `from` and `to` paths from `parts` and `step` one number, and `outside` a `{"name", "steps", "owner"}` for each service a Hand-off step hands to, with `steps` the numbers of the steps that hand to it and `owner` from Step 6, left out when none is recorded. `settings` are `{"name", "kind", "changes", "steps", "who"}`, with `steps` the numbers of the steps it touches (`[2, 3]`), `checklist` the questions for one customer with `checkNote` above them, `docs` the findings as `{"link", "claim", "verdict", "meta"}`, `questions` the line counting recent questions, `bugs` the open bugs as links, `changes` `{"version", "date", "text", "link"}` with `changesNote`, `owners` `{"label", "link" or "text", "from"}`, `reply` the suggested reply, and `notAnswered` the line for a behaviour set aside. Put code, file names, settings and flags in backticks.
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `references/hand-built.md` in this folder.

The rules below say what the renderer builds, and what each part of the data must hold.

### Sections, in this order

Sections 2 to 11 are cards, each with its title in plain text and no icon.

1. **Header** (not a card): the `/how-it-works` skill tag, the question as the page's only `h1`, then one line: "[about], as of [the date you read it]." ("Invoice search in Ledger, as of Oct 27, 2026."). No tool returns when a commit was made, so never call it the commit's date. The repository, commit and files read go in the sources footer.
2. **Short answer**: the 2 to 4 sentences, and nothing else. The apps used are in the sources footer.
3. **Where it happens**: a diagram that the renderer lays out from `map` and `steps`, so every run draws it the same way. It shows what calls what, left to right: the trigger, then a node for each file a step's `code` cites, inside one frame for the repository in `readFrom`, titled with the repository and its team, with "Code we read, at [commit]" under it, then a dashed node for each service a Hand-off step hands to, under "Outside the code we can see", with its owner or "No owner recorded". A file's node has its plain name and its file name, the same name its steps' code chips show, so there are no step numbers on it. The edges are the trigger's arrow to step 1's file, a hand-off step's arrow from its file to its service, and each link in `map.links`, labelled with its verb. A link is drawn only from what a cited line shows, never from the step order. Settings aren't in the diagram; What can change this has them. With no link, or no cited file, there's no card, since the step list already shows the order. A `map.parts` path no step cites, a cited file with no name in `map.parts`, a link to a file that isn't in `map.parts` or to itself, or a step number that isn't a step, or that cites neither of a link's files, stops the renderer with a data error.
4. **Step by step**: the trace as a numbered list, each number in a small circle, with the steps divided by lines. Each step: the sentence, then a code chip shaped like a smart link, with the `angle-brackets` icon and the file name ("UserPicker.tsx"), linking the file at the cited lines, using the `externalUrl` from `getCodeFile` with a line anchor where the host supports one. The lines and the commit are in the chip's tooltip, and the commit is in the sources footer too. Under it, a collapsed "Show the code" disclosure with up to 12 lines from the cited range, in monospace, with their line numbers and secrets cut. If the lines that matter aren't next to each other, show each run with its numbers and an ellipsis row between them. Supporting tests appear as a second chip with the test file's name, and the test's name in its tooltip. Then the `traceNote` line in small subtlest text.
5. **What can change this**, if any step depends on a setting: a table that stacks into one block per setting at 600px and narrower, with the setting or flag in monospace and its kind under it, what it changes in plain words with the steps it touches under it, and who sets it, as the code shows: "We can't see whether it's on" (a flag or experiment), "Set by the site admin", or "Set by the product that uses it" (an option a shared component is given).
6. **What to check on the account**, for a question about one customer: the `checkNote` line in small subtlest text, then the checklist as checkboxes. Ticks aren't saved.
7. **What the docs and chat say**: one row per finding, ranked as Step 7 says. Lay each out as a stacked list item, not a table column: the smart link on its own line, then the claim in a sentence, then its lozenge and the trace steps it was checked against. Source titles are long, and in a table they squeeze the claim. Nearly every source here is found by search, so this page is an exception to `teamwork-graph-context`'s labelling rule: no chip is marked as found by search. Say once in the footer that the docs and chat were found by search. Then the count of recent questions, if any, as one line of small text, and open bugs as rows with a smart link and its status lozenge.
8. **Recent changes**, if Step 4 found any: a row per change with its version and date as the label ("3.4.0 · Sep 30, 2026"), then the line and its link. Then the `changesNote` line in small subtlest text.
9. **Who owns it**: a row per owner with the kind of owner as the label: the team (a smart link if resolved), the channel to ask in, the Compass component, and where each came from under it in small subtlest text ("Declared in compass.yml"). If a hand-off goes to a service with no owner recorded, add a row for it saying so, with `/whos-the-expert` as the next step.
10. **Suggested reply**, if there is one: "Reply on" with the ticket's smart link and status, if the anchor was a ticket, then "Proposed. Check it before you send it." in small subtlest text, then the text in a quote block with a "Copy" button.
11. **Not answered here**, if Step 1 set a second behaviour aside: a card holding one line in small subtlest text.
12. **Sources footer** (not a card): a tag for each app searched, one that found nothing saying so ("No results from Google Drive") with no other mark, then the lines, as `teamwork-graph-context` describes, plus: the repositories and commits read, the number of files read and searches run, how many results were left out, by reason, where the trace stopped and why, any other indexed version of a file, any cap reached, and "Not checked: no change history for this code" if Step 4 found none.

## When live

Static only. The answer depends on reading and judging code, and on the sensitive-content rules, which page code can't apply. The explainer is pinned to the commit it read. To refresh it after the code changes, run the skill again.

## Step 9: Deliver the requested report

- Hand over the requested HTML explainer. If Atlassian Artifacts availability is confirmed as described in `teamwork-graph-context`, offer a private, read-only copy named "How it works: [the question, shortened]". Publish only if requested; report export alone does not authorise it.
- After an approved publication, offer to share it with the people who asked the question only if the user names them, and share only on request.
- If the anchor was a ticket and the report has been published, offer the comment with its published link as Writes describes. A local export or an unavailable publication service does not satisfy that condition.
