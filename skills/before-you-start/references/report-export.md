# Optional report export

Load this reference only for a requested report or publication. Preserve the findings, condition counts and source gaps from the conversational answer. Run the bundled Python renderer offline with its example and data-format reference; both shared design kits and logos are included. Do not install packages or download assets. Export does not authorize publication. Follow the shared context publication reference for capability checks and consent.

## Step 8: Build the card (only on request)

Only after the user requests the report, write its data as one JSON file and run the renderer in the skill folder:

```bash
python3 <this skill's folder>/render.py card.json before-you-start-<idea>.html
```

- **The data** has the shape of `../example.json` beside the skill entrypoint (made-up sample data). Copy its keys and fill them from the steps above. Text fields, links, lozenges and icons follow the shared rules in the `atlassian-design` skill's `references/data-format.md`. Leave out a key you have nothing for.
- **The keys.** `headline` is the h1 ("3 efforts to know about"), `verdict` the verdict lozenge and `idea` the idea restated in one sentence. Each of `efforts`, ranked, is `{"link", "class", "status", "does", "facets", "owner", "contributors", "move", "linked", "found", "earlier", "next", "note", "connected"}`: `class` the class lozenge, `status` the record's status line ("Projects · On track"), `does` the line on what it does, `facets` the matched facets and main difference, `owner` `{"name", "label", "team"}` labelled as Step 6 says (just `{"label"}` for "Owner not available" or "Owner not recorded"), `contributors` up to 2 names, `move` `{"label", "why"}`, `linked` up to 4 links and `found` up to 3, `earlier` and `next` the other phases, `note` the line for a bot-cancelled effort, and `connected` "You're already connected" when Step 3 or Step 5 found it. `message` is the suggested first message, left out for "Nothing close found". `unchecked` lists the names that matched as `{"link"}`.
- **Don't edit the page by hand.** If something's wrong, change the data and render again.
- **If Python can't run,** build the same page by hand, following `hand-built.md` beside this reference.

The rules below say what the renderer builds, and what each part of the data must hold.

### Sections, in this order

1. **Header** (not a card): eyebrow "Before you start", the headline as the page's only `h1` ("3 efforts to know about"), the verdict lozenge on the right, and the idea restated in one sentence under it in subtle text. Then, in small subtlest text: "Based on what each effort's own records say it does. The moves are suggestions."
2. **Efforts** (icon `project`): one row per effort, ranked. Each row:
   - the effort's main record as a smart link, the class lozenge, and the record's status in small subtle text ("Projects · On track")
   - one line on what it does, from its own records, with the matched facets and the main difference in small subtlest text ("Same outcome and audience · Main difference: for support leads only"). If the description came from tracked items or linked pages, say so ("From its linked work items")
   - the owner as a 24px initials avatar, name and team, labelled as Step 6 says ("Owner", "Owned by [team]", "Created by", "[Name] in Slack", "Owner not available", "Owner not recorded"), and up to 2 contributors by name
   - the move as a bold label with the reason after it ("**Join** · In progress with an update this week, and the same outcome and audience")
   - **Linked** evidence: up to 4 smart links connected to the record. **Found by search**: up to 3 smart links, with the dashed "Found by search" chip. Always two separate lists, each with its label, and leave a list out when it's empty
   - "Earlier phases" and "Next phase", for a line of work: the other records as smart links with their status
   - for a bot-cancelled effort, "Closed as inactive. The record doesn't say why." in small subtlest text
   - "You're already connected" in small text, if Step 3 or Step 5 found it
3. **Suggested first message** (icon `comment`): one message about the top effort, to its Owner, or else the person who created it or wrote it, or else its channel, naming the effort and the user's idea ("I'm about to start a daily summary for support leads. I saw Morning digest in Projects. Could we compare scope before I begin?"), in a quote block with a "Copy" button. Labelled "Suggested". When the user is already connected, write it as a follow-up between colleagues, not an introduction. Leave it out for "Nothing close found".
4. **Names that matched, not checked** (icon `search`), only if any: one line each, a smart link and its status, with "Title matches only. We couldn't read what it does."
5. **Sources footer** (not a card), as `teamwork-graph-context` describes: the apps searched, the terms searched (including echo searches), how many candidates were considered and how many efforts were shown, "N of your own items were left out", "Some results weren't used" when Step 3.1 dropped anything, whether the echo pass ran, any budget cap reached, and gaps such as owners from chat only or GitHub authors not available.

## When live

Static only. Finding efforts depends on open-ended search and on the sensitive-content judgement, which page code can't make. To refresh, run the skill again.

## Step 9: Deliver the requested report

- Hand over the requested HTML report. Offer a private, read-only Atlassian Artifact only when availability is confirmed as described in `teamwork-graph-context`, and publish only if requested. Exporting the report does not authorise publication.
- The result is for the user. Do not offer to share it with the owners shown in it; share only if the user asks and names who.
- Keep the verdict, evidence separation, suggested message and limitations from the conversational answer.
