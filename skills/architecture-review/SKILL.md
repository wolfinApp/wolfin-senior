---
name: architecture-review
description: Use when the user wants to improve a codebase's structure, or asks where it is hard to change, hard to test or tangled — surveys the areas that change most for shallow modules and leaky seams, applies the deletion test, presents ranked deepening candidates with before and after sketches, then designs the one the user picks. Also use after a bug had no good seam for its regression test, before a large refactor, and for "review the architecture", "tech debt", "this codebase is a mess", "where should we refactor", "make it easier to test".
---

# Architecture Review

Agents make code cheap to write, and that makes codebases decay faster:
modules multiply, interfaces grow, and every change touches five files.
This skill finds where the structure is costing the most, and proposes
**deepening**: turning clusters of shallow modules into deep ones, with a
lot of behavior behind a small, testable interface.

It's a survey, not a rescue. It finds candidates and hands you the best
ones. The user picks one, and only that one gets designed and built,
through the usual chain.

Say at the start: "Using architecture-review to survey <area>."

**Use this vocabulary exactly:** module, interface, depth, seam, adapter,
leverage, locality, the deletion test. Read
`../engineering-principles/references/deep-modules.md` now if you haven't
in this session. For the domain, use the project's `GLOSSARY.md` terms:
"the Order intake module", not "the OrderHandlerService".

## 1. Scope before you scan

Deepening pays off by making *future* changes cheaper, so look where change
actually happens (YAGNI applies to refactors too).

- **The user named an area** (a module, a pain point)? Take it, and skip the rest of this step.
- **Otherwise find the hot spots:**
  ```bash
  git log --since="6 months ago" --name-only --format= | grep -v '^$' | sort | uniq -c | sort -rn | head -30
  ```
  Files and folders that keep changing pull your attention first. If change
  is scattered with no hot spot, widen the window.
- **Read what's already decided:** `GLOSSARY.md`, the ADRs in that area
  (decisions not to re-litigate), and the project memory's lessons, which
  often name the places that hurt ("no good seam for the refund bug").

## 2. Explore

Walk the area, or send a fresh subagent to walk it and report back. Explore
organically and note where understanding is hard:

- Understanding one concept means bouncing between many small modules.
- **Shallow** modules: the interface is nearly as complex as the implementation.
- Pure functions extracted only to be testable, while the real bugs hide in
  how they're called (no **locality**).
- Modules that leak into each other across their seams.
- Code that is untested, or hard to test through its current interface.
- A recent bug whose regression test had no good seam.

Apply the **deletion test** to every suspect: would deleting it concentrate
complexity in one place, or just move it to every caller? "Concentrates" is
the signal you want.

## 3. Present the candidates

At most five, best first. For each:

- **Files:** the modules involved
- **Problem:** the friction, concretely ("adding a payment method means editing these 6 files")
- **Solution:** what would change, in plain words
- **Benefits:** in locality and leverage, and how the tests would improve
- **Before / after:** a small sketch (ASCII boxes or a Mermaid graph) showing the shallow cluster and the deep module it becomes
- **Strength:** Strong, Worth exploring, or Speculative
- **ADR conflict:** only if the friction is bad enough to reopen it; say which ADR and why

End with your **top recommendation** and why you'd do it first.

For a short list, write it in chat. For a long one, or when the user wants
something to share, write a self-contained HTML report to the OS temp
directory (`$TMPDIR`, else `/tmp`), never into the repo, open it for the
user, and give the path.

Don't propose interfaces yet. Ask: "Which one should we explore?"

## 4. Design the one they pick

1. **Ask the open questions in rounds** (`requirements-and-design`, Step 2):
   constraints, what depends on the module, what sits behind the seam,
   which tests survive. Facts you look up; decisions go to the user.
2. **Classify the dependencies** (in-process, local stand-in, remote but
   yours, truly external) to decide where the seam goes and how it's
   tested (`deep-modules.md`).
3. **For an interface that matters, design it twice:** three or more fresh
   subagents in parallel, each under a different constraint, then compare
   and recommend one (`deep-modules.md`).
4. **Keep the domain model current.** A new concept gets a `GLOSSARY.md`
   entry. If the user rejects a candidate for a reason a future review
   would need ("the partner API forces this split"), offer an ADR so the
   same candidate isn't proposed again.
5. **Plan it** (`writing-plans`): prefactor first, expand–migrate–contract
   for wide changes, and replace the old shallow tests with tests at the new
   interface instead of layering both.

## Rules

- Read-only until the user picks a candidate and approves its design.
- Rank by payoff where change happens, not by how ugly the code looks
  (rule 17: find out why it's that way first).
- One candidate at a time. A big-bang restructure is a rewrite in disguise.

## Red flags

| Thought | Reality |
|---|---|
| "Let me refactor it while I'm here" | Survey first, then the user picks. Unrequested refactors are scope creep. |
| "Every module should have an interface" | One adapter is a hypothetical seam. Add one when two adapters need it. |
| "This file is ugly, it's a candidate" | Ugly but stable code costs nothing. Rank by where change happens. |
| "I'll extract small functions to make it testable" | Small extracted pieces often lose locality. Test the deep module at its interface. |
| "The ADR is old, ignore it" | Reopen it explicitly, with the friction that justifies it, or respect it. |
