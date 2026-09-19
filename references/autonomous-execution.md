# Planning-first autonomous execution

Agent Web Factory defaults to a public-production outcome, not a prototype, scaffold, design exercise, or partially configured preview.

## Mandatory planning pass

Before implementation starts, create a concrete plan for every site. The plan must be derived from the user's request, current repository state, and current provider/framework documentation where external behavior can change.

The plan must define at least:

- product goal and target users;
- primary user journey and public-release acceptance criteria;
- required, optional, and explicitly rejected features;
- page/route and information architecture;
- data model and persistence requirements;
- AI capabilities and deterministic alternatives;
- authentication and authorization requirements;
- advertising, analytics, consent, and monetization requirements;
- external APIs, databases, storage, email, payments, webhooks, jobs, or other integrations;
- security, privacy, abuse-prevention, accessibility, SEO, performance, observability, and legal/disclosure requirements;
- visual states and browser QA coverage;
- deployment, domain, DNS, HTTPS, and Search Console steps;
- cost classification for each external dependency;
- blockers that genuinely require human action.

Save a concise machine-readable plan at `.web-factory/reports/<site_id>-plan.json`. Planning is not a human approval gate. Once the plan is internally coherent, continue execution automatically.

## Autonomous-to-production rule

After planning, continue implementing, testing, fixing, deploying, and re-testing until the site satisfies the `COMPLETE` acceptance contract or a truthful blocker is reached.

Do not stop merely because:

- scaffolding succeeded;
- the first build passed;
- a preview exists;
- an MVP exists;
- one test suite passed;
- an integration still needs configuration that the agent can perform;
- a zero-cost API, database, DNS record, OAuth application, environment variable, or provider setting still needs routine setup.

When a test fails, diagnose it, fix the underlying issue, and repeat the affected gates. Prefer bounded retries and root-cause fixes over repeated blind retries.

## Zero-cost external services and APIs

The agent must independently handle zero-cost technical setup when the available tools, credentials, and provider permissions allow it. This includes researching current official documentation, selecting an appropriate maintained provider, provisioning a genuinely zero-cost resource, configuring environment variables or secret stores, creating required non-billable settings, wiring SDKs/APIs, applying migrations, and running zero-cost verification.

Do not ask the user to choose routine technical details when the agent can make a production-safe choice from the requirements. Do not ask the user to copy/paste credentials when a secure connected tool or provider secret manager can complete the operation directly.

A service is only treated as zero-cost when the operation cannot create a monetary charge under the active account/configuration. A nominal free tier is NOT enough when:

- overage is automatically billable;
- a credit balance is consumed and can trigger paid replenishment;
- a billing account/card is attached and usage can exceed the free allowance;
- enabling the feature itself creates a paid subscription or metered resource;
- the provider cannot establish a hard zero-spend boundary.

Those cases are potentially billable and must use the human cost gate.

Prefer a truly zero-cost provider/configuration when it meets the production requirement without materially degrading security, reliability, or the core user experience. Do not silently replace a required paid-grade capability with an unsafe or non-production substitute merely to avoid confirmation.

## Human interaction that is not a design decision

A human may still be required for an external system's mandatory identity or consent step, for example OAuth authorization, account login, 2FA, CAPTCHA, acceptance of provider terms, organization ownership proof, or legally required real-world owner/business information.

When that happens:

1. complete every safe step that can be automated first;
2. Ask only for the minimum required human action;
3. preserve state;
4. resume automatically after the authorization/data becomes available;
5. do not reopen already resolved technical decisions.

These are authorization/identity blockers, not permission to ask broad implementation questions.

## Completion truthfulness

A site may be described as public-production ready only after all mandatory functional, security, privacy, accessibility, visual, deployment, and requested external-integration gates pass. External asynchronous states such as ad-network review or search indexing must remain truthful pending states and do not permit fabricated completion.
