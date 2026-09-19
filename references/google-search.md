# Google Search provisioning

## Correct workflow for normal sites

1. Generate and serve a valid sitemap.
2. Verify domain ownership with Google Site Verification API using DNS TXT when feasible.
3. Add Search Console domain property (`sc-domain:example.com`).
4. Submit the canonical sitemap URL.
5. Optionally use URL Inspection to observe index status.

Sitemap submission is not proof of indexing.

## Authentication scopes

Common scopes used by this skill:

- `https://www.googleapis.com/auth/siteverification`
- `https://www.googleapis.com/auth/webmasters`

Acquire OAuth credentials through an approved user-authenticated flow. Do not store refresh/access tokens in the repository.

## Indexing API

Do not use Google Indexing API for ordinary pages. It is reserved for supported job posting and livestream event page cases. Use sitemap + Search Console for ordinary websites.
