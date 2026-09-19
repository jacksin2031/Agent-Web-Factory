#!/usr/bin/env python3
"""Validate Web Factory manifest invariants using only the Python standard library."""
import argparse
import json
import re
from pathlib import Path

SITE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VALID_MODES = {"single", "batch"}
VALID_DOMAIN_MODES = {"existing", "approved", "auto", "vercel-subdomain-only"}
VALID_AUTH_PROVIDERS = {"auto", "authjs", "supabase", "clerk", "firebase", "custom"}
VALID_AUTH_METHODS = {
    "password", "magic-link", "email-otp", "phone-otp", "oauth-google",
    "oauth-github", "oauth-apple", "oauth-microsoft", "passkey", "anonymous", "other"
}
VALID_AUTHZ_MODELS = {"authenticated-user", "owner", "roles", "permissions", "rls", "custom"}
VALID_AD_PROVIDERS = {"auto", "adsense", "ad-manager", "other"}
VALID_AD_STRATEGIES = {"auto-ads", "manual-slots", "mixed"}
VALID_CONSENT_MODES = {"auto", "required", "not-required"}
VALID_ANALYTICS_PROVIDERS = {"auto", "vercel-analytics", "google-analytics", "plausible", "other"}

VALID_AI_CAPABILITIES = {
    "chat", "structured-generation", "extraction", "tool-calling", "agent",
    "rag", "file-qa", "vision", "image-generation", "image-editing",
    "speech", "transcription", "realtime-voice", "classification",
    "rewriting", "summarization", "translation", "recommendation", "other"
}


def fail(errors, message):
    errors.append(message)


def nonnegative_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def validate(manifest):
    errors = []

    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        fail(errors, "run_id must be a non-empty string")

    mode = manifest.get("mode")
    if mode not in VALID_MODES:
        fail(errors, "mode must be 'single' or 'batch'")

    execution_policy = manifest.get("execution_policy")
    if not isinstance(execution_policy, dict):
        fail(errors, "execution_policy must be an object")
    else:
        if execution_policy.get("planning_required") is not True:
            fail(errors, "execution_policy.planning_required must be true")
        if execution_policy.get("target_release") not in {"public-production", "user-limited"}:
            fail(errors, "execution_policy.target_release is invalid")
        if execution_policy.get("autonomy") != "autonomous-until-complete":
            fail(errors, "execution_policy.autonomy must be autonomous-until-complete")
        if execution_policy.get("zero_cost_external_actions") != "auto":
            fail(errors, "execution_policy.zero_cost_external_actions must be auto")
        if execution_policy.get("paid_actions") != "human-confirmation":
            fail(errors, "execution_policy.paid_actions must be human-confirmation")

    cost_policy = manifest.get("cost_policy")
    if not isinstance(cost_policy, dict):
        fail(errors, "cost_policy must be an object")
    else:
        if cost_policy.get("require_human_confirmation_for_paid_actions") is not True:
            fail(errors, "cost_policy.require_human_confirmation_for_paid_actions must be true")
        ttl = cost_policy.get("approval_ttl_minutes", 15)
        if not isinstance(ttl, int) or isinstance(ttl, bool) or not 1 <= ttl <= 1440:
            fail(errors, "cost_policy.approval_ttl_minutes must be an integer between 1 and 1440")

    sites = manifest.get("sites")
    if not isinstance(sites, list) or not sites:
        fail(errors, "sites must be a non-empty array")
        sites = []

    if mode == "single" and len(sites) != 1:
        fail(errors, "single mode must contain exactly one site")

    seen = set()
    for index, site in enumerate(sites):
        prefix = f"sites[{index}]"
        site_id = site.get("site_id")
        if not isinstance(site_id, str) or not SITE_ID_RE.fullmatch(site_id):
            fail(errors, f"{prefix}.site_id must match {SITE_ID_RE.pattern}")
        elif site_id in seen:
            fail(errors, f"duplicate site_id: {site_id}")
        else:
            seen.add(site_id)

        for field in ("brief", "project_name"):
            if not isinstance(site.get(field), str) or not site[field].strip():
                fail(errors, f"{prefix}.{field} must be a non-empty string")

        ai = site.get("ai")
        if not isinstance(ai, dict):
            fail(errors, f"{prefix}.ai must be an object")
        else:
            enabled = ai.get("enabled")
            if not isinstance(enabled, bool):
                fail(errors, f"{prefix}.ai.enabled must be a boolean")
            caps = ai.get("capabilities", [])
            if not isinstance(caps, list) or any(c not in VALID_AI_CAPABILITIES for c in caps):
                fail(errors, f"{prefix}.ai.capabilities contains an unsupported capability")
            if len(caps) != len(set(caps)):
                fail(errors, f"{prefix}.ai.capabilities must not contain duplicates")
            if enabled:
                purpose = ai.get("purpose")
                if not isinstance(purpose, str) or not purpose.strip():
                    fail(errors, f"{prefix}.ai.purpose is required when AI is enabled")
                if not caps:
                    fail(errors, f"{prefix}.ai.capabilities must be non-empty when AI is enabled")

        auth = site.get("auth")
        if not isinstance(auth, dict):
            fail(errors, f"{prefix}.auth must be an object")
        else:
            auth_enabled = auth.get("enabled")
            if not isinstance(auth_enabled, bool):
                fail(errors, f"{prefix}.auth.enabled must be a boolean")
            provider = auth.get("provider", "auto")
            if provider not in VALID_AUTH_PROVIDERS:
                fail(errors, f"{prefix}.auth.provider is unsupported")
            methods = auth.get("methods", [])
            if not isinstance(methods, list) or any(m not in VALID_AUTH_METHODS for m in methods):
                fail(errors, f"{prefix}.auth.methods contains an unsupported method")
            elif len(methods) != len(set(methods)):
                fail(errors, f"{prefix}.auth.methods must not contain duplicates")
            routes = auth.get("protected_routes", [])
            if not isinstance(routes, list) or any(not isinstance(r, str) or not r.startswith("/") for r in routes):
                fail(errors, f"{prefix}.auth.protected_routes must contain absolute application paths")
            elif len(routes) != len(set(routes)):
                fail(errors, f"{prefix}.auth.protected_routes must not contain duplicates")
            authz = auth.get("authorization_model", "authenticated-user")
            if authz not in VALID_AUTHZ_MODELS:
                fail(errors, f"{prefix}.auth.authorization_model is unsupported")
            if auth_enabled and not methods:
                fail(errors, f"{prefix}.auth.methods must be non-empty when auth is enabled")
            if not auth_enabled and routes:
                fail(errors, f"{prefix}.auth.protected_routes must be empty when auth is disabled")
            if auth_enabled and "password" in methods and auth.get("account_recovery") is not True:
                fail(errors, f"{prefix}.auth.account_recovery must be true when password auth is enabled")
            if auth.get("requires_persistent_user_data") is True and auth_enabled and authz == "authenticated-user":
                fail(errors, f"{prefix}.auth.authorization_model must explicitly isolate persistent user data")

        ads = site.get("ads")
        if not isinstance(ads, dict):
            fail(errors, f"{prefix}.ads must be an object")
        else:
            ads_enabled = ads.get("enabled")
            if not isinstance(ads_enabled, bool):
                fail(errors, f"{prefix}.ads.enabled must be a boolean")
            provider = ads.get("provider", "auto")
            if provider not in VALID_AD_PROVIDERS:
                fail(errors, f"{prefix}.ads.provider is unsupported")
            strategy = ads.get("strategy", "manual-slots")
            if strategy not in VALID_AD_STRATEGIES:
                fail(errors, f"{prefix}.ads.strategy is unsupported")
            placements = ads.get("placements", [])
            if not isinstance(placements, list) or any(not isinstance(x, str) or not x.strip() for x in placements):
                fail(errors, f"{prefix}.ads.placements must contain non-empty strings")
            elif len(placements) != len(set(placements)):
                fail(errors, f"{prefix}.ads.placements must not contain duplicates")
            consent_mode = ads.get("consent_mode", "auto")
            if consent_mode not in VALID_CONSENT_MODES:
                fail(errors, f"{prefix}.ads.consent_mode is invalid")
            publisher_id = ads.get("publisher_id")
            if publisher_id is not None and (not isinstance(publisher_id, str) or not publisher_id.strip()):
                fail(errors, f"{prefix}.ads.publisher_id must be null or a non-empty string")
            if isinstance(publisher_id, str) and any(token in publisher_id.lower() for token in ("placeholder", "0000000000000000", "your-publisher")):
                fail(errors, f"{prefix}.ads.publisher_id must not be a placeholder")
            if ads_enabled and strategy in {"manual-slots", "mixed"} and not placements:
                fail(errors, f"{prefix}.ads.placements must be non-empty for manual or mixed ad strategy")

        analytics = site.get("analytics")
        if not isinstance(analytics, dict):
            fail(errors, f"{prefix}.analytics must be an object")
        else:
            analytics_enabled = analytics.get("enabled")
            if not isinstance(analytics_enabled, bool):
                fail(errors, f"{prefix}.analytics.enabled must be a boolean")
            provider = analytics.get("provider", "auto")
            if provider not in VALID_ANALYTICS_PROVIDERS:
                fail(errors, f"{prefix}.analytics.provider is unsupported")
            consent_mode = analytics.get("consent_mode", "auto")
            if consent_mode not in VALID_CONSENT_MODES:
                fail(errors, f"{prefix}.analytics.consent_mode is invalid")
            if analytics.get("collect_sensitive_content") is not False:
                fail(errors, f"{prefix}.analytics.collect_sensitive_content must be false")

        policy = site.get("domain_policy")
        if not isinstance(policy, dict):
            fail(errors, f"{prefix}.domain_policy must be an object")
        else:
            domain_mode = policy.get("mode")
            if domain_mode not in VALID_DOMAIN_MODES:
                fail(errors, f"{prefix}.domain_policy.mode is invalid")
            if domain_mode in {"existing", "approved"}:
                domain = policy.get("domain")
                if not isinstance(domain, str) or not domain.strip():
                    fail(errors, f"{prefix}.domain_policy.domain is required for mode {domain_mode}")
            max_cost = policy.get("max_annual_cost")
            if max_cost is not None and not nonnegative_number(max_cost):
                fail(errors, f"{prefix}.domain_policy.max_annual_cost must be null or >= 0")

        google = site.get("google_search")
        if not isinstance(google, dict):
            fail(errors, f"{prefix}.google_search must be an object")

    budget = manifest.get("budget")
    if not isinstance(budget, dict):
        fail(errors, "budget must be an object")
        budget = {}

    for field in (
        "max_total_domain_cost", "max_domain_cost_each",
        "max_ai_test_cost", "max_ai_production_cost_per_period"
    ):
        value = budget.get(field)
        if value is not None and not nonnegative_number(value):
            fail(errors, f"budget.{field} must be null or >= 0")

    purchase_max = budget.get("purchase_count_max")
    if purchase_max is not None and (not isinstance(purchase_max, int) or isinstance(purchase_max, bool) or purchase_max < 0):
        fail(errors, "budget.purchase_count_max must be null or a non-negative integer")

    if "domain_purchase_preapproved" in budget:
        fail(errors, "budget.domain_purchase_preapproved is not allowed; budgets never authorize paid actions")

    period = budget.get("ai_cost_period")
    if period not in {None, "daily", "weekly", "monthly", "none"}:
        fail(errors, "budget.ai_cost_period is invalid")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    errors = validate(manifest)
    result = {"pass": not errors, "errors": errors}
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
