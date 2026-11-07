# Measuring Performance: Before and After

A number is only comparable with another number taken under the **same
conditions.** Record the conditions every time.

## Protocol

1. **Production build**, never dev mode (`npm run build && npm run start`,
   `DEBUG=False`, a release build for mobile).
2. **Same data, same machine, same URL, same build flags** before and after.
3. **3–5 runs, report the median.** Lab results vary by ±10% or more. A
   change smaller than the noise is not a win.
4. **Two device and network profiles at minimum:**

| Profile | CPU | Network | Represents |
|---|---|---|---|
| Desktop | no throttling | no throttling (or cable) | Best case |
| **Slow device + weak network** | **4× slowdown** | **Slow 4G** (≈150 ms RTT, ≈1.6 Mbps down) | Mid/low-end phones, which is most real users |
| Very weak (optional) | 6× slowdown | 3G (≈300 ms RTT, ≈400 Kbps–1.6 Mbps) | Low-end markets, congested networks |

Lighthouse's default mobile run already simulates roughly 4× CPU and Slow 4G.

5. **Record the environment** in the report: date, commit, machine, browser
   version, build mode, data size, and URL.

## Frontend

### Lighthouse (lab)
```bash
# Mobile (default: simulated Slow 4G + 4× CPU), performance only, JSON for comparison
npx lighthouse http://localhost:3000/products --only-categories=performance \
  --output=json --output-path=./.wolfin-senior/lh-before-mobile.json --chrome-flags="--headless=new"

# Desktop profile
npx lighthouse http://localhost:3000/products --preset=desktop --only-categories=performance \
  --output=json --output-path=./.wolfin-senior/lh-before-desktop.json --chrome-flags="--headless=new"

# Several runs with Lighthouse CI (median is reported)
npx @lhci/cli collect --url=http://localhost:3000/products --numberOfRuns=5
```
Read these from the JSON: `audits['largest-contentful-paint'].numericValue`,
`audits['total-blocking-time'].numericValue` (the lab proxy for INP),
`audits['cumulative-layout-shift'].numericValue`,
`audits['server-response-time'].numericValue`,
`audits['total-byte-weight'].numericValue`, and `audits['network-requests']`.

```bash
node -e 'const r=require(process.argv[1]).audits;for(const k of ["largest-contentful-paint","total-blocking-time","cumulative-layout-shift","server-response-time","total-byte-weight"])console.log(k, Math.round(r[k].numericValue*1000)/1000)' ./.wolfin-senior/lh-before-mobile.json
```

### Chrome DevTools (manual, interactions)
Performance panel → CPU: 4× slowdown, Network: Slow 4G → record the
interaction (typing in search, opening a modal, scrolling a list). Read the
INP and long tasks. Use the React or Vue DevTools profiler for render counts.

### Playwright with throttling (scripted interactions)
```typescript
const client = await page.context().newCDPSession(page);
await client.send('Emulation.setCPUThrottlingRate', { rate: 4 });
await client.send('Network.emulateNetworkConditions', {
  offline: false, latency: 150, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8,
});
const t0 = Date.now();
await page.goto(url, { waitUntil: 'networkidle' });
console.log('load ms', Date.now() - t0);
```

### Bundle size
| Tool | Command |
|---|---|
| Next.js | `next build` (prints First Load JS per route). `ANALYZE=true next build` with `@next/bundle-analyzer` |
| Vite | `npx vite-bundle-visualizer` |
| Webpack | `webpack-bundle-analyzer` on `stats.json` |
| Any | `npx source-map-explorer 'dist/**/*.js'` |
| Gzipped size of a file | `gzip -c file.js \| wc -c`, and `brotli -c file.js \| wc -c` |

### Field data (real users)
PageSpeed Insights (CrUX field data for public URLs), the RUM tool if one
is installed (criterion 30). Field p75 is what users actually experience.

## Backend

### Load testing
```bash
# autocannon (Node): 50 connections, 30 s
npx autocannon -c 50 -d 30 http://localhost:3000/api/orders

# hey
hey -z 30s -c 50 http://localhost:3000/api/orders

# wrk
wrk -t4 -c50 -d30s --latency http://localhost:3000/api/orders
```

k6 with thresholds (reusable as a regression test, criterion 31):
```javascript
import http from 'k6/http';
import { check } from 'k6';
export const options = {
  vus: 50, duration: '30s',
  thresholds: { http_req_duration: ['p(95)<300'], http_req_failed: ['rate<0.01'] },
};
export default function () {
  const res = http.get('http://localhost:3000/api/orders?page=1');
  check(res, { 'status 200': (r) => r.status === 200 });
}
```
Record **p50, p95, p99, requests/sec, and error rate.** Use realistic data
volumes, because an empty DB hides N+1 queries and missing indexes.
Never load-test production or shared environments without explicit
permission.

### Database
```sql
-- PostgreSQL: the real plan with timing and buffer usage
EXPLAIN (ANALYZE, BUFFERS) SELECT ... ;
-- Top queries by total time (needs pg_stat_statements)
SELECT query, calls, mean_exec_time, total_exec_time FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
-- MySQL 8
EXPLAIN ANALYZE SELECT ... ;
```
Look for `Seq Scan` on large tables, row estimates far from the actuals,
`Sort` spilling to disk, and nested loops over many rows.

**Queries per request** (the N+1 proof):
| Stack | How |
|---|---|
| Django | `django-debug-toolbar`, or `with self.assertNumQueries(3):` in tests |
| Rails | `bullet` gem, log query counts |
| Laravel | Debugbar, `DB::listen`, `DB::enableQueryLog()` |
| Prisma | `new PrismaClient({ log: ['query'] })` and count |
| SQLAlchemy | `echo=True`, or an event listener counting `before_cursor_execute` |
| TypeORM / Sequelize | `logging: true` |

### Micro-benchmarks
`hyperfine 'node script.js'`, `pytest-benchmark`, Go `testing.B`, JMH. Use
them only for hot functions you've already identified by profiling.

### Profilers
Node `--cpu-prof` or `clinic flame`, Python `py-spy record` or `cProfile`,
Go `pprof`, Java async-profiler or JFR, Ruby `stackprof`/`rbspy`. Profile
under load to find where time actually goes before optimizing anything.

## Mobile apps
React Native: Perf Monitor, Flipper or React Native DevTools, and release
builds only. Flutter: DevTools Performance view in `--profile` mode. Native:
Xcode Instruments and Android Studio Profiler. Test on a real low-end
device when possible.

## When you can't measure

Say so in the report and use labeled proxies: bundle size from `build`,
query counts from tests, `EXPLAIN` on a local copy, request counts from
reading the code. Give the user the exact commands from this file to run in
their environment, and the before/after numbers to compare.
