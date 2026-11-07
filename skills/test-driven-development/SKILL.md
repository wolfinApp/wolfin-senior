---
name: test-driven-development
description: Use when implementing any feature, bugfix, refactor, or behavior change, before writing the implementation code — write the failing test first, watch it fail, write minimal code to pass, then refactor. Also use when writing or changing tests, adding mocks, or when code feels hard to test. Triggers on "add tests", "write the function", "fix the bug", "اكتب تست", "سوّي الدالة".
---

# Test-Driven Development

Write the test first. Watch it fail. Write the minimal code to pass. Clean up.

**Why it matters:** a test you never saw fail proves nothing. It might test
the wrong thing, test a mock, or pass no matter what the code does. Watching
it fail is the proof that it can catch the bug. Tests written after the code
are biased by the code: they check the cases you remembered, not the ones
you'd have discovered.

## When

Always: new features, bug fixes, refactors, behavior changes.

Exceptions, only with the user's agreement: throwaway spikes, generated
code, pure configuration. If you catch yourself thinking "skip TDD just this
once", that's the rationalization this skill exists to stop.

## The iron law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Set it aside and implement fresh from the test.
Don't keep it "as a reference" and adapt it. That's testing after, with
extra steps.

## Red → Green → Refactor

### RED: write one failing test

One behavior, a clear name, real code (mocks only when unavoidable).

```typescript
// ✅ Clear name, real behavior, one thing
test('retries a failing operation until it succeeds, max 3 attempts', async () => {
  let attempts = 0;
  const op = async () => { attempts++; if (attempts < 3) throw new Error('fail'); return 'ok'; };
  expect(await retry(op)).toBe('ok');
  expect(attempts).toBe(3);
});

// ❌ Vague name, tests the mock, not the code
test('retry works', async () => {
  const mock = jest.fn().mockRejectedValueOnce(new Error()).mockResolvedValueOnce('ok');
  await retry(mock);
  expect(mock).toHaveBeenCalledTimes(2);
});
```

### Verify RED: watch it fail (mandatory)

Run it. Confirm it **fails** (an assertion failure, not an error), with the
expected message, *because the feature is missing* (not because of a typo or
an import error).
- It passes already? You're testing existing behavior. Fix the test.
- It errors? Fix the error and re-run until it fails for the right reason.

### GREEN: minimal code

Write the simplest code that passes. No extra options, no "while I'm here".

```typescript
// ✅ Just enough
async function retry<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; ; i++) {
    try { return await fn(); } catch (e) { if (i === 2) throw e; }
  }
}
// ❌ YAGNI: options nobody asked for (backoff strategies, callbacks, maxRetries)
```

### Verify GREEN: watch it pass (mandatory)

Run the test, then the **project's full suite** (`npm test`, `pytest`,
`go test ./...`, whatever the repo uses). A green run of only your file is
not a green suite. The output should be pristine, with no new warnings.
If the test fails, fix the code, not the test. If another test fails, fix it
now, and report every failure by name, including ones you didn't cause.

### REFACTOR: clean up, staying green

Only after green: remove duplication, improve names, extract helpers. Re-run
the tests after each change. Never add behavior during a refactor.

Then go back to RED for the next behavior.

## Design for testability

Hard to test usually means hard to use. Listen to the test:

| Problem | What it's telling you |
|---|---|
| Don't know how to test it | Write the API you wish you had, and the assertion first |
| Test setup is huge | The unit does too much. Split it. |
| Must mock everything | Too coupled. Inject dependencies, push I/O to the edges. |
| Test is slow | Separate pure logic from I/O, and test the logic directly |
| Flaky test | Hidden shared state or timing. See `../systematic-debugging/references/condition-based-waiting.md`. |

Aim for code that's easy to test: low complexity, automated, cheap to run,
fast. Pure functions for core logic, side effects at the boundaries.

## Writing good tests

Before writing or changing tests, adding mocks, or adding test helpers, read
`references/writing-good-tests.md`. The short version:
- Name the production change that would make this test fail. If you can't, the test is useless.
- Derive expected values by hand (literals), never with the code under test.
- Assert on real behavior, never on the existence of a mock.
- Mock only the slow or external layer, and mirror the real data structure completely.
- Test-only cleanup lives in test utilities, not in production classes.

## Bug fixes

Reproduce the bug with a failing test first. The test proves the fix and
guards against regression. To prove the regression test works: run it
(pass) → revert the fix → run it (must fail) → restore the fix → run it (pass).

## Rationalizations

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks. The test takes 30 seconds. |
| "I'll test after" | Tests written after pass immediately, which proves nothing. |
| "I already tested it manually" | Manual testing leaves no record and can't be re-run on the next change. |
| "Deleting hours of work is wasteful" | Sunk cost. Code you can't trust is the real waste. |
| "I need to explore first" | Fine. Throw the exploration away, then start with TDD. |
| "TDD slows me down" | Debugging in production is slower. |
| "The existing code has no tests" | Then add tests for the part you're changing. |

## Red flags: stop and start over

Code before the test · a test that passes immediately · can't explain why
the test failed · "I'll add tests later" · "just this once" · "it's about the
spirit, not the ritual".

## Checklist before calling it done

- [ ] Every new function or behavior has a test
- [ ] You watched each test fail, for the expected reason
- [ ] You wrote minimal code to pass
- [ ] The full suite passes, and the output is pristine
- [ ] Tests use real code (mocks only where unavoidable)
- [ ] Edge cases covered: empty, null, boundary, error, unauthorized, malformed
