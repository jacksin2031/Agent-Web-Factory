# Gemini CLI adapter

Gemini CLI supports Agent Skills. Use the repository-root `SKILL.md` unchanged.

Recommended interoperable project path:

```text
.agents/skills/agent-web-factory/
```

Gemini-native project path:

```text
.gemini/skills/agent-web-factory/
```

User-level equivalents are `~/.agents/skills/agent-web-factory/` and `~/.gemini/skills/agent-web-factory/`.

Use Gemini CLI's skill management commands to list, install, link, enable, disable, or reload skills when available. Activation consent is a runtime security feature and must not be bypassed by this skill.

Do not create a Gemini-specific fork of `SKILL.md`. Any Gemini-specific extension or MCP configuration must only wire tools and discovery; Section 15 of the core skill remains authoritative for all billable actions.

The root skill also requires planning before implementation and autonomous continuation to public-production acceptance. Genuinely zero-cost technical/API setup should proceed without routine user decision prompts; potentially billable free tiers remain subject to the human cost gate.
