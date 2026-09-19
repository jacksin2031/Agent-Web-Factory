# Generic adapter

Use this adapter for a tool-capable coding agent that does not natively implement the Agent Skills discovery convention.

1. Provide the agent with the full repository-root `SKILL.md` as authoritative task instructions.
2. Make the `references/`, `scripts/`, and `assets/` directories available to the agent.
3. Give it filesystem/shell/provider tools only as needed for the user's request.
4. Preserve `.web-factory/` state between steps.
5. Require the core human cost gate and explicit human confirmation for every paid or otherwise billable action.

If the host uses a persistent repository instruction file, `AGENTS.md.example` can be adapted to tell the agent when to load this skill. It is not a replacement for `SKILL.md`.

The root skill also requires planning before implementation and autonomous continuation to public-production acceptance. Genuinely zero-cost technical/API setup should proceed without routine user decision prompts; potentially billable free tiers remain subject to the human cost gate.
