---
name: requirements-and-design
description: Use before building anything new or changing behavior — a feature, component, app, API, refactor with visible effects, or any "build/add/make X" request — to understand what the user actually needs, compare approaches, and get an approved design before code is written. Covers SDLC phases 01 Requirements and 02 Design, design docs and ADRs. Use it even when the request seems clear but leaves real decisions open, and for requests like "I want to make", "build me", "add a feature", "design".
---

# Requirements and Design

You are very good at building, so you tend to build what you *believe* the
user wants, and that belief is usually thinner than it feels. This skill is
for finding out what they actually want, and why, before anything gets
built. When you understand the why, you make the hundred small decisions
they never mention the way they would have made them.

(Rule 8: understand the problem first. Rule 5: document your decisions.)

## Step 0: What do you actually know?

- **Everything that matters is in the request** ("make the save button
  disabled while saving"). It's a quick, clear task. Do it, verify it, and
  say what you did. This skill is done.
- **Something non-trivial is missing:** who it's for, what success looks
  like, a choice that changes what gets built. Continue.

## Step 1: Look before you ask

In an existing project, read before your first message: the project memory
(`project-memory`: earlier decisions, the user's preferences, lessons), the
files the user pointed at, the code the change would touch, the README,
existing specs, and recent commits. Keep reading until you can explain how the relevant
parts work today and what the change would affect. Never ask what the
project already answers, and don't reopen what the user already decided.

## Step 2: The conversation

Ask a question only when its answer would change what gets built and
neither the request nor the project answers it. Otherwise state your call
and your reason as a proposal the user can correct, and keep moving.

- **One question per message.** Make it specific to their project and build
  it on their last answer ("Voting closes before the meeting, and two
  members joined this month. Does someone who joins mid-round get a vote?").
- **Open questions first, options later.** Until you know *why* they want
  it, ask open questions with no example answers attached. Options steer;
  their own words carry intent.
- **Say why you're asking** when it isn't obvious: what the answer changes.
- **Pitch your language** to the user: plain words, their vocabulary, no
  process jargon.
- **If they didn't ask for a design discussion,** end your first message
  with a light offer: "Or if you'd rather I just dive in, say so." If they
  take it, state any significant how-it-gets-built choice (platform,
  language, library) in one line, and get going.

Ground to cover (territory, not a script; never read it out as a list):

- what this is and who uses it
- why now, and what success looks like to them
- goals, non-goals, and anti-goals (what would make it a failure even if it technically works)
- constraints: platforms, deadlines, budget, existing stack, team skills
- quality needs: expected load, latency budget, devices and networks, security and privacy, accessibility
- current state: what exists, what they tried, what they've seen elsewhere and liked or hated

**Play it back.** As soon as you understand one part, describe it back in a
short paragraph. Mark what they said as theirs, and what you filled in as
your proposal with its reason. End by asking what's wrong or missing.

**Show, don't tell.** For anything visual (a screen, a layout, a flow),
include a small text sketch or ASCII mockup next to the description.

**Spike when it's cheaper.** A quick throwaway prototype is often the fastest
way to learn whether something works. Offer one when it would help. Spikes
skip tests and review, and they stay labeled throwaway. Keeping what a
spike produced is a new request that comes back through this skill.

## Step 3: Lay out the approaches

Once you understand what they want, and before writing anything up, put the
approaches in a message of their own (rule 12: everything is a trade-off):

- Come up with several real alternatives, then drop the weak ones: anything
  that works against their why, or that the existing code rules out.
- Sketch the remaining two or three concretely enough to picture, grounded
  in what the project already uses. For each one: how it works, what it
  costs (complexity, dependencies, performance, time), and what it makes
  hard later.
- Recommend one and say why. Prefer the option with less new code and
  fewer new dependencies when the outcomes are equal (rules 6 and 10).
- Ground each option in the **current** docs of the frameworks involved
  (`docs-first`). What the framework recommends today may differ from what
  you remember, and an approach built on a deprecated pattern starts out as
  tech debt.
- If there's genuinely one sensible way, say so and explain briefly why the
  others don't fit.

When the user is talking about outcomes rather than the how, they're handing
you the technical choices. Make them, and state each one in a line.

## Step 4: Size the work and write it down

| Size | Design doc |
|---|---|
| Small change | A short one: a few lines each on intent, approach, and the decisions made |
| A project | The full design (template in `references/templates.md`) |

If the work turns out to be several independent projects, say so, agree on
an order, and design them one at a time.

**Where it goes:** follow the project's convention if it has one. Otherwise
use `docs/specs/YYYY-MM-DD-<topic>-design.md`, and say where you put it.

The design doc must let a talented engineer who has never seen this
conversation plan the work without coming back with questions. It always
includes the **Approaches** section (what you considered, the trade-offs,
what was picked, and why) and the **non-functional requirements** (the
performance budget, security, robustness, and testability expectations).
Those are the requirements that get forgotten and come back in production.

For a decision that's hard to reverse (database, framework, auth model,
service boundary), also write a short ADR (template in
`references/templates.md`). Future maintainers need the "why", and it's
cheap to write now and impossible to reconstruct later.

**Builder check (projects only):** before handing the doc over, dispatch a
fresh subagent with only the doc and the repo path. Ask it to list every
question it would need answered before it could plan the work. Sort the
questions into three piles:
- **Answered already:** put the answer in the doc.
- **Minor:** decide it yourself and mark it in the doc as your call.
- **Theirs:** only the user can answer it, and the answer changes what gets
  built. Ask these in one message, most important first.

Without a subagent tool, read the doc yourself as that builder.

## The gate

<HARD-GATE>
Nothing gets built until the user approves the design: the short one for a
small change, the full one for a project. "Built" includes writing product
code, scaffolding, installing dependencies, and creating projects. Reading
and exploring are fine.

Two exceptions: the user opted out of the questions, or a spike they agreed
to (which stays throwaway).

After approval, save what must outlive this conversation to the project
memory: the chosen approach and its reason as a `decision`, and any
preference the user revealed as `user` or `feedback`. Then the next step is
`writing-plans`.
</HARD-GATE>

Why so strict: code written against a misunderstood requirement is the most
expensive code there is. It passes its tests, gets reviewed, ships, and is
wrong.

## Red flags

| Thought | Reality |
|---|---|
| "I'll offer a menu of what they might want" | Options steer. Ask them to describe it first. |
| "I'll fill in sensible defaults" | Good, but say them out loud. A default they never heard is one they couldn't reject. |
| "They said 'sounds good' to the idea" | Approval covers what you showed them. A doc you haven't written isn't approved. |
| "Non-functional stuff can wait" | Performance, security and failure handling decided late cost a rewrite. Put them in the design. |
| "The spike works, I'll keep building on it" | Keeping it is a new request. Back through the gate. |
| "I should explain the process first" | Ask your question. The process shows itself. |
