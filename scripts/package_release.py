#!/usr/bin/env python3
"""Build a clean distributable ZIP for Agent Web Factory."""

import argparse
import os
import zipfile
from pathlib import Path

EXCLUDED_DIRS = {".git", ".venv", ".web-factory", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_NAMES = {".env", ".env.local", ".env.production", ".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
FORBIDDEN_SECRET_NAMES = {"id_rsa", "id_ed25519", "credentials.json", "service-account.json"}


def excluded(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return True
    if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
        return True
    if path.name.startswith(".env.") and path.name != ".env.example":
        return True
    if path.suffix.lower() == ".zip":
        return True
    return False


def build(root: Path, output: Path) -> int:
    root = root.resolve()
    output = output.resolve()
    files = []
    for path in sorted(root.rglob("*")):
        if excluded(path, root):
            continue
        if path.is_symlink():
            raise SystemExit(f"Refusing to package symlink: {path.relative_to(root)}")
        if path.is_file():
            if path.suffix.lower() in FORBIDDEN_SECRET_SUFFIXES or path.name.lower() in FORBIDDEN_SECRET_NAMES:
                raise SystemExit(f"Refusing to package potential credential file: {path.relative_to(root)}")
            files.append(path)

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = Path(root.name) / path.relative_to(root)
            zf.write(path, arcname.as_posix())
    return len(files)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    count = build(Path(args.root), Path(args.output))
    print(f"Packaged {count} files into {args.output}")


if __name__ == "__main__":
    main()
