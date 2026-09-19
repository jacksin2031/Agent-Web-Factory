# GitHub Copilot adapter

GitHub Copilot agent skills use the repository-root `SKILL.md` unchanged.

Supported project locations include:

```text
.agents/skills/agent-web-factory/
.github/skills/agent-web-factory/
```

Supported user locations include:

```text
~/.agents/skills/agent-web-factory/
~/.copilot/skills/agent-web-factory/
```

When GitHub CLI skill management is available, preview a third-party skill before installing it and use the host's validation/publishing commands as an additional release check.

Do not put purchase permission into `allowed-tools` or any host pre-approval mechanism. Tool permission and financial authorization are separate; every potentially billable action still requires the core human cost gate.

The root skill also requires planning before implementation and autonomous continuation to public-production acceptance. Genuinely zero-cost technical/API setup should proceed without routine user decision prompts; potentially billable free tiers remain subject to the human cost gate.
