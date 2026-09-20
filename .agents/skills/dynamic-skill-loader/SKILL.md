---
name: dynamic-skill-loader
description: Use the dynamic-skill-loader MCP tool to find skills for a request, then read each returned SKILL.md before following its instructions.
---

# Dynamic Skill Loader

Use this skill whenever the current request may be handled by one or more locally installed skills. The required workflow is: formulate search inputs, call the loader, inspect the returned paths, read the selected `SKILL.md` files, and only then execute the discovered skill instructions.

## 1. Decide Whether to Search

Call the loader before performing a task when the request involves a capability that may have a dedicated skill, such as web search, crawling, document operations, design, browser automation, or a domain-specific workflow.

Do not treat a skill name guessed from memory as sufficient. Search the loader so that the current skill installation and ranking determine which instructions apply.

## 2. Build the Tool Input

Extract concise capability terms from the user's request. Use terms that describe the operation, subject, and constraints. Preserve important wording from the request instead of replacing it with a generic term.

Call the MCP tool named `retrieve_skills` with this exact shape:

```json
{
  "keyword": ["<capability term>", "<subject or constraint>"],
  "original_request": "<the user's complete original request>"
}
```

Input rules:

- `keyword` is required and must be a non-empty JSON array.
- Every item in `keyword` must be a non-empty string.
- Use one to five focused terms. Do not pass a single space-separated string when multiple terms are intended.
- `original_request` is optional, but include the complete user request whenever context affects skill selection. Pass `null` only when there is no useful original request.
- Do not put explanations, markdown, or tool names inside `keyword`.
- Example for a request to find recent technology news:

```json
{
  "keyword": ["news", "web search", "recent"],
  "original_request": "Find the latest technology news from reliable sources."
}
```

## 3. Inspect the Loader Result

The result is a JSON object whose keys are skill names. Each value has this shape:

```json
{
  "name": "<skill name>",
  "score": 0.84,
  "abs_path": "C:\\Users\\<user>\\.agents\\skills\\<skill-name>\\SKILL.md"
}
```

Interpret the fields as follows:

- `name` identifies the skill to load.
- `score` is the loader's relevance score. Use it to prioritize results; do not invent a different score.
- `abs_path` is the authoritative path to the skill instructions. Use this path exactly. Do not reconstruct a path from `name`, search only by filename, or substitute a repository-local path.

Process results in descending `score` order. If scores tie, preserve the order supplied by the loader. Prefer the highest-scoring result that directly covers the request. Read additional high-scoring results when the request clearly spans multiple capabilities or when the first skill explicitly delegates to another skill.

If the result object is empty, no matching skill is available. Continue only with the normal agent workflow; do not fabricate a skill or path.

If a result is missing `name`, `score`, or `abs_path`, treat that entry as malformed, ignore it, and use any valid entries. If every entry is malformed, report that the loader result could not be used and do not claim that a skill was loaded.

## 4. Read Every Selected Skill

After choosing a result, read the file at its returned `abs_path` before taking the action covered by that skill.

Use the file-reading capability available in the host agent. Start at line 1 and read the complete file. If the reader requires a line range, read in consecutive ranges until the end of the file; do not stop after only the front matter or the first screenful. Preserve the file's headings, lists, code blocks, and referenced paths while interpreting it.

For example, if the loader returns:

```text
C:\Users\AimMetal\.agents\skills\tavily-search\SKILL.md
```

read exactly that file path. Do not read `skills/tavily-search/SKILL.md` in the current repository unless `abs_path` itself points there.

If the path does not exist or cannot be read:

1. Do not pretend that the skill was loaded.
2. Record the skill name and returned path in the response or working notes.
3. Continue with another valid ranked result if one exists.
4. If no valid skill remains, report the loading failure and use the normal workflow only when it is safe to do so.

## 5. Apply the Loaded Instructions

Treat the selected `SKILL.md` as operational instructions for the current request. Follow its prerequisites, tool-selection rules, reference-file links, output requirements, and validation steps.

When the loaded skill links to a relative reference file, resolve that link relative to the directory containing the loaded `SKILL.md`. Read a linked reference before using a procedure that depends on it. Do not copy or paraphrase a reference file into this skill.

If multiple skills are selected, combine them only when their scopes do not conflict. Apply the more specific skill to the operation it owns. When two instructions conflict, stop and resolve the conflict explicitly rather than silently choosing one.

Do not call the same loader repeatedly for the same unchanged request. Re-run it only when the request, relevant constraints, or available skill set has changed, or when a loaded skill explicitly requires another discovery pass.

## 6. Completion Checklist

Before acting:

- [ ] `retrieve_skills` was called with a non-empty `keyword` array.
- [ ] The complete original request was supplied when relevant.
- [ ] Returned entries were checked for valid `name`, `score`, and `abs_path` fields.
- [ ] The selected absolute path was read completely.
- [ ] Relative references were resolved from the selected skill's directory.
- [ ] The loaded instructions were followed for the actual task.

In the final response, mention the selected skill name when it materially affected the work. Do not expose credentials or unrelated local filesystem details.
