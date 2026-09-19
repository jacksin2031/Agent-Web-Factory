# Production website baseline

Apply this baseline to every generated production site unless a requirement makes a check inapplicable. A site can be intentionally small, but it must not be a half-finished demo presented as production-ready.

## Product completeness

- Complete the primary user journey end to end.
- Add useful empty, loading, success, validation, offline/provider-unavailable, and error states where applicable.
- Provide a real 404/not-found response and an error boundary or equivalent recovery path for dynamic applications.
- Remove placeholder copy, lorem ipsum, fake testimonials, fake counters, fake reviews, and fabricated trust claims.
- Provide a contact/support route or another clear support mechanism when users create accounts, upload data, pay, or depend on a hosted service.

## Security

- Use current patched framework/runtime versions and check current security advisories before a public release.
- Keep secrets server-side and out of source control, client bundles, logs, analytics, AI context, factory state, and reports.
- Validate and normalize untrusted input at server boundaries.
- Encode/escape untrusted output and avoid unsafe HTML injection.
- Use CSRF protections where the selected framework/auth architecture requires them.
- Rate-limit abuse-prone public endpoints such as auth, AI, contact, upload, expensive search, and mutation endpoints.
- Restrict uploads by type, size, storage path, and authorization; never trust a filename or MIME type alone.
- Add security headers appropriate to the application. At minimum evaluate CSP, HSTS on production HTTPS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and clickjacking protection through CSP `frame-ancestors` or equivalent.
- Do not rely solely on framework middleware/proxy for authorization.
- Run dependency/security audit tooling available to the chosen stack and resolve high-severity actionable findings before release.

## Privacy and data lifecycle

- Collect the minimum data needed for the feature.
- Document material processors/providers when personal data, uploads, authentication, analytics, advertising, or AI processing is enabled.
- Provide privacy disclosures when personal data is processed.
- Provide account/data deletion or a documented deletion process when persistent user data is stored.
- Define retention behavior for uploads, logs, analytics, AI conversations, and generated content where relevant.
- Never claim legal compliance merely because a template page exists; requirements are jurisdiction- and business-specific.

## SEO and discoverability

- Unique title and meta description for important indexable routes.
- Canonical URLs that resolve to the intended production host.
- `robots.txt` and `sitemap.xml` that match the indexing policy.
- Open Graph/social metadata for public shareable pages.
- Structured data only when it accurately matches visible content and the current search-engine specification.
- Human-readable navigation and internal links to important public routes.
- Do not generate doorway pages, keyword-spun pages, mass low-value location pages, or fabricated freshness signals.

## Mandatory rendered visual QA

Every production site must pass the rendered-browser workflow in `visual-testing.md`. Source-code inspection is not a visual test. Preview acceptance requires screenshot evidence at minimum mobile and desktop viewports, and production requires a rendered visual smoke test against the real canonical URL. If the active runtime cannot render/inspect the UI, visual QA is blocked and the site must not be reported as production-complete.

## Accessibility and UX

- Semantic landmarks and heading hierarchy.
- Keyboard-operable interactive controls with visible focus.
- Programmatic labels and accessible names.
- Useful validation and error messages.
- Sufficient contrast and non-color-only state communication.
- Respect reduced-motion preferences for non-essential animation.
- Usable responsive layout at common phone, tablet, and desktop widths.
- Avoid blocking the primary task with modals, ads, or consent UI.

## Performance and reliability

- Optimize images and fonts; avoid shipping unnecessary client JavaScript.
- Lazy-load non-critical third-party scripts and heavy media where appropriate.
- Avoid severe layout shift and long blocking work on primary routes.
- Set sensible request timeouts and retries; never retry irreversible mutations blindly.
- Add health/error observability appropriate to the app's complexity without logging secrets or unnecessary personal data.
- Configure caching deliberately so private/authenticated data cannot leak between users.

## Analytics

Analytics is optional and defaults off. When enabled:

- use a maintained provider;
- document the events/metrics needed rather than collecting everything;
- exclude secrets and sensitive form/AI content from analytics;
- honor consent requirements for the selected regions/provider;
- verify production traffic is not polluted by obvious local/test events when practical.

## Legal/commercial surfaces

Add only what the product actually needs. Depending on features and jurisdiction this may include:

- privacy policy;
- terms of service/use;
- cookie/consent controls;
- commercial disclosure or seller information;
- refund/cancellation terms;
- AI limitations/disclosure where material;
- contact/support information.

Do not fabricate company names, addresses, registration numbers, legal names, or operator identities. If required owner/business information is missing, leave the affected production/legal step blocked and request the real information.
