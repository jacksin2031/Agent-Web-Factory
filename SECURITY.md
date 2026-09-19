# Security policy

## Reporting

Please report security issues privately to the repository maintainer rather than opening a public exploit report when the issue could expose credentials, enable unintended paid actions, or mutate third-party infrastructure.

## Security invariants

- Never commit provider credentials, OAuth tokens, API keys, or private keys.
- Never persist secrets in `.web-factory/state.json` or approval records.
- Every paid action requires explicit human confirmation immediately before execution.
- Routine CI must use mocks and must never purchase domains, upgrade plans, provision paid resources, or consume paid AI inference.
- External model/tool output is untrusted until validated.
- Authentication is never treated as authorization; protected data and mutations require server-side authorization.
- User-owned data must be isolated across accounts, and service-role/admin credentials must never reach browser code.
- Advertising and analytics must not receive authentication credentials, private uploads, sensitive AI content, or fabricated publisher identifiers.
- Provider review/approval state must never be reported as successful before it is verified.
