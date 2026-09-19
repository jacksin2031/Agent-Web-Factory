# Agent Web Factory release checklist

## Automated release gates

- [ ] `VERSION` matches the release tag.
- [ ] `python -m pip install -r requirements-dev.txt` succeeds.
- [ ] `python scripts/run_test_shard.py core`, `manifest-cost`, and `policy-compat` all pass with no skips hiding required policy tests.
- [ ] `python scripts/validate_manifest.py assets/batch.example.json` passes.
- [ ] `python scripts/validate_plan.py assets/site-plan.example.json` passes.
- [ ] `python scripts/compatibility_check.py` passes.
- [ ] `python scripts/validate_visual_qa.py assets/visual-qa.example.json` passes.
- [ ] `python scripts/preflight.py` completes and accurately reports available/missing runtimes/tools.
- [ ] `python scripts/package_release.py --output agent-web-factory.zip` succeeds.
- [ ] Release ZIP contains `SKILL.md`, `LICENSE`, runtime matrix, adapters, tests, scripts, references, and no secret/generated artifacts.
- [ ] Release ZIP contains no `.env`, private key, credential file, `.web-factory`, cache, compiled bytecode, or embedded approval ledger.
- [ ] Repository user-visible text remains English-only.
- [ ] GitHub Actions workflow YAML parses and release workflow enforces tag/version consistency.

## Core policy gates

- [ ] Every site is planned before implementation, including features, architecture, integrations, security/privacy/accessibility/SEO/visual QA, deployment, cost classification, and release criteria; the plan validates before the site enters `PLANNED`.
- [ ] Default execution continues autonomously until public-production acceptance or a truthful external blocker; scaffold/MVP/preview alone is not completion.
- [ ] Genuinely zero-cost APIs/resources are configured autonomously when tools/permissions permit; potentially billable free tiers are routed through the human cost gate.
- [ ] Non-financial human interaction is limited to unavoidable provider identity/authorization/legal-data steps, after which execution resumes automatically.
- [ ] Every potentially billable action still requires explicit human confirmation immediately before execution.
- [ ] A budget, cap, batch instruction, tool permission, or generic approval cannot authorize future unknown paid actions.
- [ ] Cost approvals are exact-provider/item/currency/maximum-bound, short-lived, one-time, and tamper/replay resistant.
- [ ] Runtime adapters explicitly inherit the core financial safety rule and cannot weaken it.
- [ ] AI output cannot bypass authorization or trigger consequential external mutation without an authorization boundary.
- [ ] Authentication and authorization remain separate, with cross-user isolation tests for private data.
- [ ] External/provider states are reported truthfully and never inferred from submission alone.
- [ ] Resumable state prevents replay of irreversible completed actions.
- [ ] Missing tools/credentials/permissions produce blocked or pending states rather than fake success.

## Production feature gates

- [ ] AI workflow uses mock-first tests and current provider documentation for real activation.
- [ ] Auth flow tests protected routes, invalid sessions, sign-out, authorization, and cross-user isolation.
- [ ] Advertising flow separates code installation, provider review, consent/CMP, ads.txt, and live-serving states.
- [ ] Analytics excludes sensitive payloads and obeys configured consent requirements.
- [ ] Production baseline covers 404/error paths, security headers, abuse controls, accessibility, privacy/data lifecycle, performance, observability, support/contact surfaces, SEO, and applicable legal disclosures.
- [ ] Mandatory rendered visual QA cannot pass from source/DOM inspection alone and requires mobile + desktop screenshot evidence.
- [ ] A runtime without browser/visual inspection capability reports visual QA as BLOCKED rather than claiming production completion.
- [ ] Database/upload/payment/webhook/email/SMS/background-job paths use authorization, idempotency, signature/validation, rate-limit, and failure-path rules when applicable.
- [ ] Market-research flow prohibits fabricated SEO/traffic/revenue metrics and near-duplicate thin-site batches.
- [ ] Provider-specific instructions require current official documentation rather than stale prices, model IDs, DNS targets, or API assumptions.

## Runtime acceptance matrix

For each runtime marked first-class in `assets/runtime-matrix.json`, record the release-specific result in the release notes or test evidence.

Required scenarios are defined in `tests/MANUAL_E2E.md`:

- [ ] OpenAI Codex / ChatGPT Skills discovery and invocation.
- [ ] Gemini CLI discovery/activation and invocation.
- [ ] GitHub Copilot agent-skill discovery and invocation.
- [ ] Claude Code skill discovery and invocation.
- [ ] Common zero-cost single-site workflow.
- [ ] Batch/resume workflow.
- [ ] Human cost-gate refusal before an unapproved paid action.
- [ ] Changed price/item/currency requires fresh approval.
- [ ] AI/Auth cross-user isolation scenario.
- [ ] Advertising/provider-state truthfulness scenario.
- [ ] Production baseline and final-report truthfulness scenario.
- [ ] Mandatory visual QA scenario, including mobile + desktop screenshots, responsive states, and a deliberate visual defect that must fail acceptance.

A public beta MAY ship with one or more first-class runtime E2E scenarios pending only when all automated gates pass, the release is explicitly marked prerelease, and the missing runtime verification is stated as a limitation.

A stable release MUST NOT claim a first-class runtime is verified unless its real runtime acceptance scenarios were executed successfully for that release.

## External/provider safety

- [ ] No domain purchase, paid upgrade, billable model call, billable messaging send, live payment charge, or paid resource provisioning is performed merely for release testing.
- [ ] Zero-cost/read-only provider checks may run without financial approval.
- [ ] Any deliberately tested paid path has a separate, exact, explicit human confirmation recorded immediately before execution.

Do not publish a release if an automated gate fails. Do not convert an unexecuted runtime/provider scenario into a claimed PASS.
