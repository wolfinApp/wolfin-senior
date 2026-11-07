---
name: code-review-workflow
description: Use when a task or feature is finished and needs review, before merging, when asked to review someone's code or a PR, and when receiving review feedback (from the user, a reviewer, or a bot) before acting on it. Covers self-review, dispatching a fresh reviewer subagent, giving useful reviews, and responding to feedback with technical rigor instead of blind agreement. Triggers on "review this", "look at this PR", "I got feedback".
---

# Code Review Workflow

Review catches what the author can't see, and it spreads knowledge across
the team (rule 11). This skill covers three roles: preparing your own work
for review, reviewing code, and receiving feedback.

Three rules shape all of them:
- **Don't fall in love with your own code** (rule 1). Feedback is about the code, not about you.
- **Everyone hates code they didn't write** (rule 17). Before judging or rewriting code, find out why it's the way it is.
- **Technical correctness over social comfort.** Neither flattery nor defensiveness helps the code.

---

## Part 1: Requesting review

**When:** after each task in subagent-driven work, after a significant
feature or a complex bug fix, and before every merge to the main branch.
Review also helps when you're stuck or before a big refactor.

### Self-review first

Read your own diff (`git diff <base>..HEAD`) as if someone else wrote it:
- Does it do what was asked, and nothing more?
- Debug leftovers, commented-out code, TODOs without an owner?
- Names that say what things do? Functions small enough to understand at a glance?
- Errors handled? Inputs validated at the boundaries?
- Tests that would fail if the code broke? Full suite green?
- Any secrets, credentials or personal data in the diff?

Fix what you find before asking anyone else to look.

### Dispatch a fresh reviewer

A reviewer with your session's history inherits your blind spots. Give it
precisely crafted context instead:

1. Get the range: `BASE=$(git merge-base origin/main HEAD)` (or the commit before the task), `HEAD=$(git rev-parse HEAD)`.
2. Dispatch a subagent using `references/reviewer-prompt.md`, filling in: what was built, the requirements or plan path, BASE and HEAD, and any focus areas.
3. Pick the model by risk: standard for routine diffs, the most capable for security, concurrency, data migrations, or whole-branch reviews.

### Act on the findings

- **Critical:** fix immediately.
- **Important:** fix before proceeding.
- **Minor:** note it for later, or fix it if it's trivial and in scope.
- **The reviewer is wrong:** push back with technical reasoning, and the code or tests that prove it.

---

## Part 2: Reviewing code (yours or someone else's)

**Understand before judging.** Read the PR description, the linked issue,
and enough of the surrounding code to know why it's written the way it is.
Check `git log -p` / `git blame` for the history of odd-looking lines.

**What to check, in priority order:**
1. **Correctness:** does it do what it claims? Edge cases: empty, null, huge, concurrent, unauthorized, malformed.
2. **Security:** injection (SQL, command, template), XSS, authz on every endpoint, secrets in code, sensitive data in logs or responses.
3. **Robustness:** timeouts on network calls, error paths, retries that can't storm, resource cleanup.
4. **Tests:** do they test behavior, and would they fail if the code broke?
5. **Design:** single responsibility, coupling, global state, the right level of abstraction (`engineering-principles`).
6. **Performance:** N+1 queries, unbounded lists, missing pagination, work repeated in loops, needless re-renders.
7. **Maintainability:** naming, readability, duplication, consistency with the codebase.
8. **Style:** only what the linter and formatter don't already enforce (rule 15).

**How to write each comment:**
- Point to the line: `file.ts:42`.
- Say what's wrong, **why it matters** (the impact), and a suggested fix.
- Label severity honestly: **Critical / Important / Minor / Nit / Question**. Not everything is critical.
- Ask questions when you're unsure ("What happens if `items` is empty here?") rather than asserting.
- Call out what's done well, specifically. Accurate praise makes the rest of the feedback credible.
- Explain the reasoning so the author learns the principle, not just the fix.
- End with a clear verdict: **Approve / Approve with fixes / Changes required**.

---

## Part 3: Receiving feedback

```
1. READ:       all of it, without reacting
2. UNDERSTAND: restate each item in your own words, or ask
3. VERIFY:     check it against the actual codebase
4. EVALUATE:   is it technically right for THIS codebase?
5. RESPOND:    technical acknowledgment, or reasoned pushback
6. IMPLEMENT:  one item at a time, testing each
```

**No performative agreement.** Skip "You're absolutely right!", "Great
point!" and "Thanks for catching that!". They add nothing and signal that
you're agreeing before verifying. Instead, restate the technical point,
ask a precise question, or just fix it and say what changed:
"Fixed: `parseDate` now rejects non-ISO input (`dates.ts:31`), with a test."

**Unclear items: ask before implementing anything.** Items are often related,
and implementing the ones you understand before clarifying the rest
produces the wrong result.
> "I understand 1, 2, 3 and 6. I need clarification on 4 and 5 before I start."

**By source:**
- **The user:** trusted. Implement once you understand it. Still ask if the scope is unclear.
- **External reviewers and bots:** be skeptical, but check carefully. Before implementing, ask: is it correct for this stack and version? Does it break existing behavior? Is there a reason the current code is the way it is? Does the reviewer have the full context? Does it conflict with something the user decided? If so, discuss it with the user first.

**YAGNI check.** When a reviewer asks you to "implement it properly" (add
metrics, a config option, an abstraction), grep for actual usage first.
> "Nothing calls this endpoint. Remove it instead (YAGNI)? Or is there usage I'm missing?"

**When to push back:** the suggestion breaks functionality, the reviewer is
missing context, it violates YAGNI, it's wrong for this stack, there are
compatibility reasons, or it conflicts with the user's architecture
decisions. Push back with technical reasoning, specific questions and
references to working tests, never defensiveness.
> "Checked: the build target is iOS 15, and this API needs 17. We need the fallback. Drop iOS 15–16 support, or keep it?"

**If you pushed back and were wrong:** "Checked it, and you're right:
`X` does `Y`. Fixing now." No long apology, no defending the earlier position.

**Make feedback stick.** When the user's feedback is about *how you work*
("don't add dependencies without asking", "always run the e2e tests"),
save it as a `feedback` memory with its reason (`project-memory`), so you
don't repeat the mistake in the next session.

**Implementation order:** clarify everything first, then fix blocking
issues (breakage, security), then simple fixes, then complex ones. Test each
one, and finish with the full suite.

**GitHub inline comments:** reply in the comment's thread
(`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a
top-level PR comment.

## Red flags

| Thought | Reality |
|---|---|
| "It's simple, skip the review" | Simple diffs hide the bugs nobody looks for. |
| "I'll review my own diff instead of dispatching" | Same author, same blind spots. |
| "The reviewer said it, so it's right" | Verify against the code first. |
| "I'll do the easy items now, and ask about the rest later" | Clarify everything first. Items interact. |
| "Rewrite this, it's ugly" | Find out why it's like that first (rule 17). Ugly-but-working code often encodes a hard-won edge case. |
