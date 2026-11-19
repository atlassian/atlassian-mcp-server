#!/usr/bin/env python3
"""Check the delivered Gemini archive, including offline reports from extracted files."""

import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

from package_gemini import ROOT, build


def check():
    shared_config = (ROOT / '.mcp.json').read_bytes()
    with tempfile.TemporaryDirectory(prefix='test-gemini-package-') as temp:
        temp = Path(temp)
        archive = build(temp / 'gemini.zip')
        first_bytes = archive.read_bytes()
        assert build(archive).read_bytes() == first_bytes, 'Archive must be reproducible'
        with zipfile.ZipFile(archive) as zipped:
            assert '.mcp.json' in zipped.namelist()
            assert '.gemini-plugin/plugin.json' in zipped.namelist()
            assert not any(name.startswith('.claude-plugin/') for name in zipped.namelist())
            zipped.extractall(temp / 'package')
        package = temp / 'package'
        manifest = json.loads((package / '.gemini-plugin/plugin.json').read_text())
        source = json.loads((ROOT / '.gemini-plugin/plugin.json').read_text())
        assert manifest['name'] == 'atlassian'
        assert manifest['description'] == source['description']
        assert len(manifest['skills']) == 13
        assert not any(name in str(manifest['skills']) for name in ['atlassian-mcp-code-search', 'how-it-works'])
        assert json.loads((package / '.mcp.json').read_text())['mcpServers']['atlassian']['url'] == 'https://mcp.atlassian.com/v2/mcp?tools=all'
        for value in manifest['skills']:
            entry = package / value
            text = entry.read_text()
            name = re.search(r'^name:\s*["\']?([a-z0-9-]+)', text, re.M)[1]
            assert name == entry.parent.name and name.startswith('atlassian-')
            assert len(text.splitlines()) <= 500
            assert len(text.split('---', 2)[2].split()) < 3000
        for path in package.rglob('*.py'):
            ast.parse(path.read_text(), filename=str(path))
        for name in ['assess-release', 'before-you-start', 'catch-up', 'decision-trace', 'dependency-map']:
            skill = package / 'skills' / ('atlassian-' + name)
            output = temp / (name + '.html')
            subprocess.run([sys.executable, '-I', '-B', str(skill / 'render.py'), str(skill / 'example.json'), str(output)], check=True, capture_output=True)
            assert '<html' in output.read_text().lower(), name
        for kit in ['render_kit', 'render_kit_next']:
            assert (package / 'skills/atlassian-design' / kit / '__init__.py').is_file()
        for path in package.rglob('*.md'):
            fenced = False
            for line in path.read_text().splitlines():
                if line.lstrip().startswith('```'):
                    fenced = not fenced
                    continue
                if fenced:
                    continue
                for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', line):
                    if re.match(r'^(https?://|mailto:|#)', target):
                        continue
                    local = target.split('#')[0]
                    assert not local or (path.parent / local).exists(), (path, target)
    assert (ROOT / '.mcp.json').read_bytes() == shared_config, 'Builder changed shared client config'
    with tempfile.TemporaryDirectory(prefix='test-gemini-invalid-') as temp:
        root = Path(temp)
        (root / '.gemini-plugin').mkdir()
        manifest = {'skills': ['../outside/SKILL.md']}
        (root / '.gemini-plugin/plugin.json').write_text(json.dumps(manifest))
        try:
            build(root / 'bad.zip', root)
        except ValueError:
            pass
        else:
            raise AssertionError('Builder accepted a skill outside the package')
        manifest['skills'] = ['./skills/example/SKILL.md']
        (root / '.gemini-plugin/plugin.json').write_text(json.dumps(manifest))
        source = root / 'skills/example'
        overlay = root / 'gemini/overrides/example'
        source.mkdir(parents=True)
        overlay.mkdir(parents=True)
        frontmatter = '---\nname: example\ndescription: Example skill\n---\n'
        (source / 'SKILL.md').write_text(frontmatter)
        for body in ['line\n' * 501, 'word ' * 3000]:
            (overlay / 'SKILL.md').write_text(frontmatter + body)
            try:
                build(root / 'bad.zip', root)
            except ValueError:
                pass
            else:
                raise AssertionError('Builder accepted an oversized skill')
    print('Gemini package checks passed: 13 skills, standalone layout, size limits and five offline reports.')


if __name__ == '__main__':
    check()
