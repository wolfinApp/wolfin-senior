# Robustness

A robust service keeps behaving sensibly when the world misbehaves. The four
classic threats are input errors, disk failure, network overload, and
intentional attack.

## Input errors

- Validate at the boundary with a schema (Zod, Pydantic, Joi, class-validator,
  JSON Schema). Check type, range, length, format and required fields.
- Reject invalid input with a clear message saying what was wrong and what
  was expected. Don't silently coerce bad values into defaults.
- Handle the boring edge cases: empty strings, empty lists, `null`, zero,
  negative numbers, very large inputs, Unicode and RTL text, time zones,
  duplicate submissions.
- Put limits on everything: request body size, page size, upload size,
  string length, and array length.

## Disk and resource failure

- Writes can fail (disk full, permissions, read-only filesystem). Check
  results and surface errors.
- Write atomically: write to a temp file, then rename. A crash mid-write
  then never leaves a half-written file.
- Always release resources: `with` / `using` / `try-finally` / `defer` for
  files, connections, locks and temp files.
- Don't assume local disk persists in containers or serverless. Use object
  storage for anything that must survive.

## Network overload and dependency failure

- **Timeouts on every outbound call**: HTTP, DB, cache, queue. The default in
  many clients is "wait forever", which turns one slow dependency into a
  full outage as threads and connections pile up.
  ```typescript
  const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
  ```
  ```python
  requests.get(url, timeout=(3, 10))  # connect, read
  ```
- **Retry only idempotent operations,** and only a few times, with
  exponential backoff and jitter. Retries without backoff cause retry storms.
  ```
  delay = min(cap, base * 2^attempt) * random(0.5, 1.0)
  ```
- **Idempotency keys** for operations that must not run twice (payments,
  orders, emails), so client retries are safe.
- **Circuit breaker** for flaky dependencies: after N failures, fail fast
  for a cooldown period instead of hammering a struggling service.
- **Graceful degradation:** if recommendations are down, show the page
  without them. Decide what's essential and what's optional.
- **Bound your queues and pools.** An unbounded in-memory queue just moves
  the crash to later. Apply backpressure: reject with 429 or 503 rather than
  accepting work you can't finish.
- **Load shedding and rate limiting** protect the service from overload,
  intentional or not.

## Intentional attack

See `security.md`. Robustness-specific: rate limits, request size limits,
timeouts on slow clients (slowloris), limits on expensive operations (regex
on user input can cause ReDoS, and deeply nested JSON or GraphQL queries
need depth and complexity limits).

## Failing well

- **Fail fast and loudly** on programmer errors and invalid state. A crash
  with a clear message beats corrupt data.
- **Errors carry context:** what operation, which IDs, what was expected.
  `Error: failed to charge order 812 (gateway timeout after 5s)` beats
  `Error: failed`.
- **Don't swallow exceptions.** An empty `catch {}` hides the next incident.
  If you catch, either handle it meaningfully or rethrow with context.
- **Structured logs** (JSON, with request IDs) so incidents can be traced
  across services.
- **Health checks** that actually test dependencies (a readiness probe),
  separate from "the process is alive" (a liveness probe).

## Review questions

1. What happens if this input is empty, huge, malformed, or duplicated?
2. What happens if the DB, cache or API is slow? Down? Returns garbage?
3. Is every network call bounded by a timeout? Are retries safe and limited?
4. Can a crash halfway through leave inconsistent state?
5. Will the error message tell the on-call engineer what to do?
