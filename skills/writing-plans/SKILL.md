---
name: writing-plans
description: Use when you have an approved design, spec, or clear requirements for multi-step work, before touching code — turns it into a plan of small, test-first, independently shippable tasks with exact files, interfaces, commands and expected output. Use for any feature, migration, or refactor that spans more than a couple of files, and when the user says "plan it", "write a plan", "break it down".
---

# Writing Plans

Write the plan for a skilled engineer who has never seen this codebase or
this conversation. Assume they write idiomatic code once they know the exact
interface and the exact test, and that they'll make a reasonable choice
wherever the plan leaves one open. What they *can't* know is what you
decided: which files, which names and signatures, which values from the
spec, and which tests prove each task. Write those down.

Principles: DRY, YAGNI, TDD, small commits. Each task leaves the software
working (rule 14: ship early, iterate often).

Say at the start: "Using writing-plans to create the implementation plan."

**Save to:** the project's convention, or `docs/plans/YYYY-MM-DD-<feature>.md`.

## Scope check

If the spec covers several independent subsystems, suggest one plan per
subsystem. Each plan should produce working, testable software on its own.

## Check the docs first

Before naming any framework API, config key or CLI flag in the plan, run
`docs-first` for the libraries the plan uses. A plan written against a
remembered API spreads the mistake into every task. Put the versions and
the doc links in the header, and note any gotcha the docs revealed under
Global constraints.

## File structure first

Before you define tasks, map which files will be created or changed and
what each one is responsible for. This is where decomposition gets decided.

- One clear responsibility per file, with a well-defined interface.
- Prefer smaller, focused files. They're easier to hold in context and edit
  reliably.
- Files that change together live together. Split by responsibility, not by
  technical layer.
- In an existing codebase, follow its patterns. Don't restructure on your
  own. If a file you're touching has grown unwieldy, a split can be its own
  task.

## Task sizing

A task is the smallest unit that has its own test cycle and is worth a
reviewer's gate. Fold setup, configuration and docs into the task that
needs them. Split only where a reviewer could reasonably reject one task
while approving its neighbor.

**Slice vertically.** Each task is a **tracer bullet**: a narrow but
complete path through every layer it needs (schema, logic, API, UI, tests),
demoable or verifiable on its own and small enough for one fresh context
window. A plan of horizontal layers ("all the models, then all the
endpoints, then the UI") delivers nothing working until the last task and
hides integration bugs until then.

**Prefactor first.** If the existing code makes the change awkward, the
first task reshapes it without changing behavior: make the change easy,
then make the easy change.

**Declare blocking edges.** Every task names the tasks that must finish
before it can start, or "None". The **frontier** is every task whose
blockers are done; independent tasks on the frontier can run in parallel
(`executing-plans`).

**Wide refactors are the exception.** One mechanical change whose blast
radius spans the codebase (rename a column, retype a shared symbol) can't
land as a green vertical slice. Sequence it as **expand, migrate,
contract**: add the new form beside the old so nothing breaks; move callers
over in batches sized by blast radius (per package or directory), each its
own task blocked by the expand; delete the old form in a final task blocked
by every batch.

Each **step** is one action with a checkable result:
"write the failing test", "run it and watch it fail", "implement the
minimal code", "run the tests and watch them pass", "commit".

## Plan header

```markdown
# <Feature> Implementation Plan

> For the executor: use the `executing-plans` skill. Steps use checkboxes (`- [ ]`).

**Goal:** <one sentence>
**Architecture:** <2–3 sentences>
**Tech stack:** <key technologies with installed versions, checked with `docs-first`, plus doc links>
**Spec:** <path to the design doc this plan implements>
**Estimate:** <range, e.g. "4–7 tasks, ~1–2 sessions">. Assumptions: <...>. Biggest risk: <...>

## Global constraints
<Project-wide requirements copied verbatim from the spec: versions, dependency
limits, naming rules, performance budgets, platform requirements. One line each.
Every task implicitly includes these.>

## Review focus
<Up to five inputs or failure modes the spec implies but no task's tests exercise,
the ones most likely to hurt a real user (empty input, huge input, slow network,
concurrent edits, permission denied...). One line each with the expected behavior.
Then add the test that pins each one to the task that owns the code.>
```

Estimates are ranges with assumptions, not promises (rule 13).

## Task template

````markdown
### Task N: <What works after this task, in user terms>

**Blocked by:** Task 2, Task 3 (or "None: can start immediately")

**Files:**
- Create: `exact/path/new_file.py`
- Modify: `exact/path/existing.py` (the function or section)
- Test: `tests/exact/path/test_file.py`

**Interfaces:**
- Consumes: <exact signatures from earlier tasks>
- Produces: <exact names, parameter and return types later tasks rely on>

- [ ] **Step 1: Write the failing test**
```python
def test_rejects_empty_email():
    result = submit_form({"email": ""})
    assert result.error == "Email required"
```

- [ ] **Step 2: Run it and watch it fail**
Run: `pytest tests/forms/test_submit.py::test_rejects_empty_email -v`
Expected: FAIL (`AttributeError` or wrong error), not a syntax/import error

- [ ] **Step 3: Implement `submit_form(data: dict) -> FormResult` in `app/forms.py`**
One line on the approach if the signature and test leave a real choice.

- [ ] **Step 4: Run the tests and watch them pass**
Run: `pytest tests/forms -v`
Expected: all PASS, no warnings

- [ ] **Step 5: Commit**
`git commit -m "feat(forms): reject empty email on submit"`
````

## What a step contains

A step is done when the implementer can write exactly one reasonable thing
from it. It needs to be unambiguous, not complete:

- **Test step:** the test name and its assertions as code, with the spec's exact values.
- **Code step:** the exact signature, the file, and the values the spec pins.
  The implementer writes the body. Include a body only for an algorithm the
  signature and tests don't determine, or for exact copy the spec fixes.
- **Verification step:** the command and the output that means it passed.
- **Reference to another task:** point at that task's Interfaces block. Don't repeat its code.

Two failure modes. A plan longer than the code it describes has written the
code instead of planning it. And lines that decide nothing ("TBD", "handle
edge cases", "add validation", "write tests for the above") are gaps
dressed up as steps.

## Self-review

Run this checklist yourself after writing the plan:

1. **Spec coverage:** for each requirement in the spec, point to the task that implements it. Add tasks for gaps.
2. **Step scan:** every step lets the implementer write exactly one reasonable thing. Fix vague lines and over-specified bodies.
3. **Type consistency:** names and signatures match across tasks (`clearLayers()` in Task 3 vs `clearAllLayers()` in Task 7 is a bug).
4. **Slices and edges:** every task is a vertical slice that works on its own, every "Blocked by" names a real dependency, and no task waits on one it doesn't need.
5. **Review focus:** every listed failure mode has a test in its owning task.
6. **Proportion:** if code blocks are most of the document, replace bodies with signatures and assertions.
7. **Working software:** after each task, does the app still build and run?

Fix issues inline. No second review needed.

## Handoff

Save the plan, link it, and ask the user to review it. Then recommend an
execution mode and ask which they want:

- **Inline:** you implement every task yourself in this session, then one
  fresh reviewer checks the whole branch. Cheapest and fastest. Good for
  short plans and tightly coupled tasks.
- **Subagent-driven:** a fresh subagent implements each task and a fresh
  reviewer checks it before the next one starts, then a whole-branch review.
  Most thorough. Good for long plans, risky changes, and independent tasks.

"For this plan I recommend <mode>, because <one sentence: task count,
coupling, cost of a shipped mistake>."

Then use `executing-plans` with the chosen mode.
