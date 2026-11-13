---
name: handoff
description: Save where the work stands and write a handoff note, so a fresh session (or another person) can continue exactly from here.
disable-model-invocation: true
argument-hint: "[what the next session will focus on]"
---

# Handoff

Load the `project-memory` skill with the Skill tool
(`wolfin-senior:project-memory`), then:

1. **Bring the memory up to date:** append this session's steps to today's
   journal (with how each was verified), and rewrite `NOW.md` so it's true
   right now: the active task, what's done, the next step, blockers.
2. **Write the handoff note** to `.wolfin-senior/memory/handoff.md`
   (replace any older one). Focus it on: $ARGUMENTS
   - **Goal:** what we're trying to achieve, in one or two sentences
   - **State:** what works, what doesn't, what's half done (branch, uncommitted files)
   - **Decisions:** the ones the next session must not reopen, with their reasons
   - **Next steps:** in order, the first one concrete enough to start immediately
   - **Pointers:** paths or URLs to the plan, the design doc, ADRs, the PR, the
     relevant journal entries. Reference them; never copy what they say.
   - **Suggested skills:** which Wolfin Senior skills the next session should
     load first, and why
3. **Redact:** no passwords, tokens, keys or personal data in the note, only
   where they live.

Finish by telling the user the note's path, and the one line to start the
next session with: "Read .wolfin-senior/memory/handoff.md and continue."
