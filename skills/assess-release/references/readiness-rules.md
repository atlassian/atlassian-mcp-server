# readiness rules

Use the current session tools as described in the skill entrypoint. Call exposed operations directly; use discovery and a matching runner only when needed. Missing app metadata does not establish unavailability. Skip unavailable enrichments, report their impact, and retain all applicable evidence gaps.

## Step 8: Assess

### Areas

Give each of the five areas one state: **Ready**, **Conditions**, **Not ready**, **Not checked** or **Not used**.

First establish applicability. **Not used** requires the release scope, a record or the user to explicitly confirm that this area does not apply. State that reason and its source. No linked pull requests, an empty search, an unavailable app or a missing Projects project does not establish non-applicability. Assess each area independently: Code being Not used does not make Testing or Rollout Not used.

| Area | Not ready | Conditions | Ready | Not used |
| --- | --- | --- | --- | --- |
| **Work** | Any Blocked item, or any open item in To do or In progress that isn't a release check | Only In review items and release checks are open | No open items | Never: no release items means Can't assess |
| **Code** | Any Done item with an Open pull request | Any In review item with an Open pull request, 1 or more checked items Not readable, or fewer than 2 checked items with any pull request (a Gap for insufficient evidence) | Every checked item with pull requests is Merged, and at least 2 checked items have pull requests | Explicit confirmation that the release has no implementation changes requiring a code check |
| **Testing** | An open Testing check that's Blocked | An open Testing check, or no test evidence found | Test evidence found and no open Testing checks | Explicit confirmation that testing does not apply to this release |
| **Dependencies** | Any open upstream item or project that's Blocked, or whose due or target date is after the release date | Any other open upstream item or project, any upstream item that couldn't be read, or a Gap in applicable dependency coverage | No open upstream items or projects, and applicable dependency sources were checked | Explicit confirmation that this release has no applicable dependency area |
| **Rollout** | An open Rollout check that's Blocked, or an approver who declined | An open Rollout check, a Failed deployment, an approver still pending, no rollout doc found, or no deployment beyond development for the checked items | Rollout checks done, approvals given (or none set), and applicable rollout evidence checked with no outstanding condition | Explicit confirmation that rollout does not apply to this release |

For an applicable area, confirmed Not ready evidence wins. Otherwise, an area whose required records couldn't be read at all is **Not checked**, with a Gap condition explaining why. An empty successful read is not a failed read: missing evidence produces Conditions, rather than Not used. Where some evidence was checked, use Conditions for the remaining gaps. Missing Projects coverage remains a Gap condition even when the Jira links are clear; it makes Dependencies Conditions, unless the area is explicitly confirmed Not used. With no Not ready evidence, unreadable required records or outstanding conditions, use Ready.

### Findings

One row each, from this fixed set:

- **Blocker** (danger): a Blocked or flagged item; an open item with an open upstream item; or a record that says the release or an item is blocked (Step 5 item 5).
- **Unmerged code** (warning): a Done item with an open pull request, or an In review item whose pull request has had no update in 5 or more working days.
- **Open check** (warning): open Testing or Rollout checks, one row per kind ("6 rollout checks are open, all in Needs Triage"), with the count, the first two as links and the rest as a count. Checks under one readiness epic link the epic too.
- **Stalled** (warning): an In progress or In review item with no update in 10 or more working days.
- **Dependency** (warning): an open upstream item or project that isn't a Blocker.
- **Failed deployment** (warning): an item's newest deployment to an environment failed or was rolled back after an earlier success, named with the environment and date.
- **Date passed** (warning): the release date has passed and the version isn't released.
- **Gap** (neutral): evidence that couldn't be read or wasn't found (no test evidence, pull requests not readable, upstream items on another site, no rollout doc, no project found).

**Ranking.** Blockers first, by how many in-scope items wait on each (counting downstream links inside the scope), then by how long the item has been Blocked. Only a changelog gives that reliably: a Blocked status can sit in the To do category, so `statuscategorychangedate` may date a different move. For up to 2 blockers, read `listJiraIssueChangelogs` (directly or through discovery when needed, within the `getJiraIssue` cap) for the date the status became Blocked, and show "Blocked since [date]". Otherwise leave the date out, and rank by downstream count, then by key. Then the other findings in the order above. Never by priority field, issue type or age alone. An open Critical item is open work like any other.

### The verdict

First build one explicit list of **outstanding conditions** from the evidence and the Areas table. Reuse that same list in the answer and any later report:

- One condition per open In review item, open Testing or Rollout check, pending approval, unresolved Failed deployment, open upstream dependency that isn't already a Blocker, or evidence Gap. Include every reason that makes an area Conditions, including insufficient code evidence, missing test or rollout evidence, unavailable deployment evidence and missing Projects coverage. Every applicable Not checked area contributes a Gap condition.
- Give each underlying condition one stable local `id`, its affected `areas`, a type, a plain-language explanation and source links. A condition affecting Work and Code is one entry naming both areas. An open check that is also In review is one entry. Separate genuinely different requirements, such as completing a check and obtaining an approval.
- Grouping findings does not change the count: six open checks shown in one Open check finding still require six condition entries. A Gap describing the same missing evidence as another condition is not an extra condition. Stalled and Date passed findings do not add conditions on their own.
- Every Conditions area must have at least one listed condition; every applicable Not checked area must have a listed Gap. Ready and Not used areas cannot have outstanding conditions attached. Not ready areas can still have other outstanding conditions, but the Not ready state takes precedence. Check these relationships before giving the answer. Never label an area Conditions while listing zero reasons.

Count the distinct entries, then decide the verdict in this order and say which rule decided it:

1. **Can't assess:** the scope has no items, or Work is Not checked.
2. **Not ready:** 1 or more Blockers, any area is Not ready, or more than 5 outstanding conditions.
3. **Ready:** zero outstanding conditions, and every area is Ready or explicitly confirmed Not used. The summary explains any unused area.
4. **Ready with conditions:** otherwise, 1 to 5 outstanding conditions, with none of the earlier rules applying. Name and count those conditions in the answer; the count cannot be zero.

Consistency examples, with other areas Ready and no blockers unless stated:

| Evidence | Area and conditions | Verdict |
| --- | --- | --- |
| All applicable areas Ready | No conditions | Ready |
| An unresolved failed deployment | Rollout Conditions; one Failed deployment condition | Ready with conditions |
| Jira links are clear, but no Projects project was found | Dependencies Conditions; one coverage Gap | Ready with conditions |
| The user confirms this release has no implementation changes requiring code review | Code Not used, with the user's reason; other areas assessed independently | Ready if no conditions remain |
| No pull requests were found in the code sample, with no confirmation that code is unused | Code Conditions; a Gap for insufficient code evidence | Ready with conditions |
| Six open checks are grouped into one finding | Six distinct condition entries | Not ready |

What never changes the verdict: a priority field, the number of done items, a status name that sounds finished, a title, or how close the release date is. The verdict is about now. With weeks left, Not ready is normal, and the summary says how much is open without forecasting when it will close.

### Decisions needed

Up to 4, most urgent first, each one sentence in plain words, labelled "Suggested", with who holds it:

- **Holder, in this order:** an approver on the version (for sign-off), the version's driver (for scope and date), the driver or approver on a linked decision page, the owner a record names for the item (the upstream project's owner, the blocker's assignee for its own work). Otherwise "No owner recorded".
- **Typical decisions,** each only when the findings support it: whether to move open items out of the release ("Move the 8 open rollout checks, or keep them in"), whether to ship without a check that has no evidence, whether to wait for an upstream team, whether the release date stands when it has passed, and any open decision page in scope. A decision page is in scope when a record in scope links it, or its title or body names the release, an in-scope key or an in-scope epic. One found by search that doesn't is left out.
- Never suggest a new date, an estimate or an assignee.

### Stop condition

Stop when the scope is known, every open item has a status group, each area has a state, and each Blocker has its evidence link. One extra call is fine if it could change the verdict.
