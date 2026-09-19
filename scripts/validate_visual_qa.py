#!/usr/bin/env python3
"""Validate Agent Web Factory visual-QA evidence without needing a browser runtime."""

import argparse
import json
from pathlib import Path

MIN_VIEWPORTS = {
    "mobile": (320, 760),
    "desktop": (1024, 700),
}
REQUIRED_ASSERTIONS = (
    "rendered",
    "no_horizontal_overflow",
    "no_critical_overlap",
    "no_broken_media",
    "critical_controls_visible",
)
ALLOWED_METHODS = {"browser_automation", "computer_use", "manual_browser"}
ALLOWED_STATUS = {"PASS", "FAIL", "BLOCKED"}


def fail(errors, message):
    errors.append(message)


def validate(report):
    errors = []
    if report.get("schema_version") != 1:
        fail(errors, "schema_version must be 1")
    if not isinstance(report.get("site_id"), str) or not report["site_id"].strip():
        fail(errors, "site_id is required")
    if report.get("status") not in ALLOWED_STATUS:
        fail(errors, "status must be PASS, FAIL, or BLOCKED")
    if report.get("method") not in ALLOWED_METHODS:
        fail(errors, "method must identify an actual rendered-browser review")
    if not isinstance(report.get("tested_url"), str) or not report["tested_url"].strip():
        fail(errors, "tested_url is required")
    if not isinstance(report.get("executed_at"), str) or not report["executed_at"].strip():
        fail(errors, "executed_at is required")

    checks = report.get("checks")
    if not isinstance(checks, list) or not checks:
        fail(errors, "checks must contain rendered visual checks")
        checks = []

    coverage = {"mobile": False, "desktop": False}
    failing_checks = 0
    for index, check in enumerate(checks):
        prefix = f"checks[{index}]"
        if not isinstance(check, dict):
            fail(errors, f"{prefix} must be an object")
            continue
        if not isinstance(check.get("route"), str) or not check["route"].strip():
            fail(errors, f"{prefix}.route is required")
        if not isinstance(check.get("screenshot"), str) or not check["screenshot"].strip():
            fail(errors, f"{prefix}.screenshot is required as visual evidence")
        viewport = check.get("viewport")
        if not isinstance(viewport, dict):
            fail(errors, f"{prefix}.viewport is required")
            continue
        width = viewport.get("width")
        height = viewport.get("height")
        if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
            fail(errors, f"{prefix}.viewport width/height must be positive integers")
            continue
        if width <= 500 and height >= MIN_VIEWPORTS["mobile"][1]:
            coverage["mobile"] = True
        if width >= MIN_VIEWPORTS["desktop"][0] and height >= MIN_VIEWPORTS["desktop"][1]:
            coverage["desktop"] = True

        assertions = check.get("assertions")
        if not isinstance(assertions, dict):
            fail(errors, f"{prefix}.assertions is required")
            continue
        for name in REQUIRED_ASSERTIONS:
            if assertions.get(name) is not True:
                failing_checks += 1
                fail(errors, f"{prefix}.assertions.{name} must be true for a PASS report")

    if report.get("status") == "PASS":
        if not coverage["mobile"]:
            fail(errors, "PASS requires at least one mobile rendered check")
        if not coverage["desktop"]:
            fail(errors, "PASS requires at least one desktop rendered check")
        if failing_checks:
            fail(errors, "PASS cannot contain failed required visual assertions")
        unresolved = report.get("unresolved_issues", [])
        if not isinstance(unresolved, list):
            fail(errors, "unresolved_issues must be a list")
        elif any(isinstance(item, dict) and item.get("severity") in {"high", "critical", "release_blocking"} for item in unresolved):
            fail(errors, "PASS cannot contain unresolved release-blocking visual issues")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    args = parser.parse_args()
    path = Path(args.report)
    report = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(report)
    result = {"pass": not errors, "errors": errors}
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
