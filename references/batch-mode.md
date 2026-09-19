# Batch mode operating guide

## Objective

Scale website production without turning the run into an uncontrolled loop of duplicated sites, duplicate purchases, provider rate-limit failures, runaway AI usage, or unrecoverable partial state.

## Portfolio planning

Before implementation, create a compact portfolio matrix with:

- site_id
- target user
- primary job-to-be-done
- core deterministic feature/tool
- AI capability, only when it materially improves the job
- content differentiation
- monetization only if requested
- preferred domain patterns

Reject or redesign concepts that overlap substantially.

## Concurrency

Treat the following as independent pools:

- CPU-heavy local builds
- network deployments
- read-only domain availability queries
- paid actions
- DNS mutations
- Google API calls
- real AI provider tests

Keep paid actions conservative. Never fan out potentially billable operations without an explicit human approval that enumerates the exact batch and bounds the total charge.

## Idempotency

Every site has a stable site_id. Every external resource must be recorded after creation:

- Vercel project ID/name
- deployment URL/ID
- domain
- registrar order ID when available
- DNS verification status
- Search Console property
- sitemap URL
- AI provider/project identifiers that are safe to store
- approval request IDs for paid actions, but never secret keys or tokens

On resume, inspect external state first. Do not reuse expired paid-action approvals.

## Batch completion semantics

A batch can be:

- COMPLETE: all requested sites complete;
- PARTIAL: some sites complete, others failed or blocked;
- BLOCKED: shared dependency prevents continuation;
- HUMAN_CONFIRMATION_REQUIRED: the next step can spend money and requires explicit approval;
- BUDGET_STOP: the next step exceeds a configured selection or spending cap.

Never collapse PARTIAL or a human-confirmation blocker into COMPLETE.
