from pathlib import Path

from pydantic import BaseModel, Field


class SkillScoreModel(BaseModel):
    name: str = Field(description="Skill's name.")
    score: float = Field(
        description="The score of the match between the skill and user's request. The higher the score is, the better the match."
    )
    abs_path: Path = Field(description="The absolute path of the skill")
