#!/usr/bin/env python3
"""PreToolUse hook (Bash): ask the user before a git command that destroys work.

Commands that throw away uncommitted changes, rewrite or delete published
history, or erase the safety nets git keeps (stash, reflog) are not blocked:
Claude Code shows the user a permission prompt with what would be lost, and
the command runs only if they approve it. In a non-interactive run nobody can
approve, so the command is refused and Claude reads the reason.

Everyday git (status, commit, push without force, checkout of a branch,
reset --soft, clean -n, branch -d, restore --staged) passes silently.
Turn it off with WOLFIN_GIT_GUARD=off.
"""

import json
import os
import re
import shlex
import sys

SEPARATORS = set(";&|()\n")
GLOBAL_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
KEYWORDS = {"do", "then", "else", "elif", "if", "while", "until", "{", "}", "!", "time"}
# launcher -> (its options that take a value, positional args to skip before the command)
WRAPPERS = {
    "sudo": ({"-u", "-g", "-C", "-D", "-h", "-p", "-r", "-t", "-U", "-T"}, 0),
    "env": ({"-u", "-S", "-C", "--unset", "--chdir"}, 0),
    "timeout": ({"-s", "-k", "--signal", "--kill-after"}, 1),
    "nice": ({"-n", "--adjustment"}, 0),
    "xargs": ({"-I", "-n", "-P", "-L", "-d", "-E", "-s", "-a"}, 0),
    "stdbuf": ({"-i", "-o", "-e"}, 0),
    "nohup": (set(), 0), "command": (set(), 0), "exec": (set(), 0), "caffeinate": (set(), 0),
}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}


def short_flags(args, takes_value=""):
    """Letters in short option clusters, e.g. ['-xdf', '-u'] -> {'x', 'd', 'f', 'u'}.

    A letter in takes_value ends the cluster: in `-bfix-login` the rest is b's value.
    """
    letters = set()
    for arg in args:
        if arg.startswith("-") and not arg.startswith("--") and len(arg) > 1:
            for letter in arg[1:]:
                letters.add(letter)
                if letter in takes_value:
                    break
    return letters


def positionals(args, value_opts=()):
    """Arguments that aren't options or option values."""
    out, skip = [], False
    for arg in args:
        if skip:
            skip = False
        elif arg in value_opts:
            skip = True
        elif arg == "--" or not arg.startswith("-"):
            out.append(arg)
    return out


def has(args, *names):
    return any(a == n or a.startswith(n + "=") for a in args for n in names)


def check_push(args):
    if has(args, "--dry-run") or "n" in short_flags(args):
        return None
    flags = short_flags(args, "o")
    if has(args, "--force", "--force-with-lease", "--force-if-includes") or "f" in flags:
        return "force-pushes, which overwrites history on the remote that others may have pulled"
    if has(args, "--mirror"):
        return "mirrors the repository, which deletes remote branches and tags that don't exist locally"
    if has(args, "--delete", "--prune") or "d" in flags:
        return "deletes branches or tags on the remote"
    refspecs = [a for a in args if not a.startswith("-")][1:]
    if any(r.startswith("+") for r in refspecs):
        return "force-pushes a refspec (+), which overwrites history on the remote"
    if any(r.startswith(":") and len(r) > 1 for r in refspecs):
        return "deletes a branch on the remote (:branch)"
    return None


def check_reset(args):
    if has(args, "--hard"):
        return "throws away all uncommitted changes in tracked files, and they can't be recovered"
    return None


def check_clean(args):
    if has(args, "--dry-run") or "n" in short_flags(args, "e"):
        return None
    if has(args, "--force") or "f" in short_flags(args, "e"):
        return "permanently deletes untracked files (they were never committed, so git can't bring them back)"
    return None


def check_branch(args):
    flags = short_flags(args, "u")
    if "D" in flags or ((has(args, "--delete") or "d" in flags) and (has(args, "--force") or "f" in flags)):
        return "force-deletes a branch even if its commits were never merged"
    return None


def check_checkout(args, cwd=None):
    flags = short_flags(args, "bB")
    if has(args, "--force") or "f" in flags:
        return "switches with --force, which throws away uncommitted changes"
    if "--" in args and args.index("--") < len(args) - 1:
        return "overwrites files with the committed version, which throws away their uncommitted changes"
    if flags & {"b", "B"} or has(args, "--orphan"):
        return None
    paths = positionals(args, {"--conflict", "--pathspec-from-file"})
    if "." in paths:
        return "overwrites every file with the committed version, which throws away all uncommitted changes"
    if len(paths) >= 2:
        return "overwrites files with the version from another commit, which throws away their uncommitted changes"
    if len(paths) == 1:
        target = paths[0]
        if target.startswith(("./", "../", "/")) or (cwd and os.path.exists(os.path.join(cwd, target))):
            return "overwrites a file with the committed version, which throws away its uncommitted changes"
    return None


def check_restore(args):
    flags = short_flags(args, "s")
    staged = has(args, "--staged") or "S" in flags
    worktree = has(args, "--worktree") or "W" in flags
    paths = positionals(args, {"-s", "--source"})
    if paths and (worktree or not staged):
        return "restores files in the working tree, which throws away their uncommitted changes"
    return None


def check_switch(args):
    if has(args, "--discard-changes", "--force") or "f" in short_flags(args, "cC"):
        return "switches branch and throws away uncommitted changes"
    return None


def check_stash(args):
    args = [a for a in args if not a.startswith("-")]
    if args[:1] == ["drop"]:
        return "drops a stash entry, which deletes the work saved in it"
    if args[:1] == ["clear"]:
        return "deletes every stash entry and the work saved in them"
    return None


def check_reflog(args):
    if args[:1] in (["expire"], ["delete"]):
        return "erases reflog entries, the safety net used to recover lost commits"
    return None


def check_gc(args):
    if any(a in ("--prune=now", "--prune=all") or a.startswith("--prune=0") for a in args):
        return "prunes unreachable objects now, which destroys commits that could still be recovered"
    return None


def check_prune(args):
    if has(args, "--dry-run") or "n" in short_flags(args):
        return None
    return "deletes every unreachable object now, which destroys commits that could still be recovered"


def check_update_ref(args):
    if "-d" in args or has(args, "--delete"):
        return "deletes a ref directly, bypassing git's safety checks"
    return None


def check_worktree(args):
    if args[:1] == ["remove"] and (has(args, "--force") or "f" in short_flags(args[1:])):
        return "force-removes a worktree, including its uncommitted changes"
    return None


def rewrite_history(args):
    if has(args, "--analyze", "--help"):
        return None
    return "rewrites the whole history of the repository"


CHECKS = {
    "push": check_push, "reset": check_reset, "clean": check_clean, "branch": check_branch,
    "checkout": check_checkout, "restore": check_restore, "switch": check_switch,
    "stash": check_stash, "reflog": check_reflog, "gc": check_gc, "prune": check_prune,
    "update-ref": check_update_ref,
    "worktree": check_worktree, "filter-branch": rewrite_history, "filter-repo": rewrite_history,
}


HEREDOC = re.compile(r"<<-?[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
SHELL_STDIN = re.compile(r"(?:^|[;&|(]\s*)(?:sudo\s+)?(?:\S*/)?(?:ba|z|da|k)?sh(?:\s+-\S+)*\s*<<")


def split_views(command):
    """Two views of a command line, read the way the shell reads it.

    code: comments removed, heredoc bodies removed (they are data, not commands)
    unless the heredoc feeds a shell, whose body is a script that runs.
    expanding: text whose $(...) and `...` the shell would run: single-quoted
    strings and quoted heredoc bodies removed, unquoted heredoc bodies kept.
    """
    lines, code_lines, extra, pending = command.split("\n"), [], [], []
    for line in lines:
        if pending:
            delim, quoted, script = pending[0]
            if line.lstrip("\t") == delim:
                pending.pop(0)
            elif script:
                code_lines.append(line)  # a heredoc fed to a shell is a script that runs
            elif not quoted:
                extra.append(line)
            continue
        code_lines.append(line)
        script = bool(SHELL_STDIN.search(line))
        pending.extend((m.group(2), bool(m.group(1)), script) for m in HEREDOC.finditer(line))
    code = "\n".join(code_lines)

    out_code, out_exp, quote, i = [], [], None, 0
    while i < len(code):
        ch = code[i]
        if quote is None and ch == "#" and (i == 0 or code[i - 1] in " \t\n;&|()"):
            while i < len(code) and code[i] != "\n":
                i += 1
            continue
        if ch == "\\" and quote != "'" and i + 1 < len(code):
            out_code.append(code[i:i + 2]); out_exp.append(code[i:i + 2]); i += 2
            continue
        if quote is None and ch in "'\"":
            quote = ch
        elif quote == ch:
            quote = None
            out_code.append(ch); i += 1
            continue
        out_code.append(ch)
        if quote != "'" and not (quote is None and ch == "'"):
            out_exp.append(ch)
        i += 1
    return "".join(out_code), "".join(out_exp) + "\n" + "\n".join(extra)


def tokenize(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def segments(tokens):
    current = []
    for token in tokens:
        if token and set(token) <= SEPARATORS:
            if current:
                yield current
            current = []
        else:
            current.append(token)
    if current:
        yield current


def unwrap(words):
    """Index of the real command in a simple command: skips assignments, keywords and launchers."""
    i = 0
    while i < len(words):
        word = os.path.basename(words[i])
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[i]) or words[i] in KEYWORDS:
            i += 1
        elif word in WRAPPERS:
            value_opts, skip_positional = WRAPPERS[word]
            i += 1
            while i < len(words) and words[i].startswith("-"):
                if words[i] == "--":
                    i += 1
                    break
                i += 2 if words[i] in value_opts else 1
            while i < len(words) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[i]):
                i += 1
            i += skip_positional
        else:
            return i
    return i


def git_call(words):
    """(subcommand, args) if this simple command runs git, else None."""
    i = unwrap(words)
    if i >= len(words):
        return None
    name = os.path.basename(words[i])
    if name.startswith("git-") and name[4:] in CHECKS:
        return name[4:], words[i + 1:]
    if name != "git":
        return None
    i += 1
    while i < len(words) and words[i].startswith("-"):
        option = words[i]
        i += 2 if option in GLOBAL_OPTS_WITH_VALUE else 1
    if i >= len(words):
        return None
    return words[i], words[i + 1:]


def inner_scripts(words):
    """Command strings run by `bash -c '...'` or `eval ...`."""
    i = unwrap(words)
    if i >= len(words):
        return []
    name = os.path.basename(words[i])
    if name == "eval":
        return [" ".join(words[i + 1:])]
    if name in SHELLS:
        for j in range(i + 1, len(words) - 1):
            arg = words[j]
            if arg.startswith("-") and not arg.startswith("--") and "c" in arg[1:]:
                return [words[j + 1]]
    return []


def substitutions(text):
    """Commands inside $(...) and backticks, which also run."""
    return re.findall(r"\$\(([^()]*)\)", text) + re.findall(r"`([^`]*)`", text)


def dangers(command, cwd=None, depth=0):
    found = []
    code, expanding = split_views(command)
    try:
        tokens = tokenize(code)
    except ValueError:  # unbalanced quotes: check what can still be read
        tokens = code.replace("'", " ").replace('"', " ").split()
        tokens = [t for part in tokens for t in re.split(r"(&&|\|\||;|\|)", part) if t]
    for words in segments(tokens):
        call = git_call(words)
        if call and call[0] in CHECKS:
            check = CHECKS[call[0]]
            why = check(call[1], cwd) if check is check_checkout else check(call[1])
            if why:
                found.append((" ".join(["git", call[0], *call[1]]), why))
        if depth < 3:
            for script in inner_scripts(words):
                found.extend(dangers(script, cwd, depth + 1))
    if depth < 3:
        for inner in substitutions(expanding):
            found.extend(dangers(inner, cwd, depth + 1))
    return found


def main():
    if os.environ.get("WOLFIN_GIT_GUARD", "").strip().lower() in {"off", "0", "false", "no"}:
        return
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    if data.get("tool_name") != "Bash":
        return
    command = str((data.get("tool_input") or {}).get("command") or "")
    if "git" not in command:
        return
    found = dangers(command, data.get("cwd"))
    if not found:
        return
    lines = "; ".join(f"`{cmd}` {why}" for cmd, why in found)
    reason = (f"Wolfin Senior git guard: {lines}. Approve only if you meant to lose this. "
              "Safer: commit or stash first, or use a branch you can delete later.")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": reason,
    }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a broken guard must never block the shell
        pass
