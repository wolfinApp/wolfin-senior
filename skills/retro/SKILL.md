---
name: retro
description: Look back at this session and suggest changes to the environment (automated checks, coding standards, navigation pointers, tooling) so the same mistakes can't happen again.
disable-model-invocation: true
argument-hint: "[session or topic to look back on]"
---

# Retro

Look back at this session (or the one named here: $ARGUMENTS) and suggest
improvements to the **environment** the agent works in, not to the code.
The next build should start from a better place.

## 1. Gather the evidence

Read this session's journal entries in the project memory, the commits, and
the review findings. Note every wrong turn: a bug found late, a check that
failed, a file that took long to find, a step that was repeated, a
correction from the user.

## 2. Find the improvement for each

| Category | Look for | Typical fix |
|---|---|---|
| **Automated checks** | A mistake a tool could have caught. A repo with no pre-commit hook and no CI running lint, types and tests is itself a finding | A lint rule, a type, a test, a pre-commit hook or a CI job. Check first whether one exists but isn't wired up |
| **Coding standards** | The review missed a judgement call | One line in `CODING_STANDARDS.md` or `CONTRIBUTING.md`. Mechanical rules become checks, not prose |
| **Navigation** | Time spent finding a file or learning a hidden dependency | One pointer line in `CLAUDE.md` or `AGENTS.md`, or a `GLOSSARY.md` term |
| **Steering files** | Instructions in `CLAUDE.md` that are long, stale, or change nothing | Move them to standards or checks, or delete them |
| **Information access** | A fact the agent needed but couldn't get (logs, a service, docs) | Tee the dev server logs to a file, give read-only access, add a doc pointer |
| **Tool economy** | Expensive or repeated tool calls | A script, an alias, or a narrower command |
| **Memory** | Something re-learned that should have been remembered | A `lesson` or `feedback` memory (`project-memory`) |

Prefer a deterministic check over a written rule whenever the mistake is
mechanical. Keep `CLAUDE.md` short: every line there is read on every turn.

## 3. Report, most severe first

For each suggestion: what went wrong (with the evidence), the change, where
it goes, and how much effort it is. Make no changes until the user picks
which ones to apply.
