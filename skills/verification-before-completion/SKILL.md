---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, passing, working, or faster — before saying "done", committing, opening a PR, or moving to the next task. Requires running the verification command fresh and reading its output before any success claim; evidence before assertions. Applies to tests, builds, lint, bug fixes, UI changes, performance claims, and agent reports. Triggers on "خلص؟", "اشتغل؟", "تمام؟".
---

# Verification Before Completion

**Principle:** evidence before claims, always.

A claim of success without fresh evidence isn't optimism. It's a false
statement the user will act on. They'll merge it, ship it, and build on it.

## The iron law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you can't
claim it passes.

## The gate

Before claiming any status, or expressing satisfaction:

1. **Identify:** what command or check proves this claim?
2. **Run:** the full command, fresh and complete.
3. **Read:** the full output. Check the exit code and count the failures.
4. **Compare:** does the output confirm the claim?
   - No: state the actual status, with the evidence.
   - Yes: state the claim, with the evidence.
5. **Only then** make the claim.

## What each claim requires

| Claim | Requires | Not sufficient |
|---|---|---|
| Tests pass | Test command output: 0 failures | An earlier run, "should pass" |
| Linter clean | Linter output: 0 errors | A partial check |
| Build succeeds | Build command: exit 0 | Linter passing, "logs look fine" |
| Bug fixed | The original symptom, re-tested: gone | "Code changed, so it's fixed" |
| Regression test works | Red-green cycle: passes, fails with the fix reverted, passes again | Passing once |
| UI change works | The app run and the screen actually seen (screenshot or browser check) | "The component compiles" |
| It's faster | Before/after numbers, same conditions, several runs | "This should be faster" |
| Agent finished the task | The diff inspected and tests run by you | The agent's "success" report |
| Requirements met | The spec re-read and checked line by line | "Tests pass" |

## Red flags: stop

- Words like "should", "probably", "seems to", "looks correct"
- Celebrating before checking ("Done!", "Perfect!", "Works now!")
- About to commit, push or open a PR without a fresh run
- Trusting a subagent's or tool's success report
- Partial verification ("the one test I wrote passes")
- "Just this once" or "I'm confident"

## Patterns

```
✅ [ran: npm test] [saw: 34/34 passed, exit 0] → "All 34 tests pass."
❌ "Tests should pass now."

✅ [ran: npm run build] [saw: exit 0] → "Build succeeds."
❌ "Linter passed, so the build is fine."

✅ re-read plan → checklist → verify each item → "8/9 done; item 6 (CSV export) is missing."
❌ "Tests pass, phase complete."
```

## When you can't verify

Say so explicitly: what you couldn't check, why, and exactly how the user can
check it (the command, the URL, the steps). An honest "not verified" is
worth more than a confident guess.

## The stop check

With the plugin's hooks installed, a turn that changed code after the last
test, build or run command is stopped once at the end and asked to verify.
Run the check and read the output, or state exactly why it can't run. Don't
end with an unverified claim.

## Scope

This applies to exact phrases and to paraphrases, to implications of
success, and to every message that suggests the work is correct: final
summaries, commit messages, PR descriptions, and updates to the user.
