from enum import StrEnum

from mcp.server.mcpserver import Context


class AgentHarness(StrEnum):
    CODEX = "codex"
    CLAUDE_CODE = "claude-code"
    PI = "pi"
    OMP = "omp"
    GITHUB_COPILOT = "github-copilot"
    UNKNOWN = "unknown"


HARNESS_MAP = {
    "codex-mcp-client": AgentHarness.CODEX,
    "codex": AgentHarness.CODEX,
    "codex-cli": AgentHarness.CODEX,
    "openai-codex": AgentHarness.CODEX,
    "claude-code": AgentHarness.CLAUDE_CODE,
    "claude-ai": AgentHarness.CLAUDE_CODE,
    "claude": AgentHarness.CLAUDE_CODE,
    "claude-code-cli": AgentHarness.CLAUDE_CODE,
    "omp-coding-agent": AgentHarness.OMP,
    "oh-my-pi": AgentHarness.OMP,
    "pi": AgentHarness.PI,
    "pi-cli": AgentHarness.PI,
    "pi-coding-agent": AgentHarness.PI,
    "github-copilot-developer": AgentHarness.GITHUB_COPILOT,
    "copilot-cli": AgentHarness.GITHUB_COPILOT,
    "github-copilot": AgentHarness.GITHUB_COPILOT,
    "github-copilot-vscode": AgentHarness.GITHUB_COPILOT,
    "visual-studio-code": AgentHarness.GITHUB_COPILOT,
    "vscode": AgentHarness.GITHUB_COPILOT,
}


def detect_harness(ctx: Context) -> AgentHarness:
    client_info = getattr(
        getattr(ctx.session, "client_params", None),
        "client_info",
        None,
    )

    name = getattr(client_info, "name", "")
    normalized_name = "-".join(name.strip().casefold().replace("_", "-").split())

    return HARNESS_MAP.get(
        normalized_name,
        AgentHarness.UNKNOWN,
    )
