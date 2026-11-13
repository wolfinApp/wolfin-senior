# Writing Good Tests

Read this when writing or changing tests, adding mocks, or adding test
helpers.

A test exists to catch a specific break. Two principles govern everything:

```
1. Every test names the break it catches
2. Every test exercises the real thing
```

## Principle 1: Name the break

Before writing the test body, answer: **what production change would make
this test fail, and is that change a bug or a decision?** A test earns its
place by catching a wrong branch, a missing side effect, a wrong argument, a
boundary case, or a broken contract.

**Derive expectations independently.** Use literals and hand-checked
fixtures. Table-driven tests with literal expected values are ideal.

```typescript
// ❌ Mirror assertion: the same builder computes both sides, so it's always true
const expected = buildQuery({ tag: 'urgent' });
expect(buildQuery({ tag: 'urgent' })).toBe(expected);

// ✅ Hand-derived literal
expect(buildQuery({ tag: 'urgent' })).toBe('tag:"urgent"');
```

**No change detectors.** If only intentional decisions can fail a test (a
constant's value, exact wording, private structure), it fires on every
redesign and sleeps through real bugs. Instead of
`expect(MAX_RETRIES).toBe(5)`, test "a failing call is retried 5 times and
the 6th attempt never happens."

**Behavior, not text.** Don't grep a script or config for a line. Run it
against controlled inputs and assert outputs, side effects or exit codes.

**Your code, not the framework.** Test the contract at your boundaries: the
route you register, the query you emit, the payload you produce. Don't test
that the framework calls your handler. Constructors, getters and trivial
forwarding earn tests only when they validate, normalize, default, derive,
or cause side effects.

## Principle 2: Exercise the real thing

**A mock earns no assertions.** An assertion on a mock passes when the mock
exists and says nothing about the component.

```typescript
// ❌ Tests the mock
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
// ✅ Tests real behavior
expect(screen.getByRole('navigation')).toBeInTheDocument();
```

**Mock at the right level.** Learn every side effect of the real method
before replacing it. Mock only at **system boundaries**: third-party APIs,
payment and email providers, the clock, randomness, and sometimes the
database or file system (prefer a test database or an in-memory stand-in).
Never mock your own modules or internal collaborators: that tests the
wiring, not the behavior, and breaks on every refactor.

**Make boundaries easy to replace.** Pass external clients in rather than
constructing them inside (`charge(order, paymentClient)`, not `new
StripeClient()` in the body). Prefer one function per external operation
(`getUser`, `createOrder`) over one generic `fetch(endpoint, options)`, so
each double returns one shape with no branching in the test setup.

**Make doubles specific.** When arguments, call counts or ordering are part
of the contract, assert them. Give each branch (success, error, malformed)
its own fixture.

**Mirror real data completely.** Mock responses must have the full real
structure, not just the fields this test reads. Partial mocks pass while the
integration breaks.

**Production classes carry production methods only.** Cleanup that only
tests need (`reset()`, `destroy()`) goes in test utilities.

**Prefer real components over complex mocks.** When mock setup outgrows the
test logic, switch to an integration test.

## The mutation check

Before finishing, mentally mutate the production code. At least one test
should fail for each realistic mutation:
- wrong constant or argument
- wrong branch taken
- missing state change or side effect
- empty or default return
- missing validation for zero, empty, null, unauthorized, or malformed input

A mutation nothing catches marks a behavior as unprotected.

## Warning signs

- Setup and assertion share the same object, so equality is guaranteed
- **Tautological:** the expected value is computed the way the code computes
  it (`expect(total(items)).toBe(items.reduce(...))`), so the test passes by
  construction. Use a literal from an independent source: `toBe(15)`
- The test can only fail through a crash or a missing selector
- It fails on every intentional change and never on accidental breakage
- Expected values are hidden behind loops or helpers
- It asserts on a `*-mock` test ID
- A method is called only from test files
- Mock setup is more than half the test
- "Mocking just to be safe"

## Test pyramid in one line

Many fast unit tests for logic, fewer integration tests for boundaries (DB,
HTTP, queues), and a handful of end-to-end tests for critical user journeys.
Each test lives at the lowest level that can catch the break.
