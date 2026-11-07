---
name: executing-plans
description: Use when executing a written implementation plan task by task — inline yourself, with a fresh subagent per task plus review gates, or with parallel agents for independent problems. Keeps a progress ledger that survives context compaction, enforces TDD and verification per task, and ends with a whole-branch review. Use whenever the user says "execute the plan", "implement it", "نفّذ الخطة", "ابدأ التنفيذ", or hands you a plan file.
---

# Executing Plans

The plan already did the thinking. Execute it exactly, prove each step with
a test you watched fail and then pass, and leave a record that survives your
own forgetting.

Say at the start: "Using executing-plans (<mode> mode) to implement <plan>."

## Pick the mode

| Mode | When | Cost |
|---|---|---|
| **Inline** | The user chose it, the plan is short, tasks are tightly coupled, or there's no subagent tool | One context plus one final reviewer |
| **Subagent-driven** | The user chose it, the plan is long, or the change is risky. Tasks run sequentially, each with a fresh implementer and a reviewer | One fresh context per task and per review |
| **Parallel** | Two or more *independent* problems with no shared files or state (e.g. unrelated failing test files) | One agent per problem, run concurrently |

Read `references/subagent-mode.md` for subagent-driven mode and
`references/parallel-agents.md` for parallel mode. Inline mode is below.

## Ground rules (every mode)

**Continuous execution.** Don't stop between tasks to ask "should I
continue?". The user asked you to execute the plan, so execute it.

**Rulings, not stalls.** When you hit a conflict, an ambiguity or a plan
defect, decide it. The spec is the binding authority, the plan is its
argument, and your judgment settles what neither answers. Record each
decision in the ledger as:
`Ruling: <what you decided> — <why> — <what it costs if wrong>`.
A wrong ruling costs rework the user can see and undo. A session parked on a
question costs their whole day.

**Only four things stop you:**
1. An irreversible or destructive operation (dropping data, deleting files outside the task)
2. A security-sensitive action (credentials, permissions, auth changes beyond the plan)
3. A side effect outside the working tree that norms say to ask about first (push to a shared branch, merge, publish, deploy)
4. A plan so broken that every path forward is a guess

**Isolation.** Don't implement on `main`/`master` without the user's
explicit consent. Use a feature branch or a git worktree.

## Setup

1. Read the plan once, plus the spec it names. Note the Global Constraints. Make a todo per task.
2. **Create the ledger.** Conversation memory doesn't survive compaction, and
   an executor that loses its place re-implements finished tasks, which is
   the most expensive failure there is. Create
   `.wolfin-senior/plans/<plan-basename>/progress.md` at the repo root, and add
   `.wolfin-senior/` to `.git/info/exclude` so it never gets committed. The
   first line is its identity: `# Ledger — plan: <plan path>`.
   Point `NOW.md` in the project memory at the plan and this ledger
   (`project-memory`), so a fresh session knows which plan is running.
3. **Resuming?** If the ledger exists and names this plan, every task with a
   `Task N: complete` line is DONE. Don't redo it. Resume at the first task
   without one. Trust the ledger and `git log` over your recollection.
4. **Pre-flight scan.** For every task that consumes what an earlier task
   produces, compare the Interfaces blocks. Ledger each mismatch and your
   ruling on it. If nothing is shared, write `Pre-flight: no shared interfaces`.
5. Load `test-driven-development`. It governs every step below. Load
   `docs-first` too, and check the libraries the plan uses, unless the plan
   header already lists versions that the project memory confirms are fresh.

## Inline mode: the task loop

**1. Take the task.** Re-read the task's full text from the plan, even if you
remember it. Memory holds a summary. The plan holds the exact values. Record
BASE = `git rev-parse HEAD`.

**2. Work the steps in order.** Every step that runs a command has an
`Expected:` line. Run it, read the output, compare. There are three outcomes:
- **Matches:** go to the next step.
- **The code is wrong:** use `systematic-debugging`. Find the cause. Never
  patch the symptom to make the output match.
- **The plan is wrong** (contradicts the spec, mismatched interface, a command
  that can't work): make the smallest change that satisfies the spec, ledger
  it as `Task N: Ruling: ...`, and continue.

A test that passes before the implementation exists is a finding about the
test. Fix the test.

**3. Completion contract.** Before a task's ledger line, all of these are
true, with evidence from this session:
- Every test the task names exists, ran, and you read the output.
- The final run of the task's test command passed, and so did the project's full suite.
- Every `Expected:` line was compared against real output.
- Every deviation from the plan has a `Ruling:` line.

**4. Commit and record,** in the same step:
`Task N: complete (commits <base7>..<head7>, tests: <command> → <N passed>)`
Add a one-entry journal line for the task and update NOW.md's "Next" (`project-memory`).
Then mark the todo complete and take the next task.

Long test output goes to a file in the ledger directory. Read its tail
rather than flooding your context.

## Final review (every mode)

When every task is complete:

1. Build the review package: `git log --oneline <merge-base>..HEAD`,
   `git diff --stat`, and `git diff -U10` for the branch, written to one file
   in the ledger directory.
2. **With a subagent tool:** dispatch one reviewer on the most capable model,
   using the template in `../code-review-workflow/references/reviewer-prompt.md`,
   with the package path, the plan and spec paths, the plan's Review Focus
   section verbatim, and a pointer to the ledger's `Ruling:` lines. This is
   the one fresh pair of eyes the run buys. Don't replace it with your own
   read of the diff, because the author has the author's blind spots.
   **Without a subagent tool:** do that review yourself as a separate pass,
   and tell the user it was a self-review.
3. **Re-grade the findings by effect,** meaning what a real user gets if it
   ships, not whether the spec happened to mention it. Then:
   - **Critical / Important:** fix them in one pass. Each fix gets a test
     that reproduces the finding and fails first, then passes. Then run the
     full suite. Ledger: `Final: fixed <finding> — <test> RED→GREEN, suite N/N`.
   - **Minor:** ledger it as `Final: minor (deferred): <one-liner>`. Don't fix
     it unasked. Every extra fix is scope the user didn't request.
   - **A finding you won't fix** is a ruling: `Final: Ruling: <finding> — <why the code stands> — <cost if wrong>`.

## Finish

Your final message contains, verbatim from the ledger:
- **Rulings I made:** every `Ruling:` line, in order, each with its cost if wrong
- **Deferred minors:** every `minor (deferred)` line
- **Verification:** the final suite command and result

These lists are the only place the decisions you made on the user's behalf
reach them. Before deleting the ledger, copy what must outlive it into the
project memory: the outcome and the rulings into the journal, and any
decision or lesson future work depends on into a topic file. Then delete
the ledger directory (git history is the record now), clear the task from
NOW.md, and use `finishing-and-shipping`.

## Rationalizations

| Excuse | Reality |
|---|---|
| "I remember what Task N says" | You remember a summary. Re-read the task. |
| "The plan's code is right, skip watching the test fail" | A test you never saw fail proves nothing. |
| "I'll run the full suite at the end only" | Per-task runs tell you which task broke it. |
| "The plan is wrong, I'll just do the right thing" | Do it, and ledger the ruling. An unrecorded deviation is a decision made in secret. |
| "I'll update the ledger after a few tasks" | Compaction doesn't wait. One line per task, with the commit. |
| "Let me check in before the next task" | Only the four stops stop you. |
| "I read my own diff, the final review is redundant" | Same author, same blind spots. |
| "I'll fix the minors too while I'm here" | Ledger them. The user decides. |
