# Advertising and monetization

Use this reference when `site.ads.enabled` is true.

## Provider selection

Default to `provider: auto` and choose a maintained advertising platform that matches the site's audience and product constraints. Google AdSense is the default general-purpose option when the user has no provider preference and the site is eligible.

Do not create an advertising account, enroll in a paid product, or activate a paid consent platform without the human cost gate when the action can create a charge.

## AdSense production rules

For Google AdSense:

- Treat site connection, site review, ads.txt authorization, and live ad serving as separate states.
- Never report that ads are live merely because the AdSense code was installed or a site was submitted for review.
- Only report `ADS_LIVE` after provider state shows the site is approved/ready and a production smoke check confirms the integration is eligible to serve.
- Use the real publisher ID supplied by the authenticated account or user. Never invent or ship placeholder publisher IDs.
- When ads.txt is required, publish the exact provider-authorized line at `/ads.txt` and verify it is publicly reachable.
- Do not use misleading placements, fake navigation, forced clicks, click incentives, or layouts that make ads indistinguishable from product controls.
- Keep ads away from authentication forms, destructive actions, sensitive account flows, and primary AI input controls where placement could cause accidental clicks.
- Preserve Core Web Vitals and avoid layout shifts by reserving stable ad space where practical.

## Consent and privacy

Determine consent requirements from the actual traffic regions, advertising mode, analytics stack, and provider policy. Do not guess that a generic cookie banner is compliant.

When serving personalized Google publisher ads to users in the EEA, UK, or Switzerland, use a Google-certified CMP integrated with the IAB Transparency and Consent Framework as required by Google's current publisher policy. Resolve the current certified CMP requirements from official documentation at execution time.

When consent is required:

- block consent-dependent ad/analytics storage until the applicable consent state is available;
- provide a way to revisit consent choices when required;
- keep the privacy/cookie disclosures consistent with the deployed vendors;
- test denied, accepted, and unavailable-consent paths;
- do not dark-pattern users into accepting tracking.

## Ad QA

When advertising is enabled, test at least:

1. advertising scripts load only where intended;
2. no placeholder publisher/slot identifiers remain in production;
3. `/ads.txt` is correct and reachable when applicable;
4. consent-gated scripts respect denied/unknown consent where required;
5. ad containers do not cause severe cumulative layout shift;
6. ads do not cover navigation, forms, AI controls, legal notices, or content needed to complete the primary task;
7. provider review/approval state is represented truthfully in the final report;
8. no paid advertising/CMP action bypasses the human cost gate.
