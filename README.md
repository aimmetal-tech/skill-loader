<div align="center">

# Dynamic Skill Loader

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/managed%20with-uv-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![MCP](https://img.shields.io/badge/MCP-server-5B5BD6)](https://modelcontextprotocol.io/)
[![TypeSafe](https://img.shields.io/badge/ranking-TypeSafe-111827)](https://typesafe.ai/)
[![Ruff](https://img.shields.io/badge/linting-Ruff-D7FF64?logo=ruff&logoColor=111827)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An MCP server that discovers local skills and ranks them against a user's request with TypeSafe.

[English](README.md) | [简体中文](README.zh-CN.md)

</div>

## What it does

Dynamic Skill Loader is an MCP server that exposes a `retrieve_skills` tool. Given keywords and an optional original request, it:

1. Detects the connected MCP client's Harness.
2. Selects a skill root, honoring `--skills-dir` before Harness defaults.
3. Reads each skill's YAML front matter.
4. Uses TypeSafe to estimate relevance.
5. Returns up to `top_k` `SkillScoreModel` values sorted by descending score; `top_k` defaults to 5.

Each result includes the skill name, relevance score, and an absolute path to its `SKILL.md` file. A client can use that path to read the full skill instructions.

The default skill roots are `~/.codex/skills` for Codex, `~/.claude/skills` for Claude Code, and `~/.agents/skills` for other Harness values. Use `--skills-dir` to select any compatible skill directory explicitly.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- A TypeSafe API key for live ranking

## Installation

For local development:

```powershell
uv sync
```

For end users, `uvx` can install and run the published package on demand. Pass `TYPESAFE_API_KEY` and optional `--skills-dir` after the package entry point.

## Run with uvx

An MCP client can launch the published package with:

```json
{
  "command": "uvx",
  "args": [
    "dynamic-skill-loader",
    "--TYPESAFE_API_KEY",
    "your-typesafe-api-key",
    "--skills-dir",
    "~/.agents/skills"
  ]
}
```

The equivalent command line is:

```powershell
uvx dynamic-skill-loader --TYPESAFE_API_KEY your-typesafe-api-key --skills-dir ~/.agents/skills
```

To run a local checkout instead:

```powershell
uv run dynamic-skill-loader --TYPESAFE_API_KEY your-typesafe-api-key --skills-dir ./skills
```

`--skills-dir` has the highest priority. `TYPESAFE_BASE_URL` remains an environment variable for non-default TypeSafe endpoints. Avoid committing API keys to configuration files that are shared publicly.

The server exposes:

```text
retrieve_skills(
    keyword: list[str],
    original_request: str | null = null,
    top_k: int = 5,
)
```

Example input:

```json
{
  "keyword": ["web search", "recent news"],
  "original_request": "Find a skill for searching today's news.",
  "top_k": 3
}
```

`top_k` must be at least 1. Results are returned in descending relevance-score order.

## Add a skill

Create a direct child directory under the selected skill root with a `SKILL.md` file. The YAML front matter must include `name` and `description`:

```text
<skills-root>/my-skill/SKILL.md
```

```markdown
---
name: my-skill
description: A concise description of when this skill should be used.
---

# My Skill

Operational instructions for the skill go here.
```

The loader does not search nested skill directories. Keep detailed references beside the skill and link to them from `SKILL.md`. This repository includes a local skill at `.agents/skills/dynamic-skill-loader/SKILL.md`; use `--skills-dir ./.agents/skills` or another compatible external skill root when testing it locally.

## Project structure

```text
dynamic-skill-loader/
├── src/dynamic_skill_loader/
│   ├── cli.py                  # MCP server, arguments, and retrieve_skills
│   ├── jev_rank.py             # TypeSafe ranking workflow
│   ├── model.py                # SkillScoreModel
│   ├── util_detect_harness.py  # MCP client Harness detection
│   └── util_read_skill.py      # Skill roots, discovery, and metadata parsing
├── tests/                      # Focused unit tests
├── .agents/skills/
│   └── dynamic-skill-loader/SKILL.md # Repository-local loader instructions
├── .github/workflows/publish.yml # Tag-triggered PyPI publishing workflow
├── pyproject.toml              # Package metadata and dynamic-skill-loader entry point
├── uv.lock                     # Locked dependencies
├── LICENSE                     # MIT license
├── README.md
└── README.zh-CN.md
```

The published wheel contains the Python server. Skills are loaded from the selected external root at runtime rather than bundled into the wheel.

## Development

Run the test suite and checks through `uv`:

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Tests stub TypeSafe and skill discovery, so they do not require credentials or network access. See [AGENTS.md](AGENTS.md) for architecture notes and project-specific conventions.

## Release to PyPI

The GitHub Actions workflow in `.github/workflows/publish.yml` runs when a tag matching `v*.*.*` is pushed. It installs the locked environment, runs tests and Ruff lint, verifies that the tag version matches `pyproject.toml`, runs `uv build`, and publishes the distributions to PyPI.

Before creating a release tag, update the package version and lock file:

```powershell
# Edit version in pyproject.toml, for example: 0.1.1
uv lock
git add pyproject.toml uv.lock
git commit -m "Release v0.1.1"
git push origin main
git tag v0.1.1
git push origin v0.1.1
```

Configure a repository secret named `PYPI_API_TOKEN` under GitHub `Settings` → `Secrets and variables` → `Actions`. Its value should be the complete PyPI API token. Prefer a project-scoped token when the project already exists on PyPI, and never commit the token to the repository.

## License

MIT License. See [LICENSE](LICENSE) for the full text.
