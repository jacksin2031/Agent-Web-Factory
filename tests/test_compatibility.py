import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = json.loads((ROOT / "assets" / "runtime-matrix.json").read_text(encoding="utf-8"))


class RuntimeCompatibilityTests(unittest.TestCase):
    def test_required_runtime_families_present(self):
        ids = {r["id"] for r in MATRIX["runtimes"]}
        self.assertTrue({"openai", "gemini-cli", "github-copilot", "claude-code", "generic"} <= ids)

    def test_all_adapters_exist(self):
        for runtime in MATRIX["runtimes"]:
            self.assertTrue((ROOT / runtime["adapter"]).is_file(), runtime["id"])

    def test_first_class_runtimes_use_same_core_skill(self):
        for runtime in MATRIX["runtimes"]:
            if runtime["support_level"] == "first-class":
                self.assertEqual(runtime["skill_format"], "SKILL.md")

    def test_agents_alias_is_used_where_portable(self):
        by_id = {r["id"]: r for r in MATRIX["runtimes"]}
        for rid in ("openai", "gemini-cli", "github-copilot"):
            paths = by_id[rid]["project_paths"] + by_id[rid]["user_paths"]
            self.assertTrue(any(".agents/skills/agent-web-factory" in p for p in paths), rid)

    def test_claude_code_has_native_skill_path(self):
        runtime = next(r for r in MATRIX["runtimes"] if r["id"] == "claude-code")
        self.assertIn(".claude/skills/agent-web-factory", runtime["project_paths"])

    def test_paid_action_policy_cannot_be_weakened(self):
        policy = MATRIX["policy"]
        self.assertIs(policy["paid_action_human_confirmation_mandatory"], True)
        self.assertIs(policy["runtime_adapter_may_weaken_core_policy"], False)
        for path in (ROOT / "adapters").glob("*/README.md"):
            text = path.read_text(encoding="utf-8").lower()
            self.assertTrue("paid" in text or "billable" in text or "cost gate" in text, path)

    def test_planning_and_autonomy_policy_is_shared_across_runtimes(self):
        policy = MATRIX["policy"]
        self.assertIs(policy["planning_before_implementation_mandatory"], True)
        self.assertIs(policy["autonomous_until_public_production"], True)
        self.assertIs(policy["zero_cost_external_actions_auto"], True)
        for path in (ROOT / "adapters").glob("*/README.md"):
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("planning before implementation", text, path)
            self.assertIn("zero-cost", text, path)

    def test_openai_metadata_does_not_replace_core_policy(self):
        text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8").lower()
        self.assertIn("explicit human confirmation", text)
        self.assertTrue((ROOT / "SKILL.md").is_file())

    def test_generic_adapter_requires_execution_truthfulness(self):
        text = (ROOT / "references" / "runtime-compatibility.md").read_text(encoding="utf-8").lower()
        self.assertIn("mark unavailable execution stages as blocked", text)
        self.assertIn("static adapter checks are not runtime verification", text)

    def test_compatibility_script_passes(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "compatibility_check.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=20
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(json.loads(proc.stdout)["pass"])

    def test_runtime_matrix_is_english_and_versioned(self):
        self.assertEqual(MATRIX["schema_version"], 1)
        self.assertEqual(MATRIX["skill_name"], "agent-web-factory")

    def test_single_normative_skill_file(self):
        skills = [p for p in ROOT.rglob("SKILL.md") if ".git" not in p.parts]
        self.assertEqual(skills, [ROOT / "SKILL.md"], "Runtime adapters must not fork SKILL.md")

    def test_beta_runtime_status_does_not_overclaim_verification(self):
        text = (ROOT / "RUNTIME_VERIFICATION.md").read_text(encoding="utf-8").lower()
        for runtime in ("openai codex", "gemini cli", "github copilot", "claude code"):
            self.assertIn(runtime, text)
        self.assertIn("| openai codex / chatgpt skills | pass | pending |", text)
        self.assertIn("must not convert any `pending` runtime result into `pass`", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
