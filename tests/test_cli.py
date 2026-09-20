from pathlib import Path

from dynamic_skill_loader import cli
from dynamic_skill_loader.cli import STATE, build_state
from dynamic_skill_loader.model import SkillScoreModel
from dynamic_skill_loader.util_detect_harness import AgentHarness


def test_build_state_formats_multiple_keywords_and_request():
    result = build_state(["weather", "Beijing"], "What's the weather in Beijing?")

    assert result == STATE.format(
        keyword="weather, Beijing",
        original_request="What's the weather in Beijing?",
    )


def test_build_state_supports_empty_values():
    assert build_state([], None) == STATE.format(keyword="", original_request=None)


def test_build_state_preserves_multiline_request():
    request = "line one\nline two\nline three"

    assert request in build_state(["multi"], request)


def test_retrieve_skills_builds_state_and_returns_top_k_scores(monkeypatch):
    answer = {
        "high": SkillScoreModel(
            name="high", score=0.9, abs_path=Path("skills/high/SKILL.md")
        ),
        "middle": SkillScoreModel(
            name="middle", score=0.5, abs_path=Path("skills/middle/SKILL.md")
        ),
        "low": SkillScoreModel(
            name="low", score=0.2, abs_path=Path("skills/low/SKILL.md")
        ),
    }
    calls = []

    monkeypatch.setattr(cli, "detect_harness", lambda ctx: AgentHarness.UNKNOWN)

    def fake_rank_by_state(state, harness, *, skills_dir, top_k):
        calls.append((state, harness, skills_dir, top_k))
        return answer

    monkeypatch.setattr(cli, "rank_by_state", fake_rank_by_state)

    result = cli.retrieve_skills(object(), ["python", "files"], "How do I read a file?")

    assert calls == [
        (
            cli.build_state(["python", "files"], "How do I read a file?"),
            AgentHarness.UNKNOWN,
            None,
            5,
        )
    ]
    assert list(result) == ["high", "middle", "low"]
    assert [(item.name, item.score) for item in result.values()] == [
        ("high", 0.9),
        ("middle", 0.5),
        ("low", 0.2),
    ]
    assert all(isinstance(item, cli.SkillScoreModel) for item in result.values())


def test_retrieve_skills_passes_none_request(monkeypatch):
    answer = {}
    captured = []
    monkeypatch.setattr(cli, "detect_harness", lambda ctx: AgentHarness.UNKNOWN)
    monkeypatch.setattr(
        cli,
        "rank_by_state",
        lambda state, harness, *, skills_dir, top_k: (
            captured.append((state, harness, skills_dir, top_k)) or answer
        ),
    )

    assert cli.retrieve_skills(object(), ["search"]) == {}
    assert captured == [
        (cli.build_state(["search"], None), AgentHarness.UNKNOWN, None, 5)
    ]


def test_retrieve_skills_passes_custom_top_k(monkeypatch):
    answer = {}
    captured = []
    monkeypatch.setattr(cli, "detect_harness", lambda ctx: AgentHarness.UNKNOWN)
    monkeypatch.setattr(
        cli,
        "rank_by_state",
        lambda state, harness, *, skills_dir, top_k: (
            captured.append((state, harness, skills_dir, top_k)) or answer
        ),
    )

    assert cli.retrieve_skills(object(), ["search"], top_k=2) == {}
    assert captured == [
        (cli.build_state(["search"], None), AgentHarness.UNKNOWN, None, 2)
    ]
