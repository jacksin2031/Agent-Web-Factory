#!/usr/bin/env python3
"""Run one isolated Agent Web Factory test shard."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARDS = {
    "core": [
        "tests.test_skill.SkillStructureTests",
        "tests.test_skill.FactoryStateTests",
        "tests.test_skill.GoogleHelperContractTests",
    ],
    "manifest-cost": [
        "tests.test_skill.ManifestValidatorTests",
        "tests.test_skill.CostGateTests",
    ],
    "policy-compat": [
        "tests.test_skill.SiteValidatorTests",
        "tests.test_skill.SecurityAndPolicyTests",
        "tests.test_compatibility.RuntimeCompatibilityTests",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("shard", choices=sorted(SHARDS))
    args = parser.parse_args()
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "-v", *SHARDS[args.shard]],
        cwd=ROOT,
        env=env,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
