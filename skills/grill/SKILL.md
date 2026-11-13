---
name: grill
description: Stress-test a plan, feature idea or design with rounds of sharp questions, each with a recommended answer, before anything gets built.
disable-model-invocation: true
argument-hint: "[the plan or idea to stress-test]"
---

# Grill

Load the `requirements-and-design` skill with the Skill tool
(`wolfin-senior:requirements-and-design`), then run only its Step 1 (look
before you ask) and Step 2 (the conversation, in rounds) on:

$ARGUMENTS

With no argument, grill the plan or idea under discussion in this
conversation.

- Map the open decisions as a design tree and ask the whole frontier each
  round, numbered, with your recommended answer for each.
- Look up facts yourself, or with a fresh subagent. Only decisions go to the user.
- Stay in grilling mode: no product code and no files, except `GLOSSARY.md`
  terms and ADRs the user agrees to.

Done when the frontier is empty and the user confirms your play-back. Then
offer the next step: a design doc (Step 4 of `requirements-and-design`), or
`writing-plans` if the work is small.
