#!/usr/bin/env python3
"""Create, record, and verify short-lived human approvals for potentially billable actions."""

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

SENSITIVE_KEY_FRAGMENTS = (
    "token", "secret", "password", "passwd", "credential", "private_key",
    "access_key", "refresh_token", "api_key", "apikey"
)


def now():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat()


def load(path):
    p = Path(path)
    if not p.exists():
        return {"version": 1, "requests": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def atomic_save(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=p.name + ".", suffix=".tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def contains_sensitive(value, key=""):
    if isinstance(value, dict):
        for k, v in value.items():
            normalized = str(k).lower().replace("-", "_").replace(".", "_")
            if any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS):
                return True
            if contains_sensitive(v, str(k)):
                return True
    elif isinstance(value, list):
        return any(contains_sensitive(v, key) for v in value)
    return False


def canonical_request(req):
    stable = {
        "action_id": req["action_id"],
        "kind": req["kind"],
        "provider": req["provider"],
        "description": req["description"],
        "currency": req["currency"],
        "max_cost": req["max_cost"],
        "items": req.get("items", []),
    }
    return json.dumps(stable, sort_keys=True, separators=(",", ":"))


def request_digest(req):
    return hashlib.sha256(canonical_request(req).encode("utf-8")).hexdigest()


def cmd_request(args):
    ledger = load(args.ledger)
    items = json.loads(args.items_json) if args.items_json else []
    if not isinstance(items, list):
        raise SystemExit("--items-json must decode to an array")
    if args.max_cost < 0:
        raise SystemExit("--max-cost must be >= 0")
    if args.action_id in ledger.setdefault("requests", {}):
        raise SystemExit(f"action_id already exists: {args.action_id}")
    req = {
        "action_id": args.action_id,
        "kind": args.kind,
        "provider": args.provider,
        "description": args.description,
        "currency": args.currency.upper(),
        "max_cost": args.max_cost,
        "items": items,
        "status": "PENDING_HUMAN_CONFIRMATION",
        "created_at": iso(now()),
        "approval": None,
    }
    if contains_sensitive(req):
        raise SystemExit("Refusing to persist a request containing a potentially sensitive field")
    req["digest"] = request_digest(req)
    ledger.setdefault("requests", {})[args.action_id] = req
    atomic_save(args.ledger, ledger)
    print(json.dumps(req, indent=2))


def cmd_record_approval(args):
    ledger = load(args.ledger)
    req = ledger.get("requests", {}).get(args.action_id)
    if not req:
        raise SystemExit(f"Unknown action_id: {args.action_id}")
    if args.confirmed != "YES":
        raise SystemExit("Refusing to record approval without --confirmed YES")
    if args.approved_max_cost < 0:
        raise SystemExit("--approved-max-cost must be >= 0")
    if args.approved_max_cost > float(req["max_cost"]):
        raise SystemExit("Approved maximum cannot exceed the amount shown in the pending request")
    if req.get("status") != "PENDING_HUMAN_CONFIRMATION" or req.get("approval") is not None:
        raise SystemExit("Approval can only be recorded for a pending request")
    ttl = args.ttl_minutes
    if not 1 <= ttl <= 1440:
        raise SystemExit("--ttl-minutes must be between 1 and 1440")
    approved_at = now()
    req["status"] = "APPROVED"
    req["approval"] = {
        "approved_max_cost": args.approved_max_cost,
        "currency": req["currency"],
        "approved_at": iso(approved_at),
        "expires_at": iso(approved_at + timedelta(minutes=ttl)),
        "request_digest": req["digest"],
        "recorded_from_explicit_human_confirmation": True,
    }
    atomic_save(args.ledger, ledger)
    print(json.dumps(req, indent=2))


def parse_iso(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def cmd_check(args):
    ledger = load(args.ledger)
    req = ledger.get("requests", {}).get(args.action_id)
    if not req:
        raise SystemExit(f"Unknown action_id: {args.action_id}")
    approval = req.get("approval")
    errors = []
    if req.get("status") != "APPROVED" or not approval:
        errors.append("explicit human approval has not been recorded")
    else:
        if approval.get("request_digest") != request_digest(req):
            errors.append("approved request details changed after approval")
        if now() >= parse_iso(approval["expires_at"]):
            errors.append("approval expired")
        if args.current_cost is not None and args.current_cost > float(approval["approved_max_cost"]):
            errors.append("current cost exceeds the approved maximum")
        if args.currency and args.currency.upper() != approval["currency"]:
            errors.append("currency differs from the approved request")
    result = {
        "pass": not errors,
        "action_id": args.action_id,
        "status": req.get("status"),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not errors else 1)


def cmd_consume(args):
    ledger = load(args.ledger)
    req = ledger.get("requests", {}).get(args.action_id)
    if not req:
        raise SystemExit(f"Unknown action_id: {args.action_id}")
    approval = req.get("approval")
    if req.get("status") != "APPROVED" or not approval:
        raise SystemExit("Cannot consume an action without a valid approval")
    if approval.get("request_digest") != request_digest(req):
        raise SystemExit("Cannot consume because approved request details changed after approval")
    if now() >= parse_iso(approval["expires_at"]):
        raise SystemExit("Cannot consume an expired approval")
    if args.actual_cost < 0:
        raise SystemExit("--actual-cost must be >= 0")
    if args.actual_cost > float(approval["approved_max_cost"]):
        raise SystemExit("Actual cost exceeds the approved maximum")
    if args.currency.upper() != approval["currency"]:
        raise SystemExit("Actual charge currency differs from the approved request")
    req["status"] = "CONSUMED"
    req["consumed_at"] = iso(now())
    req["actual_cost"] = args.actual_cost
    atomic_save(args.ledger, ledger)
    print(json.dumps(req, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", default=".web-factory/approvals.json")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("request")
    p.add_argument("--action-id", required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--provider", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--currency", required=True)
    p.add_argument("--max-cost", required=True, type=float)
    p.add_argument("--items-json")
    p.set_defaults(func=cmd_request)

    p = sub.add_parser("record-approval")
    p.add_argument("--action-id", required=True)
    p.add_argument("--confirmed", required=True, choices=["YES"])
    p.add_argument("--approved-max-cost", required=True, type=float)
    p.add_argument("--ttl-minutes", type=int, default=15)
    p.set_defaults(func=cmd_record_approval)

    p = sub.add_parser("check")
    p.add_argument("--action-id", required=True)
    p.add_argument("--current-cost", type=float)
    p.add_argument("--currency")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("consume")
    p.add_argument("--action-id", required=True)
    p.add_argument("--actual-cost", required=True, type=float)
    p.add_argument("--currency", required=True)
    p.set_defaults(func=cmd_consume)

    args = parser.parse_args()
    if not 1 <= getattr(args, "ttl_minutes", 15) <= 1440:
        raise SystemExit("--ttl-minutes must be between 1 and 1440")
    args.func(args)


if __name__ == "__main__":
    main()
