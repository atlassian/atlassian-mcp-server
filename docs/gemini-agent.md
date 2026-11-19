# Package Atlassian MCP for Gemini Agent

Build the standalone ingestion ZIP from the repository root:

```bash
python3 -B scripts/package_gemini.py
```

The output is `dist/atlassian-gemini.zip`. Supply that package for Gemini Agent ingestion rather than ingesting the shared repository root directly. The repository's `.gemini-plugin/plugin.json` selects the source skills. The builder copies their complete support files, applies the instructions in `gemini/overrides/`, and creates a standalone root with its own `.gemini-plugin/plugin.json`, `.mcp.json`, `skills/`, README and license. It adds the `atlassian-` partner prefix to skill names and Markdown references. It does not change the shared skills, shared MCP configuration or other client manifests.

The package uses `https://mcp.atlassian.com/v2/mcp?tools=all`. This exposes permitted operations directly; OAuth consent and user permissions still control access. Each packaged workflow uses the scoped Jira/Confluence collection instructions and reports unavailable evidence. The shared repository skills continue to support their existing clients and broader capabilities.

## Included workflows

The package contains 13 skills: the six Jira/Confluence workflows, assess-release, before-you-start, catch-up, decision-trace, dependency-map, and the teamwork-graph-context and atlassian-design dependencies. Code search and how-it-works remain available to other clients but are excluded from this package.

Graph-enabled clients retain the unchanged shared skills. A missing products field means unknown coverage; actual tool availability and permission responses determine whether a check can run. An unavailable applicable release check remains an evidence gap, not a Ready or Not used result.

Both design kits, logos, workflow renderers, example data and report references are included. Requested HTML reports run offline with Python's standard library. Offline hosts skip package installation, network asset downloads, host-specific live adapters and unavailable artifact uploads. Export does not authorize publication or sharing.

## Validate before handoff

```bash
npm ci
npm run validate
npm test
python3 -B scripts/test_gemini_package.py
python3 -B scripts/test_report_placeholders.py
```

The package check builds and extracts the actual archive, checks all 13 entrypoints against the 500-line and 3,000-body-word limits, verifies names and configuration, and renders all five included workflow examples from the extracted files. It does not establish successful ingestion or live connector evaluation.

After the PR merges, align golden evaluation cases with the packaged names and available operations. Run them against agreed seeded records and write destinations, and share the pinned revision and dataset for the final connector evaluation. Keep synthetic fixtures labeled until they have been seeded and executed.
