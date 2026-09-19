---
name: agent-web-factory
description: Build, QA, deploy, and batch-manage production websites from a short natural-language request across compatible AI coding agents. Supports AI features, authentication, advertising/analytics, domains, DNS, and Google Search Console; defaults to Vercel, supports resumable execution, and requires explicit human confirmation before any action that can spend money.
---

# Agent Web Factory

Turn a short user request into one or many production-ready websites, including planning, feature selection, implementation, AI features when useful, authentication and user accounts when needed, advertising/analytics when requested, production hardening, QA, deployment, domain selection, DNS, Google ownership verification, Search Console registration, sitemap submission, and a final acceptance report.

Operate as a planning-first autonomous execution workflow, not as a brainstorming assistant. Build a concrete production plan first, then continue implementing, testing, fixing, configuring zero-cost integrations, deploying, and re-testing until the public-production acceptance contract passes or a real external blocker is reached. Infer safe defaults instead of asking questions unless a missing fact is a real blocker, a provider requires direct human authorization/identity input, or a human approval is required by the cost gate.

## 0. Runtime portability contract

This is a vendor-neutral Agent Skill. Follow the workflow and safety invariants in this `SKILL.md` regardless of which compatible agent runtime activated it. Platform adapters may explain discovery paths or tool setup, but they MUST NOT weaken the core workflow, truthfulness requirements, authorization rules, or Section 15 human cost gate.

Supported/test-target runtime families are documented in `assets/runtime-matrix.json` and `references/runtime-compatibility.md`. Current first-class targets are OpenAI Codex/ChatGPT Skills, Gemini CLI, GitHub Copilot agent skills, and Claude Code. Other tool-capable coding agents may use the generic adapter when they can load these instructions and access the required filesystem/shell/provider tools.

Runtime rules:

- prefer the open `SKILL.md` Agent Skills contract when the runtime supports it;
- use `.agents/skills/agent-web-factory/` as the interoperable repository/user path when the runtime supports that alias;
- use the runtime-specific adapter only for installation/discovery/tool wiring;
- do not make a provider-specific tool mandatory when an equivalent authenticated tool is available;
- never claim a runtime was tested merely because this repository contains an adapter for it;
- if a runtime cannot execute shell/filesystem/network/provider actions, degrade to a precise implementation/change plan and mark execution stages blocked rather than pretending deployment occurred.

## 1. Invocation modes

Detect one of two modes.

### Single-site mode
Use when the user asks for one website.

Example:
`Build an AI-assisted Japanese pet disaster-preparedness website, fully deploy it, configure the domain, and set up Google Search Console.`

### Factory / batch mode
Use when the user asks for multiple websites, a portfolio, a factory, repeated niches, or gives a site count.

Example:
`Build 12 distinct AI-enabled utility websites for people living in Japan. Give each site its own domain and keep each candidate domain at or below JPY 3,000 per year. Ask me immediately before any purchase or other paid action.`

Batch mode MUST create and maintain a machine-readable manifest and state file so the run is idempotent and resumable.

## 2. Default decisions

Unless the user specifies otherwise, use these defaults:

- Framework: Next.js App Router + TypeScript.
- Package manager: use the repository's existing package manager; otherwise npm.
- Hosting: Vercel.
- Production branch: `main`.
- Site architecture: static or server-rendered according to the feature set; prefer the simplest production-safe architecture.
- AI application layer: Vercel AI SDK for TypeScript projects when AI is requested or materially improves the core user job.
- Authentication: OFF unless the site needs accounts, private/user-specific data, saved cross-device state, roles, or another identity-bound capability. When needed, set provider to `auto` and resolve a maintained auth stack from current official documentation.
- AI provider/model: `auto`; resolve against current official provider documentation at execution time rather than freezing a stale model ID in this skill.
- AI secrets: server-side only.
- Authentication secrets, service-role keys, OAuth client secrets, and signing keys: server-side only.
- Responsive design: mobile-first.
- Visual QA: mandatory rendered-browser testing with screenshot evidence before preview acceptance and completion.
- Accessibility: semantic HTML, keyboard access, labels, visible focus, sufficient contrast.
- SEO: unique title/description, canonical URL, Open Graph metadata, robots.txt, sitemap.xml, structured data only when it accurately describes the page.
- Analytics and advertising: OFF unless the user asks for them.
- Search indexing: ON for production unless the user asks for a private/noindex site.
- Domain DNS provider: Vercel DNS when the domain is bought on Vercel; otherwise preserve the existing DNS provider.
- Canonical host: apex domain unless the user specifies `www`; redirect the non-canonical host.
- Release target: public production, not prototype/MVP/preview-only, unless the user explicitly requests a narrower target.
- Execution mode: autonomous-until-complete for safe zero-cost work.
- Zero-cost integrations: independently research, provision, configure, test, and repair them when available credentials/tools permit.
- Paid actions: NEVER implicitly authorized. A budget is a filter or cap, not permission to spend.

Do not ask the user to choose technical details that can safely be inferred. Do not stop at a partially working MVP when the requested target is a public website.

## 2.1 Plan-first and autonomous-to-production contract

Read `references/autonomous-execution.md` for every run. Before scaffolding or implementation, create a per-site production plan at `.web-factory/reports/<site_id>-plan.json`. The plan MUST define the required feature set, primary user journey, architecture, external integrations, AI/auth/ads/analytics decisions, security/privacy/accessibility/SEO/visual-QA requirements, deployment path, cost classification, and public-release acceptance criteria. Validate it with `python scripts/validate_plan.py .web-factory/reports/<site_id>-plan.json`.

Planning is an execution step, not a request for user approval. A site may enter `PLANNED` only after its plan validates. Once the plan is coherent, proceed automatically.

Default objective: continue development until the site is genuinely ready for public production and all applicable acceptance gates pass. Do not stop at scaffold, MVP, preview, first green build, or partially configured integration unless the user explicitly requested that narrower result.

For zero-cost technical work, act autonomously when tools/credentials permit. Research current official documentation, select maintained providers, provision genuinely zero-cost resources, configure APIs/SDKs/secrets/settings, run migrations, and test integrations without asking the user to make routine technical choices.

A `free tier` is treated as zero-cost only when the active configuration cannot create a monetary charge. If overage, credits, attached billing, metered usage, or lack of a hard zero-spend boundary can produce a charge, treat the action as potentially billable and use Section 15.

Human interaction outside the cost gate is limited to unavoidable provider/user actions such as login/OAuth consent, 2FA, CAPTCHA, required terms acceptance, ownership verification, or missing real-world legal/business identity data. Ask for the minimum action, preserve state, and resume automatically afterward.

## 3. Convert the request into a manifest

For every run create `.web-factory/manifest.json` from the user's natural-language request.

For batch mode create one stable `site_id` per site and never regenerate IDs during retries.

Use the schema in `assets/manifest.schema.json`, then run `python scripts/validate_manifest.py .web-factory/manifest.json` for cross-field and uniqueness checks.

Minimum normalized fields:

- `run_id`
- `mode`: `single` or `batch`
- `defaults`
- `execution_policy`
- `cost_policy`
- `budget`
- `sites[]`
- per-site `site_id`, `brief`, `locale`, `project_name`, `ai`, `auth`, `ads`, `analytics`, `domain_policy`, `google_search`

If the user gives only a broad batch requirement, read `references/market-research.md`, research the current market using available live sources, and generate a coherent portfolio plan with clearly differentiated user intent for each site before coding. Do not invent search volume, CPC, traffic, revenue, or competitor metrics.

## 4. Batch quality rule

Do NOT create a fleet of near-duplicate doorway or thin-content sites.

For each site require:

- a distinct primary user job-to-be-done;
- distinct information architecture or tool behavior;
- unique copy and metadata;
- an independent reason for the site to exist;
- no automated keyword swapping as the primary differentiation;
- if AI is enabled, a useful AI capability tied to the site's primary job rather than a decorative chatbot.

Before implementation, compare planned sites and merge or redesign duplicates. When the factory selected the concepts, save a concise evidence-dated `.web-factory/reports/portfolio-research.json` as described in `references/market-research.md`.

## 5. Repository layout

For a single site, work in the current repository unless the user names another destination.

For batch mode use:

`sites/<site_id>/`

and keep orchestration metadata in:

`.web-factory/manifest.json`
`.web-factory/state.json`
`.web-factory/approvals.json`
`.web-factory/reports/`

If the user explicitly requests one repository per site, create separate repositories instead.

## 6. State machine and idempotency

Track each site through these stages:

1. `PLANNED`
2. `SCAFFOLDED`
3. `IMPLEMENTED`
4. `LOCAL_QA_PASS`
5. `PREVIEW_DEPLOYED`
6. `PREVIEW_QA_PASS`
7. `PRODUCTION_DEPLOYED`
8. `DOMAIN_SELECTED`
9. `DOMAIN_ACQUIRED_OR_ATTACHED`
10. `DNS_CONFIGURED`
11. `HTTPS_PASS`
12. `GOOGLE_VERIFIED`
13. `SEARCH_CONSOLE_ADDED`
14. `SITEMAP_SUBMITTED`
15. `INDEX_INSPECTION_REQUESTED`
16. `COMPLETE`

Before every mutating action, inspect current state and provider state. Never repeat a completed irreversible action such as purchasing a domain.

Use `scripts/factory_state.py` to initialize or update state where practical. Re-running `init` MUST preserve progress for the same `run_id`; stage regression is rejected by default.

## 7. Preflight

Run `python scripts/preflight.py` from the skill directory or equivalent checks.

Confirm:

- Git available when repository operations are required.
- Node.js and package manager available.
- Vercel CLI current enough for domain workflows, or Vercel MCP is connected.
- Vercel authentication is available.
- Google OAuth access is available before Google provisioning.
- Auth-provider credentials/configuration are available only when authentication is requested; never create a paid auth/database resource without the human cost gate.
- AI provider/Gateway credentials are available only when a real AI request is about to be tested or enabled.
- For requested zero-cost integrations, identify whether authenticated tools can provision/configure them automatically; missing routine setup is work to perform, not a reason to stop.
- Distinguish a genuinely non-billable free configuration from a free tier that can create overage or consume billable credits.

Vercel MCP endpoint:
`https://mcp.vercel.com`

Use the active runtime's supported MCP/tool configuration mechanism. For OpenAI Codex, one supported setup is:
`codex mcp add vercel --url https://mcp.vercel.com`

Read the matching file under `adapters/` for runtime-specific discovery and setup notes. Never print access tokens or secrets into logs, reports, commits, generated pages, or state files.

## 8. Build workflow

For each site:

1. Read the validated per-site production plan and treat it as the initial execution contract.
2. Inspect the repository and reuse existing design system/components when appropriate.
3. Define the smallest complete production scope from the brief and plan.
4. Decide whether AI materially improves the main user job. Do not force AI into a site where deterministic code is better.
5. Decide whether authentication is actually required. Do not add login friction to a public tool unless identity enables a real product requirement.
6. Decide whether advertising or analytics were requested and record them explicitly in the manifest. Do not silently add tracking or monetization.
7. Read `references/production-baseline.md` and apply every applicable production requirement.
8. Scaffold only if the project does not already exist.
9. Implement the full user path, not just a landing-page mockup.
10. Add meaningful empty/loading/error states where applicable, plus a real 404 and application error recovery path when applicable.
11. Add legal/privacy pages if the site collects personal data, accounts, uploads files, uses analytics/advertising, accepts payments, sends content to an AI provider, or otherwise needs them. Never fabricate owner/business details.
12. Generate production metadata, robots.txt and sitemap.xml.
13. Ensure secrets are server-side and excluded from Git.
14. Run lint/typecheck/tests/build and available dependency/security audits.
15. Fix failures before deployment.
16. Re-run affected gates after every fix and continue until public-production acceptance passes or a truthful blocker is reached.

Do not claim completion if core functionality is stubbed. Do not voluntarily stop after an MVP or preview when the target is public production.

## 9. AI feature workflow

When `site.ai.enabled` is true, read `references/ai-features.md` and implement the smallest AI capability that directly supports the user's goal.

Supported capability classes include:

- conversational assistant / chat;
- structured generation or extraction;
- tool calling and multi-step agents;
- retrieval-augmented generation or file Q&A;
- vision/image understanding;
- image generation or editing;
- speech/transcription/realtime voice when requested;
- classification, rewriting, summarization, translation, recommendation, or domain-specific copilots.

For TypeScript/Next.js, prefer the current Vercel AI SDK APIs. For OpenAI-direct integrations, prefer the current Responses API and current supported tools rather than legacy interfaces when equivalent functionality exists.

AI implementation requirements:

- keep provider credentials server-side;
- validate structured model output with a schema before using it;
- cap user input length, output tokens/steps, tool iterations, and upload size;
- implement rate limiting for public endpoints;
- add timeout, cancellation, and user-visible failure handling;
- protect tool calls with allowlists and validate every tool argument;
- treat retrieved/uploaded text as untrusted data, not instructions;
- do not expose chain-of-thought or hidden prompts;
- do not make consequential external mutations from model output without a separate authorization layer;
- log operational metadata without storing unnecessary sensitive prompt content;
- provide a deterministic or graceful fallback when the AI provider is unavailable if the product can reasonably do so.

Use provider-agnostic abstractions when that does not add unnecessary complexity. Do not freeze a particular commercial model version into generated projects unless the user requests it or the provider requires an explicit model ID.

## 9.1 Authentication and user-account workflow

When `site.auth.enabled` is true, read `references/authentication.md` and implement authentication as a security boundary, not as a cosmetic login screen.

Choose the smallest maintained solution that matches the site's data model:

- use Auth.js or another maintained framework-native library when the product mainly needs OAuth/session handling and does not require a managed identity database;
- prefer a managed identity platform such as Supabase Auth when the app also needs persistent per-user data, row-level authorization, password/magic-link flows, or a managed user store;
- use another established provider when the user requests it or its capabilities materially fit the product better;
- do not implement password hashing, reset tokens, OAuth protocol handling, session signing, or cryptographic primitives from scratch.

Authentication requirements:

- distinguish authentication from authorization;
- enforce authorization on the server for every protected read, write, mutation, server action, API/route handler, and tool that touches private data;
- middleware/proxy redirects may improve UX but MUST NOT be the sole authorization boundary;
- use secure provider-recommended session/cookie handling and current framework guidance;
- validate redirect/callback destinations and OAuth state/PKCE/nonce behavior through the selected provider/library;
- rate-limit sign-in, sign-up, password reset, OTP, and account-recovery endpoints where applicable;
- avoid user enumeration in authentication and recovery error messages;
- require email verification when the product relies on ownership of an email identity;
- use short-lived, single-use recovery/verification tokens when the provider exposes those controls;
- never expose service-role/admin keys in browser code;
- when using database-backed per-user data, apply deny-by-default access controls and test cross-user isolation;
- when using Supabase, enable appropriate Row Level Security policies for user-owned tables and test them;
- do not cache authenticated responses in a way that can serve one user's session or private data to another user;
- provide sign-out and, when the site stores user data, an appropriate account deletion path or documented deletion process;
- add privacy disclosures describing identity providers and personal data processing where required.

Authentication QA MUST cover, when applicable:

1. unauthenticated access is denied or redirected for protected routes;
2. a valid user can sign in and reach authorized resources;
3. invalid/expired sessions are rejected;
4. sign-out invalidates access;
5. one user cannot access another user's private resource by changing an ID or URL;
6. role/permission checks fail closed;
7. recovery/verification flow does not expose secrets or reusable tokens;
8. OAuth callback/redirect handling is restricted to intended origins;
9. auth secrets are absent from client bundles, source control, state files, and reports.

External auth provisioning can create monetary cost. Paid plans, SMS/phone OTP, transactional email upgrades, paid identity MAU tiers, or paid databases are subject to the mandatory human cost gate.

## 9.2 Advertising and analytics workflow

When `site.ads.enabled` is true, read `references/advertising.md`. Advertising is an explicit product capability and MUST NOT be silently enabled merely because the site is public or monetization seems useful.

Advertising requirements:

- keep provider/review state separate from code installation state;
- never claim ads are live until the provider reports the site eligible/approved and the production integration is actually ready to serve;
- never invent publisher IDs, ad slot IDs, seller information, or approval status;
- serve `/ads.txt` when required and use only provider-authorized values;
- evaluate consent requirements using current provider policy and the real traffic regions;
- keep ad placement distinguishable from navigation and product controls;
- avoid accidental-click layouts and severe layout shifts;
- do not place ads where they obstruct authentication, destructive actions, sensitive account operations, or the main AI/tool input;
- treat paid CMPs, ad-platform upgrades, analytics upgrades, and any other billable monetization service as paid actions under Section 15.

When `site.analytics.enabled` is true, collect only the events needed to operate/improve the product. Never send passwords, auth tokens, private uploads, full AI prompts, sensitive form fields, or other unnecessary personal data to analytics. Apply consent gating where required.

If advertising is requested but provider approval is pending, the website may still be production-deployed. The final report MUST show advertising as `PENDING_PROVIDER_REVIEW`, `CONFIGURED_NOT_LIVE`, or another truthful state rather than claiming full monetization completion.

## 9.3 Production baseline

Read `references/production-baseline.md` and `references/visual-testing.md` for every site. The production baseline covers product completeness, security headers and input handling, privacy/data lifecycle, SEO, accessibility, performance, reliability, analytics hygiene, support/contact surfaces, and jurisdiction-dependent legal/commercial pages.

Do not manufacture legal identity information, compliance claims, reviews, testimonials, user counts, certifications, security guarantees, or business registrations. Missing required real-world legal/business data is a blocker for the affected disclosure, not permission to invent it.

Before public deployment, resolve current high-severity framework/runtime advisories against official sources and use a patched maintained release.

## 9.4 Data and external integrations

When a site stores durable data, accepts uploads, takes payments/subscriptions, sends email/SMS, receives webhooks, exposes contact forms, or runs background jobs, read `references/data-and-integrations.md`.

Key invariants:

- use maintained providers and official SDKs/protocols rather than rolling cryptography or payment handling;
- keep production credentials server-side and separate environments where practical;
- authorize private data on every server-side read/write;
- make migrations, webhooks and retryable jobs idempotent;
- verify webhook signatures and never trust client/model-supplied prices, entitlements or owner IDs;
- keep uploads private by default and validate type/size/path server-side;
- rate-limit contact/auth/message endpoints and other abuse-prone integrations;
- test provider failure/timeout behavior;
- require the Section 15 human cost gate before paid databases/storage, billable messaging, real payment-mode activation/acceptance charges, or other potentially billable external resources.

If an integration needs DNS changes (for example email-domain verification), merge only the provider-required records and preserve unrelated DNS records.

## 10. AI cost and production gate

Real AI inference can incur usage charges. Treat every real provider request as potentially billable unless the provider/account explicitly proves that the operation is zero-cost.

During implementation and routine CI:

- use mocks, fixtures, or provider test doubles by default;
- do not send real prompts to a paid model merely to prove the UI works;
- never create a paid AI key, paid AI resource, paid database, paid storage resource, or paid plan without the human cost gate in Section 15.

Before a real billable AI smoke test or before activating a production AI integration that can create usage charges:

1. identify the provider, project, operation, and current pricing basis when available;
2. propose a concrete spending envelope, such as an exact one-time maximum or a project/key budget for a defined period;
3. show that information to the human;
4. receive explicit human confirmation;
5. record the approval with `scripts/cost_gate.py`;
6. configure provider-side budget/spend limits when supported;
7. only then execute the approved billable operation.

An AI usage budget limits spend; it does not itself authorize spend.

## 11. Local QA gate

A site cannot advance to deployment unless all applicable checks pass:

- production build succeeds;
- typecheck succeeds;
- lint succeeds or the project has no linter;
- automated tests pass when present;
- AI paths have mock/contract tests when AI is enabled;
- authentication and authorization tests pass when auth is enabled, including cross-user isolation for private user data;
- advertising/consent contract tests pass when ads are enabled;
- analytics excludes sensitive payloads and obeys the configured consent path when analytics is enabled;
- a real 404/not-found response exists;
- applicable security headers and abuse controls are configured;
- database/upload/payment/email/webhook/background-job failure and authorization paths are tested when those integrations are present;
- no obvious placeholder content, fabricated claims, or fake social proof remains;
- no broken internal links in critical paths;
- sitemap and robots are generated correctly;
- canonical metadata is coherent;
- production pages do not unintentionally contain `noindex`;
- basic keyboard navigation works;
- mobile viewport is usable;
- visual QA tooling is available or the run is explicitly blocked before preview acceptance;
- no provider secret is present in client bundles or source control.

## 12. Preview deployment gate

Deploy to Vercel preview first.

Visual testing is mandatory. Read `references/visual-testing.md`. `PREVIEW_QA_PASS` MUST NOT be recorded from source inspection, DOM inspection, HTTP checks, or automated unit tests alone. The rendered interface must be opened in a real browser or computer-use environment and visually inspected with screenshot evidence.

At minimum, test the primary user journey at 390 x 844 and 1440 x 900 CSS-pixel viewports, plus breakpoint-sensitive tablet coverage when applicable. Save `.web-factory/reports/<site_id>-visual-qa.json` and validate it with `python scripts/validate_visual_qa.py ...`. If the active runtime cannot render and inspect the UI, mark preview QA `BLOCKED` and do not claim production readiness.

Validate the preview before promoting to production:

- deployment reaches READY state;
- homepage and key routes return expected 2xx/3xx status;
- server/API functions return expected responses;
- no high-severity runtime errors in deployment logs;
- assets load;
- critical form/tool flow works;
- AI routes handle mocked/provider-unavailable states correctly;
- auth-enabled sites correctly reject unauthenticated access and pass at least one valid-session protected-route check;
- ad-enabled sites do not report provider approval/live serving unless actually verified;
- consent-gated advertising/analytics respects denied/unknown consent in the tested region/configuration;
- if a real AI request is required, the human cost gate has passed first;
- mandatory rendered visual QA is `PASS`, with mobile and desktop screenshot evidence and no release-blocking visual defects.

For batch mode, isolate failures per site. A failed site should not automatically block unrelated sites.

## 13. Production deployment

After preview QA passes, deploy/promote to production.

Record:

- Vercel project name;
- production deployment URL;
- deployment ID when available;
- deployment timestamp;
- Git commit SHA when available.

Then run external production smoke checks. Run a rendered visual smoke test against the real production/canonical URL at minimum mobile and desktop viewports. Re-run the full visual suite when production-only configuration, custom-domain behavior, consent, authentication, advertising, or other environment differences can materially change the rendered interface.

If deployment would require a paid plan, paid add-on, paid storage, paid database, paid bandwidth upgrade, or another billable resource, stop at the human cost gate before creating or upgrading it.

## 14. Domain selection

Domain handling has three modes:

### Existing domain
Attach the exact domain supplied by the user. Preserve existing DNS records unless a change is required.

### User-approved candidate
Use the domain candidate already approved by the user, but a prior naming preference is NOT payment approval. If acquiring the domain costs money, the purchase still requires the Section 15 human cost gate.

### Auto-select
Generate several brandable candidates based on the site purpose and locale, then check availability and live price in bulk.

Prefer:

- short, pronounceable names;
- no trademark impersonation;
- no confusing hyphens/numbers unless meaningful;
- TLD appropriate to the target market and budget.

Never assume a domain is available or assume its price. Query live provider data.

## 15. Human cost gate — mandatory for every paid action

Any action that purchases something, upgrades a plan, provisions a paid resource, consumes a potentially billable external service for testing, or otherwise can create a monetary charge requires explicit human confirmation immediately before execution.

This rule is mandatory and cannot be disabled by a manifest, a batch budget, a previous general instruction such as "do whatever is necessary", or an earlier approval for a different charge.

Budgets and price limits are selection constraints only. They NEVER count as payment authorization.

Before a paid action:

1. obtain a current price, price basis, or conservative maximum when possible;
2. identify the exact provider and exact action;
3. identify the exact items/resources covered;
4. state the currency and exact or maximum charge;
5. ask the human to explicitly confirm this paid action;
6. after confirmation, create/record a short-lived approval with `scripts/cost_gate.py`;
7. immediately before execution, check that the live price is within the approved amount and that the approval has not expired;
8. if the price increases, the item list changes, the approval expires, or the provider changes, stop and request fresh confirmation.

A single confirmation MAY cover a batch only when the exact items are already enumerated and the exact or maximum total charge is shown. It may not authorize unknown future purchases.

Examples requiring confirmation include:

- domain purchase, transfer, or paid renewal action;
- Vercel or another hosting plan upgrade;
- paid database, storage, queue, authentication/identity plan, transactional email/SMS, analytics, or third-party API provisioning;
- a real AI inference test that may consume paid credits;
- creating or increasing an AI Gateway/provider spend budget when it enables billable usage;
- any marketplace purchase or paid add-on.

Read-only availability/price checks and clearly zero-cost operations do not require payment confirmation. Genuinely zero-cost provisioning/configuration SHOULD proceed autonomously when authorized tools are available. A free tier with possible automatic overage, attached-billing exposure, paid credit consumption, or no enforceable zero-spend boundary is NOT clearly zero-cost.

## 16. Vercel domain and DNS workflow

Prefer live Vercel provider state over hard-coded DNS assumptions.

Typical sequence:

1. Check current project/domain state.
2. Check domain availability and current price.
3. If purchase is required, pass the Section 15 human cost gate for the exact domain and current price.
4. Purchase only while that approval remains valid, or attach an existing domain.
5. Add domain to the correct Vercel project.
6. Run domain inspection to obtain required DNS configuration.
7. Apply the provider-recommended DNS records.
8. Preserve unrelated MX/TXT/CAA records.
9. Add canonical host redirect if both apex and `www` are attached.
10. Re-run domain inspection.
11. Confirm HTTPS certificate and an external HTTPS request.

When Vercel manages DNS, use Vercel CLI/API/MCP. When an external provider is authoritative, use that provider if an authenticated tool is available; otherwise stop at a precise DNS change plan instead of pretending the records were changed.

Do not hard-code a Vercel A/CNAME target when `vercel domains inspect` supplies a project-specific requirement.

## 17. Google ownership verification

Use Google Site Verification API with `DNS_TXT` for domain properties whenever feasible.

Workflow:

1. Obtain an OAuth token authorized for Site Verification and Search Console.
2. Request a DNS TXT verification token for the domain.
3. Add the TXT record using the authoritative DNS provider.
4. Wait/retry for DNS visibility using bounded exponential backoff.
5. Call Site Verification API to verify ownership.
6. Record `GOOGLE_VERIFIED` only after Google confirms ownership.

`scripts/google_search_console.py` contains helper operations for token retrieval, verification, Search Console property creation, sitemap submission and URL inspection.

## 18. Search Console provisioning

After ownership is verified:

1. Add the domain property as `sc-domain:<domain>`.
2. Submit `https://<canonical-host>/sitemap.xml`.
3. Use URL Inspection on the canonical homepage as an observability check when credentials/quota permit.
4. Record submission results.

For ordinary websites, do NOT use Google's Indexing API as a generic indexing shortcut. Only use it for pages that actually qualify under Google's supported `JobPosting` or livestream `BroadcastEvent` use cases.

Never report "Google indexed" merely because a sitemap was submitted. Distinguish:

- ownership verified;
- Search Console property added;
- sitemap submitted;
- URL inspected;
- indexed according to inspection data.

## 19. Batch execution strategy

In batch mode, use staged concurrency rather than launching every mutation at once.

Recommended defaults:

- planning/scaffolding: up to 5 sites concurrently;
- builds/tests: up to 3 sites concurrently or lower if RAM/CPU is constrained;
- preview deploys: up to 3 concurrently;
- domain availability checks: bulk API when supported;
- paid actions: do not execute concurrently unless one explicit human approval covers the exact enumerated batch and the provider supports safe atomic/bounded execution;
- DNS/Search Console: up to 3 domains concurrently with retry/backoff;
- real AI tests: keep concurrency low and within the human-approved spending envelope.

Adjust downward when provider rate limits or local resource pressure appear.

Checkpoint after every stage by updating `.web-factory/state.json`.

If the run is interrupted, resume from provider state + state file rather than starting over. Never reuse an expired paid-action approval after a resume.

## 20. Failure policy

Classify failures:

- `SITE_LOCAL`: implementation/test issue affecting one site;
- `PROVIDER_SITE`: deployment/domain issue affecting one site;
- `SHARED_AUTH`: expired/missing shared authentication;
- `SHARED_QUOTA`: provider quota/rate limit;
- `HUMAN_COST_GATE`: paid action requires confirmation or fresh approval;
- `BUDGET_GATE`: action would exceed a configured selection/spend cap;
- `EXTERNAL_DNS`: DNS provider not automatable with available credentials/tools;
- `HUMAN_AUTHORIZATION`: provider requires direct login/OAuth/2FA/CAPTCHA/terms/ownership action that cannot be delegated.

For site-local failures, continue unrelated sites and report the failed site.

For shared authentication, budget, permissions, human-authorization, or human-cost blockers, stop the affected stage cleanly and preserve state. Ask only for the minimum unavoidable human action, then resume the blocked stage automatically once it is resolved.

For implementation/test failures, keep iterating on diagnosis and fixes rather than returning a partial site. Do not silently downgrade production requirements.

## 21. Acceptance checks

A site is `COMPLETE` only when all user-requested stages are satisfied, the planned public-production acceptance criteria are met, and mandatory preview plus production visual testing has passed. A missing browser/visual capability is a truthful `BLOCKED` condition, not permission to infer visual correctness from source code.

For full one-click production deployment, require:

- implementation complete;
- local QA pass;
- production deployment live;
- core AI feature works in production when AI was requested, with a real provider smoke check only after the required human cost approval;
- authentication, protected routes, authorization, and cross-user isolation work in production when accounts were requested;
- custom domain live if requested;
- DNS verified;
- HTTPS pass;
- robots/sitemap reachable;
- Google ownership verified if requested;
- Search Console property added if requested;
- sitemap submitted if requested;
- advertising integration is truthfully reported if requested, including provider review and ads.txt state;
- analytics/consent behavior is verified if requested;
- the production baseline has no unresolved release-blocking security, privacy, accessibility, or functional issue.

Run `scripts/validate_site.py https://example.com` for a final HTTP/SEO smoke check when possible.

## 22. Final report

For single-site mode, report:

- what was built;
- AI capability/provider integration and whether the real provider path was tested;
- authentication provider/methods and authorization checks when accounts are enabled;
- advertising provider, ads.txt, consent, and provider-review/live-serving status when ads are enabled;
- analytics provider and consent status when analytics is enabled;
- production-baseline/security status and any known limitations;
- repository/project;
- production URL;
- custom domain;
- deployment status;
- DNS/HTTPS status;
- Google verification status;
- sitemap status;
- URL inspection/index status if checked;
- costs actually incurred;
- approvals used for paid actions, without exposing secrets;
- any remaining external action.

For batch mode, additionally create `.web-factory/reports/final.json` and a concise table with one row per site.

Never say "complete" when an external step, required AI production check, required plan item, or human cost approval is still pending. Unless blocked by a truly external human/provider condition, continue working instead of returning a partial result.
