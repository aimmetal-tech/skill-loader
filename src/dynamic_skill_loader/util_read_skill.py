from pathlib import Path

import frontmatter

from dynamic_skill_loader.util_detect_harness import AgentHarness


def get_skill_root(
    harness: AgentHarness,
    home: Path | None = None,
    skills_dir: Path | None = None,
) -> Path:
    if skills_dir is not None:
        return skills_dir.expanduser()

    home = Path.home() if home is None else home

    if harness is AgentHarness.CODEX:
        return home / ".codex" / "skills"
    if harness is AgentHarness.CLAUDE_CODE:
        return home / ".claude" / "skills"
    return home / ".agents" / "skills"


def find_skill_meta_files(root: Path) -> list[Path]:
    if not root.is_dir():
        raise NotADirectoryError(f"不是有效目录：{root}")
    root = root.resolve()
    return sorted(root.glob("*/SKILL.md"), key=lambda p: p.parent.name)


def read_skill_metadata(path: Path):
    post = frontmatter.load(path)
    return post.metadata


if __name__ == "__main__":
    skills_path = find_skill_meta_files(root=Path("skills"))
    for skill_path in skills_path:
        print(skill_path)
    meta = read_skill_metadata(Path("skills/tavily-search/SKILL.md"))
    print(meta["name"])
