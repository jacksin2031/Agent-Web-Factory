# Mandatory visual and rendered-browser QA

Visual QA is a release gate for every website produced by Agent Web Factory. Source review, DOM inspection, unit tests, Lighthouse-style metrics, and HTTP smoke checks are useful, but none of them can replace looking at the rendered interface.

## Core rule

A site MUST NOT be marked `PREVIEW_QA_PASS` or `COMPLETE` until an actual browser-rendered visual test has been executed and recorded.

Use, in order of preference:

1. an existing project browser/E2E suite with screenshot support;
2. Playwright or an equivalent browser automation tool;
3. an authenticated computer-use/browser tool supplied by the active agent runtime;
4. a human browser review recorded in the visual QA report when automation is unavailable.

Reading HTML/CSS/React source, checking only the DOM, or reasoning about how the page should look does not count as visual testing.

If the active runtime has no way to render and inspect the UI, mark visual QA `BLOCKED` and do not claim production acceptance.

## Required viewport coverage

At minimum, render and inspect the primary user journey at:

- mobile: 390 x 844 CSS pixels;
- desktop: 1440 x 900 CSS pixels.

Also test a tablet-sized viewport such as 768 x 1024 when the layout contains sidebars, multi-column content, dense navigation, dashboards, editors, tables, or other breakpoint-sensitive UI.

If the product explicitly targets another device class, add the relevant viewport rather than replacing the minimum mobile and desktop checks.

## Required routes and states

Test the homepage plus every critical route required to complete the site's primary job. Include applicable states such as:

- loading, empty, success, validation, and error states;
- 404/not-found and application error recovery;
- signed-out, sign-in, signed-in, protected, and permission-denied states when authentication is enabled;
- AI idle, generating/streaming, completed, cancelled, rate-limited, and provider-error states when AI is enabled;
- ad slot reserved/loading/configured-not-live states when advertising is enabled;
- consent denied/unknown/accepted UI when consent controls are required;
- dialogs, drawers, menus, dropdowns, toasts, sticky headers/footers, and long-content states that can create overlap or z-index bugs;
- dark mode when the product exposes it.

Use mocks or deterministic fixtures for states that would otherwise require a paid provider call. The financial cost gate still applies to any real potentially billable provider action.

## Visual assertions

For each inspected route/state, check at least:

- no unintended horizontal scrolling;
- no clipped, overlapping, off-screen, or unreachable critical content;
- no broken images, icons, fonts, or obvious asset failures;
- text is readable and does not collide, truncate important meaning, or overflow controls;
- primary controls are visible, usable, and not obscured by sticky UI, ads, banners, keyboards, or consent surfaces;
- dialogs, menus, popovers, and overlays have correct stacking and remain inside the viewport;
- responsive layout changes are coherent rather than merely scaled down;
- touch targets on mobile are practically usable;
- visible focus and keyboard states are not hidden by styling;
- animation does not hide content and respects reduced-motion behavior where applicable;
- ad containers do not create severe layout shift or imitate product/navigation controls;
- no placeholder secrets, development banners, debug overlays, or broken skeletons appear in production-facing UI.

Visual QA does not replace accessibility testing. Contrast, labels, semantic structure, keyboard behavior, and screen-reader concerns remain part of the accessibility gate.

## Screenshot evidence

Capture screenshots for every required viewport and enough critical states to prove the visual review occurred. Store generated evidence outside the application source tree when practical, for example:

`.web-factory/reports/visual/<site_id>/`

Create a machine-readable report such as:

`.web-factory/reports/<site_id>-visual-qa.json`

The report should include the site ID, tested URL, method, timestamp, viewport dimensions, route/state, screenshot path, pass/fail assertions, and unresolved issues. Validate it with:

`python scripts/validate_visual_qa.py .web-factory/reports/<site_id>-visual-qa.json`

Do not commit screenshots containing private user data, authentication tokens, secrets, personal uploads, or sensitive AI conversations to a public repository.

## Visual regression

When a trusted baseline exists, use screenshot comparison for stable deterministic views. Treat visual diff tooling as an aid, not as the sole acceptance decision: dynamic content, fonts, dates, ads, animations, and third-party widgets can create noisy diffs.

Do not create or overwrite a baseline merely to make a failing diff pass. Review the change first, then deliberately accept the new baseline only when the UI change is intended.

## Preview and production requirements

Before `PREVIEW_QA_PASS`:

- execute the full required visual test against the preview deployment;
- save screenshot/report evidence;
- resolve all release-blocking visual defects;
- validate the visual QA report as `PASS`.

After production deployment, run a visual smoke test against the real production/canonical URL at minimum mobile and desktop viewports. Re-run the full visual suite when production-only configuration, custom-domain behavior, consent, authentication, advertising, or other environment differences can materially alter the rendered interface.

A production site with unresolved release-blocking visual defects is not `COMPLETE`.
