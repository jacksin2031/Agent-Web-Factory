# Runtime verification status

Version: `0.10.0-beta.3`

This file distinguishes repository-level compatibility from real host execution. Adapter presence and static contract tests do not prove that a specific AI runtime discovered, activated, and executed the skill correctly.

| Runtime | Adapter/contract tests | Real runtime E2E | Release status |
| --- | --- | --- | --- |
| OpenAI Codex / ChatGPT Skills | PASS | PENDING | Public beta target |
| Gemini CLI | PASS | PENDING | Public beta target |
| GitHub Copilot agent skills | PASS | PENDING | Public beta target |
| Claude Code | PASS | PENDING | Public beta target |
| Generic tool-capable agent | PASS | Host-specific | Best effort |

The current build environment does not provide the first-class runtime CLIs, so real discovery/invocation tests have not been executed for this release candidate. The mandatory rendered visual-QA and planning-first autonomous-completion runtime scenarios in `tests/MANUAL_E2E.md` are therefore also pending real-host execution.

Before marking a runtime `runtime-verified`, execute the applicable scenarios in `tests/MANUAL_E2E.md` on a real installation and retain release-specific evidence without secrets.

A stable release must not convert any `PENDING` runtime result into `PASS` without real execution evidence.
