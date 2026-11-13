"""Behaviour tests for the plugin's hooks.

Each hook is run the way Claude Code runs it: as a subprocess that reads the
hook's JSON input on stdin and prints its decision on stdout.

Run from the repository root:  python3 -m unittest discover -s tests -v
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, "hooks")
GATE_VARS = ("WOLFIN_CODE_GATE", "WOLFIN_VERIFY_GATE", "WOLFIN_MEMORY_GATE",
             "WOLFIN_REMINDER", "WOLFIN_GIT_GUARD", "CLAUDE_PROJECT_DIR")


def run_hook(name, payload=None, env=None, cwd=None):
    """Run a hook and return its parsed JSON output, or None when it printed nothing."""
    path = os.path.join(HOOKS, name)
    cmd = [sys.executable, "-I", path] if name.endswith(".py") else [path]
    base = {k: v for k, v in os.environ.items() if k not in GATE_VARS}
    base["CLAUDE_PLUGIN_ROOT"] = ROOT
    base.update(env or {})
    result = subprocess.run(cmd, input=json.dumps(payload or {}), capture_output=True,
                            text=True, env=base, cwd=cwd or tempfile.gettempdir(), timeout=30)
    if result.returncode != 0:
        raise AssertionError(f"{name} exited {result.returncode}: {result.stderr}")
    out = result.stdout.strip()
    return json.loads(out) if out else None


def bash(command, **env):
    return run_hook("git-guard.py", {"tool_name": "Bash", "tool_input": {"command": command}}, env=env)


def decision(out):
    return ((out or {}).get("hookSpecificOutput") or {}).get("permissionDecision")


class GitGuard(unittest.TestCase):
    DESTRUCTIVE = [
        "git push --force origin main",
        "git push -f",
        "git push -uf origin feature",
        "git push --force-with-lease",
        "git push origin +main",
        "git push origin :old-branch",
        "git push --delete origin old-branch",
        "git push --mirror backup",
        "git reset --hard HEAD~1",
        "git reset --hard",
        "git clean -fd",
        "git clean -xdf",
        "git clean --force",
        "git branch -D feature",
        "git branch --delete --force feature",
        "git checkout -- .",
        "git checkout .",
        "git checkout -f main",
        "git checkout HEAD -- src/app.ts",
        "git restore src/app.ts",
        "git restore .",
        "git restore --staged --worktree src/app.ts",
        "git switch --discard-changes main",
        "git stash drop",
        "git stash clear",
        "git filter-branch --tree-filter 'rm -f secrets' HEAD",
        "git filter-repo --path secrets --invert-paths",
        "git reflog expire --expire=now --all",
        "git gc --prune=now",
        "git update-ref -d refs/heads/old",
        "git worktree remove --force ../wt",
        "cd repo && git reset --hard origin/main",
        "npm test; git clean -fdx",
        "FOO=1 git -C /tmp/repo reset --hard",
        "git -c core.editor=true push -f origin main",
        "git --no-pager stash clear",
        "echo $(git reset --hard)",
        "echo `git stash clear`",
        'git commit -m "fix `git reset --hard`"',
        "git status\ngit reset --hard",
        'for b in a b; do git branch -D "$b"; done',
        "if true; then git reset --hard; fi",
        "{ git reset --hard; }",
        "! git stash clear",
        "git branch --merged | grep -v main | xargs git branch -D",
        "timeout 30 git push -f",
        "sudo -u me git clean -fd",
        "env -i git reset --hard",
        "bash -c 'git reset --hard'",
        "sh -lc \"git stash clear\"",
        "eval 'git stash clear'",
        "git checkout HEAD src/app.ts",
        "git checkout ./src",
        "git prune",
        "git gc --prune=0",
        "git-filter-repo --path secrets --invert-paths",
        "git stash -q drop",
        "bash <<'EOF'\ngit reset --hard\nEOF",
    ]
    SAFE = [
        "git status",
        "git push origin main",
        "git push -u origin feature",
        "git push --dry-run --force origin main",
        "git reset --soft HEAD~1",
        "git reset HEAD src/app.ts",
        "git clean -n",
        "git clean -fdn",
        "git branch -d merged-feature",
        "git checkout main",
        "git checkout -b new-feature",
        "git restore --staged src/app.ts",
        "git stash",
        "git stash pop",
        "git log --oneline -5",
        'git commit -m "docs: explain why git reset --hard is dangerous"',
        'echo "git reset --hard"',
        "npm test",
        "ls -la",
        "git commit -m 'Guard `git push -f`'",
        "git commit -m \"$(cat <<'EOF'\nfeat: ask before `git reset --hard`\n\nhistory; git push --force now asks\nEOF\n)\"",
        "git checkout -bfix-login",
        "git switch -cfeature",
        "git checkout feature/login",
        "git filter-repo --analyze",
        "git push origin :",
        "git checkout main # .",
        "echo 'git reset --hard' | cat",
        "git prune --dry-run",
        "git checkout -",
        "cat <<'EOF' > notes.md\ngit reset --hard\nEOF",
        'git commit -m "first line\n\nsecond line mentions reset --hard"',
    ]

    def test_destructive_commands_ask_the_user(self):
        for command in self.DESTRUCTIVE:
            with self.subTest(command=command):
                out = bash(command)
                self.assertEqual(decision(out), "ask")
                reason = out["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertIn("Wolfin Senior", reason)

    def test_everyday_commands_pass_silently(self):
        for command in self.SAFE:
            with self.subTest(command=command):
                self.assertIsNone(bash(command))

    def test_reason_names_what_would_be_lost(self):
        reason = bash("git reset --hard")["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("uncommitted", reason)

    def test_can_be_turned_off(self):
        self.assertIsNone(bash("git push --force", WOLFIN_GIT_GUARD="off"))

    def test_ignores_other_tools_and_bad_input(self):
        self.assertIsNone(run_hook("git-guard.py", {"tool_name": "Edit", "tool_input": {"file_path": "a.py"}}))
        self.assertIsNone(run_hook("git-guard.py", {}))

    def test_checkout_of_an_existing_file_asks(self):
        with tempfile.TemporaryDirectory() as cwd:
            open(os.path.join(cwd, "app.ts"), "w").close()
            payload = {"tool_name": "Bash", "cwd": cwd, "tool_input": {"command": "git checkout app.ts"}}
            self.assertEqual(decision(run_hook("git-guard.py", payload)), "ask")
            payload["tool_input"]["command"] = "git checkout main"
            self.assertIsNone(run_hook("git-guard.py", payload))

    def test_unbalanced_quotes_still_checked(self):
        self.assertEqual(decision(bash("git reset --hard && echo 'oops")), "ask")


def write_transcript(entries):
    fh = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    with fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")
    return fh.name


def prompt(text="do it", ts=None):
    stamp = ts or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {"type": "user", "timestamp": stamp, "message": {"role": "user", "content": text}}


def tool(name, **tool_input):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": uuid.uuid4().hex, "name": name, "input": tool_input}]}}


class CodeGate(unittest.TestCase):
    def gate(self, path, transcript_entries, **env):
        transcript = write_transcript(transcript_entries)
        payload = {"session_id": uuid.uuid4().hex, "transcript_path": transcript,
                   "tool_name": "Write", "tool_input": {"file_path": path}}
        return run_hook("code-gate.py", payload, env=env), payload

    def test_code_edit_refused_until_both_skills_loaded(self):
        out, _ = self.gate("/proj/app.py", [prompt()])
        self.assertEqual(decision(out), "deny")
        reason = out["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("docs-first", reason)
        self.assertIn("test-driven-development", reason)

    def test_names_only_the_missing_skill(self):
        out, _ = self.gate("/proj/app.py", [prompt(), tool("Skill", skill="wolfin-senior:docs-first")])
        reason = out["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertNotIn("docs-first,", reason)
        self.assertIn("test-driven-development", reason)

    def test_allowed_once_skills_are_loaded(self):
        out, _ = self.gate("/proj/app.ts", [prompt(), tool("Skill", skill="wolfin-senior:docs-first"),
                                           tool("Skill", skill="wolfin-senior:test-driven-development")])
        self.assertIsNone(out)

    def test_non_code_files_and_memory_are_never_gated(self):
        self.assertIsNone(self.gate("/proj/README.md", [prompt()])[0])
        self.assertIsNone(self.gate("/proj/.wolfin-senior/memory/x.py", [prompt()])[0])

    def test_stops_refusing_after_three_refusals(self):
        transcript = write_transcript([prompt()])
        payload = {"session_id": uuid.uuid4().hex, "transcript_path": transcript,
                   "tool_name": "Edit", "tool_input": {"file_path": "/proj/app.go"}}
        outs = [run_hook("code-gate.py", payload) for _ in range(4)]
        self.assertEqual([decision(o) for o in outs], ["deny", "deny", "deny", None])

    def test_can_be_turned_off(self):
        self.assertIsNone(self.gate("/proj/app.py", [prompt()], WOLFIN_CODE_GATE="off")[0])

    def test_scratch_files_outside_the_project_are_not_gated(self):
        with tempfile.TemporaryDirectory() as proj, tempfile.TemporaryDirectory() as scratch:
            transcript = write_transcript([prompt()])
            base = {"session_id": uuid.uuid4().hex, "transcript_path": transcript, "cwd": proj, "tool_name": "Write"}
            outside = dict(base, tool_input={"file_path": os.path.join(scratch, "repro.mjs")})
            inside = dict(base, tool_input={"file_path": os.path.join(proj, "src", "app.mjs")})
            self.assertIsNone(run_hook("code-gate.py", outside, env={"CLAUDE_PROJECT_DIR": proj}))
            self.assertEqual(decision(run_hook("code-gate.py", inside, env={"CLAUDE_PROJECT_DIR": proj})), "deny")


def load(script):
    import importlib.util
    spec = importlib.util.spec_from_file_location(script.replace("-", "_"), os.path.join(HOOKS, script))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProjectBoundary(unittest.TestCase):
    """Only throwaway files in a temp folder outside the project escape the gates."""

    def test_inside_handles_symlinks_slashes_and_case(self):
        for script in ("code-gate.py", "stop-gate.py"):
            mod = load(script)
            with self.subTest(script=script), tempfile.TemporaryDirectory() as base:
                proj, ext = os.path.join(base, "proj"), os.path.join(base, "ext")
                os.makedirs(proj); os.makedirs(ext)
                os.symlink(ext, os.path.join(proj, "lib"))
                self.assertTrue(mod.inside(os.path.join(proj, "lib", "x.py"), proj))
                self.assertTrue(mod.inside(os.path.join(proj, "a.py"), proj + "/"))
                self.assertTrue(mod.inside(proj, proj))
                self.assertTrue(mod.inside("relative/a.py", proj))
                self.assertFalse(mod.inside(os.path.join(base, "other", "a.py"), proj))
                if sys.platform == "darwin":
                    self.assertTrue(mod.inside(os.path.join(proj.upper(), "A.PY"), proj))

    def test_files_outside_the_project_but_not_in_a_temp_folder_stay_gated(self):
        with tempfile.TemporaryDirectory() as proj:
            payload = {"session_id": uuid.uuid4().hex, "transcript_path": write_transcript([prompt()]),
                       "cwd": proj, "tool_name": "Write", "tool_input": {"file_path": "/srv/other-repo/app.py"}}
            self.assertEqual(decision(run_hook("code-gate.py", payload, env={"CLAUDE_PROJECT_DIR": proj})), "deny")


class StopGate(unittest.TestCase):
    def stop(self, entries, cwd, **env):
        payload = {"transcript_path": write_transcript(entries), "cwd": cwd, "stop_hook_active": False}
        env.setdefault("CLAUDE_PROJECT_DIR", cwd)
        return run_hook("stop-gate.py", payload, env=env)

    def test_unverified_code_change_is_held_once(self):
        with tempfile.TemporaryDirectory() as cwd:
            out = self.stop([prompt(), tool("Edit", file_path=f"{cwd}/app.py")], cwd, WOLFIN_MEMORY_GATE="off")
            self.assertEqual(out["decision"], "block")
            self.assertIn("Verify", out["reason"])

    def test_test_run_after_last_edit_counts_as_verified(self):
        with tempfile.TemporaryDirectory() as cwd:
            entries = [prompt(), tool("Edit", file_path=f"{cwd}/app.py"), tool("Bash", command="python3 -m pytest -q")]
            self.assertIsNone(self.stop(entries, cwd, WOLFIN_MEMORY_GATE="off"))

    def test_work_without_a_log_entry_asks_for_one(self):
        with tempfile.TemporaryDirectory() as cwd:
            out = self.stop([prompt(), tool("Write", file_path=f"{cwd}/notes.md")], cwd)
            self.assertIn("Log", out["reason"])

    def test_log_written_this_turn_satisfies_it(self):
        with tempfile.TemporaryDirectory() as cwd:
            earlier = datetime.fromtimestamp(time.time() - 60, timezone.utc).isoformat().replace("+00:00", "Z")
            mem = os.path.join(cwd, ".wolfin-senior", "memory")
            os.makedirs(mem)
            with open(os.path.join(mem, "NOW.md"), "w", encoding="utf-8") as fh:
                fh.write("# Now\n")
            self.assertIsNone(self.stop([prompt(ts=earlier), tool("Write", file_path=f"{cwd}/notes.md")], cwd))

    def test_never_blocks_twice(self):
        with tempfile.TemporaryDirectory() as cwd:
            payload = {"transcript_path": write_transcript([prompt(), tool("Edit", file_path=f"{cwd}/a.py")]),
                       "cwd": cwd, "stop_hook_active": True}
            self.assertIsNone(run_hook("stop-gate.py", payload, env={"CLAUDE_PROJECT_DIR": cwd}))

    def test_scratch_files_outside_the_project_dont_count_as_work(self):
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as scratch:
            entries = [prompt(), tool("Write", file_path=os.path.join(scratch, "repro.mjs"))]
            self.assertIsNone(self.stop(entries, cwd))

    def test_reading_only_turn_passes(self):
        with tempfile.TemporaryDirectory() as cwd:
            self.assertIsNone(self.stop([prompt(), tool("Read", file_path=f"{cwd}/a.py")], cwd))


class ContextHooks(unittest.TestCase):
    def test_session_start_injects_router_and_memory_paths(self):
        with tempfile.TemporaryDirectory() as cwd:
            out = run_hook("session-start", env={"CLAUDE_PROJECT_DIR": cwd}, cwd=cwd)
            context = out["hookSpecificOutput"]["additionalContext"]
            self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
            self.assertIn("# Using Wolfin Senior", context)
            self.assertIn(os.path.join(cwd, ".wolfin-senior", "memory"), context)

    def test_session_start_includes_now_md(self):
        with tempfile.TemporaryDirectory() as cwd:
            mem = os.path.join(cwd, ".wolfin-senior", "memory")
            os.makedirs(mem)
            with open(os.path.join(mem, "NOW.md"), "w", encoding="utf-8") as fh:
                fh.write('# Now\nNext: ship "v2" \\ tab\there\n')
            out = run_hook("session-start", env={"CLAUDE_PROJECT_DIR": cwd}, cwd=cwd)
            self.assertIn('Next: ship "v2"', out["hookSpecificOutput"]["additionalContext"])

    def test_prompt_reminder_and_its_switch(self):
        out = run_hook("prompt-reminder")
        self.assertIn("Wolfin Senior (strict)", out["hookSpecificOutput"]["additionalContext"])
        self.assertIsNone(run_hook("prompt-reminder", env={"WOLFIN_REMINDER": "off"}))


class HooksConfig(unittest.TestCase):
    def test_every_hook_command_points_at_an_existing_script(self):
        with open(os.path.join(HOOKS, "hooks.json"), encoding="utf-8") as fh:
            config = json.load(fh)["hooks"]
        scripts = []
        for groups in config.values():
            for group in groups:
                for hook in group["hooks"]:
                    command = hook["command"]
                    start = command.index("${CLAUDE_PLUGIN_ROOT}/") + len("${CLAUDE_PLUGIN_ROOT}/")
                    scripts.append(command[start:].split('"')[0])
        self.assertIn("hooks/git-guard.py", scripts)
        for script in scripts:
            with self.subTest(script=script):
                path = os.path.join(ROOT, script)
                self.assertTrue(os.path.isfile(path))
                if not script.endswith(".py"):
                    self.assertTrue(os.access(path, os.X_OK))


if __name__ == "__main__":
    unittest.main()
