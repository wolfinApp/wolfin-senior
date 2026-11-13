---
name: review
description: Review a PR, branch, commit or your uncommitted changes on two axes (spec and standards), with every finding proven by a concrete failure scenario.
disable-model-invocation: true
argument-hint: "[PR number, branch, commit, or nothing for current changes]"
---

# Review

Load the `code-review-workflow` skill with the Skill tool
(`wolfin-senior:code-review-workflow`) and run Part 2, "Reviewing code", on:

$ARGUMENTS

With no argument, review the uncommitted changes (`git diff HEAD` plus
untracked files), or the current branch against its merge base if the tree
is clean.

- Find the spec (the PR's linked issue, the plan or design doc, or what the
  user asked for in this conversation). With none, say so and review
  Standards only.
- For a large diff, run the Spec and Standards axes in two fresh subagents
  in parallel (`../code-review-workflow/references/reviewer-prompt.md`).
- Read-only: don't edit, push or post anything unless the user asks.

End with the verdict, the findings under Spec and Standards, and what you
didn't review.
