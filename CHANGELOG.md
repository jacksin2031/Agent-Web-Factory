# Changelog

## 0.10.0-beta.4 - 2026-09-19

- Add one-command Quick Start installation for Skills CLI, GitHub CLI, and Windows PowerShell.
- Add `install.ps1` with staged replacement, identity validation, runtime targeting, and user/project scopes.
- Publish the complete multi-runtime Agent Web Factory source tree from a checksum-verified archive.
- Keep paid-action human confirmation mandatory across every supported runtime.

All notable changes to Agent Web Factory are documented here.

## 0.10.0-beta.3 - 2026-09-19

### Added

- Mandatory planning-first production plan for every site, including feature inventory, architecture, integrations, cost classification, QA, deployment, and release criteria.
- Autonomous-to-production execution contract: continue build/test/fix/configure/deploy cycles until public-production acceptance passes or a genuine external blocker is reached.
- `references/autonomous-execution.md` defining zero-cost API/resource automation and minimal human-interaction rules.
- Manifest-level execution policy for planning, production target, zero-cost automation, and paid-action confirmation.

### Changed

- Genuinely zero-cost APIs, resources, and routine provider configuration are handled autonomously when authenticated tools permit.
- Free tiers that can create overage, consume billable credits, use attached billing, or lack a hard zero-spend boundary are treated as potentially billable and still require explicit human confirmation.
- Scaffold, MVP, first successful build, and preview deployment no longer satisfy the default completion target.

## 0.10.0-beta.2 - 2026-09-19

### Added

- Mandatory real browser-rendered visual QA before preview acceptance and production completion.
- Mobile and desktop screenshot evidence requirements, plus breakpoint-sensitive tablet coverage when applicable.
- Visual checks for responsive layout, clipping/overlap, broken media, overlays, auth/AI/ads states, and production-only rendering differences.
- `references/visual-testing.md`, `assets/visual-qa.example.json`, and `scripts/validate_visual_qa.py`.
- Manual E2E scenario proving a deliberate visual defect blocks acceptance until fixed.

### Changed

- `PREVIEW_QA_PASS` now requires a validated rendered visual-QA report; source or DOM inspection alone cannot satisfy the gate.
- Runtimes without browser/visual inspection capability must report visual QA as `BLOCKED` rather than infer a pass.

## 0.10.0-beta.1 - 2026-09-19

### Added

- Vendor-neutral Agent Web Factory core using one normative `SKILL.md`.
- First-class adapters for OpenAI Codex/ChatGPT Skills, Gemini CLI, GitHub Copilot agent skills, and Claude Code.
- Generic adapter for other tool-capable coding agents.
- Runtime compatibility matrix and automated cross-runtime contract validation.
- Multi-runtime manual E2E acceptance corpus for discovery, invocation, zero-cost deployment, batch resume, financial safety, AI/auth isolation, ads state, and production truthfulness.
- Portable preflight reporting for Codex, Gemini CLI, Claude Code, and GitHub CLI availability.

### Changed

- Renamed the project from Codex Web Factory to Agent Web Factory.
- Runtime-specific instructions now handle only discovery and tool wiring; core workflow and financial safety policy remain shared.
- Stable-release criteria now distinguish static adapter compatibility from real runtime verification.

## 0.9.0-beta.1 - 2026-09-19

### Added

- Single-site and resumable batch website factory workflows.
- Production AI application support with mock-first testing and paid-inference cost gates.
- Authentication and authorization workflows with cross-user isolation requirements.
- Advertising and analytics manifests, AdSense/ads.txt/consent guidance, and truthful provider-review states.
- Production baseline for security, privacy, accessibility, performance, SEO, error handling, support, and observability.
- Data/integration guidance for databases, uploads, payments, webhooks, messaging, contact forms, and background jobs.
- Evidence-dated market/competitor research for factory-selected site portfolios, including anti-thin-site and no-fabricated-metrics rules.
- Vercel deployment, domain/DNS, HTTPS, Google Site Verification, Search Console, sitemap, and URL inspection workflows.
- Mandatory explicit human confirmation immediately before every potentially billable action.
- Idempotent state tracking, short-lived paid-action approvals, manifest validation, site validation, CI, release packaging, and manual E2E acceptance tests.
