# Agent Web Factory

Agent Web Factory is a vendor-neutral Agent Skill for turning a short natural-language requirement into one or many production-ready websites. It plans the complete feature set first, then autonomously continues through implementation, current market research when needed, testing, repair, zero-cost integration setup, AI features, authentication/authorization, advertising/analytics, production hardening, mandatory rendered visual QA, Vercel deployment, domains/DNS, Google Site Verification, Search Console, sitemap submission, and truthful final acceptance reporting.

The same root `SKILL.md` is the normative workflow across supported AI coding agents. Runtime-specific files only explain installation, discovery, or tool wiring; they are not allowed to weaken the core safety policy.

## Runtime targets

First-class adapter targets:

- OpenAI Codex / ChatGPT Skills
- Gemini CLI
- GitHub Copilot agent skills
- Claude Code

A generic adapter is included for other tool-capable coding agents that can read the core instructions and access the required filesystem/shell/provider tools.

See `assets/runtime-matrix.json`, `references/runtime-compatibility.md`, and `RUNTIME_VERIFICATION.md` for the exact compatibility contract and release-specific verification state.

## Core behavior

- Planning-first: every site gets a concrete feature/architecture/integration/release plan before implementation.
- Autonomous-to-production: the agent keeps building, testing, fixing, configuring, deploying, and re-testing until public-production acceptance passes or a genuine external blocker is reached.
- Genuinely zero-cost APIs/services are selected and configured by the agent without asking the user to make routine technical choices; potentially billable free tiers still require the financial cost gate.
- Single-site and resumable batch/factory mode.
- Evidence-dated market/competitor research when the factory is asked to choose site ideas; fabricated SEO, traffic, CPC, or revenue metrics are prohibited.
- AI-native site support: chat, structured generation/extraction, agents/tool calling, RAG/file Q&A, vision, image generation/editing, and speech/realtime flows when appropriate.
- Authentication is generated only when the product needs it, with server-side authorization and cross-user isolation tests.
- Advertising is explicit and provider-aware; provider review status, ads.txt, consent/CMP requirements, and live-serving status are tracked separately.
- Analytics is optional and must not receive secrets, private uploads, authentication credentials, or sensitive AI/form payloads.
- A production baseline covers 404/error handling, security headers, abuse protection, privacy/data lifecycle, accessibility, performance, support surfaces, SEO, observability, and legal/commercial disclosures when applicable.
- Optional production patterns cover databases, uploads, payments, webhooks, transactional email/SMS, contact forms, and background jobs with idempotency and cost controls.
- Provider/model selection is resolved from current official documentation at execution time instead of being frozen in this repository.
- Paid actions always require explicit human confirmation immediately before execution.
- Budgets and price limits filter choices but never count as permission to spend.
- Routine CI uses mocks/test doubles instead of billable AI calls or paid infrastructure.
- Human interaction outside payment approval is minimized to unavoidable provider identity/authorization steps such as OAuth consent, 2FA, CAPTCHA, required terms, ownership proof, or real legal/business identity data.
- Every generated site must pass real browser-rendered visual QA with mobile + desktop screenshot evidence; source inspection alone can never satisfy the visual gate.

## Financial safety invariant

Any purchase, paid plan, paid resource, real potentially billable AI request, production payment activation, billable messaging operation, or other action that can create a monetary charge requires explicit human confirmation immediately before that exact action.

General instructions such as "do everything necessary", a budget, a price cap, or permission granted for another item are not payment authorization.

`scripts/cost_gate.py` records short-lived approvals for exact provider/item/currency/maximum-charge tuples. Price, currency, provider, item-list, or request-digest changes invalidate the approval.

This rule applies identically on every runtime adapter.

## Installation

### OpenAI Codex / ChatGPT Skills

Repository scope:

```text
.agents/skills/agent-web-factory/
```

User scope:

```text
~/.agents/skills/agent-web-factory/
```

### Gemini CLI

Recommended interoperable repository scope:

```text
.agents/skills/agent-web-factory/
```

Gemini-native repository scope:

```text
.gemini/skills/agent-web-factory/
```

### GitHub Copilot

Repository scope can use:

```text
.agents/skills/agent-web-factory/
.github/skills/agent-web-factory/
```

### Claude Code

Repository scope:

```text
.claude/skills/agent-web-factory/
```

For host-specific notes, read the matching `adapters/<runtime>/README.md`.

## Example prompts

Single site:

```text
Use Agent Web Factory to plan the required features first, then build an AI-assisted Japanese rental move-in cost advisor all the way to public production. Use deterministic calculations for prices and AI for explanations and question answering. Handle all genuinely zero-cost APIs and technical setup autonomously. Deploy it to Vercel, find a suitable .jp or .com domain, and prepare Search Console. Ask me for explicit confirmation immediately before any action that can cost money.
```

Batch:

```text
Use Agent Web Factory to build 10 distinct AI-enabled utility websites for people living in Japan. Give each site an independent Vercel project. Find domains below JPY 3,000/year and keep the shortlist under JPY 25,000 total, but do not buy anything until you show me the exact domains and current total price and I explicitly confirm. Complete DNS, HTTPS, Search Console, and sitemap submission after approved purchases.
```

## Optional Vercel MCP

The official Vercel MCP endpoint used by compatible runtimes is:

```text
https://mcp.vercel.com
```

For Codex, one setup command is:

```bash
codex mcp add vercel --url https://mcp.vercel.com
```

Other runtimes should use their own MCP/tool configuration mechanism.

## Automated testing

Install test-only dependencies, then run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/run_test_shard.py core
python scripts/run_test_shard.py manifest-cost
python scripts/run_test_shard.py policy-compat
python scripts/validate_visual_qa.py assets/visual-qa.example.json
python scripts/validate_plan.py assets/site-plan.example.json
python scripts/validate_manifest.py assets/batch.example.json
python scripts/compatibility_check.py
python scripts/preflight.py
python scripts/package_release.py --output agent-web-factory.zip
```

The automated suite validates:

- Skill metadata and English-only repository text;
- Python/JSON/YAML integrity;
- manifest schema and cross-field invariants;
- AI/auth/ads/analytics policy contracts;
- resumable/idempotent state behavior;
- secret-storage safeguards;
- paid-action approval anti-replay/tamper/currency/price rules;
- production-site HTTP/SEO validator behavior;
- Google helper contracts;
- runtime adapter and compatibility-matrix invariants;
- mandatory visual-QA policy and evidence-report validation;
- planning-first/autonomous-to-production policy, machine-readable site-plan validation, and zero-cost-vs-billable external-service classification;
- release ZIP cleanliness.

## Runtime E2E testing

Static tests cannot prove that a host actually discovers, activates, and follows the skill. `tests/MANUAL_E2E.md` therefore defines a common runtime acceptance corpus plus host-specific discovery checks.

A runtime is marked `runtime-verified` for a release only after its real installation passes the required scenarios. Merely including an adapter does not count as runtime verification.

Routine E2E must use zero-cost operations, provider sandboxes, mocks, or free subdomains unless a human explicitly confirms the exact paid action through the cost gate.

## Release channels

`0.x` prereleases are public-beta builds. They may be published when all automated gates pass and any unexecuted real-runtime/provider scenarios are disclosed as limitations.

`1.0.0` stable is reserved for a release that passes the release checklist and the required real-runtime acceptance matrix for the first-class runtimes designated by that release.

## Truthfulness and external states

Agent Web Factory automates only what available credentials, permissions, tools, and provider APIs actually allow. External reviews and asynchronous decisions such as advertising approval, DNS propagation, certificate issuance, OAuth-provider review, or Google indexing are never reported as complete before the relevant provider confirms them.

If credentials, tools, legal identity information, permissions, or human approval are missing, the affected stage remains blocked/pending. The agent may continue unrelated safe work, but it must never fabricate completion.

## Security

Read `SECURITY.md` before reporting vulnerabilities. Never include real credentials, `.env` files, private keys, approval ledgers, generated factory state, or customer data in a public release archive.

## License

MIT. See `LICENSE`.
