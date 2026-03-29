---
name: update-large-confluence-page
description: "Edit large Confluence pages section-by-section without exceeding LLM context limits. When an agent needs to: (1) Update a specific section of a large Confluence page, (2) Edit pages whose ADF body exceeds 10-20 KB, (3) Modify one part of an RFC or design doc without destroying layout, or (4) List the table of contents of a Confluence page to decide what to edit. Uses a helper script that bypasses the LLM for bulk data transfer while the LLM decides what to change."
---

# Update Large Confluence Page

## Keywords
large page, big page, update section, edit section, confluence section, page too large, ADF too big, partial update, section edit, replace section, list sections, table of contents, page outline, RFC edit, design doc edit, update heading, edit heading, large document, context limit, token limit

## Overview

Edit specific sections of large Confluence pages without passing the entire page body through the LLM context window.

**The problem:** Confluence pages with rich content (RFCs, design docs, runbooks) produce ADF bodies of 40–70 KB. The MCP `updateConfluencePage` tool requires the full body as an inline parameter, which is impractical when the ADF exceeds the model's working context.

**The solution:** A helper script (`scripts/confluence_section_editor.py`) that communicates directly with the Confluence REST API. The LLM stays in the **control plane** (deciding *what* to edit), while the script handles the **data plane** (moving bulk ADF data). The script identifies heading-delimited sections in the ADF tree and performs surgical splice operations to replace only the targeted section.

**Use this skill when:**
- A `getConfluencePage` response is very large or was persisted to a file by the agent runtime
- The user wants to edit one section of a multi-section page
- Using `updateConfluencePage` with `contentFormat: "markdown"` would destroy layout macros

---

## Prerequisites

The helper script requires three environment variables for Confluence Cloud authentication:

| Variable | Description |
|---|---|
| `CONFLUENCE_URL` | Site base URL, e.g. `https://yoursite.atlassian.net` |
| `CONFLUENCE_EMAIL` | Atlassian account email |
| `CONFLUENCE_API_TOKEN` | [Atlassian API token](https://id.atlassian.com/manage-profile/security/api-tokens) |

The script uses only Python standard library modules (no `pip install` required).

---

## Workflow

### Step 1: Determine Whether This Skill Is Needed

Try fetching the page normally first:

```
getConfluencePage(
  cloudId="...",
  pageId="PAGE_ID",
  contentFormat="adf"
)
```

**If the response is small** (fully visible in context, under ~10 KB): use `updateConfluencePage` directly — this skill is not needed.

**If the response is large** (truncated, persisted to file, or the user reports context issues): proceed to Step 2.

---

### Step 2: List Page Sections

Run the helper script to get a compact table of contents:

```bash
python scripts/confluence_section_editor.py list-sections --page-id PAGE_ID
```

This outputs a lightweight summary like:

```
Page: Q3 Architecture RFC
ADF size: 62,481 bytes  (147 top-level nodes)
Sections: 9

  [0]     (preamble — before first heading)  (2 nodes, idx 0:2)
  [1] H1  Introduction  (4 nodes, idx 2:6)
  [2] H2    Background  (3 nodes, idx 6:9)
  [3] H2    Motivation  (5 nodes, idx 9:14)
  [4] H1  Design  (2 nodes, idx 14:16)
  [5] H2    Architecture  (8 nodes, idx 16:24)
  [6] H2    Data Model  (6 nodes, idx 24:30)
  [7] H1  Implementation Plan  (12 nodes, idx 30:42)
  [8] H1  Conclusion  (3 nodes, idx 42:45)
```

**Present this to the user** and ask which section they want to edit.

---

### Step 3: Extract the Target Section (Optional)

If the user needs to see the current content before editing:

```bash
python scripts/confluence_section_editor.py get-section \
  --page-id PAGE_ID \
  --section "Architecture" \
  --output /tmp/section.json
```

This writes only the targeted section's ADF nodes to a file. Read it and present a summary to the user.

---

### Step 4: Write New Section Content

Create a file with the replacement content. Two formats are supported:

#### Option A: Markdown (recommended for most edits)

Write the new section content as Markdown. The script converts it to ADF and preserves the original heading automatically.

```bash
# Write the new content to a temp file
cat > /tmp/new_section.md << 'EOF'
The architecture follows a microservices pattern with three layers:

- **API Gateway** — handles routing and auth
- **Service Mesh** — inter-service communication via gRPC
- **Data Layer** — PostgreSQL with read replicas

```python
class ServiceRegistry:
    def discover(self, name: str) -> Endpoint:
        ...
```

See the ADR in Confluence for trade-off analysis.
EOF
```

#### Option B: Raw ADF JSON (for precision edits preserving macros)

Export the section, modify the JSON, save it back:

```bash
python scripts/confluence_section_editor.py get-section \
  --page-id PAGE_ID --section "Architecture" -o /tmp/section.json

# ... edit /tmp/section.json ...

# Then update with --format adf
```

---

### Step 5: Apply the Section Update

```bash
python scripts/confluence_section_editor.py update-section \
  --page-id PAGE_ID \
  --section "Architecture" \
  --content-file /tmp/new_section.md \
  --format markdown \
  --message "Updated Architecture section per review feedback"
```

The script will:
1. Fetch the full page ADF from Confluence (bypasses LLM context)
2. Locate the section by heading text
3. Splice in the new content, preserving everything else
4. Push the update via Confluence REST API v2

Output:
```
Updated section 'Architecture' in 'Q3 Architecture RFC' (v12)
```

---

## How Section Identification Works

ADF documents store content as a flat array of top-level block nodes under `doc.content[]`. The script scans this array and splits it into sections using heading nodes as delimiters:

1. **Preamble** — any nodes before the first heading (level 0)
2. **Heading sections** — each heading node plus every subsequent node until the next heading of equal or higher precedence

This mirrors the [W3C HTML document outline algorithm](https://html.spec.whatwg.org/multipage/sections.html#outline). The replacement operation is a simple array splice — O(n) with zero risk to nodes outside the targeted section.

See `references/adf-section-model.md` for a visual explanation.

---

## Decision Guide

| Scenario | Approach |
|---|---|
| Page < 10 KB | Use `updateConfluencePage` directly |
| Page > 10 KB, layout doesn't matter | `updateConfluencePage` with `contentFormat: "markdown"` |
| Page > 10 KB, must preserve layout | **Use this skill** (section-level edit) |
| Need to edit multiple sections | Run `update-section` once per section |
| Need to reorder sections | Export all sections via `get-section`, rebuild, update full page |

---

## Edge Cases

### Page with No Headings
The entire document is treated as one section. The script will still work but cannot target sub-parts.

### Section Heading Not Found
The script prints available headings and exits with an error. Use a substring of the heading text for fuzzy matching.

### Concurrent Edits
Confluence uses optimistic locking via version numbers. If someone else edits the page between fetch and update, the update will fail with a 409 conflict. Re-run the command to fetch the latest version and retry.

### Markdown Conversion Limitations
The built-in Markdown → ADF converter handles headings, paragraphs, bullet lists, code blocks, bold, italic, and inline code. For complex content (tables, panels, layouts, macros), use the `--format adf` option with hand-edited ADF JSON.

---

## Tips

- **Always list sections first** to verify the heading text matches what you expect
- **Use `--format adf`** when updating sections that contain Confluence macros, panels, or layout blocks
- **Keep section edits atomic** — update one section per command for clean version history
- **Check the version message** in Confluence page history to verify the update landed

---

## When NOT to Use This Skill

- Page is small enough to pass through `updateConfluencePage` normally
- You need to restructure the entire page (add/remove/reorder sections)
- You are creating a new page from scratch (use `createConfluencePage` instead)
- The edit is to page metadata only (title, labels, parent) — use the standard MCP tools

---

## Quick Reference

```bash
# List all sections (table of contents)
python scripts/confluence_section_editor.py list-sections --page-id 12345

# Extract one section to a file
python scripts/confluence_section_editor.py get-section --page-id 12345 \
  --section "Design" -o /tmp/design.json

# Update a section from Markdown
python scripts/confluence_section_editor.py update-section --page-id 12345 \
  --section "Design" --content-file /tmp/new_design.md

# Update a section from raw ADF JSON
python scripts/confluence_section_editor.py update-section --page-id 12345 \
  --section "Design" --content-file /tmp/design.json --format adf

# Run tests
python -m unittest scripts/test_confluence_section_editor -v
```
