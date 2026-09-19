# Contributing

1. Keep all Skill content, scripts, examples, and repository documentation in English.
2. Run `python -m pip install -r requirements-dev.txt`.
3. Run `python -m unittest discover -s tests -p 'test_*.py' -v`.
4. Run `python scripts/validate_manifest.py assets/batch.example.json`.
5. Do not add tests that spend money or require real paid AI inference in routine CI.
6. Any change that can create an external monetary charge must preserve the explicit human cost gate.
7. Keep external mutations idempotent and resumable whenever possible.
8. Auth-enabled changes must include authorization tests, not only sign-in UI tests.
9. Ad/analytics changes must preserve consent, provider-state truthfulness, ads.txt, and sensitive-data boundaries.
10. Changes to the generated-site baseline must consider security, privacy, accessibility, performance, SEO, and error handling.
11. Before a tagged release, follow `RELEASE_CHECKLIST.md`.
