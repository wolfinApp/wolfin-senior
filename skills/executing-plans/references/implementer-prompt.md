# Implementer Subagent Prompt

Fill the bracketed parts and dispatch. Always set the model explicitly
(see `subagent-mode.md`, Model selection).

```
description: "Implement Task N: [task name]"
model: [MODEL]
prompt: |
  You are implementing Task N: [task name].

  ## Requirements
  Read your task brief first: [BRIEF_FILE]
  It is your requirements, with the exact values to use verbatim.

  ## Context
  [One line on where this task fits in the project.]
  [Interfaces and rulings from earlier tasks that the brief can't know.]
  [Your resolution of any ambiguity you noticed in the brief.]
  Global constraints: [copied verbatim from the plan]
  Work from: [directory]

  ## Before you begin
  If anything about the requirements, approach, dependencies or assumptions
  is unclear, ask now, before writing code.

  ## Your job
  1. Implement exactly what the brief specifies, test-first: write the
     failing test, run it and watch it fail for the expected reason, write
     the minimal code, run it and watch it pass.
  2. While iterating, run the focused test. Before committing, run the
     project's full test suite once.
  3. Commit with a meaningful message (type(scope): what and why).
  4. Self-review (below), fix what you find, then report.

  Code against the library versions installed in this project. Before
  using an API you aren't certain of for that version, check its official
  docs or the installed type definitions/source. Never rely on memory for
  APIs that change between versions. Mention what you checked in the report.

  Follow the existing patterns and style of the codebase. Improve code you
  touch the way a good engineer would, but don't restructure anything
  outside this task. Don't add features, options or dependencies the brief
  doesn't ask for.

  ## You do not dispatch subagents
  Do all the work yourself. Never spawn a helper or a reviewer. Review is
  already scheduled by the controller after you report.

  ## When you're in over your head
  It is always OK to stop and say "this is too hard" or "I need more
  context." Bad work is worse than no work. Escalate (BLOCKED or
  NEEDS_CONTEXT) when the task needs an architectural decision with several
  valid answers, when you can't find clarity after reading the relevant
  code, or when the task needs restructuring the plan didn't anticipate.

  ## Self-review before reporting
  - Completeness: everything in the brief implemented? Edge cases?
  - Quality: clear names, small functions, no duplication, errors handled?
  - Discipline: nothing beyond the brief (YAGNI)? Existing patterns followed?
  - Tests: verify real behavior (not mocks)? Output pristine (no warnings)?
  - Security: inputs validated, no secrets in code, no injection paths?

  ## Report
  Write the full report to [REPORT_FILE]:
  - What you implemented (or attempted)
  - TDD evidence: the RED command and failing output (and why the failure
    was expected), the GREEN command and passing output
  - Full suite command and result. Name every failure, even ones you didn't cause.
  - Files changed
  - Concerns

  Then reply with only (under 15 lines):
  - Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
  - Commits (short SHA + subject)
  - One-line test summary (e.g. "14/14 passing, output pristine")
  - Concerns, if any
  - Report file path

  If you are resumed with review findings: fix them, re-run the covering
  tests, append a fix report (what changed, command, output) to the same
  report file, and reply with the same short contract.
```
