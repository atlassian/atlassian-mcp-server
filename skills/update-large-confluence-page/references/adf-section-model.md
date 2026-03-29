# ADF Section Model

How the Confluence Section Editor identifies and manipulates sections within
Atlassian Document Format (ADF) documents.

## ADF Structure

An ADF document is a JSON tree with a root `doc` node containing a flat array
of top-level block nodes:

```
doc
 ├── paragraph          ← preamble (before first heading)
 ├── heading (H1)       ← section 1 starts
 ├── paragraph
 ├── paragraph
 ├── heading (H2)       ← section 2 starts
 ├── paragraph
 ├── codeBlock
 ├── heading (H1)       ← section 3 starts
 ├── paragraph
 └── table
```

## Section Boundaries

A **section** is defined as:

1. A `heading` node (the section start marker)
2. Every subsequent top-level node until the next `heading` of **equal or
   higher** precedence (equal or lower `level` number)

Content before the first heading is the **preamble** (level 0).

### Example

Given this document structure:

```
[0]  paragraph "Preamble"         ─┐ preamble section
                                   ─┘
[1]  heading H1 "Introduction"    ─┐
[2]  paragraph "Intro text"        │ "Introduction" section
[3]  paragraph "More intro"       ─┘
[4]  heading H2 "Background"      ─┐
[5]  paragraph "Background text"  ─┘ "Background" section
[6]  heading H2 "Motivation"      ─┐
[7]  paragraph "Why we do this"   ─┘ "Motivation" section
[8]  heading H1 "Design"          ─┐
[9]  paragraph "Design overview"  ─┘ "Design" section
```

The section editor produces:

| # | Heading | Level | Indices | Nodes |
|---|---------|-------|---------|-------|
| 0 | (preamble) | 0 | 0:1 | 1 |
| 1 | Introduction | 1 | 1:4 | 3 |
| 2 | Background | 2 | 4:6 | 2 |
| 3 | Motivation | 2 | 6:8 | 2 |
| 4 | Design | 1 | 8:10 | 2 |

## Section Replacement (Tree Surgery)

Replacing a section is a three-part array splice on `doc.content[]`:

```
result = content[:start] + new_nodes + content[end:]
```

### Before replacement (targeting "Background"):

```
[ preamble | H1-Intro | p | p | H2-Background | p | H2-Motivation | p | H1-Design | p ]
  ──────────────────────────  ^^^^^^^^^^^^^^^^^^^  ──────────────────────────────────────
  preserved (before)           replaced              preserved (after)
```

### After replacement:

```
[ preamble | H1-Intro | p | p | H2-Background | NEW-p | H2-Motivation | p | H1-Design | p ]
  ──────────────────────────  ^^^^^^^^^^^^^^^^^^^^  ──────────────────────────────────────
  unchanged                    new content            unchanged
```

Key properties:
- **O(n)** time complexity (single pass to identify, single splice to replace)
- **Zero risk** to nodes outside the target section
- **Version preserved** — the doc wrapper (`version`, `type`) is carried over
- **Immutable** — the original document is never mutated; a new doc is returned

## Heading Text Extraction

Heading nodes contain an array of inline nodes. The section editor concatenates
all `text`-type children to derive the section label:

```json
{
  "type": "heading",
  "attrs": { "level": 2 },
  "content": [
    { "type": "text", "text": "Status: " },
    { "type": "status", "attrs": { "text": "Done" } },
    { "type": "text", "text": " review" }
  ]
}
```

Extracted heading text: `"Status:  review"` (non-text nodes are skipped).

## Section Search

The `find_section` function matches headings in priority order:

1. **Exact match** (case-insensitive): query `"Design"` matches heading `"Design"`
2. **Substring match** (case-insensitive): query `"Motiv"` matches `"Motivation"`

This allows agents to use abbreviated heading names without needing the exact text.
