# Condition-Based Waiting

Flaky tests often guess at timing with arbitrary delays. They pass on a fast
laptop and fail under load or in CI.

**Principle:** wait for the condition you actually care about, not a guess
about how long it takes.

## Use it when

- Tests contain `setTimeout`, `sleep`, `time.sleep()`, or `Thread.sleep()` to "let things settle"
- Tests pass alone and fail in parallel or in CI
- You're waiting for async work: events, state changes, files, DB rows, DOM updates

Not when you're testing timing itself (debounce intervals, throttling, TTLs).
For that, use fake timers and document the value.

## Pattern

```typescript
// ❌ Guessing
await new Promise(r => setTimeout(r, 50));
expect(getResult()).toBeDefined();

// ✅ Waiting for the condition
await waitFor(() => getResult() !== undefined, 'result to be set');
expect(getResult()).toBeDefined();
```

Generic helper:

```typescript
async function waitFor<T>(cond: () => T | undefined | null | false, what: string, timeoutMs = 5000): Promise<T> {
  const start = Date.now();
  for (;;) {
    const v = cond();            // read fresh state every iteration
    if (v) return v;
    if (Date.now() - start > timeoutMs) throw new Error(`Timed out after ${timeoutMs}ms waiting for ${what}`);
    await new Promise(r => setTimeout(r, 10));
  }
}
```

```python
def wait_for(cond, what, timeout=5.0, interval=0.01):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if (v := cond()):
            return v
        time.sleep(interval)
    raise TimeoutError(f"timed out after {timeout}s waiting for {what}")
```

Most frameworks have one built in. Prefer it: Testing Library `waitFor` /
`findBy*`, Playwright auto-waiting `expect(locator).toBeVisible()`, Cypress
retries, pytest-asyncio with `asyncio.wait_for`, Awaitility in Java.

## Quick patterns

| Waiting for | Condition |
|---|---|
| An event | `events.find(e => e.type === 'DONE')` |
| A state | `machine.state === 'ready'` |
| A count | `items.length >= 5` |
| A file | `fs.existsSync(path)` |
| A DOM element | `await screen.findByRole('dialog')` |

## Mistakes

- **Polling too fast** (every 1 ms): wastes CPU. Use around 10 ms.
- **No timeout:** hangs forever. Always time out, with a clear message.
- **Stale data:** reading state once before the loop. Call the getter inside it.

## When a fixed delay *is* right

Wait for the triggering condition first, then use a delay derived from known
timing, and comment it:

```typescript
await waitForEvent(mgr, 'TOOL_STARTED');
await sleep(200); // tool ticks every 100 ms; need 2 ticks to observe partial output
```
