import pytest
from pydantic import ValidationError

from dynamic_skill_loader.model import SkillScoreModel


def test_skill_score_model_accepts_valid_values(tmp_path):
    skill_path = tmp_path / "SKILL.md"
    result = SkillScoreModel(
        name="tavily-search", score=0.85, abs_path=skill_path
    )

    assert result.name == "tavily-search"
    assert result.score == 0.85
    assert result.abs_path == skill_path


@pytest.mark.parametrize("field", ["name", "score", "abs_path"])
def test_skill_score_model_requires_all_fields(field):
    values = {
        "name": "example",
        "score": 0.5,
        "abs_path": "skills/example/SKILL.md",
    }
    values.pop(field)

    with pytest.raises(ValidationError):
        SkillScoreModel(**values)


def test_skill_score_model_rejects_invalid_score():
    with pytest.raises(ValidationError):
        SkillScoreModel(name="example", score="not-a-score")
