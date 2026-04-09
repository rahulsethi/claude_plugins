<!-- File: docs/examples/home-CLAUDE.example.md -->
<!-- Version: v1 -->

# Personal Claude Code Rules

## Planning
- For any multi-file or release-related task, explore first, then propose a plan, then implement.
- Summarize what changed after each logical milestone.

## Context discipline
- Keep one session per repo and one main objective.
- Use subagents for research-heavy work.
- Use `/clear` between unrelated tasks.

## Coding style
- Prefer exact commands and concrete validation steps.
- Keep generated docs structured and concise.
- Do not invent unsupported config fields or install paths.

## Plugin work
- Validate with `claude plugin validate .` before discussing release.
- Test with `--plugin-dir` before marketplace installation.
- Keep wrapper plugins thin unless there is a clear need for runtime complexity.
