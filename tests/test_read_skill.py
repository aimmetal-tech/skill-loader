from pathlib import Path

import pytest

from dynamic_skill_loader.util_detect_harness import AgentHarness
from dynamic_skill_loader.util_read_skill import (
    find_skill_meta_files,
    get_skill_root,
    read_skill_metadata,
)


def test_get_skill_root_selects_harness_directory(tmp_path: Path):
    assert get_skill_root(AgentHarness.CODEX, tmp_path) == tmp_path / ".codex" / "skills"
    assert get_skill_root(AgentHarness.CLAUDE_CODE, tmp_path) == (
        tmp_path / ".claude" / "skills"
    )
    assert get_skill_root(AgentHarness.PI, tmp_path) == tmp_path / ".agents" / "skills"


def test_get_skill_root_prefers_explicit_directory(tmp_path: Path):
    explicit_dir = tmp_path / "shared-skills"

    assert get_skill_root(
        AgentHarness.CODEX,
        tmp_path,
        skills_dir=explicit_dir,
    ) == explicit_dir


def test_find_skill_meta_files_returns_sorted_skill_files(tmp_path: Path):
    (tmp_path / "zulu").mkdir()
    (tmp_path / "alpha").mkdir()
    (tmp_path / "ignored").mkdir()
    (tmp_path / "zulu" / "SKILL.md").write_text(
        "---\nname: zulu\n---\n", encoding="utf-8"
    )
    (tmp_path / "alpha" / "SKILL.md").write_text(
        "---\nname: alpha\n---\n", encoding="utf-8"
    )
    (tmp_path / "ignored" / "README.md").write_text("ignored", encoding="utf-8")

    assert find_skill_meta_files(tmp_path) == [
        tmp_path / "alpha" / "SKILL.md",
        tmp_path / "zulu" / "SKILL.md",
    ]


def test_find_skill_meta_files_rejects_non_directory(tmp_path: Path):
    file_path = tmp_path / "skills.txt"
    file_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        find_skill_meta_files(file_path)


def test_find_skill_meta_files_returns_empty_for_empty_directory(tmp_path: Path):
    assert find_skill_meta_files(tmp_path) == []


def test_read_skill_metadata_parses_front_matter(tmp_path: Path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(
        "---\nname: example\ndescription: Example skill\n---\n\n# Example\n",
        encoding="utf-8",
    )

    assert read_skill_metadata(skill_path) == {
        "name": "example",
        "description": "Example skill",
    }
