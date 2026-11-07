---
name: systematic-debugging
description: Use when encountering any bug, error, crash, failing or flaky test, build failure, unexpected behavior, or production incident, before proposing any fix — finds the root cause through evidence (reproduce, trace, compare, hypothesize, test one change at a time) instead of guessing. Use especially under time pressure or after a fix already failed. Triggers on "it's broken", "not working", "error", "it crashed", "fix it".
---

# Systematic Debugging

Find the root cause before attempting a fix. A symptom fix is a failure that
hasn't happened yet (rule 3).

## The iron law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Until Phase 1 is done, you may not propose a fix.

Use this especially when it feels unnecessary: under time pressure, when the
fix "seems obvious", when a previous fix didn't work. Systematic debugging
is faster than guess-and-check thrashing, every time.

## Phase 1: Root cause investigation

1. **Read the error completely.** Read the whole stack trace, the line
   numbers, the error codes and the warnings above it. The answer is often
   right there.
2. **Reproduce it reliably.** Get the exact steps, and check whether it
   happens every time. If you can't reproduce it, gather more data, but
   don't guess.
3. **Check what changed:** `git diff`, `git log`, new dependencies,
   config, environment, data. `git bisect` finds the breaking commit
   mechanically when the history is long.
4. **Instrument the boundaries in multi-component systems** (UI → API →
   service → DB, CI → build → deploy). Before fixing anything, log what
   enters and leaves each component, and check that config and env vars
   propagate. Run once, see *where* it breaks, then investigate that
   component.
5. **Trace the data backwards.** When the error surfaces deep in the call
   stack, find where the bad value originated: what called this with it,
   and what called that. Fix at the source, not where it surfaced. Full
   technique: `references/root-cause-tracing.md`.

## Phase 2: Pattern analysis

1. **Find working examples** of similar code in the same codebase.
2. **Read the reference implementation completely** if you're following a
   pattern or library. Don't skim.
3. **List every difference** between the working and broken versions,
   however small. Don't assume "that can't matter".
4. **Know the dependencies:** config, environment, versions, and the
   assumptions the code makes. Check the docs and changelog for the version
   actually installed (`docs-first`). Many "bugs" are a behavior change
   between versions, or an API used as it worked in an older release.

## Phase 3: Hypothesis and test

1. **One hypothesis, written down:** "I think X is the root cause because Y."
2. **Test it minimally:** the smallest possible change, one variable at a time.
3. **Did it confirm?** If yes, go to Phase 4. If no, form a *new* hypothesis.
   Don't stack fixes on top of each other.
4. **Don't know?** Say "I don't understand X yet." Research, add
   instrumentation, or ask. Pretending is the expensive path (rule 18).

## Phase 4: Fix

1. **Write a failing test that reproduces the bug** (`test-driven-development`).
   Use an automated test if at all possible, otherwise a minimal repro script.
2. **One fix, at the root cause.** No "while I'm here" refactors bundled in.
3. **Verify:** the new test passes, the full suite passes, and the original
   symptom is gone (`verification-before-completion`).
4. **Consider defense in depth.** Once the cause is fixed, ask whether the
   bad value should also be stopped at other layers, so this class of bug
   becomes impossible rather than merely fixed: `references/defense-in-depth.md`.
5. **Remember it** (`project-memory`): log the root cause and the fix in the
   journal. If the cause was non-obvious (an environment quirk, a library
   gotcha, a misleading error), save it as a `lesson` memory, so the next
   session recognizes it in minutes instead of hours. Log failed hypotheses
   too, so they aren't retried after a compaction.

### If the fix didn't work

Stop and count your attempts.
- **Fewer than 3:** go back to Phase 1 with what you just learned.
- **3 or more: stop fixing and question the architecture.** The signs: each
  fix reveals a new problem somewhere else, fixes need "massive
  refactoring", or every fix creates new symptoms. That isn't a failed
  hypothesis, it's a wrong design. Discuss it with the user before
  attempt #4.

## Special cases

- **Flaky or timing-dependent tests:** replace arbitrary sleeps with
  condition-based waiting. See `references/condition-based-waiting.md`.
- **Test pollution** (a test passes alone, fails in the suite): bisect the
  test order to find the polluter, which is the test that leaves shared
  state behind.
- **Performance problems** ("it's slow"): the same discipline, but the
  evidence is measurement. Use `performance-optimization`. Profile before
  touching code.
- **Several independent failures:** investigate in parallel, one agent per
  domain (`../executing-plans/references/parallel-agents.md`), but only
  once you're sure they're unrelated.
- **Truly environmental or external** (a third-party outage, hardware):
  document what you investigated, add appropriate handling (timeout, retry,
  a clear error message), and add logging so next time is faster. But 95% of
  "no root cause" cases are incomplete investigations.

## Red flags: stop and return to Phase 1

- "Quick fix for now, investigate later"
- "Let me just try changing X"
- Several changes at once, then "run the tests"
- "It's probably X" without evidence
- Proposing fixes before tracing the data flow
- "One more attempt" after two have already failed
- The user says "stop guessing", "is that actually happening?", "we're stuck?"

## Rationalizations

| Excuse | Reality |
|---|---|
| "Simple issue, no process needed" | Simple bugs have root causes too, and the process is fast on them. |
| "Emergency, no time" | Thrashing takes longer than investigating. |
| "Multiple fixes at once saves time" | You can't tell which one worked, and you add new bugs. |
| "I see the problem" | Seeing a symptom isn't understanding the cause. |
| "I'll write the test after the fix works" | Untested fixes don't stick. |

## Quick reference

| Phase | Do | Done when |
|---|---|---|
| 1. Root cause | Read errors, reproduce, check changes, instrument, trace | You know WHAT broke and WHY |
| 2. Pattern | Compare with working code and references | You know the difference |
| 3. Hypothesis | One theory, one minimal test | Confirmed, or a new theory |
| 4. Fix | Failing test → one fix → full verification | Bug gone, suite green |
