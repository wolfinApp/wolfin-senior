#!/usr/bin/env python3
"""PreToolUse hook: no code edits before docs-first and test-driven-development.

Every Edit/Write of a source-code file is refused until both skills have
been loaded in the session (running docs-first's versions.py also counts
for docs-first). The refusal names what's missing. After 3 refusals in one
session the gate lets edits through, so a session can never be trapped by
it (for example, a subagent that can't load skills). Throwaway files in a
temp folder outside the project (a repro script) are not gated.
Turn it off with WOLFIN_CODE_GATE=off.
"""

import json
import os
import re
import sys
import tempfile

CODE_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro",
    ".py", ".rb", ".php", ".go", ".java", ".kt", ".kts", ".scala", ".swift",
    ".dart", ".rs", ".cs", ".fs", ".ex", ".exs", ".erl", ".clj", ".c", ".h",
    ".cc", ".cpp", ".hpp", ".m", ".mm", ".lua", ".r", ".jl", ".sol", ".zig",
    ".prisma", ".graphql", ".gql", ".ipynb",
}
# skill name -> raw transcript substrings that prove it was loaded or run
REQUIRED = {
    "docs-first": ("skills/docs-first", "docs-first/scripts/versions.py"),
    "test-driven-development": ("skills/test-driven-development",),
}
MAX_DENIALS = 3


def inside(path, root):
    """True if path is in the project folder (relative paths count as inside).

    Compares both the literal and the symlink-resolved paths, so a file under a
    linked folder in the project counts, and ignores letter case on macOS and
    Windows, whose file systems usually do.
    """
    if not root or not os.path.isabs(path):
        return True
    fold = str.lower if sys.platform in ("darwin", "win32") else str

    def under(p, r):
        p, r = fold(p), fold(r).rstrip(os.sep)
        return p == r or p.startswith(r + os.sep) or not r

    return (under(os.path.abspath(path), os.path.abspath(root))
            or under(os.path.realpath(path), os.path.realpath(root)))


def scratch(path, root):
    """A throwaway file: outside the project and inside a temp folder."""
    if inside(path, root):
        return False
    temps = {tempfile.gettempdir(), os.environ.get("TMPDIR", ""), "/tmp", "/var/tmp"}
    return any(t and inside(path, t) and os.path.isabs(path) for t in temps)


def skill_call(line, name):
    """True if this transcript line is a Skill tool call for `name`."""
    try:
        entry = json.loads(line)
    except ValueError:
        return False
    for block in (entry.get("message") or {}).get("content") or []:
        if (isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill"
                and str((block.get("input") or {}).get("skill", "")).endswith(name)):
            return True
    return False


def loaded_skills(transcripts):
    found = set()
    for transcript in transcripts:
        try:
            with open(transcript, encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    for name, markers in REQUIRED.items():
                        if name in found or name not in line:  # every marker contains the name
                            continue
                        if any(m in line for m in markers) or skill_call(line, name):
                            found.add(name)
        except OSError:
            continue
    return found


def main():
    if os.environ.get("WOLFIN_CODE_GATE", "").strip().lower() in {"off", "0", "false", "no"}:
        return
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    tool_input = data.get("tool_input") or {}
    path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if os.path.splitext(path)[1].lower() not in CODE_EXT or "/.wolfin-senior/" in path:
        return
    if scratch(path, os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd")):
        return  # a throwaway script in a temp folder isn't project code

    transcripts = [p for p in (data.get("transcript_path"), data.get("agent_transcript_path")) if p]
    missing = [name for name in REQUIRED if name not in loaded_skills(transcripts)]
    if not missing:
        return

    session = re.sub(r"[^A-Za-z0-9_-]", "_", str(data.get("session_id") or "unknown"))[:80]
    counter = os.path.join(tempfile.gettempdir(), f"wolfin-senior-code-gate-{session}")
    try:
        with open(counter, encoding="utf-8") as fh:
            denials = int(fh.read().strip() or 0)
    except (OSError, ValueError):
        denials = 0
    if denials >= MAX_DENIALS:
        return
    with open(counter, "w", encoding="utf-8") as fh:
        fh.write(str(denials + 1))

    reason = (
        f"Wolfin Senior (strict): edit of {os.path.basename(path)} refused. Missing in this session: "
        + ", ".join(missing) + ". Load each with the Skill tool and follow it: docs-first checks the "
        "installed vs latest versions and the current official docs for the APIs you'll use; "
        "test-driven-development means writing the failing test before this code. Then retry the edit. "
        f"(Refusal {denials + 1} of {MAX_DENIALS}; after that the gate stops refusing.)"
    )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a broken gate must never block edits
        pass
