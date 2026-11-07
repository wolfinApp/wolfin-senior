# Parallel Agents

When several problems are genuinely independent (different subsystems,
different failing test files, unrelated bugs), working them one after
another wastes time. Dispatch one agent per independent problem domain and
let them run concurrently.

## When to use it

Use it when:
- There are 2+ problems, each understandable without context from the others
- They share no files and no state, so fixing one can't change another
- Each one has a clear, checkable goal ("make `abort.test.ts` pass")

Don't use it when:
- The failures may be related. Fixing one might fix the others, so investigate together first.
- You don't yet know what's broken. Do exploratory debugging first (`systematic-debugging`).
- The agents would edit the same files or use the same resources (ports, DB, fixtures).

## Pattern

1. **Group by domain.** Example: `abort.test.ts` (abort logic),
   `batch.test.ts` (batch completion), `approval.test.ts` (race conditions).
2. **Write a focused prompt per agent.** Each one is:
   - **Scoped:** one file or subsystem
   - **Self-contained:** paste the exact error messages and test names
   - **Constrained:** "don't change code outside X", "don't just raise timeouts"
   - **Specific about output:** "return the root cause and a summary of the changes"
3. **Dispatch them all in one message.** Several dispatch calls in one
   response run in parallel. One per response runs them sequentially.
4. **Integrate:** read each summary, check whether agents touched the same
   code, run the **full** suite, and spot-check the diffs. Agents make
   systematic errors, and their success reports are claims, not evidence.

## Example prompt

```
Fix the 3 failing tests in src/agents/abort.test.ts:
1. "aborts tool with partial output": expects 'interrupted at' in message
2. "mixed completed and aborted tools": fast tool aborted instead of completed
3. "tracks pendingToolCount": expects 3 results, gets 0

These look like timing issues. Find the real cause: are they races in the
test, or bugs in the abort implementation? Replace arbitrary sleeps with
condition-based waiting. Don't just increase timeouts. Don't change code
outside src/agents/.

Return: the root cause, the changes you made (files and why), and the test command output.
```

## Common mistakes

| Mistake | Fix |
|---|---|
| "Fix all the tests" | One domain per agent |
| "Fix the race condition" (no context) | Paste the errors and the test names |
| No constraints | State what must not change |
| "Fix it" | Ask for root cause + changes + evidence |
| Trusting the summaries | Run the full suite yourself |
