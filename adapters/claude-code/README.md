# Claude Code adapter

Claude Code supports reusable skills under `.claude/skills/<name>/SKILL.md`. Install or link the same Agent Web Factory directory; do not copy and edit a separate core workflow.

Project scope:

```text
.claude/skills/agent-web-factory/
```

User scope:

```text
~/.claude/skills/agent-web-factory/
```

The skill may be invoked explicitly or selected automatically by the runtime when relevant. Claude-specific permission or hook configuration may provide additional safeguards, but it must never weaken Section 15 of the root `SKILL.md`.

A real runtime acceptance run must verify that the skill is discoverable, can read bundled references/scripts, blocks paid actions before human confirmation, and preserves resumable factory state.

The root skill also requires planning before implementation and autonomous continuation to public-production acceptance. Genuinely zero-cost technical/API setup should proceed without routine user decision prompts; potentially billable free tiers remain subject to the human cost gate.
