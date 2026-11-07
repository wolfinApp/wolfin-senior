---
name: performance-optimization
description: Use whenever an app, site, API, or database is slow or needs to be faster, or the user asks for a performance audit, speed optimization, Core Web Vitals, load time, bundle size, slow queries, scaling, or caching. Audits 31 techniques (skeleton loading, WebP/AVIF, lazy loading, code splitting, SSR/SSG, CDN, Brotli/Gzip, caching, Redis, N+1 queries, indexes, pagination, connection pooling, job queues, debounce, virtualization, re-renders, streaming, timeouts, OpenTelemetry, RUM, performance testing, and more). It inspects the code first, reports the status, priority and impact of each, then applies only the fitting improvements, measuring before and after on slow devices and weak networks. Triggers on "slow", "optimize", "speed up", "performance", "بطيء", "حسّن الأداء", "سرّع الموقع", "التطبيق ثقيل".
---

# Performance Optimization

Performance work fails in two ways: optimizing the wrong thing (no
measurable gain, more complexity), and breaking something while doing it.
This skill prevents both. **Inspect first, measure first, change one thing
at a time, prove every gain.**

Say at the start: "Using performance-optimization to audit before changing anything."

## Non-negotiable rules

1. **Inspect the code and architecture before proposing anything.** No
   recommendation without evidence from this codebase (file:line, config,
   measurement).
2. **Classify every criterion:** applied, not applied, needs improvement,
   not applicable, or unknown.
3. **Apply a technique only if it genuinely fits this app.** Its stack, its
   scale, its users. A technique that doesn't fit is marked ➖ and left alone.
4. **No duplicate or complexity-adding changes without a benefit.** Don't add
   a second caching or data-fetching layer, memoize everything, or add
   infrastructure to fix what a code change would.
5. **Preserve all functionality, design and behavior.** Same output, same
   UI, same API contracts. Performance changes are refactors, so behavior
   must not change.
6. **Measure before and after,** including a **slow device** (4× CPU
   throttle) and a **weak network** (Slow 4G or 3G). A claimed improvement
   without numbers is not an improvement (`verification-before-completion`).

## Phase 1: Scope (2 minutes)

From the request and the repo, establish:
- **What's slow, for whom?** A page, an endpoint, a job, the whole app? On which devices and networks do users actually run it?
- **The stack:** frontend framework, rendering mode, backend, DB and ORM, hosting.
- **Targets:** use the user's targets if they have them. Otherwise the defaults are LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1, TTFB ≤ 0.8 s (field, p75), and API p95 within the budget the product needs.

Don't ask what the repo can answer. If the main complaint is unclear, ask
one question ("Which screen or action feels slowest?") and inspect in the
meantime.

## Phase 2: Inspect

1. **Run the inventory script** for facts and leads:
   ```bash
   mkdir -p .wolfin-senior && python3 <this-skill-dir>/scripts/inventory.py . > .wolfin-senior/perf-inventory.md
   ```
   (`.wolfin-senior/` holds local working files and the project memory. Add it to `.git/info/exclude` so it's never committed.)
   It reports the stack, image and font formats with sizes, build-output
   sizes, possibly unused JS dependencies, and code signals for every
   criterion. **Signals are leads, not verdicts.** A match for "redis" might
   be a comment. No match might mean the feature lives in infrastructure you
   can't see.
2. **Read the code paths that matter:** the slow screen or endpoint, the app
   entry point, the routing, data fetching, the DB access layer, server
   middleware, the build config, and the deploy config.
3. **For each criterion, check `references/checklist.md`.** It says how to
   detect it, when it applies, when to skip it, what "done right" looks
   like, and the pitfalls.

## Phase 3: Baseline measurement (before)

Measure before changing anything, using `references/measurement.md`:
- **Frontend:** Lighthouse or DevTools on (a) desktop with no throttling,
  and (b) mobile with 4× CPU and Slow 4G. Add 3G for low-end markets. Record
  LCP, INP/TBT, CLS, TTFB, total JS (gzipped), total transfer, and request
  count. Take the median of 3–5 runs.
- **Backend:** p50, p95 and p99 latency, throughput, and error rate under
  realistic concurrency (k6, autocannon, hey, wrk), plus queries per request
  and the slowest queries (`EXPLAIN ANALYZE`, the slow query log).
- **Write down the environment** (machine, build mode, data size, URL), so
  "after" is measured under the same conditions.

If you can't run the app or reach the environment, say so plainly. Use
proxies (bundle size from the build, query counts in tests, `EXPLAIN`
plans, micro-benchmarks) and label them as proxies. Give the user the exact
commands to get real numbers.

## Phase 4: Report (before any change)

Write the short audit using the exact format in
`references/report-template.md`:
- Context and baseline numbers.
- **A table of all 31 criteria:** status, evidence, priority, expected
  impact (on which metric), effort.
- An ordered plan of what you'll change first, and why.
- A separate list of items that **need the user's approval:** anything that
  adds infrastructure or cost (CDN, Redis, a queue, a load balancer,
  moving servers or regions, a telemetry vendor), changes the DB schema or
  data, changes visible design or UX, or adds a significant dependency.

Status legend: ✅ applied well · ⚠️ partial or needs improvement · ❌ not
applied, and relevant · ➖ not applicable · ❓ unknown (it lives in infra
you can't see; say what would tell you).

**Priority** = impact × confidence ÷ (effort + risk):
- **P0:** a big, measurable win on the user's actual complaint, low risk. Do it first.
- **P1:** a clear win, moderate effort or risk.
- **P2:** worthwhile, but smaller or less certain.
- **P3:** only matters at larger scale, or marginal. Note it, don't do it now.

Keep the report short: one line per criterion. Details go in the evidence
column as file:line pointers, not paragraphs.

## Phase 5: Improve, one change at a time

After the report, go on to the appropriate improvements, unless the user
asked for the report only. Do the P0 and P1 items that are in-code,
low-risk and clearly fitting. Wait for a yes on the "needs approval" items.

For each change:
1. **One technique, the smallest change that delivers it.** Follow the
   project's patterns, and reuse what's already installed (don't add SWR if
   React Query is there).
2. **Protect behavior:** run the existing tests. If the area has no tests,
   add a characterization test first (`test-driven-development`). For UI
   changes, compare screenshots before and after. The design must look the
   same.
3. **Measure the targeted metric** under the same conditions as the baseline.
4. **Keep it or revert it:** keep it only if the gain is real and outside
   the noise. If there's no measurable gain, revert it. You'd be adding
   complexity for nothing (rule 6).
5. **Commit separately,** with the numbers in the message:
   `perf(products): virtualize product grid (INP 480→120 ms on 4× CPU)`.

Stop and report when the remaining items are P3, need approval, or the
targets are met.

Log the baseline and every kept or reverted change, with its numbers, in
the project journal, and keep NOW.md pointing at the audit and the next
item (`project-memory`). An audit often spans several sessions. Without
this, the next session re-measures and re-tries things that were already
ruled out.

## Phase 6: Final report

Add a "Results" section to the report: a before/after table per metric and
condition (desktop, mobile with slow network), each change with its
measured effect, the changes reverted for no gain, the approval-pending
items, and what to monitor in production (RUM, alerts) so regressions get
caught.

## Pitfalls that make things slower or break them

| Tempting move | Why it backfires |
|---|---|
| Lazy-loading the hero or above-the-fold image | Delays LCP. Use eager loading plus `fetchpriority="high"` for the LCP image. |
| `React.memo` / `useMemo` everywhere | Comparison costs and complexity with no gain. Memoize only what the profiler shows. |
| Code-splitting tiny modules | More requests and waterfalls. Split routes and heavy, rarely used components. |
| Caching without an invalidation plan | Users see stale or wrong data. Define the TTL and invalidation first. |
| Adding Redis for one slow query | Fix the query or the index first. A cache hides the problem and adds a service. |
| Debouncing a button click | Feels broken. Debounce typing or resizing, and disable the button while submitting. |
| Optimistic UI on operations that often fail | Flicker and lost trust. Use it for actions that almost always succeed, with rollback. |
| Compressing in the app *and* at the proxy | Double work. Compress once, at the edge or proxy if one exists. |
| Retrying without timeouts or backoff | Turns a slowdown into an outage. |
| Optimizing from a dev build | Dev builds are slow by design. Always measure production builds. |
