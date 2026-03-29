#!/usr/bin/env python3
"""
Tests for confluence_section_editor.py

Covers:
  - ADF section identification (core algorithm)
  - Section search / extraction / replacement ("tree surgery")
  - Markdown → ADF conversion
  - Input sanitisation
  - Auth and page-data helpers
  - CLI argument parsing
  - End-to-end command smoke tests (HTTP mocked)

Run:
    python -m pytest test_confluence_section_editor.py -v
    # or, without pytest:
    python -m unittest test_confluence_section_editor -v
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from io import BytesIO
from typing import Dict, List
from unittest.mock import MagicMock, patch

from confluence_section_editor import (
    _heading_text,
    _make_auth_header,
    _parse_inline,
    _sanitize_page_id,
    build_parser,
    extract_section_nodes,
    find_section,
    get_auth,
    get_page_version,
    identify_sections,
    markdown_to_adf_nodes,
    parse_adf_body,
    replace_section,
)


# ── Test fixtures ────────────────────────────────────────────────────────

def _h(level: int, text: str) -> Dict:
    """Shorthand: build an ADF heading node."""
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [{"type": "text", "text": text}],
    }


def _p(text: str) -> Dict:
    """Shorthand: build an ADF paragraph node."""
    return {
        "type": "paragraph",
        "content": [{"type": "text", "text": text}],
    }


def _doc(*nodes: Dict) -> Dict:
    """Shorthand: wrap nodes in an ADF root document."""
    return {"version": 1, "type": "doc", "content": list(nodes)}


REALISTIC_DOC = _doc(
    _p("Preamble paragraph"),
    _h(1, "Introduction"),
    _p("Intro body text"),
    _p("More intro text"),
    _h(2, "Background"),
    _p("Background details"),
    _h(2, "Motivation"),
    _p("Motivation details"),
    _h(1, "Design"),
    _p("Design overview"),
    _h(2, "Architecture"),
    _p("Architecture details"),
    _p("Architecture diagram ref"),
    _h(2, "Data Model"),
    _p("Data model text"),
    _h(1, "Conclusion"),
    _p("Conclusion text"),
)


# ── identify_sections ────────────────────────────────────────────────────

class TestIdentifySections(unittest.TestCase):
    """Core algorithm: splitting an ADF doc into heading-delimited sections."""

    def test_empty_document(self):
        doc = _doc()
        self.assertEqual(identify_sections(doc), [])

    def test_no_headings(self):
        doc = _doc(_p("Hello"), _p("World"))
        sections = identify_sections(doc)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["level"], 0)
        self.assertEqual(sections[0]["start_index"], 0)
        self.assertEqual(sections[0]["end_index"], 2)
        self.assertEqual(sections[0]["node_count"], 2)

    def test_single_heading_no_preamble(self):
        doc = _doc(_h(1, "Only Section"), _p("Body"))
        sections = identify_sections(doc)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["heading"], "Only Section")
        self.assertEqual(sections[0]["level"], 1)
        self.assertEqual(sections[0]["start_index"], 0)
        self.assertEqual(sections[0]["end_index"], 2)
        self.assertEqual(sections[0]["node_count"], 2)

    def test_preamble_detected(self):
        doc = _doc(_p("Preamble"), _h(1, "Section 1"), _p("Body"))
        sections = identify_sections(doc)
        self.assertEqual(len(sections), 2)
        self.assertIn("preamble", sections[0]["heading"].lower())
        self.assertEqual(sections[0]["start_index"], 0)
        self.assertEqual(sections[0]["end_index"], 1)
        self.assertEqual(sections[1]["heading"], "Section 1")
        self.assertEqual(sections[1]["start_index"], 1)
        self.assertEqual(sections[1]["end_index"], 3)

    def test_consecutive_headings(self):
        doc = _doc(_h(1, "A"), _h(1, "B"), _h(1, "C"))
        sections = identify_sections(doc)
        self.assertEqual(len(sections), 3)
        for sec in sections:
            self.assertEqual(sec["node_count"], 1)

    def test_realistic_document_section_count(self):
        sections = identify_sections(REALISTIC_DOC)
        headings = [s["heading"] for s in sections]
        self.assertIn("Introduction", headings)
        self.assertIn("Design", headings)
        self.assertIn("Conclusion", headings)
        preamble = [s for s in sections if s["level"] == 0]
        self.assertEqual(len(preamble), 1, "Expected exactly one preamble")

    def test_realistic_document_indices_are_contiguous(self):
        sections = identify_sections(REALISTIC_DOC)
        total_nodes = len(REALISTIC_DOC["content"])
        self.assertEqual(sections[0]["start_index"], 0)
        self.assertEqual(sections[-1]["end_index"], total_nodes)
        for a, b in zip(sections, sections[1:]):
            self.assertEqual(
                a["end_index"],
                b["start_index"],
                f"Gap between '{a['heading']}' and '{b['heading']}'",
            )

    def test_heading_with_no_body_nodes(self):
        doc = _doc(_h(1, "Empty"), _h(1, "Also Empty"))
        sections = identify_sections(doc)
        self.assertEqual(sections[0]["node_count"], 1)
        self.assertEqual(sections[1]["node_count"], 1)

    def test_heading_level_preserved(self):
        doc = _doc(_h(3, "Deep"), _p("Body"))
        sections = identify_sections(doc)
        self.assertEqual(sections[0]["level"], 3)

    def test_missing_content_key(self):
        self.assertEqual(identify_sections({}), [])
        self.assertEqual(identify_sections({"content": []}), [])


# ── _heading_text ────────────────────────────────────────────────────────

class TestHeadingText(unittest.TestCase):

    def test_simple_text(self):
        node = _h(1, "Hello")
        self.assertEqual(_heading_text(node), "Hello")

    def test_multi_run_text(self):
        node = {
            "type": "heading",
            "attrs": {"level": 1},
            "content": [
                {"type": "text", "text": "Hello "},
                {"type": "text", "text": "World"},
            ],
        }
        self.assertEqual(_heading_text(node), "Hello World")

    def test_mixed_inline_nodes(self):
        node = {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [
                {"type": "text", "text": "Status: "},
                {"type": "status", "attrs": {"text": "Done"}},
                {"type": "text", "text": " item"},
            ],
        }
        self.assertEqual(_heading_text(node), "Status:  item")

    def test_empty_content(self):
        node = {"type": "heading", "content": []}
        self.assertEqual(_heading_text(node), "")

    def test_no_content_key(self):
        node = {"type": "heading"}
        self.assertEqual(_heading_text(node), "")


# ── find_section ─────────────────────────────────────────────────────────

class TestFindSection(unittest.TestCase):

    def setUp(self):
        self.sections = identify_sections(REALISTIC_DOC)

    def test_exact_match(self):
        result = find_section(self.sections, "Introduction")
        self.assertIsNotNone(result)
        self.assertEqual(result["heading"], "Introduction")

    def test_case_insensitive(self):
        result = find_section(self.sections, "introduction")
        self.assertIsNotNone(result)
        self.assertEqual(result["heading"], "Introduction")

    def test_substring_match(self):
        result = find_section(self.sections, "Conclu")
        self.assertIsNotNone(result)
        self.assertEqual(result["heading"], "Conclusion")

    def test_no_match(self):
        self.assertIsNone(find_section(self.sections, "Nonexistent"))

    def test_exact_preferred_over_substring(self):
        sections = [
            {"heading": "Design", "level": 1, "start_index": 0, "end_index": 1, "node_count": 1},
            {"heading": "Design Overview", "level": 2, "start_index": 1, "end_index": 2, "node_count": 1},
        ]
        result = find_section(sections, "Design")
        self.assertEqual(result["heading"], "Design")

    def test_empty_sections_list(self):
        self.assertIsNone(find_section([], "anything"))


# ── extract_section_nodes ────────────────────────────────────────────────

class TestExtractSectionNodes(unittest.TestCase):

    def test_single_section(self):
        doc = _doc(_h(1, "Title"), _p("Body1"), _p("Body2"))
        sections = identify_sections(doc)
        nodes = extract_section_nodes(doc, sections[0])
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0]["type"], "heading")
        self.assertEqual(nodes[1]["type"], "paragraph")

    def test_preamble_extraction(self):
        doc = _doc(_p("Pre"), _h(1, "H"), _p("Body"))
        sections = identify_sections(doc)
        preamble = [s for s in sections if s["level"] == 0][0]
        nodes = extract_section_nodes(doc, preamble)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["type"], "paragraph")

    def test_middle_section(self):
        sections = identify_sections(REALISTIC_DOC)
        design_sec = find_section(sections, "Design")
        nodes = extract_section_nodes(REALISTIC_DOC, design_sec)
        self.assertTrue(len(nodes) >= 1)
        self.assertEqual(nodes[0], REALISTIC_DOC["content"][design_sec["start_index"]])


# ── replace_section ──────────────────────────────────────────────────────

class TestReplaceSection(unittest.TestCase):

    def test_replace_preserves_surrounding(self):
        doc = _doc(
            _p("Before"),
            _h(1, "Target"),
            _p("Old body"),
            _h(1, "After"),
            _p("Keep me"),
        )
        sections = identify_sections(doc)
        target = find_section(sections, "Target")
        new_nodes = [_h(1, "Target"), _p("New body")]
        result = replace_section(doc, target, new_nodes)
        self.assertEqual(result["content"][0], _p("Before"))
        self.assertEqual(result["content"][-1], _p("Keep me"))
        self.assertEqual(result["content"][-2], _h(1, "After"))

    def test_replace_middle_section(self):
        doc = _doc(
            _h(1, "A"), _p("a-body"),
            _h(1, "B"), _p("b-body"),
            _h(1, "C"), _p("c-body"),
        )
        sections = identify_sections(doc)
        sec_b = find_section(sections, "B")
        replacement = [_h(1, "B"), _p("REPLACED")]
        result = replace_section(doc, sec_b, replacement)
        self.assertEqual(len(result["content"]), 6)
        self.assertEqual(result["content"][2], _h(1, "B"))
        self.assertEqual(result["content"][3], _p("REPLACED"))
        self.assertEqual(result["content"][0], _h(1, "A"))
        self.assertEqual(result["content"][4], _h(1, "C"))

    def test_replace_with_fewer_nodes(self):
        doc = _doc(
            _h(1, "A"), _p("a1"), _p("a2"), _p("a3"),
            _h(1, "B"), _p("b"),
        )
        sections = identify_sections(doc)
        sec_a = find_section(sections, "A")
        result = replace_section(doc, sec_a, [_h(1, "A")])
        self.assertEqual(len(result["content"]), 3)
        self.assertEqual(result["content"][0], _h(1, "A"))
        self.assertEqual(result["content"][1], _h(1, "B"))

    def test_replace_with_more_nodes(self):
        doc = _doc(_h(1, "A"), _h(1, "B"))
        sections = identify_sections(doc)
        sec_a = find_section(sections, "A")
        result = replace_section(doc, sec_a, [_h(1, "A"), _p("x"), _p("y")])
        self.assertEqual(len(result["content"]), 4)
        self.assertEqual(result["content"][-1], _h(1, "B"))

    def test_replace_preserves_version(self):
        doc = {"version": 1, "type": "doc", "content": [_h(1, "A"), _p("a")]}
        sections = identify_sections(doc)
        result = replace_section(doc, sections[0], [_h(1, "A")])
        self.assertEqual(result["version"], 1)
        self.assertEqual(result["type"], "doc")

    def test_replace_does_not_mutate_original(self):
        doc = _doc(_h(1, "A"), _p("original"))
        original_content_len = len(doc["content"])
        sections = identify_sections(doc)
        replace_section(doc, sections[0], [_h(1, "A"), _p("new"), _p("extra")])
        self.assertEqual(len(doc["content"]), original_content_len)

    def test_round_trip_identity(self):
        """Replacing a section with its own nodes produces an identical doc."""
        sections = identify_sections(REALISTIC_DOC)
        for sec in sections:
            original_nodes = extract_section_nodes(REALISTIC_DOC, sec)
            result = replace_section(REALISTIC_DOC, sec, original_nodes)
            self.assertEqual(
                result["content"],
                REALISTIC_DOC["content"],
                f"Round-trip failed for section '{sec['heading']}'",
            )


# ── _sanitize_page_id ───────────────────────────────────────────────────

class TestSanitizePageId(unittest.TestCase):

    def test_valid_numeric(self):
        self.assertEqual(_sanitize_page_id("12345"), "12345")

    def test_valid_large_number(self):
        self.assertEqual(_sanitize_page_id("9" * 20), "9" * 20)

    def test_rejects_alpha(self):
        with self.assertRaises(ValueError):
            _sanitize_page_id("abc")

    def test_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            _sanitize_page_id("../etc/passwd")

    def test_rejects_mixed(self):
        with self.assertRaises(ValueError):
            _sanitize_page_id("123abc")

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            _sanitize_page_id("")

    def test_rejects_special_chars(self):
        for bad in ["12 34", "12/34", "12;34", "12&34"]:
            with self.assertRaises(ValueError, msg=f"Should reject '{bad}'"):
                _sanitize_page_id(bad)


# ── _make_auth_header ────────────────────────────────────────────────────

class TestMakeAuthHeader(unittest.TestCase):

    def test_basic_encoding(self):
        header = _make_auth_header("user@example.com", "token123")
        self.assertTrue(header.startswith("Basic "))
        import base64
        decoded = base64.b64decode(header.split(" ", 1)[1]).decode()
        self.assertEqual(decoded, "user@example.com:token123")


# ── get_page_version ─────────────────────────────────────────────────────

class TestGetPageVersion(unittest.TestCase):

    def test_normal(self):
        self.assertEqual(get_page_version({"version": {"number": 5}}), 5)

    def test_missing_version(self):
        self.assertEqual(get_page_version({}), 1)

    def test_string_number(self):
        self.assertEqual(get_page_version({"version": {"number": "3"}}), 3)


# ── parse_adf_body ──────────────────────────────────────────────────────

class TestParseAdfBody(unittest.TestCase):

    def test_string_value(self):
        adf = {"version": 1, "type": "doc", "content": []}
        page = {"body": {"atlas_doc_format": {"value": json.dumps(adf)}}}
        self.assertEqual(parse_adf_body(page), adf)

    def test_dict_value(self):
        adf = {"version": 1, "type": "doc", "content": []}
        page = {"body": {"atlas_doc_format": {"value": adf}}}
        self.assertEqual(parse_adf_body(page), adf)

    def test_missing_body(self):
        self.assertIsNone(parse_adf_body({}))

    def test_missing_atlas_doc_format(self):
        self.assertIsNone(parse_adf_body({"body": {}}))


# ── get_auth ─────────────────────────────────────────────────────────────

class TestGetAuth(unittest.TestCase):

    @patch.dict(os.environ, {
        "CONFLUENCE_URL": "https://site.atlassian.net/",
        "CONFLUENCE_EMAIL": "a@b.com",
        "CONFLUENCE_API_TOKEN": "tok",
    })
    def test_success(self):
        url, email, token = get_auth()
        self.assertEqual(url, "https://site.atlassian.net")
        self.assertEqual(email, "a@b.com")
        self.assertEqual(token, "tok")

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_vars_exits(self):
        with self.assertRaises(SystemExit):
            get_auth()

    @patch.dict(os.environ, {
        "CONFLUENCE_URL": "https://x.atlassian.net",
        "CONFLUENCE_EMAIL": "",
        "CONFLUENCE_API_TOKEN": "tok",
    })
    def test_empty_email_exits(self):
        with self.assertRaises(SystemExit):
            get_auth()


# ── Markdown → ADF ──────────────────────────────────────────────────────

class TestParseInline(unittest.TestCase):

    def test_plain_text(self):
        nodes = _parse_inline("hello world")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["text"], "hello world")
        self.assertNotIn("marks", nodes[0])

    def test_bold(self):
        nodes = _parse_inline("say **bold** things")
        texts = [n["text"] for n in nodes]
        self.assertIn("bold", texts)
        bold_node = [n for n in nodes if n["text"] == "bold"][0]
        self.assertEqual(bold_node["marks"], [{"type": "strong"}])

    def test_inline_code(self):
        nodes = _parse_inline("use `code` here")
        code_node = [n for n in nodes if n.get("marks")][0]
        self.assertEqual(code_node["text"], "code")
        self.assertEqual(code_node["marks"], [{"type": "code"}])

    def test_italic(self):
        nodes = _parse_inline("an *italic* word")
        italic_node = [n for n in nodes if n.get("marks")][0]
        self.assertEqual(italic_node["text"], "italic")
        self.assertEqual(italic_node["marks"], [{"type": "em"}])

    def test_empty_string(self):
        nodes = _parse_inline("")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["text"], "")


class TestMarkdownToAdf(unittest.TestCase):

    def test_heading(self):
        nodes = markdown_to_adf_nodes("# Title")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["type"], "heading")
        self.assertEqual(nodes[0]["attrs"]["level"], 1)
        self.assertEqual(nodes[0]["content"][0]["text"], "Title")

    def test_heading_levels(self):
        for level in range(1, 7):
            md = "#" * level + " Heading"
            nodes = markdown_to_adf_nodes(md)
            self.assertEqual(nodes[0]["attrs"]["level"], level)

    def test_paragraph(self):
        nodes = markdown_to_adf_nodes("Just a paragraph.")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["type"], "paragraph")

    def test_bullet_list_dash(self):
        md = "- Item A\n- Item B\n- Item C"
        nodes = markdown_to_adf_nodes(md)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["type"], "bulletList")
        self.assertEqual(len(nodes[0]["content"]), 3)

    def test_bullet_list_asterisk(self):
        md = "* One\n* Two"
        nodes = markdown_to_adf_nodes(md)
        self.assertEqual(nodes[0]["type"], "bulletList")
        self.assertEqual(len(nodes[0]["content"]), 2)

    def test_code_block(self):
        md = "```python\nprint('hi')\n```"
        nodes = markdown_to_adf_nodes(md)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["type"], "codeBlock")
        self.assertEqual(nodes[0]["attrs"]["language"], "python")
        self.assertEqual(nodes[0]["content"][0]["text"], "print('hi')")

    def test_code_block_no_language(self):
        md = "```\nsome code\n```"
        nodes = markdown_to_adf_nodes(md)
        self.assertNotIn("attrs", nodes[0])

    def test_empty_input(self):
        self.assertEqual(markdown_to_adf_nodes(""), [])

    def test_blank_lines_skipped(self):
        md = "Para 1\n\n\nPara 2"
        nodes = markdown_to_adf_nodes(md)
        self.assertEqual(len(nodes), 2)
        self.assertTrue(all(n["type"] == "paragraph" for n in nodes))

    def test_mixed_content(self):
        md = "# Title\n\nSome text.\n\n- A\n- B\n\n```\ncode\n```"
        nodes = markdown_to_adf_nodes(md)
        types = [n["type"] for n in nodes]
        self.assertEqual(types, ["heading", "paragraph", "bulletList", "codeBlock"])


# ── CLI parser ───────────────────────────────────────────────────────────

class TestBuildParser(unittest.TestCase):

    def test_list_sections(self):
        parser = build_parser()
        args = parser.parse_args(["list-sections", "--page-id", "123"])
        self.assertEqual(args.command, "list-sections")
        self.assertEqual(args.page_id, "123")

    def test_get_section(self):
        parser = build_parser()
        args = parser.parse_args([
            "get-section", "--page-id", "456", "--section", "Intro",
        ])
        self.assertEqual(args.section, "Intro")

    def test_update_section_defaults(self):
        parser = build_parser()
        args = parser.parse_args([
            "update-section", "--page-id", "789",
            "--section", "Design", "--content-file", "new.md",
        ])
        self.assertEqual(args.format, "markdown")
        self.assertIsNone(args.message)

    def test_update_section_explicit_format(self):
        parser = build_parser()
        args = parser.parse_args([
            "update-section", "--page-id", "789",
            "--section", "X", "--content-file", "f.json", "--format", "adf",
        ])
        self.assertEqual(args.format, "adf")

    def test_missing_required_arg(self):
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["list-sections"])


# ── End-to-end command smoke tests (I/O mocked) ─────────────────────────

def _fake_page_response(adf_doc: Dict, title: str = "Test Page") -> Dict:
    """Build a fake Confluence page API response."""
    return {
        "id": "99999",
        "title": title,
        "version": {"number": 3},
        "body": {
            "atlas_doc_format": {
                "value": json.dumps(adf_doc),
            }
        },
    }


def _mock_urlopen(response_data: Dict):
    """Return a context-manager mock for urllib.request.urlopen."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


_ENV = {
    "CONFLUENCE_URL": "https://test.atlassian.net",
    "CONFLUENCE_EMAIL": "test@test.com",
    "CONFLUENCE_API_TOKEN": "fake-token",
}


class TestCmdListSections(unittest.TestCase):

    @patch.dict(os.environ, _ENV)
    @patch("confluence_section_editor.urlopen")
    def test_prints_sections(self, mock_open):
        doc = _doc(_h(1, "Alpha"), _p("body"), _h(1, "Beta"), _p("body"))
        mock_open.return_value = _mock_urlopen(_fake_page_response(doc))
        args = build_parser().parse_args(["list-sections", "--page-id", "100"])
        from io import StringIO
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            args.func(args)
        finally:
            sys.stdout = old_stdout
        output = captured.getvalue()
        self.assertIn("Alpha", output)
        self.assertIn("Beta", output)
        self.assertIn("Sections: 2", output)


class TestCmdGetSection(unittest.TestCase):

    @patch.dict(os.environ, _ENV)
    @patch("confluence_section_editor.urlopen")
    def test_prints_json(self, mock_open):
        doc = _doc(_h(1, "Target"), _p("content"))
        mock_open.return_value = _mock_urlopen(_fake_page_response(doc))
        args = build_parser().parse_args([
            "get-section", "--page-id", "100", "--section", "Target",
        ])
        from io import StringIO
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            args.func(args)
        finally:
            sys.stdout = old_stdout
        parsed = json.loads(captured.getvalue())
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["type"], "heading")

    @patch.dict(os.environ, _ENV)
    @patch("confluence_section_editor.urlopen")
    def test_missing_section_exits(self, mock_open):
        doc = _doc(_h(1, "Other"), _p("body"))
        mock_open.return_value = _mock_urlopen(_fake_page_response(doc))
        args = build_parser().parse_args([
            "get-section", "--page-id", "100", "--section", "Nonexistent",
        ])
        with self.assertRaises(SystemExit):
            args.func(args)


class TestCmdUpdateSection(unittest.TestCase):

    @patch.dict(os.environ, _ENV)
    @patch("confluence_section_editor.urlopen")
    def test_update_calls_put(self, mock_open):
        doc = _doc(_h(1, "Target"), _p("old"))
        updated_resp = _fake_page_response(doc, "Test Page")
        updated_resp["version"]["number"] = 4

        call_count = {"n": 0}
        def side_effect(req):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _mock_urlopen(_fake_page_response(doc))
            return _mock_urlopen(updated_resp)

        mock_open.side_effect = side_effect

        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("New content paragraph.\n")
            tmp_path = f.name

        try:
            args = build_parser().parse_args([
                "update-section", "--page-id", "100",
                "--section", "Target", "--content-file", tmp_path,
            ])
            from io import StringIO
            captured = StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                args.func(args)
            finally:
                sys.stdout = old_stdout
            output = captured.getvalue()
            self.assertIn("Updated section", output)
            self.assertEqual(call_count["n"], 2)
        finally:
            os.unlink(tmp_path)

    @patch.dict(os.environ, _ENV)
    @patch("confluence_section_editor.urlopen")
    def test_update_adf_format(self, mock_open):
        doc = _doc(_h(1, "Target"), _p("old"))
        updated_resp = _fake_page_response(doc)
        updated_resp["version"]["number"] = 4

        call_count = {"n": 0}
        def side_effect(req):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _mock_urlopen(_fake_page_response(doc))
            return _mock_urlopen(updated_resp)

        mock_open.side_effect = side_effect

        import tempfile
        adf_nodes = [_h(1, "Target"), _p("new via adf")]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(adf_nodes, f)
            tmp_path = f.name

        try:
            args = build_parser().parse_args([
                "update-section", "--page-id", "100",
                "--section", "Target", "--content-file", tmp_path,
                "--format", "adf",
            ])
            from io import StringIO
            captured = StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                args.func(args)
            finally:
                sys.stdout = old_stdout
            self.assertIn("Updated section", captured.getvalue())
        finally:
            os.unlink(tmp_path)


# ── Large-document stress test (issue #106 scenario) ────────────────────

class TestLargeDocumentScenario(unittest.TestCase):
    """
    Simulate the real-world scenario from issue #106:
    a 50+ KB ADF page with many sections, tables, and code blocks.
    Verify section identification + replacement works at scale.
    """

    @staticmethod
    def _build_large_doc(num_sections: int = 25) -> Dict:
        nodes: List[Dict] = [_p("Preamble: RFC-style large document")]
        for i in range(num_sections):
            nodes.append(_h(1, f"Section {i}"))
            for j in range(8):
                nodes.append(_p(f"Content paragraph {j} of section {i}. " * 10))
            nodes.append({
                "type": "codeBlock",
                "attrs": {"language": "python"},
                "content": [{"type": "text", "text": f"def func_{i}():\n    pass\n" * 5}],
            })
        return _doc(*nodes)

    def test_section_count(self):
        doc = self._build_large_doc(25)
        sections = identify_sections(doc)
        headings = [s for s in sections if s["level"] > 0]
        self.assertEqual(len(headings), 25)

    def test_document_exceeds_threshold(self):
        doc = self._build_large_doc(25)
        size_bytes = len(json.dumps(doc))
        self.assertGreater(size_bytes, 40_000, "Doc should exceed 40 KB")

    def test_replace_one_section_preserves_rest(self):
        doc = self._build_large_doc(25)
        original_len = len(doc["content"])
        sections = identify_sections(doc)
        target = find_section(sections, "Section 12")
        self.assertIsNotNone(target)

        replacement = [_h(1, "Section 12"), _p("REPLACED")]
        result = replace_section(doc, target, replacement)

        old_count = target["node_count"]
        expected_len = original_len - old_count + 2
        self.assertEqual(len(result["content"]), expected_len)

        sec0_nodes = extract_section_nodes(
            result,
            find_section(identify_sections(result), "Section 0"),
        )
        original_sec0 = extract_section_nodes(
            doc,
            find_section(sections, "Section 0"),
        )
        self.assertEqual(sec0_nodes, original_sec0)

    def test_indices_contiguous_after_replace(self):
        doc = self._build_large_doc(10)
        sections = identify_sections(doc)
        target = find_section(sections, "Section 5")
        result = replace_section(doc, target, [_h(1, "Section 5"), _p("new")])
        new_sections = identify_sections(result)
        for a, b in zip(new_sections, new_sections[1:]):
            self.assertEqual(
                a["end_index"], b["start_index"],
                f"Gap after replacing section 5: '{a['heading']}' -> '{b['heading']}'",
            )


# ── Markdown heading preservation on update ──────────────────────────────

class TestHeadingPreservation(unittest.TestCase):
    """When updating with markdown that lacks a heading, the original is kept."""

    def test_heading_auto_prepended(self):
        doc = _doc(_h(2, "Original Title"), _p("old"))
        sections = identify_sections(doc)
        sec = sections[0]
        new_nodes = markdown_to_adf_nodes("New paragraph only.")
        if new_nodes and new_nodes[0].get("type") != "heading":
            original_heading = doc["content"][sec["start_index"]]
            if original_heading.get("type") == "heading":
                new_nodes.insert(0, original_heading)
        result = replace_section(doc, sec, new_nodes)
        self.assertEqual(result["content"][0]["type"], "heading")
        self.assertEqual(
            result["content"][0]["content"][0]["text"], "Original Title"
        )

    def test_heading_not_duplicated_when_present(self):
        doc = _doc(_h(2, "Title"), _p("old"))
        sections = identify_sections(doc)
        sec = sections[0]
        new_nodes = markdown_to_adf_nodes("## Title\n\nNew paragraph.")
        result = replace_section(doc, sec, new_nodes)
        headings = [n for n in result["content"] if n["type"] == "heading"]
        self.assertEqual(len(headings), 1)


if __name__ == "__main__":
    unittest.main()
