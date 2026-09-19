#!/usr/bin/env python3
import json
import os
import shutil
import subprocess

CORE_TOOLS = ["git", "node", "npm", "npx", "vercel"]
RUNTIME_TOOLS = ["codex", "gemini", "claude", "gh"]


def version(cmd):
    try:
        p = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=10)
        out = (p.stdout or p.stderr).strip().splitlines()
        return out[0] if out else "available"
    except Exception as exc:
        return f"error: {exc.__class__.__name__}"


def main():
    tools = {}
    for cmd in CORE_TOOLS:
        path = shutil.which(cmd)
        tools[cmd] = {"available": bool(path), "path": path, "version": version(cmd) if path else None}

    runtimes = {}
    for cmd in RUNTIME_TOOLS:
        path = shutil.which(cmd)
        runtimes[cmd] = {"available": bool(path), "path": path, "version": version(cmd) if path else None}

    auth = {
        "VERCEL_TOKEN_present": bool(os.getenv("VERCEL_TOKEN")),
        "GOOGLE_ACCESS_TOKEN_present": bool(os.getenv("GOOGLE_ACCESS_TOKEN")),
        "OPENAI_API_KEY_present": bool(os.getenv("OPENAI_API_KEY")),
        "AI_GATEWAY_API_KEY_present": bool(os.getenv("AI_GATEWAY_API_KEY")),
        "AUTH_SECRET_present": bool(os.getenv("AUTH_SECRET")),
        "SUPABASE_URL_present": bool(os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")),
        "SUPABASE_PUBLISHABLE_KEY_present": bool(os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")),
        "CLERK_SECRET_KEY_present": bool(os.getenv("CLERK_SECRET_KEY")),
    }
    result = {"tools": tools, "agent_runtimes": runtimes, "auth_env": auth}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
