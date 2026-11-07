# Design Templates

Two templates: the full design doc for a project, and the ADR for a single
hard-to-reverse decision. Drop sections that genuinely don't apply, but say
"None" instead of silently omitting the non-functional ones. An empty
section you checked is information. A missing one is a question.

---

## Full design doc

```markdown
# <Feature / Project Name> — Design

**Date:** YYYY-MM-DD   **Status:** Draft | Approved   **Owner:** <name>

## 1. Intent
What this is, who it's for, and why it matters now. Two or three sentences
in the user's terms.

## 2. Success criteria
How we'll know it worked: observable outcomes, ideally measurable
("checkout completes in < 2 s on a mid-range phone over 4G").

## 3. Scope
- **Goals:** ...
- **Non-goals:** things we're deliberately not doing now
- **Anti-goals:** what would make this a failure even if it technically works

## 4. Current state
How the relevant parts work today (files, modules, data flow). What this
change touches.

## 5. Constraints
Stack, platforms, deadlines, team, compatibility, budget, regulations.

## 6. Approaches considered
| Approach | How it works | Pros | Cons / cost | Verdict |
|---|---|---|---|---|
| A | ... | ... | ... | **Chosen**, because ... |
| B | ... | ... | ... | Rejected, because ... |

## 7. Design
- Components and their responsibilities (one responsibility each)
- Interfaces between them (signatures, API contracts, events)
- Data model and migrations
- Key flows (sequence in a few numbered steps, or a small diagram)
- UI sketch (ASCII) if there's a screen

## 8. Non-functional requirements
- **Performance:** latency/throughput budgets, payload and bundle budgets, target devices and networks
- **Security:** authn/authz, input validation, secrets, data exposure, abuse cases
- **Robustness:** what happens on bad input, disk failure, network timeouts, overload, partial failure
- **Observability:** logs, metrics, traces, alerts that tell us it's healthy
- **Testability:** how it will be tested (unit / integration / e2e), what is hard to test and how we handle it
- **Accessibility / i18n:** RTL, languages, screen readers, if relevant

## 9. Decisions
| Decision | Made by | Reason |
|---|---|---|
| Use PostgreSQL full-text search instead of Elasticsearch | User | Fewer moving parts; data < 1M rows |
| Debounce search input at 300 ms | Claude (my call) | Standard UX value; cheap to change |

## 10. Risks and open questions
Biggest risks first, each with a mitigation. Open questions with who answers them.

## 11. Rollout
Feature flag? Migration order? Backward compatibility? Rollback plan?

## 12. Left to the builder
Choices a competent engineer can make without changing what gets built.
```

---

## ADR (Architecture Decision Record)

One file per decision, numbered, never edited after acceptance. A new
decision supersedes an old one. Location: the project's convention, or
`docs/adr/NNNN-<short-title>.md`.

```markdown
# NNNN. <Decision title in present tense, e.g. "Use Redis for session storage">

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded by NNNN

## Context
The forces at play: the problem, constraints, requirements, and what
makes this decision necessary now.

## Options
1. **<Option A>**: one line. Pros / cons.
2. **<Option B>**: one line. Pros / cons.
3. **Do nothing**: what happens if we don't decide.

## Decision
We will <option>, because <the deciding reasons>.

## Consequences
- What becomes easier
- What becomes harder, or what we're giving up
- Follow-up work this creates
- How we'd know it was the wrong call, and what reversing it would cost
```
