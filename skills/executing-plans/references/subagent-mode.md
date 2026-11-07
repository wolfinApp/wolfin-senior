# Subagent-Driven Mode

A fresh implementer subagent per task, a fresh reviewer per task, and one
whole-branch review at the end. You are the **controller**: you coordinate,
keep the ledger, and judge. You don't write the code yourself, so your
context stays clean for coordination and every change gets an independent
review.

Everything in the main skill still applies: the ground rules, the ledger,
the pre-flight scan, the final review and the finish.

## Model selection

Use the least powerful model that can do each role well, and **always name
the model explicitly** when dispatching. An omitted model inherits the
session's, which is often the most expensive.

| Role | Model tier |
|---|---|
| Implementer, mechanical task (1–2 files, complete spec, plan contains the code) | Fast / cheap |
| Implementer, integration (several files, judgment, pattern matching) | Standard |
| Implementer, design-heavy task | Most capable |
| Task reviewer | Standard as the floor. Most capable for subtle concurrency, security or data changes |
| Fix rounds 4–5 | At least one tier above the implementer that got stuck |
| Final whole-branch review | Most capable |

Turn count beats token price. Cheap models often take 2–3× the turns on
multi-step work, so use mid-tier as the floor whenever the implementer works
from prose rather than transcribing code.

## Per-task loop

1. **Record BASE** = `git rev-parse HEAD`.
2. **Write the task brief to a file:** copy the task's full text from the plan
   into `.wolfin-senior/plans/<plan>/task-N-brief.md`. The brief is the single
   source of requirements. Never make a subagent read the whole plan.
3. **Dispatch the implementer** with `implementer-prompt.md` (in this
   directory). The dispatch contains: one line on where the task fits, the
   brief path ("read this first, it is your requirements"), interfaces and
   rulings from earlier tasks it can't know, your resolution of any
   ambiguity you noticed, and the report path
   `.wolfin-senior/plans/<plan>/task-N-report.md`. Don't paste accumulated history
   from earlier tasks. A fresh subagent needs its task, the interfaces it
   touches, and the global constraints. Nothing else.
4. **Handle the status:**
   - **DONE:** go to review.
   - **DONE_WITH_CONCERNS:** read the concerns. If they're about correctness or scope, resolve them before review.
   - **NEEDS_CONTEXT:** provide the missing context and re-dispatch.
   - **BLOCKED:** change something before retrying: more context, a more
     capable model, a smaller task, or a ruling that fixes the plan. Never
     re-send the same task unchanged to the same model.
5. **Dispatch the task reviewer** with `task-reviewer-prompt.md` (in this
   directory), giving it the brief path, the report path, a diff file
   (`git log --oneline BASE..HEAD; git diff --stat BASE..HEAD; git diff -U10 BASE..HEAD`
   written to `.wolfin-senior/plans/<plan>/task-N-diff.txt`), and the global
   constraints verbatim. Use the BASE you recorded, never `HEAD~1`, which
   silently drops all but the last commit of a multi-commit task.
   Don't pre-judge findings ("don't flag X", "at most Minor"). If you're
   tempted to, you're trying to skip a review loop.
6. **Fix loop** when the review reports spec ❌ or any Critical/Important finding:
   - Minor findings go straight to the ledger as `Task N: minor (deferred): ...` and never enter the loop.
   - **Rounds 1–3:** send the open findings verbatim to the original
     implementer (resume it if your harness supports that, otherwise give a
     fresh one the brief, report and findings). It fixes, re-runs the
     covering tests, and appends a fix report.
   - **Rounds 4–5:** a fresh implementer on a more capable model: "A prior
     implementer attempted this N times; you own it now. Read the report
     file for what was tried."
   - Every round ends with a **scoped re-review** of the fix diff only:
     each finding gets ADDRESSED or NOT ADDRESSED, plus any new breakage
     *in the fix*.
   - Ledger each round: `Task N: fix round R/5 (X addressed, Y open — ...)`.
   - **Breaker:** after round 5, adjudicate the open findings yourself. Park
     the contestable ones with a ruling. For anything real and load-bearing,
     rule on the smallest unblocking change and carry it into the next task.
     Every adjudication is a ledger line. A silent discard is forbidden.
7. **Complete:** `Task N: complete (commits <base7>..<head7>, review clean)`.

Never dispatch two implementers in parallel on the same branch, because
they'll conflict. Implementers and reviewers never dispatch subagents of
their own. The review seats you dispatch are the only ones.

## Waiting

While subagents run and you have local work (ledger updates, the next
brief), keep working. When idle, wait in bounded stretches. Between
stretches, post one line of status and check for children that finished
without reporting.

## Rationalizations

| Excuse | Reality |
|---|---|
| "I'll fix it myself, dispatching is overhead" | Controller fixes pollute your context and skip review. |
| "Close enough on spec compliance" | A spec gap means not done. Fix it, or hit the cap and adjudicate. |
| "One more round will converge" | Past the cap, the failure is structural. Adjudicate. |
| "The fix was tiny, skip the re-review" | Unreviewed fixes are how regressions land. |
