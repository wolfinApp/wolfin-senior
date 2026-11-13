#!/usr/bin/env python3
"""Stop hook: a turn that changed things must be verified and logged.

Checks the turn that is ending (everything after the user's last prompt):
1. Verification: if a source-code file was edited and no test, build, lint
   or run command came after the last code edit, ask for one.
   Off with WOLFIN_VERIFY_GATE=off.
2. Logging: if files were edited or a git commit/merge/push ran, and neither
   NOW.md nor today's journal in the project memory changed since the
   prompt, ask for a log entry. Off with WOLFIN_MEMORY_GATE=off.

Blocks at most once per turn (stop_hook_active), so it can never loop.
Allows the stop on any error.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
GIT_ACTIONS = ("git commit", "git merge", "git push", "git rebase", "git cherry-pick")
CODE_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro",
    ".py", ".rb", ".php", ".go", ".java", ".kt", ".kts", ".scala", ".swift",
    ".dart", ".rs", ".cs", ".fs", ".ex", ".exs", ".erl", ".clj", ".c", ".h",
    ".cc", ".cpp", ".hpp", ".m", ".mm", ".lua", ".r", ".jl", ".sol", ".zig",
    ".prisma", ".graphql", ".gql", ".ipynb",
}
VERIFY = re.compile(
    r"\b(?:(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:test|build|lint|check|typecheck|verify)"
    r"|npx\s+(?:tsc|jest|vitest|eslint|playwright|mocha)|tsc|jest|vitest|mocha|eslint|pytest|mypy|ruff"
    r"|python3?\s+-m\s+(?:pytest|unittest|mypy|ruff|py_compile)|go\s+(?:test|build|vet)"
    r"|cargo\s+(?:test|build|check|clippy)|phpunit|php\s+artisan\s+test|rspec|rake\s+test"
    r"|mvn\s+(?:test|verify|package)|gradlew?\s+(?:test|build|check)|dotnet\s+(?:test|build)"
    r"|flutter\s+(?:test|analyze)|dart\s+(?:test|analyze)|swift\s+(?:test|build)|xcodebuild"
    r"|deno\s+(?:test|check)|node\s+--(?:test|check)|make\s+(?:test|check)"
    r"|node\s+\S+\.[cm]?[jt]s|python3?\s+\S+\.py|ruby\s+\S+\.rb|go\s+run)\b"
)


def off(var):
    return os.environ.get(var, "").strip().lower() in {"off", "0", "false", "no"}


def repo_paths(start):
    """Return (memory dir, git info/exclude path or None) for the main checkout."""
    root, exclude = start, None
    try:
        common = subprocess.run(
            ["git", "-C", start, "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        if common:
            exclude = os.path.join(common, "info", "exclude")
        if common.endswith("/.git"):
            root = common[: -len("/.git")]
        elif common:
            top = subprocess.run(
                ["git", "-C", start, "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, timeout=5,
            ).stdout.strip()
            root = top or start
    except (OSError, subprocess.SubprocessError):
        pass
    return os.path.join(root, ".wolfin-senior", "memory"), exclude


def ensure_excluded(exclude):
    """Keep .wolfin-senior/ out of commits without touching the project's .gitignore."""
    if not exclude:
        return
    try:
        text = ""
        if os.path.exists(exclude):
            with open(exclude, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        if any(line.strip() in {".wolfin-senior", ".wolfin-senior/", "/.wolfin-senior", "/.wolfin-senior/"} for line in text.splitlines()):
            return
        os.makedirs(os.path.dirname(exclude), exist_ok=True)
        with open(exclude, "a", encoding="utf-8") as fh:
            fh.write(("" if not text or text.endswith("\n") else "\n") + ".wolfin-senior/\n")
    except OSError:
        pass


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


def is_prompt(entry):
    """A real user prompt: not a tool result, not meta, not a subagent line."""
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isSidechain"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        return not any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)
    return False


def scan(transcript, root=None):
    """Facts about the turn after the last prompt. Throwaway files outside root don't count."""
    turn = None
    with open(transcript, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if is_prompt(entry):
                turn = {"start": entry.get("timestamp"), "worked": False, "unverified_code": False}
                continue
            if turn is None or entry.get("type") != "assistant" or entry.get("isSidechain"):
                continue
            for block in (entry.get("message") or {}).get("content") or []:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name, tool_input = block.get("name", ""), block.get("input") or {}
                if name in EDIT_TOOLS:
                    path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
                    if scratch(path, root):
                        continue
                    turn["worked"] = True
                    if os.path.splitext(path)[1].lower() in CODE_EXT and "/.wolfin-senior/" not in path:
                        turn["unverified_code"] = True
                elif name == "Bash":
                    command = str(tool_input.get("command", ""))
                    if any(action in command for action in GIT_ACTIONS):
                        turn["worked"] = True
                    if VERIFY.search(command):
                        turn["unverified_code"] = False
    if turn and turn["start"]:
        try:
            turn["start"] = datetime.fromisoformat(turn["start"].replace("Z", "+00:00")).timestamp()
        except ValueError:
            turn["start"] = None
    return turn


def touched_since(path, since):
    try:
        return os.path.getmtime(path) >= since - 1
    except OSError:
        return False


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    if data.get("stop_hook_active"):
        return
    transcript = data.get("transcript_path")
    if not transcript or not os.path.isfile(transcript):
        return
    project = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    turn = scan(transcript, project)
    if not turn or not turn["start"] or not turn["worked"]:
        return

    todo = []
    if turn["unverified_code"] and not off("WOLFIN_VERIFY_GATE"):
        todo.append(
            "Verify (verification-before-completion): code changed after the last test/build/run "
            "command. Run the project's tests (or build, lint, or the program itself) now and read "
            "the output. If it truly can't run, say exactly why in your final message."
        )
    if not off("WOLFIN_MEMORY_GATE"):
        mem, exclude = repo_paths(project)
        ensure_excluded(exclude)
        journal = os.path.join(mem, "journal", time.strftime("%Y-%m-%d") + ".md")
        now = os.path.join(mem, "NOW.md")
        if not (touched_since(journal, turn["start"]) or touched_since(now, turn["start"])):
            todo.append(
                f"Log (project-memory): append a short entry to {journal} (what was asked, what you "
                "did with files, how you verified it as command -> result, decisions with their "
                f"reason, next step) and rewrite {now} with the current task, progress and next step. "
                "Create the directory and files if missing."
            )
    if not todo:
        return
    steps = " ".join(f"({i}) {t}" for i, t in enumerate(todo, 1))
    reason = (f"Wolfin Senior (strict): before finishing this turn: {steps} "
              "Then end the turn with one short line, without repeating your previous answer.")
    print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a broken gate must never trap the session
        pass
