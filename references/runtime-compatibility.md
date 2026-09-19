# Runtime compatibility

Agent Web Factory uses one vendor-neutral `SKILL.md` as the normative workflow. Runtime adapters exist only to explain discovery paths and tool wiring. They must not duplicate or relax core security policy.

## First-class targets

### OpenAI Codex / ChatGPT Skills

Use the open Agent Skills-compatible `SKILL.md` package. Repository-local and user-level `.agents/skills` locations are supported by Codex. The optional `agents/openai.yaml` file provides OpenAI-specific UI/dependency metadata and is not part of the portable policy layer.

### Gemini CLI

Gemini CLI supports Agent Skills and recognizes `.agents/skills` as an interoperable alias in addition to its `.gemini/skills` paths. Activation may require user consent in Gemini CLI. The core skill must remain usable without Gemini-specific files.

### GitHub Copilot

GitHub Copilot agent skills use a `SKILL.md` directory and support `.agents/skills`, `.github/skills`, and user-level skill locations. Copilot-specific installation mechanisms must load the same core directory rather than a forked copy of the workflow.

### Claude Code

Claude Code supports reusable skills under `.claude/skills/<name>/SKILL.md`. Install or link the same Agent Web Factory directory there. Do not maintain a separate Claude-specific `SKILL.md` because that would allow policy drift.

## Generic agents

A generic coding agent can use Agent Web Factory when it can:

- read this repository and the full `SKILL.md`;
- create and modify files;
- execute local commands or delegate them to an authenticated execution tool;
- access current web/provider information when required;
- preserve `.web-factory` state between steps;
- stop and obtain explicit human approval before every paid action.

If an agent cannot perform one of those operations, it may still plan the work, generate code, or produce exact provider change instructions, but it must mark unavailable execution stages as blocked.

## Compatibility levels

- `first-class`: a documented native skill-loading path exists and this repository contains a runtime adapter plus shared contract tests.
- `best-effort`: the core instructions can be injected or read, but discovery/invocation semantics depend on the host.
- `runtime-verified`: the manual E2E matrix has been executed on a real installation of that runtime for the current release.

Static adapter checks are not runtime verification. Never claim a host is runtime-verified without recording the real E2E result for the release.

## Cross-runtime invariants

Every runtime must preserve all of the following:

1. No purchase or potentially billable action without explicit human confirmation immediately before execution.
2. A budget or general instruction never counts as payment authorization.
3. Provider state and external approvals are reported truthfully.
4. Secrets stay out of source control, client bundles, state files, reports, and model-visible logs where avoidable.
5. Authentication is not authorization; private data is authorized server-side and tested for cross-user isolation.
6. AI/tool output cannot bypass authorization or the paid-action gate.
7. Resumable state must prevent replay of completed irreversible actions.
8. Missing tools or credentials produce a blocked/pending stage rather than a fabricated success.
