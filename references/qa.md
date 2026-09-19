# Production acceptance checklist

A site should pass, where applicable. Rendered visual testing is mandatory; see `visual-testing.md`.

- package install reproducible
- typecheck
- lint
- tests
- production build
- preview smoke test
- production smoke test
- canonical metadata
- unique title and description
- robots.txt reachable
- sitemap.xml reachable
- no accidental noindex
- 404 behavior
- key tool/form flow
- mobile usability
- actual browser-rendered visual QA at mobile and desktop viewports with screenshot evidence
- no release-blocking overlap, clipping, horizontal overflow, broken media, or obscured critical controls
- keyboard accessibility basics
- HTTPS
- domain redirect/canonical consistency
- no secrets in client bundle or repository
- no high-severity production log errors

## Additional AI acceptance checks

When AI is enabled:

- AI API secrets are server-side only
- AI endpoints have rate/input/output/step limits
- structured output is schema-validated where applicable
- tool calls are allowlisted and argument-validated
- RAG/uploaded content is treated as untrusted data
- provider timeout/cancellation/error states are handled
- CI uses mocks rather than paid inference
- any real potentially billable provider smoke test has a current human approval record
- production AI spend controls are configured when supported and approved
