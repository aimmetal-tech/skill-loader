from pathlib import Path

from typesafe_sdk import Choice, TypeSafeClient

from dynamic_skill_loader.model import SkillScoreModel
from dynamic_skill_loader.util_detect_harness import AgentHarness
from dynamic_skill_loader.util_read_skill import (
    find_skill_meta_files,
    get_skill_root,
    read_skill_metadata,
)


def rank_by_state(
    state: str,
    harness: AgentHarness = AgentHarness.UNKNOWN,
    skills_dir: Path | None = None,
    top_k: int = 5,
):
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    client = TypeSafeClient()

    skills_path = find_skill_meta_files(
        root=get_skill_root(harness, skills_dir=skills_dir)
    )

    skills_criteria = {}

    dict_model: dict[str, SkillScoreModel] = {}

    for skill_path in skills_path:
        meta_json_str = read_skill_metadata(skill_path)
        skill_name = meta_json_str["name"]
        skills_criteria[skill_name] = meta_json_str

        dict_model[skill_name] = SkillScoreModel(
            name=skill_name, score=0.0, abs_path=skill_path
        )

    response = client.system_one(
        state=state,
        questions={
            "skill_relevant": Choice(
                instructions="Is this skill relevant to the user's question/request?",
                criteria=skills_criteria,
            )
        },
    )

    answer = response.choices["skill_relevant"]
    ranking = sorted(answer.probabilities.items(), key=lambda kv: kv[1], reverse=True)
    for name, score in ranking:
        model = dict_model[name]
        model.score = score

    ranked_models = sorted(
        dict_model.items(), key=lambda item: item[1].score, reverse=True
    )
    return dict(ranked_models[:top_k])


if __name__ == "__main__":
    rank_by_state("搜索今日新闻")
