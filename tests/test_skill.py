import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(*args, cwd=None, expect=0, env=None, timeout=20):
    try:
        proc = subprocess.run(
            list(args), cwd=cwd or ROOT, text=True, capture_output=True, env=env, timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(
            f"Command timed out after {timeout}s: {' '.join(map(str, args))}\n"
            f"STDOUT:\n{exc.stdout or ''}\nSTDERR:\n{exc.stderr or ''}"
        ) from exc
    if proc.returncode != expect:
        raise AssertionError(
            f"Command returned {proc.returncode}, expected {expect}: {' '.join(map(str, args))}\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


class SkillStructureTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "assets" / "manifest.schema.json",
            ROOT / "assets" / "batch.example.json",
            SCRIPTS / "preflight.py",
            SCRIPTS / "factory_state.py",
            SCRIPTS / "validate_manifest.py",
            SCRIPTS / "validate_site.py",
            SCRIPTS / "google_search_console.py",
            SCRIPTS / "cost_gate.py",
            SCRIPTS / "package_release.py",
            ROOT / "references" / "ai-features.md",
            ROOT / "references" / "authentication.md",
            ROOT / "references" / "advertising.md",
            ROOT / "references" / "production-baseline.md",
            ROOT / "references" / "visual-testing.md",
            ROOT / "references" / "autonomous-execution.md",
            ROOT / "assets" / "visual-qa.example.json",
            ROOT / "assets" / "site-plan.example.json",
            ROOT / "assets" / "site-plan.schema.json",
            SCRIPTS / "validate_visual_qa.py",
            SCRIPTS / "validate_plan.py",
            ROOT / "references" / "data-and-integrations.md",
            ROOT / "references" / "market-research.md",
            ROOT / "CHANGELOG.md",
            ROOT / "VERSION",
            ROOT / "LICENSE",
            ROOT / "SECURITY.md",
            ROOT / "RELEASE_CHECKLIST.md",
            ROOT / "RUNTIME_VERIFICATION.md",
            ROOT / "CONTRIBUTING.md",
            ROOT / ".github" / "workflows" / "ci.yml",
            ROOT / ".github" / "workflows" / "release.yml",
            ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
            ROOT / "assets" / "runtime-matrix.json",
            SCRIPTS / "compatibility_check.py",
            SCRIPTS / "run_test_shard.py",
            ROOT / "references" / "runtime-compatibility.md",
            ROOT / "adapters" / "openai" / "README.md",
            ROOT / "adapters" / "gemini-cli" / "README.md",
            ROOT / "adapters" / "github-copilot" / "README.md",
            ROOT / "adapters" / "claude-code" / "README.md",
            ROOT / "adapters" / "generic" / "README.md",
            ROOT / "requirements-dev.txt",
        ]
        for path in required:
            self.assertTrue(path.is_file(), f"Missing required file: {path.relative_to(ROOT)}")

    def test_skill_frontmatter(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(match, "SKILL.md must start with YAML frontmatter")
        import yaml
        data = yaml.safe_load(match.group(1))
        self.assertEqual(data.get("name"), "agent-web-factory")
        self.assertIsInstance(data.get("description"), str)
        self.assertGreater(len(data["description"].strip()), 20)

    def test_openai_yaml_shape(self):
        import yaml
        data = yaml.safe_load((ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        self.assertIn("interface", data)
        self.assertIn("display_name", data["interface"])
        self.assertIn("short_description", data["interface"])
        tools = data.get("dependencies", {}).get("tools", [])
        self.assertTrue(any(t.get("type") == "mcp" and t.get("value") == "vercel" for t in tools))

    def test_version_matches_changelog(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertRegex(version, r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
        self.assertIn(f"## {version} -", changelog)

    def test_github_workflows_parse(self):
        import yaml
        for path in (ROOT / ".github" / "workflows").glob("*.yml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertIsInstance(data, dict, path.name)
            self.assertIn("jobs", data, path.name)

    def test_release_workflow_enforces_tag_version_and_tests(self):
        text = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        self.assertIn('test "v$(cat VERSION)" = "${GITHUB_REF_NAME}"', text)
        self.assertIn("python scripts/run_test_shard.py", text)
        self.assertIn("sha256sum", text)
        self.assertIn("gh release create", text)
        self.assertIn("--prerelease", text)

    def test_all_user_visible_text_is_english_only(self):
        cjk = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]")
        suffixes = {".md", ".py", ".yaml", ".yml", ".json", ".txt"}
        offenders = []
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes:
                text = path.read_text(encoding="utf-8")
                if cjk.search(text):
                    offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [], f"CJK text found in: {offenders}")

    def test_python_scripts_compile(self):
        scripts = sorted(SCRIPTS.glob("*.py"))
        self.assertTrue(scripts)
        run(sys.executable, "-m", "py_compile", *map(str, scripts))

    def test_release_package_excludes_generated_and_secret_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "release.zip"
            run(sys.executable, str(SCRIPTS / "package_release.py"), "--output", str(output))
            with zipfile.ZipFile(output) as zf:
                names = zf.namelist()
            bad = [
                name for name in names
                if "__pycache__" in name
                or name.endswith((".pyc", ".pyo"))
                or Path(name).name in {".env", ".env.local", ".env.production"}
                or "/.git/" in name
                or "/.web-factory/" in name
            ]
            self.assertEqual(bad, [], f"Release ZIP contains generated/secret artifacts: {bad}")
            self.assertTrue(any(name.endswith("/SKILL.md") for name in names))

    def test_release_packager_refuses_private_key_files(self):
        secret = ROOT / "temporary-test.key"
        try:
            secret.write_text("not-a-real-key", encoding="utf-8")
            with tempfile.TemporaryDirectory() as td:
                output = Path(td) / "release.zip"
                proc = run(sys.executable, str(SCRIPTS / "package_release.py"), "--output", str(output), expect=1)
                self.assertIn("potential credential file", proc.stderr)
        finally:
            secret.unlink(missing_ok=True)

    def test_json_files_parse(self):
        for path in ROOT.rglob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))

    def test_example_matches_json_schema(self):
        import jsonschema
        schema = json.loads((ROOT / "assets" / "manifest.schema.json").read_text(encoding="utf-8"))
        example = json.loads((ROOT / "assets" / "batch.example.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(example)

    def test_site_plan_example_passes_schema_and_validator(self):
        import jsonschema
        schema = json.loads((ROOT / "assets" / "site-plan.schema.json").read_text(encoding="utf-8"))
        example = json.loads((ROOT / "assets" / "site-plan.example.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(example)
        out = run(sys.executable, str(SCRIPTS / "validate_plan.py"), str(ROOT / "assets" / "site-plan.example.json"))
        self.assertTrue(json.loads(out.stdout)["pass"])


class ManifestValidatorTests(unittest.TestCase):
    def example(self):
        return json.loads((ROOT / "assets" / "batch.example.json").read_text(encoding="utf-8"))

    def validate_file(self, obj, expect):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.json"
            path.write_text(json.dumps(obj), encoding="utf-8")
            return run(sys.executable, str(SCRIPTS / "validate_manifest.py"), str(path), expect=expect)

    def test_example_passes_cross_field_validation(self):
        out = self.validate_file(self.example(), 0)
        self.assertTrue(json.loads(out.stdout)["pass"])

    def test_duplicate_site_id_fails(self):
        obj = self.example()
        obj["sites"].append(dict(obj["sites"][0]))
        out = self.validate_file(obj, 1)
        self.assertIn("duplicate site_id", out.stdout)

    def test_approved_domain_requires_domain(self):
        obj = self.example()
        obj["sites"][0]["domain_policy"] = {"mode": "approved", "domain": None}
        out = self.validate_file(obj, 1)
        self.assertIn("domain is required", out.stdout)

    def test_budget_cannot_preapprove_purchases(self):
        obj = self.example()
        obj["budget"]["domain_purchase_preapproved"] = True
        out = self.validate_file(obj, 1)
        self.assertIn("budgets never authorize paid actions", out.stdout)

    def test_paid_action_confirmation_policy_is_mandatory(self):
        obj = self.example()
        obj["cost_policy"]["require_human_confirmation_for_paid_actions"] = False
        out = self.validate_file(obj, 1)
        self.assertIn("must be true", out.stdout)

    def test_execution_policy_requires_planning_and_autonomy(self):
        obj = self.example()
        obj["execution_policy"]["planning_required"] = False
        obj["execution_policy"]["autonomy"] = "ask-before-every-step"
        out = self.validate_file(obj, 1)
        self.assertIn("planning_required must be true", out.stdout)
        self.assertIn("autonomy must be autonomous-until-complete", out.stdout)

    def test_execution_policy_requires_zero_cost_auto_and_paid_confirmation(self):
        obj = self.example()
        obj["execution_policy"]["zero_cost_external_actions"] = "ask"
        obj["execution_policy"]["paid_actions"] = "auto"
        out = self.validate_file(obj, 1)
        self.assertIn("zero_cost_external_actions must be auto", out.stdout)
        self.assertIn("paid_actions must be human-confirmation", out.stdout)

    def test_ai_enabled_requires_purpose_and_capability(self):
        obj = self.example()
        obj["sites"][0]["ai"] = {"enabled": True, "purpose": "", "capabilities": []}
        out = self.validate_file(obj, 1)
        self.assertIn("ai.purpose is required", out.stdout)
        self.assertIn("ai.capabilities must be non-empty", out.stdout)

    def test_unsupported_ai_capability_fails(self):
        obj = self.example()
        obj["sites"][0]["ai"]["capabilities"] = ["mind-reading"]
        out = self.validate_file(obj, 1)
        self.assertIn("unsupported capability", out.stdout)


    def test_auth_enabled_requires_method(self):
        obj = self.example()
        obj["sites"][0]["auth"] = {"enabled": True, "provider": "auto", "methods": []}
        out = self.validate_file(obj, 1)
        self.assertIn("auth.methods must be non-empty", out.stdout)

    def test_password_auth_requires_recovery(self):
        obj = self.example()
        obj["sites"][0]["auth"] = {
            "enabled": True, "provider": "supabase", "methods": ["password"],
            "authorization_model": "owner", "account_recovery": False
        }
        out = self.validate_file(obj, 1)
        self.assertIn("account_recovery must be true", out.stdout)

    def test_disabled_auth_cannot_protect_routes(self):
        obj = self.example()
        obj["sites"][0]["auth"] = {
            "enabled": False, "provider": "auto", "methods": [], "protected_routes": ["/private"]
        }
        out = self.validate_file(obj, 1)
        self.assertIn("protected_routes must be empty", out.stdout)

    def test_persistent_user_data_requires_explicit_authorization_model(self):
        obj = self.example()
        obj["sites"][0]["auth"] = {
            "enabled": True, "provider": "auto", "methods": ["magic-link"],
            "requires_persistent_user_data": True, "authorization_model": "authenticated-user"
        }
        out = self.validate_file(obj, 1)
        self.assertIn("must explicitly isolate persistent user data", out.stdout)

    def test_single_mode_requires_exactly_one_site(self):
        obj = self.example()
        obj["mode"] = "single"
        obj["sites"].append({**obj["sites"][0], "site_id": "sample-tool-b"})
        out = self.validate_file(obj, 1)
        self.assertIn("exactly one site", out.stdout)

    def test_ads_manual_strategy_requires_placement(self):
        obj = self.example()
        obj["sites"][0]["ads"] = {
            "enabled": True, "provider": "adsense", "strategy": "manual-slots",
            "placements": [], "consent_mode": "auto"
        }
        out = self.validate_file(obj, 1)
        self.assertIn("placements must be non-empty", out.stdout)

    def test_ads_placeholder_publisher_id_is_rejected(self):
        obj = self.example()
        obj["sites"][0]["ads"]["publisher_id"] = "pub-0000000000000000"
        out = self.validate_file(obj, 1)
        self.assertIn("must not be a placeholder", out.stdout)

    def test_analytics_sensitive_collection_must_be_false(self):
        obj = self.example()
        obj["sites"][0]["analytics"] = {
            "enabled": True, "provider": "google-analytics",
            "consent_mode": "auto", "collect_sensitive_content": True
        }
        out = self.validate_file(obj, 1)
        self.assertIn("collect_sensitive_content must be false", out.stdout)


class FactoryStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest = self.root / "manifest.json"
        obj = json.loads((ROOT / "assets" / "batch.example.json").read_text(encoding="utf-8"))
        self.manifest.write_text(json.dumps(obj), encoding="utf-8")
        self.state = self.root / "state.json"

    def tearDown(self):
        self.temp.cleanup()

    def cmd(self, *args, expect=0):
        return run(sys.executable, str(SCRIPTS / "factory_state.py"), *args, expect=expect)

    def test_init_creates_state(self):
        self.cmd("init", "--manifest", str(self.manifest), "--state", str(self.state))
        data = json.loads(self.state.read_text(encoding="utf-8"))
        site = data["sites"]["sample-tool-a"]
        self.assertEqual(site["stage"], "PLANNED")
        self.assertEqual(site["status"], "PENDING")

    def test_reinit_same_run_preserves_progress(self):
        self.cmd("init", "--manifest", str(self.manifest), "--state", str(self.state))
        self.cmd("set", "--state", str(self.state), "--site", "sample-tool-a", "--stage", "IMPLEMENTED")
        self.cmd("init", "--manifest", str(self.manifest), "--state", str(self.state))
        data = json.loads(self.state.read_text(encoding="utf-8"))
        self.assertEqual(data["sites"]["sample-tool-a"]["stage"], "IMPLEMENTED")

    def test_different_run_id_refuses_overwrite(self):
        self.cmd("init", "--manifest", str(self.manifest), "--state", str(self.state))
        obj = json.loads(self.manifest.read_text(encoding="utf-8"))
        obj["run_id"] = "another-run"
        other = self.root / "other.json"
        other.write_text(json.dumps(obj), encoding="utf-8")
        out = self.cmd("init", "--manifest", str(other), "--state", str(self.state), expect=1)
        self.assertIn("State belongs to run_id", out.stderr)

    def test_stage_regression_refused(self):
        self.cmd("init", "--manifest", str(self.manifest), "--state", str(self.state))
        self.cmd("set", "--state", str(self.state), "--site", "sample-tool-a", "--stage", "PRODUCTION_DEPLOYED")
        out = self.cmd(
            "set", "--state", str(self.state), "--site", "sample-tool-a", "--stage", "IMPLEMENTED", expect=1
        )
        self.assertIn("Refusing stage regression", out.stderr)

    def test_sensitive_external_field_refused(self):
        self.cmd("init", "--manifest", str(self.manifest), "--state", str(self.state))
        out = self.cmd(
            "external", "--state", str(self.state), "--site", "sample-tool-a",
            "--key", "access_token", "--value", "do-not-store", expect=1
        )
        self.assertIn("potentially sensitive", out.stderr)

    def test_resource_identifier_can_be_persisted(self):
        self.cmd("init", "--manifest", str(self.manifest), "--state", str(self.state))
        self.cmd(
            "external", "--state", str(self.state), "--site", "sample-tool-a",
            "--key", "vercel_project_id", "--value", "prj_123"
        )
        data = json.loads(self.state.read_text(encoding="utf-8"))
        self.assertEqual(data["sites"]["sample-tool-a"]["external"]["vercel_project_id"], "prj_123")


class SiteValidatorTests(unittest.TestCase):
    def serve(self, robots="User-agent: *\nDisallow:\n"):
        import threading
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                host = f"http://127.0.0.1:{self.server.server_port}"
                if self.path == "/":
                    body = (
                        "<!doctype html><html><head>"
                        "<title>Validator Test</title>"
                        "<meta name=\"description\" content=\"A validator fixture.\">"
                        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
                        "<meta property=\"og:title\" content=\"Validator Test\">"
                        f"<link rel=\"canonical\" href=\"{host}/\">"
                        "</head><body>ok</body></html>"
                    ).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
                    self.send_header("X-Frame-Options", "DENY")
                elif self.path == "/robots.txt":
                    body = robots.encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                elif self.path == "/sitemap.xml":
                    body = (
                        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
                        f"<url><loc>{host}/</loc></url></urlset>"
                    ).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/xml")
                else:
                    body = b"not found"
                    self.send_response(404)
                    self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server

    def test_valid_fixture_passes(self):
        server = self.serve()
        try:
            url = f"http://127.0.0.1:{server.server_port}"
            proc = run(sys.executable, str(SCRIPTS / "validate_site.py"), url, "--allow-http", expect=0)
            result = json.loads(proc.stdout)
            self.assertTrue(result["pass"])
            self.assertTrue(result["checks"]["404"]["pass"])
            self.assertTrue(result["checks"]["sitemap.xml"]["pass"])
            self.assertTrue(result["checks"]["x_content_type_options"]["pass"])
            self.assertTrue(result["checks"]["frame_protection"]["pass"])
        finally:
            server.shutdown()
            server.server_close()

    def test_global_robots_block_fails(self):
        server = self.serve("User-agent: *\nDisallow: /\n")
        try:
            url = f"http://127.0.0.1:{server.server_port}"
            proc = run(sys.executable, str(SCRIPTS / "validate_site.py"), url, "--allow-http", expect=1)
            result = json.loads(proc.stdout)
            self.assertFalse(result["checks"]["robots.txt"]["pass"])
            self.assertTrue(result["checks"]["robots.txt"]["globally_blocked"])
        finally:
            server.shutdown()
            server.server_close()


class GoogleHelperContractTests(unittest.TestCase):
    def load_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("google_search_console", SCRIPTS / "google_search_console.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_google_token_endpoint_and_body_contract(self):
        module = self.load_module()
        captured = {}
        def fake_request(method, url, body=None):
            captured.update(method=method, url=url, body=body)
            return 200, {"method": "DNS_TXT", "token": "sample"}
        module.request = fake_request
        module.verify_token("example.com")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["url"], "https://www.googleapis.com/siteVerification/v1/token")
        self.assertEqual(captured["body"]["site"], {"type": "INET_DOMAIN", "identifier": "example.com"})
        self.assertEqual(captured["body"]["verificationMethod"], "DNS_TXT")

    def test_search_console_domain_property_is_encoded(self):
        module = self.load_module()
        captured = {}
        def fake_request(method, url, body=None):
            captured.update(method=method, url=url, body=body)
            return 200, {}
        module.request = fake_request
        module.add_property("example.com")
        self.assertEqual(captured["method"], "PUT")
        self.assertTrue(captured["url"].endswith("/sites/sc-domain%3Aexample.com"))

    def test_missing_google_token_fails_before_network(self):
        env = os.environ.copy()
        env.pop("GOOGLE_ACCESS_TOKEN", None)
        proc = run(sys.executable, str(SCRIPTS / "google_search_console.py"), "get-dns-token", "example.com", expect=1, env=env)
        self.assertIn("GOOGLE_ACCESS_TOKEN is required", proc.stderr)


class CostGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.temp.name) / "approvals.json"

    def tearDown(self):
        self.temp.cleanup()

    def cmd(self, *args, expect=0):
        return run(
            sys.executable, str(SCRIPTS / "cost_gate.py"),
            "--ledger", str(self.ledger), *args, expect=expect
        )

    def request(self, max_cost=12.50):
        return self.cmd(
            "request",
            "--action-id", "domain-order-1",
            "--kind", "domain_purchase",
            "--provider", "vercel",
            "--description", "Purchase exact test domain",
            "--currency", "USD",
            "--max-cost", str(max_cost),
            "--items-json", '[{"domain":"example-test.invalid","quoted_cost":12.5}]',
        )

    def test_pending_request_is_not_approved(self):
        self.request()
        out = self.cmd("check", "--action-id", "domain-order-1", "--current-cost", "12.5", "--currency", "USD", expect=1)
        self.assertIn("explicit human approval has not been recorded", out.stdout)

    def test_approval_requires_explicit_yes(self):
        self.request()
        out = run(
            sys.executable, str(SCRIPTS / "cost_gate.py"),
            "--ledger", str(self.ledger),
            "record-approval", "--action-id", "domain-order-1",
            "--confirmed", "YES", "--approved-max-cost", "12.5", expect=0
        )
        self.assertIn('"status": "APPROVED"', out.stdout)

    def test_price_increase_invalidates_execution(self):
        self.request()
        self.cmd("record-approval", "--action-id", "domain-order-1", "--confirmed", "YES", "--approved-max-cost", "12.5")
        out = self.cmd("check", "--action-id", "domain-order-1", "--current-cost", "13.0", "--currency", "USD", expect=1)
        self.assertIn("current cost exceeds the approved maximum", out.stdout)

    def test_currency_change_invalidates_execution(self):
        self.request()
        self.cmd("record-approval", "--action-id", "domain-order-1", "--confirmed", "YES", "--approved-max-cost", "12.5")
        out = self.cmd("check", "--action-id", "domain-order-1", "--current-cost", "12.5", "--currency", "JPY", expect=1)
        self.assertIn("currency differs", out.stdout)

    def test_consumed_approval_cannot_be_checked_again(self):
        self.request()
        self.cmd("record-approval", "--action-id", "domain-order-1", "--confirmed", "YES", "--approved-max-cost", "12.5")
        self.cmd("consume", "--action-id", "domain-order-1", "--actual-cost", "12.5", "--currency", "USD")
        out = self.cmd("check", "--action-id", "domain-order-1", "--current-cost", "12.5", "--currency", "USD", expect=1)
        self.assertIn("explicit human approval has not been recorded", out.stdout)

    def test_sensitive_fields_are_refused(self):
        out = self.cmd(
            "request",
            "--action-id", "bad",
            "--kind", "paid_ai_test",
            "--provider", "provider",
            "--description", "Bad request",
            "--currency", "USD",
            "--max-cost", "1",
            "--items-json", '[{"api_key":"secret"}]',
            expect=1,
        )
        self.assertIn("potentially sensitive", out.stderr)

    def test_duplicate_action_id_is_refused(self):
        self.request()
        out = self.cmd(
            "request",
            "--action-id", "domain-order-1",
            "--kind", "domain_purchase",
            "--provider", "vercel",
            "--description", "Duplicate",
            "--currency", "USD",
            "--max-cost", "12.5",
            "--items-json", '[{"domain":"example-test.invalid","quoted_cost":12.5}]',
            expect=1,
        )
        self.assertIn("action_id already exists", out.stderr)

    def test_ttl_over_one_day_is_refused(self):
        self.request()
        out = run(
            sys.executable, str(SCRIPTS / "cost_gate.py"),
            "--ledger", str(self.ledger),
            "record-approval", "--action-id", "domain-order-1",
            "--confirmed", "YES", "--approved-max-cost", "12.5",
            "--ttl-minutes", "1441", expect=1
        )
        self.assertIn("between 1 and 1440", out.stderr)

    def test_consume_rejects_currency_mismatch(self):
        self.request()
        self.cmd("record-approval", "--action-id", "domain-order-1", "--confirmed", "YES", "--approved-max-cost", "12.5")
        out = self.cmd("consume", "--action-id", "domain-order-1", "--actual-cost", "12.5", "--currency", "EUR", expect=1)
        self.assertIn("currency differs", out.stderr)

    def test_consume_rejects_tampered_approved_request(self):
        self.request()
        self.cmd("record-approval", "--action-id", "domain-order-1", "--confirmed", "YES", "--approved-max-cost", "12.5")
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        data["requests"]["domain-order-1"]["items"][0]["domain"] = "changed.invalid"
        self.ledger.write_text(json.dumps(data), encoding="utf-8")
        out = self.cmd("consume", "--action-id", "domain-order-1", "--actual-cost", "12.5", "--currency", "USD", expect=1)
        self.assertIn("request details changed", out.stderr)


class SecurityAndPolicyTests(unittest.TestCase):
    def test_planning_first_autonomous_production_policy(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference = (ROOT / "references" / "autonomous-execution.md").read_text(encoding="utf-8")
        self.assertIn("Plan-first and autonomous-to-production contract", skill)
        self.assertIn("continue development until the site is genuinely ready for public production", skill)
        self.assertIn("Genuinely zero-cost provisioning/configuration SHOULD proceed autonomously", skill)
        self.assertIn("A nominal free tier is NOT enough", reference)
        self.assertIn("Ask only for the minimum required human action", reference)

    def test_plan_validator_rejects_billable_auto_execution(self):
        plan = json.loads((ROOT / "assets" / "site-plan.example.json").read_text(encoding="utf-8"))
        plan["integrations"][1]["action_policy"] = "auto"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            out = run(sys.executable, str(SCRIPTS / "validate_plan.py"), str(path), expect=1)
            self.assertIn("human-cost-gate", out.stdout)

    def test_skill_prohibits_generic_indexing_api(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("do not use google's indexing api", text)
        self.assertIn("never report \"google indexed\" merely because a sitemap was submitted", text)

    def test_every_paid_action_requires_human_confirmation(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("mandatory for every paid action", text)
        self.assertIn("budgets and price limits are selection constraints only", text)
        self.assertIn("requires explicit human confirmation immediately before execution", text)
        self.assertIn("real ai inference can incur usage charges", text)

    def test_skill_does_not_allow_budget_preapproval(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertNotIn("batch preapproval", text)
        self.assertIn("it may not authorize unknown future purchases", text)

    def test_ai_guidance_present(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("vercel ai sdk", text)
        self.assertIn("responses api", text)
        self.assertIn("retrieval-augmented generation", text)
        self.assertIn("rate limiting", text)
        self.assertIn("treat retrieved/uploaded text as untrusted data", text)

    def test_secret_storage_is_prohibited(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("never print access tokens or secrets", text)

    def test_skill_requires_server_side_authorization_for_auth(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("authentication from authorization", text)
        self.assertIn("middleware/proxy redirects", text)
        self.assertIn("cross-user isolation", text)

    def test_auth_reference_requires_cost_gate_and_secret_isolation(self):
        text = (ROOT / "references" / "authentication.md").read_text(encoding="utf-8").lower()
        self.assertIn("human cost gate", text)
        self.assertIn("service-role", text)
        self.assertIn("user a cannot", text)

    def test_ai_auth_isolation_guidance_present(self):
        text = (ROOT / "references" / "ai-features.md").read_text(encoding="utf-8").lower()
        self.assertIn("verified server-side session", text)
        self.assertIn("never let the model", text)
        self.assertIn("cross-user", text)

    def test_manual_e2e_covers_auth_ai_isolation(self):
        text = (ROOT / "tests" / "MANUAL_E2E.md").read_text(encoding="utf-8").lower()
        self.assertIn("authenticated ai data isolation", text)
        self.assertIn("prompt injection", text)
        self.assertIn("separate explicit human confirmation", text)

    def test_advertising_guidance_is_truthful_and_consent_aware(self):
        text = (ROOT / "references" / "advertising.md").read_text(encoding="utf-8").lower()
        self.assertIn("never report that ads are live", text)
        self.assertIn("ads.txt", text)
        self.assertIn("google-certified cmp", text)
        self.assertIn("human cost gate", text)

    def test_production_baseline_covers_core_release_areas(self):
        text = (ROOT / "references" / "production-baseline.md").read_text(encoding="utf-8").lower()
        for phrase in ("security headers", "404", "accessibility", "privacy", "rate-limit", "account/data deletion", "performance", "observability"):
            self.assertIn(phrase, text)

    def test_visual_testing_is_a_mandatory_rendered_gate(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        visual = (ROOT / "references" / "visual-testing.md").read_text(encoding="utf-8").lower()
        checklist = (ROOT / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8").lower()
        self.assertIn("visual testing is mandatory", skill)
        self.assertIn("source inspection", skill)
        self.assertIn("390 x 844", skill)
        self.assertIn("1440 x 900", skill)
        self.assertIn("must not be marked `preview_qa_pass` or `complete`", visual)
        self.assertIn("screenshot evidence", visual)
        self.assertIn("blocked", visual)
        self.assertIn("mandatory rendered visual qa", checklist)

    def test_visual_qa_example_passes_validator(self):
        example = ROOT / "assets" / "visual-qa.example.json"
        out = run(sys.executable, str(SCRIPTS / "validate_visual_qa.py"), str(example))
        self.assertTrue(json.loads(out.stdout)["pass"])

    def test_visual_qa_validator_rejects_missing_desktop_coverage(self):
        report = json.loads((ROOT / "assets" / "visual-qa.example.json").read_text(encoding="utf-8"))
        report["checks"] = [report["checks"][0]]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "visual.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            out = run(sys.executable, str(SCRIPTS / "validate_visual_qa.py"), str(path), expect=1)
            self.assertIn("desktop", out.stdout.lower())

    def test_market_research_prohibits_fabricated_metrics_and_thin_batches(self):
        text = (ROOT / "references" / "market-research.md").read_text(encoding="utf-8").lower()
        self.assertIn("do not invent keyword volume", text)
        self.assertIn("doorway pages", text)
        self.assertIn("evidence date", text)
        self.assertIn("build / merge / reject", text)

    def test_integration_guidance_covers_payments_webhooks_and_uploads(self):
        text = (ROOT / "references" / "data-and-integrations.md").read_text(encoding="utf-8").lower()
        for phrase in ("payment", "webhook signatures", "idempotent", "file uploads", "ssrf", "human cost gate"):
            self.assertIn(phrase, text)

    def test_skill_requires_current_security_advisory_check(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("current high-severity framework/runtime advisories", text)
        self.assertIn("patched maintained release", text)

    def test_manual_e2e_covers_ads_and_production_baseline(self):
        text = (ROOT / "tests" / "MANUAL_E2E.md").read_text(encoding="utf-8").lower()
        self.assertIn("advertising provider state", text)
        self.assertIn("consent denied", text)
        self.assertIn("production baseline", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
