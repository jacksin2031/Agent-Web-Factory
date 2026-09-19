# Domain and DNS runbook

## Selection

For automatic naming, create a shortlist per site and query live availability/pricing. Avoid trademark-like or deceptive names.

A price ceiling is only a selection constraint. It does not authorize a purchase.

## Purchase

Buying, transferring, or otherwise paying for a domain requires explicit human confirmation for the exact domain(s) and current exact or maximum total price immediately before execution.

A single confirmation can cover a batch only when every domain is enumerated and the exact or maximum total charge is shown. General batch budgets do not authorize unknown future purchases.

Record the approval with `scripts/cost_gate.py`, re-check price before purchase, and request fresh confirmation if the price or item list changes or the approval expires.

## Attachment

Attach the domain to the intended Vercel project, then inspect the domain to learn the exact DNS requirements.

## DNS safety

Before writing records:

1. list existing records when possible;
2. identify the authoritative DNS provider;
3. preserve unrelated MX, TXT, CAA and verification records;
4. never mass-delete DNS records to simplify setup;
5. make the smallest required change;
6. verify after propagation.

If DNS is external and there is no authenticated tool for that provider, emit the exact record plan and mark the stage blocked rather than claiming success.
