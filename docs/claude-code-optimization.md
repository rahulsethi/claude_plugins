<!-- File: docs/claude-code-optimization.md -->
<!-- Version: v1 -->

# Claude Code Optimization Notes

## Session hygiene

- Keep one session focused on one repo and one goal.
- Use `/clear` between unrelated tasks.
- Use plan mode before multi-file changes.
- Keep project `CLAUDE.md` small; push repeatable workflows into skills.

## Context discipline

- Do not open both the backend repo and the marketplace repo in the same session unless needed.
- Use subagents for research-heavy or read-only exploration.
- Use skills for repeatable Datasphere flows instead of re-explaining them in prompts.

## Recommended working pattern

1. Explore current structure.
2. Ask Claude to produce a concrete plan.
3. Execute one change set.
4. Validate.
5. Commit.
6. Clear the session if the next task is meaningfully different.

## Best default model usage

- Use the main conversation for planning and integration.
- Use `haiku` research-style subagents for cheaper repository scanning.
- Use `sonnet` for file generation and skill design.
- Use `opus` only for architecture or release-sensitive reasoning.

## Low-token prompt style

Prefer prompts like these:

```text
Explore the repo and propose the minimum file set needed for the next step. Do not edit yet.
```

```text
Implement the approved scaffold only. Keep the backend external. Show exact validation commands at the end.
```

```text
Review only the files changed in this step and point out any structural mistakes before editing.
```

## Good defaults for this project

- Prefer plugins over ad hoc `.claude/` only config because this project is meant to be shared.
- Prefer skills over custom commands when the behavior is multi-step and tool-orchestration heavy.
- Prefer subagents over agent teams for now because they are simpler and cheaper.
- Do not add hooks until the plugin is stable.
- Keep the wrapper thin and treat the Datasphere MCP server as the product backend.

## Useful built-ins to rely on

- `/help`
- `/agents`
- `/memory`
- `/config`
- `/stats`
- `/plugin ...`
- `/reload-plugins`

## IDE guidance

- Terminal-first is enough for building this scaffold.
- VS Code is a strong second choice when you want inline plan review and easier diff acceptance.
- JetBrains is a good option if your Python workflow already lives there.
