from pathlib import Path
from types import SimpleNamespace

from dynamic_skill_loader import jev_rank


def test_rank_by_state_loads_metadata_and_returns_ranked_models(monkeypatch):
    skill_paths = [Path("skills/first/SKILL.md"), Path("skills/second/SKILL.md")]
    metadata = {
        skill_paths[0]: {"name": "first", "description": "First skill"},
        skill_paths[1]: {"name": "second", "description": "Second skill"},
    }
    captured = {}
    probabilities = {"first": 0.2, "second": 0.9}

    class FakeClient:
        def system_one(self, *, state, questions):
            captured["state"] = state
            captured["questions"] = questions
            return SimpleNamespace(
                choices={
                    "skill_relevant": SimpleNamespace(
                        probabilities=probabilities
                    )
                }
            )

    monkeypatch.setattr(jev_rank, "TypeSafeClient", FakeClient)
    monkeypatch.setattr(jev_rank, "find_skill_meta_files", lambda root: skill_paths)
    monkeypatch.setattr(jev_rank, "read_skill_metadata", metadata.__getitem__)

    result = jev_rank.rank_by_state("find search skills")

    assert list(result) == ["second", "first"]
    assert result["second"].name == "second"
    assert result["second"].score == 0.9
    assert result["second"].abs_path == skill_paths[1]
    assert result["first"].name == "first"
    assert result["first"].score == 0.2
    assert result["first"].abs_path == skill_paths[0]
    assert captured["state"] == "find search skills"
    question = captured["questions"]["skill_relevant"]
    assert question.criteria == {
        "first": {"name": "first", "description": "First skill"},
        "second": {"name": "second", "description": "Second skill"},
    }
