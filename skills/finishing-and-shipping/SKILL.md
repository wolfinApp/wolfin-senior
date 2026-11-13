---
name: finishing-and-shipping
description: Use when implementation is complete and the work needs to be committed, integrated, released, or handed over — writing meaningful commit messages, choosing merge vs pull request vs keep, writing PR descriptions, checking deployment readiness (migrations, config, rollback, monitoring), and planning maintenance follow-ups. Covers SDLC phases 05 Deployment and 06 Maintenance. Triggers on "commit this", "open a PR", "merge", "deploy", "release", "ship it", "publish".
---

# Finishing and Shipping

Code isn't done when it works on your machine. It's done when it's
integrated, deployable, observable, and someone else can understand why it
changed. Software is never finished (rule 7): shipping well means leaving a
clear trail for the next change.

Say at the start: "Using finishing-and-shipping to wrap up this work."

## Step 1: Verify

Run the project's full test suite, the linter or type checker, and the build
(`verification-before-completion`). If anything fails, report the failures
and stop. Nothing below happens on a red tree.

## Step 2: Commit well (rule 9)

A commit message is a letter to the engineer who runs `git blame` on this
line in two years. Tell them **why**.

**Format** (Conventional Commits, unless the project uses something else.
Check `git log --oneline -20` first and match it):

```
<type>(<scope>): <what changed, imperative, ≤ 72 chars>

<why: the problem, the reason for this approach, the trade-offs.>
<impact: behavior changes, migrations, config, breaking changes.>

Refs: #123
```

Types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`.
Add `!` (or a `BREAKING CHANGE:` footer) for breaking changes.

| ❌ | ✅ |
|---|---|
| `fix bug` | `fix(cart): prevent negative quantity when decrementing at 1` |
| `updates` | `perf(api): batch product lookups to remove N+1 on /orders (p95 820→140 ms)` |
| `WIP` | `refactor(auth): extract token validation into TokenVerifier` |

**One logical change per commit.** Don't mix a refactor with a behavior
change. Stage selectively (`git add -p`). Never commit secrets, build
artifacts, or local config. Check `git diff --cached` before committing.

Respect the project's attribution and sign-off rules (CLAUDE.md, CONTRIBUTING).

## Step 3: Choose the integration path

Determine the base branch (from the plan, the conversation, or the
upstream). If it's unclear, ask: "This branch split from `main`, is that
right?" Merging into the wrong base is expensive to undo.

Present exactly these options and wait for the user's choice. Integration
is their decision:

```
Implementation complete and verified. What would you like to do?
1. Merge into <base> locally
2. Push and open a Pull Request
3. Keep the branch as-is for now
```

- **Merge locally:** switch to the base, pull, merge, **run the tests on the
  merged result**, and only then delete the feature branch
  (`git branch -d`). If the merged result fails, stop and investigate.
  Nothing has been pushed, so it's recoverable.
- **Pull request:** `git push -u origin <branch>`, then create the PR (with
  `gh pr create` or the forge's tooling), following the repo's PR template.
  Report the URL. Keep the branch and worktree, because review fixes happen
  there.
- **Keep:** report the branch name and location.

**Never, without an explicit request:** force-push, delete a branch that has
unmerged work, discard commits, or remove a worktree that contains
uncommitted files. A rejected push means the remote moved. Investigate it,
don't overwrite it. To discard work, the user must ask for it explicitly,
and you list exactly what will be lost and get confirmation first.

### PR description template

Use the repo's own template if it has one. Otherwise:

```markdown
## Summary
<The smallest visual that makes the change clear, then two or three
sentences in user-facing terms. Link the issue or spec.>

## Evidence
- **Before:** <screenshot, output, or the failing test run>
- **After:** <screenshot, output, or the passing test run>

## Merge danger
**Door:** one-way | two-way
**Blast radius:** <one or two words: "checkout", "every API client", "none">
<What could go wrong, how we'd notice, how to roll back.>
```

**Summary: pick the smallest view that makes the point.** A call tree for
control flow, a shallow file tree for a refactor, pseudocode for an
algorithm, a Mermaid sequence diagram for components talking, or a `diff`
block of the tree when the point is what changed:

```diff
 submitForm
   createSession
     persistPrompt
+    expandSkillMention
     launchAgent
```

One visual is usually enough. Keep only the calls, files and states the
reviewer needs.

**Evidence: show it works, before and after.** A screenshot is the best
evidence for a visual change. Test or console output is next: show the
exact test that failed before and passes now. "Tests pass" with no output
is not evidence.

**Merge danger: can we walk it back?** A two-way door is cheap to undo
(revert the commit, turn the flag off). A one-way door isn't: dropped
columns, published API changes, sent emails, deleted data, rewritten
history. Call one-way doors out loudly, and say what the rollback is for
everything else.

## Step 4: Deployment readiness (SDLC 05)

For changes going to production, walk `references/release-checklist.md`. The
essentials:
- **Migrations are backward compatible** (expand → migrate → contract), so
  old and new code can run side by side during the rollout.
- **Config and secrets** for every environment exist and are documented.
- **Risky changes ship behind a feature flag** or a staged rollout.
- **A rollback plan exists** and is quick (revert, flag off, redeploy the
  previous version).
- **Observability is in place:** logs, metrics and alerts that would show
  if this change broke something.

## Step 5: Maintenance handoff (SDLC 06)

End with an honest wrap-up for the user:
- What shipped, and how it was verified (with evidence)
- **Known limitations and follow-ups:** short and concrete, nothing hidden
- What to watch after the release (the metric or log that tells you it's healthy)
- Docs and changelog updated, or a note that they need to be
- **When the work went sideways** (a wrong turn, a bug found late, a long
  search for a file), suggest one improvement to the *environment* that
  would have prevented it: a lint rule or test for a mechanical mistake, a
  line in the coding standards for a judgement call, a pointer in
  `CLAUDE.md` for something hard to find. The user can ask for a full
  retrospective with `/wolfin-senior:retro`.

Record the same in the project memory (`project-memory`): a journal entry
for the release (commits, PR URL, verification), NOW.md cleared of the
finished task with the follow-ups listed under "Next", and any decision
future work depends on saved as a topic file.

## Red flags

| Thought | Reality |
|---|---|
| "Tests passed earlier" | Run them on the tree you're about to integrate. |
| "They obviously want it merged" | Present the options and wait. |
| "Push rejected, force-push will fix it" | The remote moved. Investigate first. |
| "The migration is simple, it can't break" | Old code runs against the new schema during deploys. Keep it compatible. |
| "Commit message doesn't matter" | It's the only documentation every change is guaranteed to have. |
