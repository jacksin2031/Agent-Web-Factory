# Authentication and authorization guide

## Principle

Add accounts only when identity unlocks a real product requirement: private data, saved cross-device state, collaboration, paid entitlements, roles, personalization, or another identity-bound feature. Public calculators and content sites should remain account-free unless the user asks otherwise.

Authentication answers **who the user is**. Authorization answers **what that user may access or change**. A login screen without server-side authorization is not a complete security implementation.

## Provider selection

Resolve current provider capabilities and pricing from official documentation at execution time. Do not freeze this Skill to a provider plan or stale package version.

For Next.js projects:

- Auth.js is a strong default for framework-native OAuth/session flows where the application does not need a managed identity database.
- Supabase Auth is a strong default when the application also needs a managed Postgres database, persistent user profiles, magic-link/password flows, or Row Level Security for user-owned data.
- Other maintained providers such as Clerk, Firebase Authentication, an enterprise IdP, or a user-specified provider are valid when their capabilities better match the product.
- Do not create a custom password/session/OAuth implementation when a maintained library or identity provider can satisfy the requirement.

## Supported manifest methods

The manifest can express password, magic link, email OTP, phone OTP, OAuth providers, passkeys, anonymous sessions, or another documented method. Only implement methods that the selected provider currently supports.

Phone OTP, SMS, transactional email, managed databases, and identity-provider plans can become billable. The normal human cost gate applies before any paid provisioning or billable test.

## Next.js server boundary

For protected data and mutations, perform the authorization decision on the server. A proxy/middleware redirect is useful for navigation but is not sufficient as the only protection. Every sensitive server action, route handler, API endpoint, database mutation, file operation, and AI tool that reaches private resources must independently verify the current identity and permission.

Do not use static or shared caching for authenticated responses if it could mix sessions or private data across users. Follow the current auth-provider guidance for cookie/session refresh and framework caching behavior.

## Database authorization

For per-user records, default to owner isolation. Store a stable user identifier and enforce access in the database or trusted server layer.

When using Supabase:

- enable RLS on user-owned tables;
- create explicit policies for SELECT/INSERT/UPDATE/DELETE as required;
- avoid broad policies that trust a client-supplied user ID;
- derive the current user from verified auth context;
- never expose the service-role secret to the browser;
- test that User A cannot fetch or mutate User B's rows even by manually changing a resource identifier.

## Password and recovery flows

Prefer provider-managed password storage and recovery. Do not design password hashing, salts, reset tokens, or session cryptography in generated application code.

When password login is enabled, account recovery must be enabled unless the product has an explicit documented reason not to support it. Use non-enumerating error messages and provider controls for verification, token expiry, and replay prevention.

## OAuth

Use provider/library OAuth support rather than hand-rolling protocol requests. Restrict callback URLs and post-login redirects to expected origins. Keep client secrets server-side. Use the selected library/provider's current state, PKCE, and nonce protections where applicable.

## Session security

Use the selected provider/library's secure cookie/session defaults. Production sessions must use HTTPS. Reject expired, revoked, malformed, or missing sessions. Sign-out must remove or invalidate access.

## Account lifecycle

When the application stores user data, provide an appropriate deletion flow or a clearly documented deletion request process. Delete or detach user-owned data according to the product's retention rules. If the site supports profile export or portability, ensure exports are scoped to the authenticated account.

## AI + authentication

For authenticated AI products:

- derive usage limits and entitlements from server-verified identity, not browser claims;
- never allow a model to choose or override the authenticated user ID;
- authorize every model tool call that accesses user data;
- namespace vector stores, files, conversation history, and retrieval indexes by tenant/user as required;
- test prompt/tool paths for cross-user data leakage;
- do not include auth secrets, session tokens, reset tokens, or OAuth credentials in model context.

## Acceptance checklist

An auth-enabled site is not production-ready until applicable checks pass:

- sign-up/sign-in/sign-out work;
- protected pages reject unauthenticated access;
- protected server mutations reject unauthenticated access;
- valid sessions survive normal navigation and refresh;
- expired/invalid sessions fail closed;
- role/permission checks fail closed;
- cross-user ID tampering cannot expose or mutate another user's data;
- password recovery or verification works when enabled;
- OAuth redirect/callback configuration is restricted correctly;
- auth secrets are not in Git, browser bundles, logs, factory state, or final reports;
- privacy/legal disclosures are present when personal data is collected;
- no paid auth/SMS/email/database operation occurs without explicit human confirmation.
