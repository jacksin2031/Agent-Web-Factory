#!/usr/bin/env python3
"""Validate an Agent Web Factory per-site production plan."""
import argparse
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "assets" / "site-plan.schema.json").read_text(encoding="utf-8"))


def validate_cross_fields(plan):
    errors = []
    integrations = plan.get("integrations", [])
    for index, integration in enumerate(integrations):
        cost_class = integration.get("cost_class")
        action_policy = integration.get("action_policy")
        prefix = f"integrations[{index}]"
        if cost_class == "zero-cost" and action_policy not in {"auto", "human-authorization"}:
            errors.append(f"{prefix}: zero-cost integration must use auto or human-authorization")
        if cost_class in {"potentially-billable", "paid"} and action_policy != "human-cost-gate":
            errors.append(f"{prefix}: potentially billable or paid integration must use human-cost-gate")
        if cost_class == "unknown" and action_policy != "research-required":
            errors.append(f"{prefix}: unknown cost requires research-required before execution")

    gates = set(plan.get("quality_gates", []))
    mandatory = {"functional", "security", "accessibility", "visual", "production-smoke"}
    missing = sorted(mandatory - gates)
    if missing:
        errors.append("quality_gates missing mandatory gates: " + ", ".join(missing))
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan")
    args = parser.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    errors = []
    try:
        jsonschema.Draft202012Validator(SCHEMA).validate(plan)
    except jsonschema.ValidationError as exc:
        errors.append(exc.message)
    errors.extend(validate_cross_fields(plan))
    print(json.dumps({"pass": not errors, "errors": errors}, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
