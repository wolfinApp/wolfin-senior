# Domain Language

A project goes faster when the user, the code and the agent use one word for
each concept. "The materialization cascade" beats "the problem when a lesson
inside a section is given a spot on disk", in every message, every test name
and every variable. The glossary is where those words live.

## Where it lives

Most repos have one context:

```
/
├── GLOSSARY.md
└── docs/adr/
    ├── 0001-event-sourced-orders.md
    └── 0002-postgres-for-the-write-model.md
```

A repo with several bounded contexts has a `GLOSSARY-MAP.md` at the root
that points to one `GLOSSARY.md` per context and says how they relate.

Create these files lazily: the glossary when the first term is settled,
`docs/adr/` when the first ADR is needed. Follow the project's own
convention if it already has one.

## Format

```markdown
# <Context name>

<One or two sentences: what this context is and why it exists.>

## Language

**Order**:
A customer's request to buy one or more products, from checkout to delivery.
_Avoid_: purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: bill, payment request
```

## Rules

- **Be opinionated.** When several words exist for one concept, pick the best
  and list the others under _Avoid_.
- **One or two sentences per term.** Say what it is, not how it's built.
- **Only this project's concepts.** General programming terms (timeout,
  retry, cache) don't belong, however often the code uses them.
- **No implementation.** The glossary is not a spec, a scratch pad or a
  design doc. File paths, tables and classes go elsewhere.
- **Group** terms under subheadings when natural clusters appear.

## During a design conversation

- **Challenge conflicts.** "Your glossary defines *cancellation* as the whole
  order, but you mean one line item. Which is it?"
- **Sharpen fuzzy words.** "You said *account*. Do you mean the Customer or
  the User login? They're different things here."
- **Test with scenarios.** Invent concrete edge cases that force the
  boundary between two concepts into the open.
- **Check the code.** When the user says how something works, check whether
  the code agrees, and surface any contradiction.
- **Write it down now.** Update the glossary the moment a term is settled.
  Don't batch.

## ADRs: the three-part test

Offer an ADR only when all three hold:

1. **Hard to reverse:** changing your mind later has a real cost.
2. **Surprising without context:** a future reader will look at the code and
   wonder why it was done this way.
3. **A real trade-off:** there were genuine alternatives, and one was picked
   for specific reasons.

Typical ADRs: the architectural shape ("the write model is event-sourced"),
how contexts talk to each other, technology with lock-in (database, message
bus, auth provider), ownership and scope boundaries, deliberate deviations
from the obvious path ("raw SQL instead of the ORM, because..."),
constraints the code can't show ("no AWS, for compliance"), and rejected
alternatives whose rejection isn't obvious.

An ADR can be a single paragraph: the context, what was decided, and why.
Add options and consequences only when they carry real information. Number
them in sequence (`0001-slug.md`, `0002-slug.md`) and never edit an accepted
one: a new ADR supersedes it.

When the user rejects a proposal for a reason a future reviewer would need
("we tried that, the partner API rate-limits it"), offer to record it as an
ADR, so nobody proposes the same thing again in six months.
