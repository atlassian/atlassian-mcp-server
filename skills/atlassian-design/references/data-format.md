# Data for a kit renderer

A skill with a `render.py` builds its page from one JSON data file: you write the data, and the renderer builds the page from the kit's components. The skill's `example.json` (made-up sample data) shows its keys, and its `SKILL.md` says what goes in each section. This file has the rules every renderer shares.

## Text fields

- A text field is plain text, not HTML or Markdown. The renderer escapes it.
- It can hold `{0}`, `{1}` and so on, replaced by the item's `links` in order. A single `link` counts as `{0}`. The renderer refuses a page that leaves a placeholder unfilled.
- Text in backticks, such as a file name, setting or flag (`` `pageSize` ``), shows as code.

```json
{"text": "Riley Novak asked you to approve {0}", "links": [{"title": "SRCH-412 Split facet fields out of the main search index", "url": "https://example.atlassian.net/browse/SRCH-412", "icon": "task"}]}
```

## Links

Every link is a smart link, `{"title", "url", "icon", "app", "found", "status", "note"}`. Only `title` is required.

- **`title`:** the object's real title, as you fetched it or as the person gave it, never the URL. If you only have a URL, fetch the title. If you still can't, use a readable form such as the domain plus the last path segment (`atlassian.design · tokens`). Never make one up.
- **Jira work items** put the key before the title: `SRCH-412 Split facet fields out of the main search index`.
- **`url`:** the object's real URL. A link with no `url` shows as plain text that says no link is available.
- **`icon`:** one of the icon names below, matched to the object's type.
- **`app`:** the app's name, for third-party objects (`Google Docs`, `Slack`, `GitHub`). It shows after the title, because the icon alone can't say which app it is.
- **`found`:** `true` for an item found by search rather than linked, as `teamwork-graph-context` describes. It shows the "Found by search" label.
- **`status`:** a lozenge after the title, when the status is known (a Jira work item's status, a project's state).
- **`note`:** a few words inside the chip after the title, such as a recording's length ("22 min") or "No access".

## Lozenges

A lozenge is `{"text", "tone"}`, with `tone` one of `success`, `warning`, `danger`, `information`, `discovery` and `neutral`. A plain string is a neutral lozenge. Colour always comes with its text, so the text has to say the state on its own.

## The footer

The sources footer is `{"tags", "lines"}`:

- `tags`: one `{"text"}` per app searched, and `{"text": "No results from Zoom", "muted": true}` for an app that returned nothing
- `lines`: text fields, as the skill's footer rules say

## Mockups

Set `"mockup": true` for sample data. It adds the note at the top of the page. Follow the mockup rules in `teamwork-graph-context`.

## Leave out what you don't have

Leave out a key you have nothing for, and its section shows its empty line. Don't fill it with placeholder text. When a key the renderer needs is missing, it stops and names where, for example `data error: people[1].evidence[0]: missing "link"`. Add the key and render again.

## Don't edit the page by hand

The renderer's output is the page. If something's wrong, change the data and render again.

## Icon names

For links, match the object's type:

| Object | Icon |
|---|---|
| Confluence page, blog or live doc, a third-party page (Figma, Atlassian Artifact) | `page` |
| A document (Google Docs, Word, SharePoint) | `doc` |
| Confluence whiteboard | `whiteboard` |
| Confluence folder or space | `folder` |
| Jira work item, Jira Service Management request, third-party ticket | `task` |
| Jira epic | `epic` |
| Product Discovery idea | `lightbulb` |
| Jira project, Atlassian project | `project` |
| Goal | `goal` |
| Loom video, meeting recording | `video` |
| Pull request | `pull-request` |
| Repository | `repo` |
| Comment or chat message | `comment` |
| Chat channel | `hashtag` |
| Calendar event | `calendar` |
| Person | `person` |
| Team | `teams` |
| A saved search, such as a JQL link | `search` |
| Incident or alert | `flag` |
| Deployment, pipeline or any other web page | `globe` |

For sections and rows, the kit also has `people-group`, `book`, `decision`, `location`, `check`, `copy`, `sparkle`, `changes`, `info`, `clock`, `note`, `list-numbered`, `tree`, `link`, `priority-blocker`, `arrow-right`, `angle-brackets`, `warning`, `settings` and `list-checklist`. Any other name shows as `globe`.
