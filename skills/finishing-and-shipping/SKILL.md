---
name: finishing-and-shipping
description: Use when implementation is complete and the work needs to be committed, integrated, released, or handed over — writing meaningful commit messages, choosing merge vs pull request vs keep, writing PR descriptions, checking deployment readiness (migrations, config, rollback, monitoring), and planning maintenance follow-ups. Covers SDLC phases 05 Deployment and 06 Maintenance. Triggers on "commit this", "open a PR", "merge", "deploy", "release", "ارفع", "سوّي commit", "انشر".
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

```markdown
## What
<one paragraph: the change, in user-facing terms>

## Why
<the problem or requirement; link the issue/spec>

## How
<key decisions and trade-offs; anything a reviewer should look at closely>

## Testing
<commands run and results; manual checks; screenshots or recordings for UI>

## Risk & rollback
<what could go wrong, how we'd notice, how to revert (flag off / revert commit / down-migration)>
```

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
