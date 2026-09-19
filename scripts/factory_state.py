#!/usr/bin/env python3
import argparse
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

STAGES = [
    "PLANNED", "SCAFFOLDED", "IMPLEMENTED", "LOCAL_QA_PASS",
    "PREVIEW_DEPLOYED", "PREVIEW_QA_PASS", "PRODUCTION_DEPLOYED",
    "DOMAIN_SELECTED", "DOMAIN_ACQUIRED_OR_ATTACHED", "DNS_CONFIGURED",
    "HTTPS_PASS", "GOOGLE_VERIFIED", "SEARCH_CONSOLE_ADDED",
    "SITEMAP_SUBMITTED", "INDEX_INSPECTION_REQUESTED", "COMPLETE"
]

SENSITIVE_KEY_FRAGMENTS = (
    "token", "secret", "password", "passwd", "credential", "private_key",
    "access_key", "refresh_token", "api_key", "apikey"
)


def now():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, obj):
    """Atomically replace state so interruption cannot leave truncated JSON."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=p.name + ".", suffix=".tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, p)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def fresh_site_state():
    timestamp = now()
    return {
        "stage": "PLANNED",
        "status": "PENDING",
        "history": [{"stage": "PLANNED", "status": "PENDING", "at": timestamp}],
        "external": {},
    }


def cmd_init(args):
    manifest = load(args.manifest)
    path = Path(args.state)

    if path.exists() and not args.force:
        state = load(path)
        existing_run_id = state.get("run_id")
        if existing_run_id != manifest["run_id"]:
            raise SystemExit(
                f"State belongs to run_id {existing_run_id!r}, not {manifest['run_id']!r}. "
                "Use --force only if you intentionally want to replace it."
            )

        # Resume safely: retain all existing site progress and only add new site IDs.
        state.setdefault("sites", {})
        for site in manifest["sites"]:
            state["sites"].setdefault(site["site_id"], fresh_site_state())
        state["updated_at"] = now()
        save(path, state)
        print(args.state)
        return

    state = {
        "run_id": manifest["run_id"],
        "updated_at": now(),
        "sites": {s["site_id"]: fresh_site_state() for s in manifest["sites"]},
    }
    save(path, state)
    print(args.state)


def cmd_set(args):
    if args.stage not in STAGES:
        raise SystemExit(f"Unknown stage: {args.stage}")
    state = load(args.state)
    site = state["sites"].get(args.site)
    if not site:
        raise SystemExit(f"Unknown site_id: {args.site}")

    current = site.get("stage", "PLANNED")
    if current not in STAGES:
        raise SystemExit(f"State contains unknown current stage: {current}")
    if STAGES.index(args.stage) < STAGES.index(current) and not args.allow_regression:
        raise SystemExit(
            f"Refusing stage regression from {current} to {args.stage}. "
            "Use --allow-regression only for an intentional repair workflow."
        )

    site["stage"] = args.stage
    site["status"] = args.status
    event = {"stage": args.stage, "status": args.status, "at": now()}
    if args.note:
        event["note"] = args.note
    site.setdefault("history", []).append(event)
    state["updated_at"] = now()
    save(args.state, state)


def looks_sensitive(key):
    normalized = key.lower().replace("-", "_").replace(".", "_")
    return any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS)


def cmd_external(args):
    if looks_sensitive(args.key):
        raise SystemExit(
            f"Refusing to persist potentially sensitive external field {args.key!r}. "
            "Store resource identifiers and statuses, never credentials or tokens."
        )
    state = load(args.state)
    site = state["sites"].get(args.site)
    if not site:
        raise SystemExit(f"Unknown site_id: {args.site}")
    site.setdefault("external", {})[args.key] = args.value
    state["updated_at"] = now()
    save(args.state, state)


def cmd_summary(args):
    state = load(args.state)
    rows = []
    for site_id, item in state["sites"].items():
        rows.append({"site_id": site_id, "stage": item.get("stage"), "status": item.get("status")})
    print(json.dumps({"run_id": state.get("run_id"), "sites": rows}, indent=2, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("init")
    a.add_argument("--manifest", required=True)
    a.add_argument("--state", default=".web-factory/state.json")
    a.add_argument("--force", action="store_true", help="Replace an existing state file intentionally")
    a.set_defaults(func=cmd_init)

    a = sub.add_parser("set")
    a.add_argument("--state", default=".web-factory/state.json")
    a.add_argument("--site", required=True)
    a.add_argument("--stage", required=True)
    a.add_argument("--status", default="PASS")
    a.add_argument("--note")
    a.add_argument("--allow-regression", action="store_true")
    a.set_defaults(func=cmd_set)

    a = sub.add_parser("external")
    a.add_argument("--state", default=".web-factory/state.json")
    a.add_argument("--site", required=True)
    a.add_argument("--key", required=True)
    a.add_argument("--value", required=True)
    a.set_defaults(func=cmd_external)

    a = sub.add_parser("summary")
    a.add_argument("--state", default=".web-factory/state.json")
    a.set_defaults(func=cmd_summary)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
