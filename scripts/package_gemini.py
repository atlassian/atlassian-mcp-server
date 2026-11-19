#!/usr/bin/env python3
"""Build the standalone Gemini Agent package without changing shared client files."""

import argparse
import json
from pathlib import Path
import re
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parent.parent


def build(output, root=ROOT):
    manifest = json.loads((root / '.gemini-plugin/plugin.json').read_text())
    selected = []
    for value in manifest['skills']:
        match = re.fullmatch(r'\./skills/([a-z0-9-]+)/SKILL\.md', value)
        if not match:
            raise ValueError(f'Invalid Gemini skill path: {value}')
        selected.append(match[1])
    if not selected or len(selected) != len(set(selected)):
        raise ValueError('Gemini skills must be nonempty and unique')

    names = {name: name if name.startswith('atlassian-') else 'atlassian-' + name
             for name in selected}
    if len(set(names.values())) != len(names):
        raise ValueError('Partner-prefixed skill names must be unique')
    # Rewrite only complete skill identifiers in Markdown, including sibling links.
    identifiers = re.compile(r'(?<![\w-])(' + '|'.join(map(re.escape, sorted(names, key=len, reverse=True))) + r')(?![\w-])')

    with tempfile.TemporaryDirectory(prefix='atlassian-gemini-') as temp:
        package = Path(temp)
        for name in selected:
            source = root / 'skills' / name
            overlay = root / 'gemini' / 'overrides' / name
            for directory in [source, overlay]:
                if directory.is_symlink() or not directory.is_dir():
                    raise ValueError(f'Missing skill directory or unsupported symlink: {directory}')
                for path in sorted(directory.rglob('*')):
                    if path.is_symlink():
                        raise ValueError(f'Symlinks cannot be packaged: {path}')
                    if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc' or path.name == '.DS_Store':
                        continue
                    target = package / 'skills' / names[name] / path.relative_to(directory)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if path.suffix == '.md':
                        text = identifiers.sub(lambda match: names[match[0]], path.read_text())
                        target.write_text(text)
                    else:
                        target.write_bytes(path.read_bytes())
            entry = package / 'skills' / names[name] / 'SKILL.md'
            text = entry.read_text()
            if not text.startswith('---\n') or len(text.split('---', 2)) != 3:
                raise ValueError(f'Missing frontmatter: {name}')
            body = text.split('---', 2)[2]
            if len(text.splitlines()) > 500 or len(body.split()) >= 3000:
                raise ValueError(f'Gemini skill exceeds 500 lines or 3,000 body words: {name}')

        manifest['skills'] = [f'./skills/{names[name]}/SKILL.md' for name in selected]
        manifest['mcpServers'] = './.mcp.json'
        (package / '.gemini-plugin').mkdir()
        (package / '.gemini-plugin/plugin.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
        config = json.loads((root / '.mcp.json').read_text())
        config['mcpServers']['atlassian']['url'] = 'https://mcp.atlassian.com/v2/mcp?tools=all'
        (package / '.mcp.json').write_text(json.dumps(config, indent=2) + '\n')
        (package / 'LICENSE').write_bytes((root / 'LICENSE').read_bytes())
        (package / 'README.md').write_text(
            '# Atlassian MCP for Gemini Agent\n\n'
            'Connect to Jira, Confluence and Rovo Search through the flat v2 MCP surface. '
            'Available operations depend on OAuth consent and user permissions. '
            'Code-search workflows are not included in this package.\n\n'
            'Skills call exposed operations directly and report unavailable checks. '
            'Use the bundled Python renderers, examples and design kits for requested offline HTML reports; '
            'no package installs or asset downloads are needed. '
            'Publishing and sharing require available tools and user authorization.\n'
        )
        if (root / 'CHANGELOG.md').is_file():
            (package / 'CHANGELOG.md').write_bytes((root / 'CHANGELOG.md').read_bytes())
        output = Path(output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(package.rglob('*')):
                if path.is_file():
                    info = zipfile.ZipInfo(path.relative_to(package).as_posix(), (1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, path.read_bytes())
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/atlassian-gemini.zip')
    args = parser.parse_args()
    print(build(args.output))
