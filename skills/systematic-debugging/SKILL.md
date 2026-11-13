---
name: systematic-debugging
description: Use when encountering any bug, error, crash, failing or flaky test, build failure, unexpected behavior, or production incident, before proposing any fix — first builds one command that fails on this exact bug, shrinks the repro, then finds the root cause through evidence (ranked falsifiable hypotheses, one change at a time) instead of guessing, and fixes it with a regression test at the right seam. Use especially under time pressure or after a fix already failed. Triggers on "it's broken", "not working", "error", "it crashed", "fix it", "debug this".
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

**Redact as you go.** This skill has you show commands, output and captured
requests. Replace every secret with `<REDACTED>` before showing it, and
build loops that read credentials from environment variables.

## Phase 1: Root cause investigation

1. **Read the error completely.** Read the whole stack trace, the line
   numbers, the error codes and the warnings above it. The answer is often
   right there.
2. **Build a feedback loop that goes red.** This is the step everything
   else depends on. With one command that fails on *this* bug, you will find
   the cause; without one, no amount of reading code will. Ways to build
   it, roughly in order of preference:
   - a failing test at whatever seam reaches the bug (unit, integration, e2e)
   - a `curl` or HTTP script against the running dev server
   - the CLI with a fixture input, diffed against known-good output
   - a headless browser script that drives the UI and asserts on the DOM, console or network
   - a captured request, payload or event log replayed through the code path
   - a throwaway harness that calls the failing code path directly
   - a property or fuzz loop for "sometimes wrong" (1,000 random inputs)
   - a bisection script for `git bisect run`, when it broke between two known states
   - a differential run: the same input through the old and new version, outputs diffed

   **Tighten it:** make it faster (skip unrelated setup), sharper (assert
   the exact symptom, not "didn't crash") and deterministic (pin the time,
   seed randomness, isolate the file system, stub the network). For a flaky
   bug the goal is a higher reproduction rate: loop the trigger 100 times,
   run in parallel, add load, until it fails often enough to debug.

   **Done when** you can name one command, already run and its output shown,
   that drives the real code path, fails on the user's exact symptom, gives
   the same verdict every run, takes seconds, and needs no human. If you
   genuinely can't build one, stop and say so: list what you tried, and ask
   for access to an environment that reproduces it, a redacted artifact (a
   HAR file, logs, a recording with timestamps), or permission to add
   temporary instrumentation. No loop, no theories.
3. **Minimise.** Shrink the repro to the smallest case that still fails.
   Cut inputs, callers, config and steps one at a time, re-running the loop
   after each cut. Done when every remaining piece is load-bearing: remove
   any one and the loop goes green. A small repro leaves fewer suspects and
   becomes the regression test.
4. **Check what changed:** `git diff`, `git log`, new dependencies,
   config, environment, data. `git bisect` finds the breaking commit
   mechanically when the history is long.
5. **Instrument the boundaries in multi-component systems** (UI → API →
   service → DB, CI → build → deploy). Before fixing anything, log what
   enters and leaves each component, and check that config and env vars
   propagate. Run once, see *where* it breaks, then investigate that
   component.
6. **Trace the data backwards.** When the error surfaces deep in the call
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

1. **Rank three to five hypotheses before testing any.** One hypothesis
   anchors you on the first plausible idea. Each must be falsifiable, so
   write its prediction: "If X is the cause, then changing Y makes the bug
   disappear." A hypothesis without a prediction is a hunch: sharpen it or
   drop it.
2. **Show the ranked list to the user** before testing. They often know at a
   glance which one to drop ("we deployed a change to #3 yesterday"). Don't
   wait on it if they're away.
3. **Test the top one minimally:** one variable at a time, each probe tied to
   a prediction. Prefer a debugger or REPL; otherwise add targeted logs at
   the boundaries that tell the hypotheses apart, never "log everything and
   grep". **Tag every debug log** with one unique prefix (`[DEBUG-a4f2]`) so
   removing them later is a single grep.
4. **Did it confirm?** If yes, go to Phase 4. If no, cross it off and test
   the next. Don't stack fixes on top of each other.
5. **Don't know?** Say "I don't understand X yet." Research, add
   instrumentation, or ask. Pretending is the expensive path (rule 18).

## Phase 4: Fix

1. **Turn the minimised repro into a failing test** (`test-driven-development`)
   at the **right seam**: one where the test exercises the bug the way it
   actually happens at the call site. If the only available seam is too
   shallow to reproduce it (the bug needs several callers, the unit can't
   recreate the chain that triggered it), a test there gives false
   confidence. Say so: "no good seam" is itself a finding, and it belongs in
   `architecture-review`.
2. **One fix, at the root cause.** No "while I'm here" refactors bundled in.
3. **Verify:** the new test passes, the full suite passes, and the Phase 1
   loop, run against the original (not minimised) scenario, is green
   (`verification-before-completion`).
4. **Clean up before you say "fixed":**
   - [ ] every `[DEBUG-...]` log removed (grep the prefix)
   - [ ] throwaway harnesses and scripts deleted, or moved somewhere clearly marked
   - [ ] the confirmed hypothesis written in the commit message, so the next person learns it
5. **Consider defense in depth.** Once the cause is fixed, ask whether the
   bad value should also be stopped at other layers, so this class of bug
   becomes impossible rather than merely fixed: `references/defense-in-depth.md`.
6. **Remember it** (`project-memory`): log the root cause and the fix in the
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
- Reading code to build a theory before you have a command that goes red
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
| 1. Root cause | Read errors, build a red loop, minimise, check changes, instrument, trace | One command fails on this exact bug, and you know where |
| 2. Pattern | Compare with working code and references | You know the difference |
| 3. Hypothesis | 3–5 ranked, falsifiable theories; test the top one | One confirmed by its prediction |
| 4. Fix | Test at the right seam → one fix → full verification → cleanup | Loop green, suite green, debug logs gone |
