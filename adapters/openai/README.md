# OpenAI adapter

This adapter covers OpenAI Codex and ChatGPT Skills-capable environments. The normative workflow is the repository-root `SKILL.md`.

## Install

Repository scope:

```text
.agents/skills/agent-web-factory/
```

User scope:

```text
~/.agents/skills/agent-web-factory/
```

The root `agents/openai.yaml` is optional OpenAI-specific metadata for display and dependencies. Do not move core policy into that file.

For Codex, Vercel MCP can be added with:

```bash
codex mcp add vercel --url https://mcp.vercel.com
```

A real runtime acceptance run must verify discovery, explicit/implicit invocation, script access, blocked paid actions, resumable state, and at least one zero-cost deployment path before the runtime is marked verified for a stable release.

The root skill also requires planning before implementation and autonomous continuation to public-production acceptance. Genuinely zero-cost technical/API setup should proceed without routine user decision prompts; potentially billable free tiers remain subject to the human cost gate.
