# Agent Guide

## Project purpose

This repository is a Python 3.12 MCP server that discovers local skills and ranks them against a user request with TypeSafe. The public entry point is the `dynamic-skill-loader` console script, which calls `dynamic_skill_loader:main`.

## Development commands

Run commands through `uv` so the locked environment and Python 3.12 requirement are respected:

```powershell
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Use `uv run ruff format .` only when intentionally applying formatting. The Ruff configuration is in [pyproject.toml](pyproject.toml): 88-character lines, double quotes, and import sorting with `dynamic_skill_loader` as first-party.

When running the real TypeSafe integration, pass the API key through the MCP server arguments:

```json
{
	"args": ["run", "dynamic-skill-loader", "--TYPESAFE_API_KEY", "your-typesafe-api-key"]
}
```

The CLI writes this value to `TYPESAFE_API_KEY` before starting the server. Do not commit real API keys. Unit tests should stub the TypeSafe client instead of making network calls.

Published users can run the console script with `uvx dynamic-skill-loader`. The MCP configuration should use `command: "uvx"` and pass `dynamic-skill-loader`, `--TYPESAFE_API_KEY`, and optionally `--skills-dir` in `args`. Local development uses `uv run dynamic-skill-loader`.

Releases are automated by [.github/workflows/publish.yml](.github/workflows/publish.yml). The workflow runs for tags matching `v*.*.*`, runs tests and `ruff check`, verifies that the tag version matches `pyproject.toml`, builds with `uv build`, and publishes `dist/` to PyPI with the `PYPI_API_TOKEN` repository secret. Do not commit or print the token.

## Architecture

- [src/dynamic_skill_loader/cli.py](src/dynamic_skill_loader/cli.py) defines the MCP server, the `retrieve_skills` tool, the `top_k` tool parameter (default 5), and the request state template. Keep protocol-facing changes here.
- [src/dynamic_skill_loader/cli.py](src/dynamic_skill_loader/cli.py) also parses `--TYPESAFE_API_KEY` and `--skills-dir` before starting the MCP server.
- [src/dynamic_skill_loader/jev_rank.py](src/dynamic_skill_loader/jev_rank.py) selects the skill root, discovers skill metadata, calls TypeSafe, sorts `SkillScoreModel` values by descending score, and truncates the result to `top_k`.
- [src/dynamic_skill_loader/util_read_skill.py](src/dynamic_skill_loader/util_read_skill.py) owns skill-root selection, skill discovery, and YAML front matter parsing.
- [src/dynamic_skill_loader/model.py](src/dynamic_skill_loader/model.py) contains the Pydantic response model.
- [tests/](tests/) mirrors these modules. Prefer focused unit tests with `monkeypatch` or small fake clients for external integrations.

## Skill layout

A loadable skill is a direct child of the selected skills root with a `SKILL.md` file. Its YAML front matter must provide at least `name` and `description`; the loader searches only `<root>/*/SKILL.md`, not nested directories. `find_skill_meta_files` resolves the root and returns paths sorted by directory name. Preserve absolute paths in values returned to callers.

The root selection priority is:

1. `--skills-dir`, when supplied to the MCP server.
2. `~/.codex/skills` for Codex.
3. `~/.claude/skills` for Claude Code.
4. `~/.agents/skills` for all other Harness values.

`--skills-dir` supports `~` and takes precedence over Harness-based selection.

When adding or changing a skill, keep its operational instructions in that skill's own `SKILL.md` and preserve links to its reference files instead of duplicating reference content elsewhere.

The published wheel contains the Python server only. Skills remain external runtime data and are discovered from the selected root; do not assume the repository-local `.agents/skills/` directory is bundled into the wheel.

## Project structure

The current tracked project structure is:

```text
dynamic-skill-loader/
├── .agents/skills/dynamic-skill-loader/SKILL.md
├── .github/workflows/publish.yml
├── src/dynamic_skill_loader/
│   ├── __init__.py
│   ├── cli.py
│   ├── jev_rank.py
│   ├── model.py
│   ├── util_detect_harness.py
│   └── util_read_skill.py
├── tests/
│   ├── test_cli.py
│   ├── test_jev_rank.py
│   ├── test_model.py
│   └── test_read_skill.py
├── .gitignore
├── .python-version
├── AGENTS.md
├── LICENSE
├── README.md
├── README.zh-CN.md
├── pyproject.toml
└── uv.lock
```

Module responsibilities are:

- `src/dynamic_skill_loader/cli.py`: MCP protocol surface and startup arguments.
- `src/dynamic_skill_loader/jev_rank.py`: TypeSafe ranking and result construction.
- `src/dynamic_skill_loader/util_detect_harness.py`: MCP client Harness normalization and classification.
- `src/dynamic_skill_loader/util_read_skill.py`: skill-root selection, direct-child discovery, and front matter parsing.
- `src/dynamic_skill_loader/model.py`: Pydantic response model.
- `.agents/skills/dynamic-skill-loader/SKILL.md`: repository-local instructions for using the loader skill.
- `.github/workflows/publish.yml`: tag-triggered test, build, and PyPI publishing workflow.
- `tests/`: focused unit tests for the modules above.
- `pyproject.toml` and `uv.lock`: package metadata, entry point, and locked dependencies.
- `LICENSE`: MIT license for the project.

Ignored runtime artifacts such as `.venv/`, `dist/`, `.pytest_cache/`, `.ruff_cache/`, `__pycache__/`, and `.env` are not part of the tracked project structure.

## Structure synchronization rules

Treat `AGENTS.md`, `README.md`, and `README.zh-CN.md` as synchronized project documentation. Before completing a change, inspect the actual directory and tracked-file structure, then compare it with the project structure documented above.

The same change must update both `AGENTS.md` and `README.md` when it does any of the following:

- adds, deletes, moves, or renames a file or directory;
- changes a file's responsibility, a module boundary, an entry point, or a data flow;
- changes test, build, packaging, or verification commands, or the location or shape of a deliverable;
- adds a security, privacy, or installation constraint that developers must follow.

When a change affects user-facing documentation, keep `README.zh-CN.md` synchronized as well. If the actual directory or tracked-file structure differs from the documented project structure, the task is not complete until the documentation is corrected and the structure has been checked again.

## Change and test conventions

- Keep public MCP tool behavior and the `SkillScoreModel` shape stable unless the change explicitly requires a contract update.
- Keep `retrieve_skills.top_k` defaulted to 5 and reject values below 1; update both README files and tests when changing this contract.
- Test formatting of the generated state separately from ranking behavior.
- For ranking tests, patch `TypeSafeClient`, skill discovery, and metadata loading; do not require credentials or network access.
- For CLI tests, verify argument parsing and environment setup for `--TYPESAFE_API_KEY` and `--skills-dir` without using real credentials or external services.
- Assert ranking order when changing score handling, because callers receive an insertion-ordered dictionary.
- When changing release behavior, preserve the tag/version match check and the `PYPI_API_TOKEN` secret name unless the release contract is intentionally updated.
- Add regression coverage for invalid directories, missing or malformed metadata, and path-resolution behavior when touching skill discovery.
- Avoid editing generated/cache directories such as `.venv`, `.pytest_cache`, and `.ruff_cache`.
