import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from pydantic import Field

from dynamic_skill_loader.jev_rank import rank_by_state
from dynamic_skill_loader.model import SkillScoreModel
from dynamic_skill_loader.util_detect_harness import detect_harness

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)

mcp = MCPServer("my-mcp")
SKILLS_DIR: Path | None = None

STATE = """<KEYWORD>
{keyword}
</KEYWORD>

<ORIGINAL_REQUEST>
{original_request}
</ORIGINAL_REQUEST>
"""


def build_state(keyword, original_request) -> str:
    return STATE.format(keyword=", ".join(keyword), original_request=original_request)


@mcp.tool()
def retrieve_skills(
    ctx: Context,
    keyword: Annotated[
        list[str],
        Field(
            description="The keyword of user's question or request, using to search relevant skills."
        ),
    ],
    original_request: Annotated[
        str | None, Field(description="The original request or question from user.")
    ] = None,
) -> dict[str, SkillScoreModel]:
    """Retrieve skills by keyword and original request"""
    harness = detect_harness(ctx)
    logger.info("Detected agent harness: %s", harness)
    state = build_state(keyword, original_request)
    answer = rank_by_state(state, harness, skills_dir=SKILLS_DIR)
    return answer


# @mcp.tool
# def open_skills(
#     path: Annotated[str, Field(description="Absolute root path of the skill")],
# ):
#     """ "Open skill by name"""
#     skill_root_abs_path = Path(path)


def main():
    global SKILLS_DIR

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--skills-dir", type=Path)
    parser.add_argument("--TYPESAFE_API_KEY")
    args, _ = parser.parse_known_args()
    SKILLS_DIR = args.skills_dir

    if args.TYPESAFE_API_KEY is not None:
        os.environ["TYPESAFE_API_KEY"] = args.TYPESAFE_API_KEY

    if SKILLS_DIR is not None:
        logger.info("Using skills directory from --skills-dir: %s", SKILLS_DIR)
    mcp.run()
