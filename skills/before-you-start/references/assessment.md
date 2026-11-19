# assessment

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

## Step 7: Assess

### Is it about the idea?

An effort overlaps the idea only when its **own records** say so, as Step 5 defines them: a project description or update, an epic description, a page or doc body, a README, a Loom description, or a search snippet of that body. Never infer an overlap from a title match alone. Compare what it does with the facets from Step 1 that aren't blank:

- **Outcome matches** when the effort produces the same kind of thing for the same purpose. It matches **in part** when only one of those holds: the same thing for another purpose, the same purpose served another way, or the same capability built for a different consumer (a merge pipeline that feeds another product).
- **Audience matches** when it's for the same users or teams.
- **Mechanism matches** when it works the same way and is delivered the same way (the same sources, the same kind of agent, the same channel). Compare delivery only when the user gave a mechanism. It matches in part when one of its two parts does ("AI-generated" but baked into a file, not "shown while it plays").

Count a full match as 1 and a match in part as a half, for ranking. Write down the **main difference** in one phrase ("runs once a week, not on every change", "for support leads, not every user"), or "none found". The card shows it.

A candidate whose description you couldn't read, or that matches only on its title, goes in "Names that matched, not checked" (up to 3), with its record's status and no class.

### Status

- **Projects** use Pending, On track, At risk, Off track, Paused, Done and Cancelled, with phases Pending, In progress, Paused and Done.
- **Jira** uses its workflow statuses and resolutions.
- **A page, doc, repository or Loom** has no status field. Use its status line if it has one ("Status: In progress"). Otherwise, it's **active** if it was edited, or the repository had a merged pull request, in the last 90 days, and shows as "Page · edited Oct 2026". Older than that, it shows its date and is inactive.
- **Active** means Pending, On track, At risk, Off track, In progress, To do, or the 90-day rule above. Paused is inactive but not finished.
- **A page that documents a shipped feature** (a guide, "getting started", help or release notes) means the work shipped: the effort is Done before, however recently the page was edited.
- **Dates on developer docs and Artifacts** found by search are often crawl dates: treat them as unknown.
- **An effort with several records** takes its status from its main record. With no project or epic, it takes the newest date among its records.

Show the record's own status beside the class, in plain text ("Projects · Paused").

### Classes

One per effort. Decide in this order, and take the first that fits:

| Class | When | Lozenge |
| --- | --- | --- |
| **Cancelled** | The record's status is Cancelled, or a Jira resolution of Won't Do, Declined or Duplicate, and the outcome matches fully or in part | neutral |
| **Done before** | The record is Done, Completed or Resolved as Done, or a page or update says it shipped, and the outcome matches fully or in part, and nothing in the same line of work is still active | success |
| **Same** | The outcome matches fully, every other facet the user gave matches fully, and its records name no different audience. It may be active, paused or inactive | warning |
| **Partial overlap** | The outcome matches in part, or fully with a different audience, scope or delivery, or it covers part of the idea | information |
| **Adjacent** | The outcome differs, but the mechanism or the audience matches, so it could share parts or users | discovery |

Anything that matches none of these isn't an effort to know about: drop it.

**Cancelled is not failed.** Read who cancelled it:
- If the cancelling update was posted by a bot or automation (a creator with "bot" or "automation" in its name, or text such as "deemed abandoned", "cleanup process" or "closed due to inactivity"), the label is "Closed as inactive" in small text beside the lozenge. The record says nothing about why the work stopped. Never say it was tried and failed, abandoned or rejected. This holds for a bot-cancelled project in "Names that matched, not checked" too.
- Only say why work stopped when a person wrote the reason in an update or comment, and link it.

### Ranking

Rank the efforts checked in Step 5 by how closely each matches the idea. Only those checked efforts are eligible for the main results:

1. The number of facets matched, most first.
2. Then active before paused, and paused before done and cancelled.
3. Then by class: Same, Partial overlap, Done before, Cancelled, Adjacent.
4. Then efforts with an owner from a record before those without.
5. Then by the latest update, newest first.

Don't rank by an effort's size, its team, its owner's seniority, its project status colour or how many hits it got. Show at most **4** efforts. If any checked effort is In progress, the closest one is among them. Otherwise, if any checked effort is active, at least one active effort is. If more qualify, say "and N more" in the footer with their names as plain text.

### The move

One move per effort, with a one-line reason that cites its evidence:

| Class | Move | Unless |
| --- | --- | --- |
| Same, active, with an owner | **Join**: the work is already moving, so offer to contribute rather than start a second one | It's Pending, Paused, inactive or has no owner: then **Talk** |
| Partial overlap | **Differentiate**: agree with the owner where one effort ends and the other starts, using the main difference | It covers most of the idea's outcome, for the same audience, and is in progress: then **Join**. It's inactive and its plan or design is written up: then **Reuse** |
| Done before | **Reuse**: use what was built, or what was learned, before building again | Nothing reusable is linked or recorded (no repo, page, demo, or an update recording a launch or GA): then **Talk** |
| Cancelled | **Talk**: ask the owner what happened before repeating it | |
| Adjacent | **Reuse** when it has a shipped part the idea could use | Otherwise **Talk** |

With no owner, the move stays, and the reason names the channel or page to go through. The moves are suggestions. Write each reason from the records ("Same outcome and audience, in progress, update 3 days ago"), never from a guess about the people.

### Headline

- **"Before you start: N efforts to know about"**, where N is the number of efforts shown.
- The verdict lozenge, decided by rule:
  - **"Someone's already on this"** (warning): at least one Same effort that's active, or any effort whose move is Join.
  - **"Related work exists"** (information): efforts were found, but none is an active Same or a Join.
  - **"Nothing close found"** (neutral): no efforts. Show the terms searched and the apps covered, and the "Names that matched, not checked", so the user can judge the search. Never say nothing like it exists: say nothing close was found with these words.
