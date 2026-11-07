# Audit Report Template

Use this exact structure. Write the prose in the user's language (Arabic if
they wrote in Arabic). Keep technical names (WebP, N+1, LCP) as they are.
Save it to `docs/performance/YYYY-MM-DD-audit.md` (or the project's
convention), and show the summary in chat.

```markdown
# Performance Audit — <App> — <YYYY-MM-DD>

## Context
- **Stack:** <framework / rendering mode / backend / DB+ORM / hosting>
- **Scope inspected:** <routes, endpoints, modules read>
- **Main complaint:** <what's slow, for whom>
- **Measured on:** <commit, machine, build mode, data size, URL>

## Baseline (before)
| Metric | Desktop | Mobile 4× CPU + Slow 4G | Target |
|---|---|---|---|
| LCP | 1.4 s | 4.8 s | ≤ 2.5 s |
| TBT (lab proxy for INP) | 90 ms | 1,250 ms | ≤ 200 ms |
| CLS | 0.02 | 0.18 | ≤ 0.1 |
| TTFB | 0.3 s | 0.9 s | ≤ 0.8 s |
| JS shipped (gzip) | 610 KB | 610 KB | — |
| Requests / transfer | 84 / 3.1 MB | 84 / 3.1 MB | — |
| `GET /api/orders` p95 @50 conns | 820 ms | — | ≤ 300 ms |
<Label proxies clearly: "(proxy: from build output)". Write "not measured, reason: ..." where applicable.>

## Status of all 31 criteria
Legend: ✅ applied well · ⚠️ partial / needs improvement · ❌ not applied (relevant) · ➖ not applicable · ❓ unknown
Priority: P0 do first · P1 clear win · P2 worthwhile · P3 later / at scale

| # | Criterion | Status | Evidence | Priority | Expected impact | Effort |
|---|---|---|---|---|---|---|
| 1 | Skeleton Loading | ⚠️ | `ProductList.tsx:40` full-page spinner | P2 | Perceived speed, CLS | S |
| 2 | WebP / AVIF | ❌ | 38 PNG/JPG in `public/` = 9.2 MB, largest `hero.png` 2.1 MB | P0 | LCP −1–2 s on mobile | S |
| 3 | Lazy Loading | ⚠️ | `<img>` without `loading` in `Gallery.tsx`; hero OK | P1 | Initial bytes −40% | S |
| … | … | … | … | … | … | … |
| 21 | N+1 Queries | ❌ | `orders/service.ts:55` loops `findUnique` per item (≈101 queries/request) | P0 | p95 820 → ~150 ms | S |
| 27 | Server / DB Proximity | ❓ | No region config in repo; DB host `eu-west-1` | — | Up to −80 ms/query | — |
<Every one of the 31 rows. One line each. Effort: S (< 1 h) · M (half a day) · L (days).>

## Plan (in this order)
1. **#21 N+1 on /api/orders**: biggest measured cost, low risk, one file.
2. **#2 WebP/AVIF for static images**: LCP image is a 2.1 MB PNG.
3. …

## Needs your approval
- **#25 Redis caching**: adds a service (cost + ops). Only worthwhile after #21/#22 if p95 is still above target.
- **#14 CDN**: DNS + hosting change.
- **#22 Index on `orders(customer_id, created_at)`**: production schema migration.

## Not applicable
#13 AI Streaming (no LLM features) · #11 Virtualization (lists ≤ 20 items) · …
```

After the improvements, append:

```markdown
## Results (after)
| Change | Commit | Metric | Before | After | Kept? |
|---|---|---|---|---|---|
| #21 Eager-load order items | a1b2c3d | `/api/orders` p95 @50 | 820 ms | 140 ms | ✅ |
| #2 Hero → AVIF + srcset | d4e5f6a | Mobile LCP | 4.8 s | 2.6 s | ✅ |
| #12 Memo on `Row` | 9f8e7d6 | INP while filtering | 210 ms | 205 ms | ❌ reverted (within noise) |

| Metric | Before (desktop / mobile) | After (desktop / mobile) |
|---|---|---|
| LCP | 1.4 s / 4.8 s | 1.0 s / 2.4 s |
| … | … | … |

**Behavior check:** <tests run + result; screenshots compared; API responses diffed>
**Still open:** <approval-pending items, P2/P3 items>
**Monitor in production:** <RUM metric / dashboard / alert that would show a regression>
```
