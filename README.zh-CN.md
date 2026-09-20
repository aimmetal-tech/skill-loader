<div align="center">

# Dynamic Skill Loader

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/managed%20with-uv-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![MCP](https://img.shields.io/badge/MCP-server-5B5BD6)](https://modelcontextprotocol.io/)
[![TypeSafe](https://img.shields.io/badge/ranking-TypeSafe-111827)](https://typesafe.ai/)
[![Ruff](https://img.shields.io/badge/linting-Ruff-D7FF64?logo=ruff&logoColor=111827)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个使用 TypeSafe 发现本地技能并根据用户请求进行相关性排序的 MCP 服务。

[English](README.md) | [简体中文](README.zh-CN.md)

</div>

## 功能

Dynamic Skill Loader 是一个提供 `retrieve_skills` 工具的 MCP 服务。它接收关键词和可选的原始请求，并完成以下工作：

1. 检测当前连接的 MCP 客户端 Harness。
2. 选择技能根目录，并让 `--skills-dir` 优先于 Harness 默认目录。
3. 读取每个技能的 YAML front matter。
4. 使用 TypeSafe 评估技能相关性。
5. 按得分从高到低返回最多 `top_k` 个 `SkillScoreModel` 结果，`top_k` 默认为 5。

每个结果包含技能名称、相关性得分，以及该技能 `SKILL.md` 文件的绝对路径。MCP 客户端可以使用这个路径读取完整的技能说明。

默认目录为：Codex 使用 `~/.codex/skills`，Claude Code 使用 `~/.claude/skills`，其他 Harness 使用 `~/.agents/skills`。可以通过 `--skills-dir` 显式指定任意兼容的技能目录。

## 环境要求

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- 用于实际排序的 TypeSafe API key

## 安装

本地开发：

```powershell
uv sync
```

终端用户可以使用 `uvx` 按需安装并运行已发布的包。在包入口点之后传入 `TYPESAFE_API_KEY` 和可选的 `--skills-dir`。

## 使用 uvx 启动

MCP 客户端配置示例：

```json
{
  "command": "uvx",
  "args": [
    "dynamic-skill-loader",
    "--TYPESAFE_API_KEY",
    "your-typesafe-api-key",
    "--skills-dir",
    "~/.agents/skills"
  ]
}
```

对应的命令行：

```powershell
uvx dynamic-skill-loader --TYPESAFE_API_KEY your-typesafe-api-key --skills-dir ~/.agents/skills
```

本地 checkout 的启动方式：

```powershell
uv run dynamic-skill-loader --TYPESAFE_API_KEY your-typesafe-api-key --skills-dir ./skills
```

`--skills-dir` 具有最高优先级。使用非默认 TypeSafe 服务地址时，仍通过环境变量设置 `TYPESAFE_BASE_URL`。不要将 API key 提交到公开共享的配置文件中。

服务提供以下工具：

```text
retrieve_skills(
    keyword: list[str],
    original_request: str | null = null,
    top_k: int = 5,
)
```

输入示例：

```json
{
  "keyword": ["web search", "recent news"],
  "original_request": "Find a skill for searching today's news.",
  "top_k": 3
}
```

`top_k` 必须至少为 1。返回结果会按照相关性得分从高到低排序。

## 添加技能

在选定的技能根目录下创建一个直接子目录，并在其中添加 `SKILL.md`。YAML front matter 必须至少包含 `name` 和 `description`：

```text
<skills-root>/my-skill/SKILL.md
```

```markdown
---
name: my-skill
description: A concise description of when this skill should be used.
---

# My Skill

Operational instructions for the skill go here.
```

当前加载器不会搜索嵌套的技能目录。详细参考资料应放在技能目录附近，并从 `SKILL.md` 建立链接。本仓库包含一个本地技能 `.agents/skills/dynamic-skill-loader/SKILL.md`；本地测试时可以使用 `--skills-dir ./.agents/skills`，也可以指定其他兼容的外部技能根目录。

## 项目结构

```text
dynamic-skill-loader/
├── src/dynamic_skill_loader/
│   ├── cli.py                  # MCP 服务、参数和 retrieve_skills
│   ├── jev_rank.py             # TypeSafe 排序流程
│   ├── model.py                # SkillScoreModel
│   ├── util_detect_harness.py  # MCP 客户端 Harness 检测
│   └── util_read_skill.py      # 技能目录、发现和元数据解析
├── tests/                      # 单元测试
├── .agents/skills/
│   └── dynamic-skill-loader/SKILL.md # 仓库内的 loader 使用说明
├── .github/workflows/publish.yml # 由 tag 触发的 PyPI 发布流程
├── pyproject.toml              # 包元数据和 dynamic-skill-loader 入口点
├── uv.lock                     # 锁定的依赖
├── LICENSE                     # MIT 许可证
├── README.md
└── README.zh-CN.md
```

发布 wheel 包含 Python 服务代码；技能在运行时从选定的外部目录加载，不会打包进 wheel。

## 开发

通过 `uv` 运行测试和检查：

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

测试会替换 TypeSafe 客户端和技能发现逻辑，因此不需要凭据或网络连接。架构说明和项目约定请参阅 [AGENTS.md](AGENTS.md)。

## 发布到 PyPI

`.github/workflows/publish.yml` 会在推送匹配 `v*.*.*` 的 tag 时运行。它会安装锁定的环境、运行测试和 Ruff lint、校验 tag 版本与 `pyproject.toml` 一致、执行 `uv build`，然后将构建产物发布到 PyPI。

创建发布 tag 前，先更新包版本和锁文件：

```powershell
# 修改 pyproject.toml 中的 version，例如：0.1.1
uv lock
git add pyproject.toml uv.lock
git commit -m "Release v0.1.1"
git push origin main
git tag v0.1.1
git push origin v0.1.1
```

在 GitHub 仓库的 `Settings` → `Secrets and variables` → `Actions` 中创建名为 `PYPI_API_TOKEN` 的 repository secret，值填写完整的 PyPI API token。项目已存在于 PyPI 时优先使用项目级 token，并且不要把 token 提交到仓库。

## 许可证

本项目采用 MIT 许可证，完整文本请参阅 [LICENSE](LICENSE)。
