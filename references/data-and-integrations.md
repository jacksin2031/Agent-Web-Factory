# Data, payments, messaging, uploads, and external integrations

Use this reference whenever the generated product stores durable data, accepts uploads, sends messages, receives webhooks, charges users, runs background work, or depends on an external API.

## Database and durable state

- Choose the smallest maintained datastore that matches the access pattern; do not provision a database for a purely static tool.
- Define schema constraints, ownership/tenant boundaries, indexes, and migrations explicitly.
- Use server-side authorization for every private record access. Database policies such as RLS are defense in depth, not a substitute for understanding the application authorization model.
- Keep administrative/service credentials server-side.
- Use environment separation for local/preview/production when the provider supports it.
- Make migrations repeatable and review destructive migrations before production.
- Define backup/restore or export expectations when user data would be costly to lose. Do not claim backups exist unless configured and verified.
- Define deletion and retention behavior for account data, logs, uploads, and generated artifacts.

Provisioning or upgrading a paid database is subject to the human cost gate.

## File uploads and object storage

- Enforce size, count, extension and MIME checks server-side; inspect file signatures when the risk warrants it.
- Generate storage keys rather than trusting client filenames or paths.
- Keep private uploads private by default; use short-lived signed access where appropriate.
- Authorize every read/write/delete independently.
- Consider malware/content scanning for public sharing or higher-risk upload types.
- Prevent SVG/HTML/scriptable uploads from becoming same-origin XSS unless intentionally sanitized and isolated.
- Remove abandoned temporary uploads where practical.

Paid storage, scanning, CDN, transformation, or egress actions are subject to the human cost gate when they can create a charge.

## Payments and subscriptions

When the product accepts money, prefer an established payment provider and its hosted/maintained payment primitives instead of handling card data directly.

- Develop and test in provider test/sandbox mode by default.
- Treat client-provided price, plan, product, entitlement, discount, tax, and user IDs as untrusted.
- Derive sellable price/product identifiers from server-controlled configuration/provider state.
- Verify webhook signatures using the provider's official library or documented algorithm.
- Make webhook/event handling idempotent and safe against replay/out-of-order delivery.
- Grant entitlements from verified provider state/events, not from the browser redirect alone.
- Reconcile cancellation, refund, failed payment, chargeback, and subscription-status changes where relevant.
- Do not log payment secrets or unnecessary payment/customer personal data.
- Add applicable pricing, billing, cancellation/refund, and commercial disclosures using real business information only.

Switching to a live payment mode can cause processor fees or real financial transactions. Require explicit human confirmation immediately before activating live mode or executing any real transaction used for acceptance testing.

## Transactional email, SMS, and notifications

- Use a maintained provider and authenticated sending domain when production delivery is required.
- Separate transactional messages from marketing consent/preferences.
- Avoid account enumeration through message/recovery responses.
- Do not put secrets into analytics or message templates.
- Validate recipient addresses/numbers and rate-limit abuse-prone flows.
- Configure bounce/complaint handling when the provider/product requires it.
- For production email, configure the provider-required SPF/DKIM/DMARC-related DNS records carefully without overwriting unrelated records.

Paid email/SMS messages, dedicated IPs, provider upgrades, or other billable messaging are subject to the human cost gate.

## Contact forms and abuse prevention

- Validate inputs server-side.
- Rate-limit and add anti-automation controls proportional to abuse risk.
- Avoid publishing private destination email addresses in client code when a server relay is available.
- Sanitize or safely encode user-submitted text before inserting it into HTML emails, dashboards, logs, tickets, or AI prompts.
- Provide a success/error state without exposing internal provider details.

## Webhooks and external APIs

- Verify webhook authenticity/signatures before processing.
- Store provider event IDs or another deduplication key when retries are possible.
- Bound retries and use exponential backoff for safe idempotent operations.
- Never retry irreversible mutations blindly.
- Validate outbound URLs and prevent SSRF when users or models can influence destinations.
- Use allowlists for high-impact tool/API actions.
- Set connection/read timeouts and handle provider degradation visibly.
- Respect provider rate limits and current API versions from official documentation.

## Background jobs and schedulers

- Make jobs idempotent or deduplicated.
- Define retry/dead-letter behavior for important asynchronous work.
- Keep job payloads free of unnecessary secrets/sensitive content.
- Record enough status for support/debugging without turning logs into a shadow database of personal data.
- Avoid schedules that can unexpectedly create runaway third-party or AI cost.

## Acceptance tests

Exercise the applicable failure paths, not only the happy path:

1. unauthorized data access fails closed;
2. malformed/oversized upload is rejected;
3. duplicate webhook/event does not duplicate side effects;
4. provider timeout/failure yields a recoverable state;
5. real payment mode is not activated accidentally;
6. contact/auth/message abuse is rate-limited;
7. destructive data/account action has the intended confirmation and authorization boundary;
8. no paid external resource bypasses the human cost gate.
