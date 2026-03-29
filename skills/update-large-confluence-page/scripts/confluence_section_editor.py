#!/usr/bin/env python3
"""
Confluence Section Editor — surgical section-level editing for large pages.

Solves the problem described in
https://github.com/atlassian/atlassian-mcp-server/issues/106:

Large Confluence pages (50-70 KB ADF) cannot be practically updated via MCP
tools because the entire page body must pass through the LLM's context window.

This script operates as a **data plane** that bypasses the LLM for bulk data
transfer while the LLM remains the **control plane** that decides *what* to
edit.

Approach
--------
ADF (Atlassian Document Format) documents are flat arrays of top-level block
nodes under ``doc.content[]``.  Headings create *implicit* sections — a
section is a heading node followed by every subsequent node up to the next
heading of equal or higher level (lower ``attrs.level`` number).  This mirrors
the W3C HTML document-outline algorithm.

By treating the document as a sequence of sections we can:
  1. List sections (compact table of contents) — O(n) scan, tiny output.
  2. Extract a single section — O(n) scan, small output.
  3. Replace a section — O(n) splice, all other content preserved.

Usage
-----
::

    python confluence_section_editor.py list-sections --page-id PAGE_ID
    python confluence_section_editor.py get-section   --page-id PAGE_ID --section "Heading"
    python confluence_section_editor.py update-section --page-id PAGE_ID --section "Heading" \\
                                                       --content-file new.md [--format markdown]

Environment variables
---------------------
CONFLUENCE_URL        Base URL, e.g. https://yoursite.atlassian.net
CONFLUENCE_EMAIL      Atlassian account email
CONFLUENCE_API_TOKEN  Atlassian API token (not password)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from base64 import b64encode


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def get_auth() -> Tuple[str, str, str]:
    """Return ``(base_url, email, token)`` from environment variables."""
    url = os.environ.get("CONFLUENCE_URL", "")
    email = os.environ.get("CONFLUENCE_EMAIL", "")
    token = os.environ.get("CONFLUENCE_API_TOKEN", "")
    if not all([url, email, token]):
        print(
            "Error: CONFLUENCE_URL, CONFLUENCE_EMAIL, and "
            "CONFLUENCE_API_TOKEN must all be set.",
            file=sys.stderr,
        )
        sys.exit(1)
    return url.rstrip("/"), email, token


def _make_auth_header(email: str, token: str) -> str:
    """Build a Basic-auth header value."""
    credentials = f"{email}:{token}"
    encoded = b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


# ---------------------------------------------------------------------------
# Low-level HTTP helpers (stdlib only — no ``requests`` dependency)
# ---------------------------------------------------------------------------

def _api_get(url: str, email: str, token: str) -> Any:
    """Issue an authenticated GET and return parsed JSON."""
    req = Request(url)
    req.add_header("Authorization", _make_auth_header(email, token))
    req.add_header("Accept", "application/json")
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _api_put(url: str, email: str, token: str, payload: Any) -> Any:
    """Issue an authenticated PUT with a JSON body and return parsed JSON."""
    body = json.dumps(payload).encode()
    req = Request(url, data=body, method="PUT")
    req.add_header("Authorization", _make_auth_header(email, token))
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urlopen(req) as resp:
        return json.loads(resp.read().decode())


# ---------------------------------------------------------------------------
# Confluence page I/O
# ---------------------------------------------------------------------------

def fetch_page(base_url: str, email: str, token: str, page_id: str) -> Dict:
    """Fetch a Confluence page including its ADF body."""
    url = (
        f"{base_url}/wiki/api/v2/pages/{_sanitize_page_id(page_id)}"
        "?body-format=atlas_doc_format"
    )
    return _api_get(url, email, token)


def get_page_version(page_data: Dict) -> int:
    """Extract the current version number from a page response."""
    return int(page_data.get("version", {}).get("number", 1))


def parse_adf_body(page_data: Dict) -> Optional[Dict]:
    """Extract the ADF document dict from a page API response."""
    body = page_data.get("body", {})
    adf_repr = body.get("atlas_doc_format", {})
    value = adf_repr.get("value")
    if isinstance(value, str):
        return json.loads(value)
    return value


def update_page(
    base_url: str,
    email: str,
    token: str,
    page_id: str,
    title: str,
    new_adf: Dict,
    current_version: int,
    version_message: str = "",
) -> Dict:
    """Submit a full page update to Confluence Cloud (REST API v2)."""
    url = f"{base_url}/wiki/api/v2/pages/{_sanitize_page_id(page_id)}"
    payload = {
        "id": page_id,
        "status": "current",
        "title": title,
        "body": {
            "representation": "atlas_doc_format",
            "value": json.dumps(new_adf),
        },
        "version": {
            "number": current_version + 1,
            "message": version_message
            or "Section updated via confluence_section_editor",
        },
    }
    return _api_put(url, email, token, payload)


# ---------------------------------------------------------------------------
# Input sanitisation
# ---------------------------------------------------------------------------

_PAGE_ID_RE = re.compile(r"^[0-9]+$")


def _sanitize_page_id(page_id: str) -> str:
    """Ensure ``page_id`` is a numeric string to prevent path injection."""
    if not _PAGE_ID_RE.match(page_id):
        raise ValueError(
            f"Invalid page ID '{page_id}'. Must be a numeric string."
        )
    return page_id


# ---------------------------------------------------------------------------
# ADF section identification
# ---------------------------------------------------------------------------

def _heading_text(node: Dict) -> str:
    """Extract the plain-text content of a heading ADF node."""
    parts: List[str] = []
    for child in node.get("content", []):
        if child.get("type") == "text":
            parts.append(child.get("text", ""))
    return "".join(parts)


def identify_sections(adf_doc: Dict) -> List[Dict]:
    """
    Identify heading-delimited sections in an ADF document.

    A *section* starts at a ``heading`` node and extends through every
    subsequent top-level node until the next heading of equal or higher
    precedence (equal or lower ``level`` number).  Content before the first
    heading is returned as a *preamble* section with ``level: 0``.

    Returns a list of section descriptors::

        [
            {
                "heading":     "Section Title",
                "level":       2,
                "start_index": 4,
                "end_index":   9,       # exclusive
                "node_count":  5,
            },
            ...
        ]
    """
    content: List[Dict] = adf_doc.get("content", [])
    if not content:
        return []

    sections: List[Dict] = []
    first_heading_idx: Optional[int] = None

    for i, node in enumerate(content):
        if node.get("type") == "heading":
            first_heading_idx = i
            break

    if first_heading_idx is None:
        return [
            {
                "heading": "(entire document — no headings)",
                "level": 0,
                "start_index": 0,
                "end_index": len(content),
                "node_count": len(content),
            }
        ]

    if first_heading_idx > 0:
        sections.append(
            {
                "heading": "(preamble — before first heading)",
                "level": 0,
                "start_index": 0,
                "end_index": first_heading_idx,
                "node_count": first_heading_idx,
            }
        )

    current: Optional[Dict] = None
    for i, node in enumerate(content):
        if node.get("type") != "heading":
            continue
        level = node.get("attrs", {}).get("level", 1)
        if current is not None:
            current["end_index"] = i
            current["node_count"] = i - current["start_index"]
            sections.append(current)
        current = {
            "heading": _heading_text(node),
            "level": level,
            "start_index": i,
            "end_index": None,
            "node_count": None,
        }

    if current is not None:
        current["end_index"] = len(content)
        current["node_count"] = len(content) - current["start_index"]
        sections.append(current)

    return sections


def find_section(
    sections: List[Dict], heading_query: str
) -> Optional[Dict]:
    """
    Find a section by heading text.

    Matching order:
      1. Exact match (case-insensitive).
      2. Substring match (case-insensitive), first hit wins.

    Returns ``None`` when no section matches.
    """
    query = heading_query.lower()
    exact = [s for s in sections if s["heading"].lower() == query]
    if exact:
        return exact[0]
    partial = [s for s in sections if query in s["heading"].lower()]
    return partial[0] if partial else None


def extract_section_nodes(adf_doc: Dict, section: Dict) -> List[Dict]:
    """Return the raw ADF nodes that belong to *section*."""
    content = adf_doc.get("content", [])
    return content[section["start_index"] : section["end_index"]]


# ---------------------------------------------------------------------------
# ADF tree surgery — section replacement
# ---------------------------------------------------------------------------

def replace_section(
    adf_doc: Dict, section: Dict, new_nodes: List[Dict]
) -> Dict:
    """
    Return a new ADF document with *section*'s nodes replaced by *new_nodes*.

    Everything outside the section is preserved byte-for-byte.
    """
    content = adf_doc.get("content", [])
    spliced = (
        content[: section["start_index"]]
        + new_nodes
        + content[section["end_index"] :]
    )
    return {
        "version": adf_doc.get("version", 1),
        "type": "doc",
        "content": spliced,
    }


# ---------------------------------------------------------------------------
# Lightweight Markdown → ADF conversion
# ---------------------------------------------------------------------------

def _parse_inline(text: str) -> List[Dict]:
    """Convert inline markdown (bold, italic, code) to ADF text nodes."""
    nodes: List[Dict] = []
    buf = ""
    i = 0
    while i < len(text):
        # inline code
        if text[i] == "`":
            end = text.find("`", i + 1)
            if end != -1:
                if buf:
                    nodes.append({"type": "text", "text": buf})
                    buf = ""
                nodes.append(
                    {
                        "type": "text",
                        "text": text[i + 1 : end],
                        "marks": [{"type": "code"}],
                    }
                )
                i = end + 1
                continue
        # bold
        if text[i : i + 2] == "**":
            end = text.find("**", i + 2)
            if end != -1:
                if buf:
                    nodes.append({"type": "text", "text": buf})
                    buf = ""
                nodes.append(
                    {
                        "type": "text",
                        "text": text[i + 2 : end],
                        "marks": [{"type": "strong"}],
                    }
                )
                i = end + 2
                continue
        # italic (single *)
        if (
            text[i] == "*"
            and (i == 0 or text[i - 1] != "*")
            and (i + 1 < len(text) and text[i + 1] != "*")
        ):
            end = text.find("*", i + 1)
            if end != -1 and (end + 1 >= len(text) or text[end + 1] != "*"):
                if buf:
                    nodes.append({"type": "text", "text": buf})
                    buf = ""
                nodes.append(
                    {
                        "type": "text",
                        "text": text[i + 1 : end],
                        "marks": [{"type": "em"}],
                    }
                )
                i = end + 1
                continue
        buf += text[i]
        i += 1
    if buf:
        nodes.append({"type": "text", "text": buf})
    return nodes or [{"type": "text", "text": text}]


def markdown_to_adf_nodes(markdown_text: str) -> List[Dict]:
    """
    Convert simple Markdown to a list of ADF top-level nodes.

    Supported constructs: headings (``#``–``######``), paragraphs, bullet
    lists (``-`` / ``*``), fenced code blocks, and inline bold / italic /
    code.  For richer content, pass pre-built ADF JSON directly.
    """
    nodes: List[Dict] = []
    lines = markdown_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # fenced code block
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines: List[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            node: Dict = {
                "type": "codeBlock",
                "content": [{"type": "text", "text": "\n".join(code_lines)}],
            }
            if lang:
                node["attrs"] = {"language": lang}
            nodes.append(node)
            continue

        # heading
        if stripped.startswith("#"):
            level = 0
            while level < len(stripped) and stripped[level] == "#":
                level += 1
            level = min(level, 6)
            heading_text = stripped[level:].strip()
            nodes.append(
                {
                    "type": "heading",
                    "attrs": {"level": level},
                    "content": [{"type": "text", "text": heading_text}],
                }
            )
            i += 1
            continue

        # bullet list
        if stripped.startswith("- ") or stripped.startswith("* "):
            items: List[Dict] = []
            while i < len(lines) and (
                lines[i].strip().startswith("- ")
                or lines[i].strip().startswith("* ")
            ):
                item_text = lines[i].strip()[2:]
                items.append(
                    {
                        "type": "listItem",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": _parse_inline(item_text),
                            }
                        ],
                    }
                )
                i += 1
            nodes.append({"type": "bulletList", "content": items})
            continue

        # paragraph (default)
        nodes.append(
            {"type": "paragraph", "content": _parse_inline(stripped)}
        )
        i += 1

    return nodes


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_list_sections(args: argparse.Namespace) -> None:
    """Print a compact table of contents for the page."""
    base_url, email, token = get_auth()
    page_data = fetch_page(base_url, email, token, args.page_id)
    adf_doc = parse_adf_body(page_data)
    if not adf_doc:
        print("Error: could not parse ADF body.", file=sys.stderr)
        sys.exit(1)

    sections = identify_sections(adf_doc)
    total_nodes = len(adf_doc.get("content", []))
    total_bytes = len(json.dumps(adf_doc))

    print(f"Page: {page_data.get('title', '(unknown)')}")
    print(f"ADF size: {total_bytes:,} bytes  ({total_nodes} top-level nodes)")
    print(f"Sections: {len(sections)}\n")

    for idx, sec in enumerate(sections):
        indent = "  " * max(sec["level"] - 1, 0)
        tag = f"H{sec['level']}" if sec["level"] > 0 else "   "
        print(
            f"  [{idx}] {tag} {indent}{sec['heading']}  "
            f"({sec['node_count']} nodes, "
            f"idx {sec['start_index']}:{sec['end_index']})"
        )

    if args.json:
        print()
        print(json.dumps(sections, indent=2))


def cmd_get_section(args: argparse.Namespace) -> None:
    """Extract one section's ADF and print or save it."""
    base_url, email, token = get_auth()
    page_data = fetch_page(base_url, email, token, args.page_id)
    adf_doc = parse_adf_body(page_data)

    sections = identify_sections(adf_doc)
    section = find_section(sections, args.section)
    if section is None:
        print(
            f"Error: no section matching '{args.section}'.",
            file=sys.stderr,
        )
        print("Available sections:", file=sys.stderr)
        for s in sections:
            print(f"  - {s['heading']}", file=sys.stderr)
        sys.exit(1)

    nodes = extract_section_nodes(adf_doc, section)

    if args.output:
        with open(args.output, "w") as fh:
            json.dump(nodes, fh, indent=2)
        print(f"Section '{section['heading']}' written to {args.output}")
    else:
        print(json.dumps(nodes, indent=2))


def cmd_update_section(args: argparse.Namespace) -> None:
    """Replace a section's content and push the update."""
    base_url, email, token = get_auth()
    page_data = fetch_page(base_url, email, token, args.page_id)
    adf_doc = parse_adf_body(page_data)
    version = get_page_version(page_data)
    title = page_data.get("title", "")

    sections = identify_sections(adf_doc)
    section = find_section(sections, args.section)
    if section is None:
        print(
            f"Error: no section matching '{args.section}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(args.content_file, "r") as fh:
        raw = fh.read()

    if args.format == "adf":
        new_nodes = json.loads(raw)
        if not isinstance(new_nodes, list):
            new_nodes = [new_nodes]
    else:
        new_nodes = markdown_to_adf_nodes(raw)
        if new_nodes and new_nodes[0].get("type") != "heading":
            original_heading = adf_doc["content"][section["start_index"]]
            if original_heading.get("type") == "heading":
                new_nodes.insert(0, original_heading)

    new_adf = replace_section(adf_doc, section, new_nodes)
    msg = args.message or f"Updated section: {section['heading']}"
    result = update_page(
        base_url, email, token, args.page_id, title, new_adf, version, msg
    )

    new_ver = result.get("version", {}).get("number", "?")
    print(
        f"Updated section '{section['heading']}' in "
        f"'{result.get('title', args.page_id)}' (v{new_ver})"
    )


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser (extracted for testability)."""
    parser = argparse.ArgumentParser(
        description="Confluence Section Editor — surgical section-level page editing",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ls_p = sub.add_parser(
        "list-sections", help="List page sections (table of contents)"
    )
    ls_p.add_argument("--page-id", required=True, help="Confluence page ID")
    ls_p.add_argument(
        "--json", action="store_true", help="Also emit JSON output"
    )
    ls_p.set_defaults(func=cmd_list_sections)

    gs_p = sub.add_parser(
        "get-section", help="Extract one section's ADF content"
    )
    gs_p.add_argument("--page-id", required=True, help="Confluence page ID")
    gs_p.add_argument(
        "--section", required=True, help="Heading text (substring match)"
    )
    gs_p.add_argument("--output", "-o", help="Write ADF to this file")
    gs_p.set_defaults(func=cmd_get_section)

    us_p = sub.add_parser(
        "update-section", help="Replace a section's content"
    )
    us_p.add_argument("--page-id", required=True, help="Confluence page ID")
    us_p.add_argument(
        "--section", required=True, help="Heading text (substring match)"
    )
    us_p.add_argument(
        "--content-file", required=True, help="File with new content"
    )
    us_p.add_argument(
        "--format",
        choices=["markdown", "adf"],
        default="markdown",
        help="Content file format (default: markdown)",
    )
    us_p.add_argument("--message", "-m", help="Version message")
    us_p.set_defaults(func=cmd_update_section)

    return parser


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
