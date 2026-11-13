---
name: requirements-and-design
description: Use before building anything new or changing behavior — a feature, component, app, API, refactor with visible effects, or any "build/add/make X" request — to understand what the user actually needs and get an approved design before code is written. Asks the open decisions in rounds, each with a recommended answer, looks up facts instead of asking, keeps a shared glossary of domain terms, prototypes questions talk can't settle, compares approaches, and writes the design doc and ADRs. Covers SDLC phases 01 Requirements and 02 Design. Use it even when the request seems clear but leaves real decisions open, and for "I want to make", "build me", "add a feature", "design", "grill me".
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

## Step 2: The conversation, in rounds

Ask a question only when its answer would change what gets built and
neither the request nor the project answers it. Otherwise state your call
and your reason as a proposal the user can correct, and keep moving.

Map the open decisions as a **design tree**: each decision branches into
the ones that depend on it. The **frontier** is every open decision whose
prerequisites are already settled. Work the tree in **rounds**:

- **Start with the why.** Until you know *why* they want it, ask that alone,
  open, with no example answers attached. Options steer; their own words
  carry intent.
- **Then ask the whole frontier in one message,** numbered, at most five.
  A question whose answer depends on another question still open belongs to
  a later round.
- **Recommend an answer for each,** worded so that "yes" accepts it. Make
  each question specific to their project and build it on what they already
  said ("Voting closes before the meeting, and two members joined this
  month. Should someone who joins mid-round get a vote?").
- **Facts are yours, decisions are theirs.** Never ask what you can look up
  (the code, the docs, the config, one command). When a frontier question
  needs a fact, find it yourself, or send a fresh subagent to find it while
  you ask the rest of the round.
- **Recompute after every round.** Settled answers unlock the questions that
  hung off them.

Format a round like this:

```
**Q1. <short title>**: <the question, with the choices if there are any>
→ Recommended: <your answer, and the one-line reason>

**Q2. ...**
```

**Done when the frontier is empty:** every branch visited, nothing silently
assumed. Then play the whole picture back (below) and wait for the user to
confirm it before Step 3.

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

**Speak the project's language.** If the project has a `GLOSSARY.md`, use
its terms in every question, doc and name. When the user uses a word that
conflicts with it, or a vague one ("account": the customer or the login?),
say so and settle on one term. Record each settled term right away, and
offer an ADR only for decisions that pass the three-part test. Format and
rules: `references/domain-language.md`.

**Prototype when talk can't settle it.** Some questions need a runnable
answer. Build a throwaway prototype that answers exactly one question:
- **"Does this logic or state model hold up?"** One self-contained HTML
  file with buttons that drive the state through the hard cases, showing the
  full state after every action, so even a non-developer can try it.
- **"What should this look like?"** Two to four radically different
  variations on one route, switchable with a URL parameter.

Prototypes are named and placed so nobody mistakes them for product code,
start with one command, keep state in memory, and skip tests and polish.
When it has answered the question, write the question and the verdict into
the design doc. Keeping the prototype's code is a new request that comes
back through this skill.

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

Write an ADR (template in `references/templates.md`) when a decision is
all three: **hard to reverse** (database, framework, auth model, service
boundary), **surprising without context** (a future reader would ask "why
did they do it this way?"), and **the result of a real trade-off**. Future
maintainers need the "why", and it's cheap to write now and impossible to
reconstruct later. If any of the three is missing, skip the ADR: an easy
decision gets reversed, an obvious one needs no record.

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

Two exceptions: the user opted out of the questions, or a prototype they agreed
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
| "I'll ask one thing and wait" | Ask the whole frontier, each with your recommendation. One question per message wastes their time. |
| "Which version are you on?" | That's a fact. Look it up yourself. Only decisions go to the user. |
| "I'll fill in sensible defaults" | Good, but say them out loud. A default they never heard is one they couldn't reject. |
| "They said 'sounds good' to the idea" | Approval covers what you showed them. A doc you haven't written isn't approved. |
| "Non-functional stuff can wait" | Performance, security and failure handling decided late cost a rewrite. Put them in the design. |
| "The prototype works, I'll keep building on it" | Keeping it is a new request. Back through the gate. |
| "I should explain the process first" | Ask your question. The process shows itself. |
