#!/usr/bin/env python3
"""Validate Agent Web Factory runtime adapter metadata and portable policy invariants."""

import argparse
import json
import re
from pathlib import Path

REQUIRED_RUNTIME_IDS = {"openai", "gemini-cli", "github-copilot", "claude-code", "generic"}
MANDATORY_CORE_PHRASES = (
    "human cost gate",
    "requires explicit human confirmation immediately before execution",
    "budgets and price limits are selection constraints only",
    "never say \"complete\"",
)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    matrix_path = root / "assets" / "runtime-matrix.json"
    skill_path = root / "SKILL.md"
    if not matrix_path.is_file():
        return ["missing assets/runtime-matrix.json"]
    if not skill_path.is_file():
        return ["missing SKILL.md"]

    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if matrix.get("skill_name") != "agent-web-factory":
        errors.append("runtime matrix skill_name must be agent-web-factory")
    policy = matrix.get("policy", {})
    if policy.get("paid_action_human_confirmation_mandatory") is not True:
        errors.append("runtime matrix must require human confirmation for paid actions")
    if policy.get("runtime_adapter_may_weaken_core_policy") is not False:
        errors.append("runtime adapters must not be allowed to weaken core policy")

    runtimes = matrix.get("runtimes", [])
    ids = {r.get("id") for r in runtimes}
    missing = sorted(REQUIRED_RUNTIME_IDS - ids)
    if missing:
        errors.append(f"missing runtime adapters: {', '.join(missing)}")

    for runtime in runtimes:
        rid = runtime.get("id", "<unknown>")
        adapter = runtime.get("adapter")
        if not adapter or not (root / adapter).is_file():
            errors.append(f"{rid}: adapter file missing: {adapter}")
        if runtime.get("automated_contract_tested") is not True:
            errors.append(f"{rid}: automated_contract_tested must be true")
        if runtime.get("support_level") == "first-class" and runtime.get("skill_format") != "SKILL.md":
            errors.append(f"{rid}: first-class runtime must load SKILL.md")

    skill = skill_path.read_text(encoding="utf-8").lower()
    for phrase in MANDATORY_CORE_PHRASES:
        if phrase.lower() not in skill:
            errors.append(f"core policy phrase missing: {phrase}")

    if not re.match(r"^---\n.*?\n---\n", skill_path.read_text(encoding="utf-8"), re.S):
        errors.append("SKILL.md must start with YAML frontmatter")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = validate(root)
    result = {"pass": not errors, "errors": errors}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
