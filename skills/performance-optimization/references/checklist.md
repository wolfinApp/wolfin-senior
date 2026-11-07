# The 31 Criteria: Detect, Decide, Apply

For each criterion: **what** it is, **applies when** / **skip when (➖)**,
how to **detect** it in code, what **✅ done right** looks like, how to
**apply** it, what to **measure**, and the **pitfalls**. The inventory
script's signals point you to files. Always read them before deciding.

## Contents

**A. Loading and rendering (frontend)**
1 Skeleton Loading · 2 WebP / AVIF · 3 Lazy Loading · 4 Code Splitting · 5 SSR / Static Generation · 6 Third-Party Scripts · 7 Font Optimization · 8 Unused Dependencies

**B. Runtime responsiveness (frontend)**
9 Debounce · 10 Optimistic UI · 11 Virtualization · 12 Unnecessary Re-renders · 13 AI Streaming

**C. Network and delivery**
14 CDN · 15 Brotli / Gzip · 16 Browser Caching · 17 Duplicate API Calls · 18 Parallel Requests · 19 Pagination · 20 API Timeouts

**D. Backend and data**
21 N+1 Queries · 22 Database Indexes · 23 Required Columns Only · 24 Connection Pooling · 25 Redis Caching · 26 Background Job Queue · 27 Server / Database Proximity · 28 Load Balancing

**E. Observability and testing**
29 OpenTelemetry · 30 Real User Monitoring · 31 Performance Testing

---

## A. Loading and rendering

### 1. Skeleton Loading
- **What:** placeholder shapes matching the final layout while content loads, instead of blank screens or full-page spinners.
- **Applies:** content that takes over ~300 ms to arrive (lists, cards, dashboards, profile pages). **Skip:** instant or local data, server-rendered pages that arrive complete.
- **Detect:** `skeleton`, `Skeleton`, `animate-pulse`, `Shimmer`, `placeholder`. Counter-signals: full-screen `Spinner`, `CircularProgress`, `Loading...`, or a conditional `if (loading) return <Spinner/>` at page level.
- **✅ Done right:** the skeleton has the same dimensions as the real content (no layout shift when data arrives), and it's shown only after a short delay or for slow loads. In Next.js, `loading.tsx` / `<Suspense fallback>`.
- **Apply:** build the skeleton from the real component's layout (reuse its container and sizes). Respect `prefers-reduced-motion` for shimmer.
- **Measure:** CLS (should not increase), perceived load (filmstrip in DevTools or WebPageTest).
- **Pitfalls:** skeletons of a different size than the content *cause* CLS. Don't change the final design.

### 2. WebP / AVIF
- **What:** modern image formats that are typically 25–50% smaller than JPEG/PNG at similar quality.
- **Applies:** any raster images in the app (photos, banners, product images, uploads). **Skip:** SVG icons and logos (already vector), images that are already WebP/AVIF.
- **Detect:** the inventory's image table (count and bytes by format, largest files). `next/image`, `@nuxt/image`, `<picture>`, `type="image/avif"`, `sharp`, an image CDN (Cloudinary, imgix, Cloudflare Images).
- **✅ Done right:** served as AVIF/WebP with a fallback, sized to the display size (`srcset`/`sizes`), compressed, with explicit `width`/`height` (or `aspect-ratio`) to prevent CLS. User uploads converted on upload or by an image CDN.
- **Apply:** prefer the framework's image component or the existing image pipeline. For static assets, convert at build time (sharp, squoosh, `vite-imagetools`), or use `<picture>` with AVIF → WebP → JPEG sources. Keep the visual quality the same, and compare visually.
- **Measure:** image bytes transferred, LCP (when the LCP element is an image).
- **Pitfalls:** AVIF encoding is slow at runtime, so do it at build time or with caching. Don't degrade quality visibly. Old email clients and some tools need fallbacks.

### 3. Lazy Loading
- **What:** defer offscreen images, iframes and heavy components until they're needed.
- **Applies:** long pages with below-the-fold media, embeds (maps, videos, social widgets), and heavy widgets not visible initially. **Skip:** above-the-fold content, and the LCP image.
- **Detect:** `loading="lazy"`, `IntersectionObserver`, `lazysizes`, `react-lazyload`. Framework image components lazy-load by default (`next/image`).
- **✅ Done right:** below-fold `<img>` and `<iframe>` have `loading="lazy"`. The LCP/hero image is eager with `fetchpriority="high"`. Placeholder dimensions are reserved.
- **Apply:** add `loading="lazy"` and `decoding="async"` to offscreen images and iframes. Use facade patterns for heavy embeds (a static thumbnail that loads the YouTube player on click).
- **Measure:** initial transfer size, request count, LCP (must not get worse).
- **Pitfalls:** lazy-loading the LCP image is one of the most common LCP regressions. Lazy content without reserved space causes CLS.

### 4. Code Splitting
- **What:** ship only the JavaScript needed for the current route or interaction, and load the rest on demand.
- **Applies:** SPAs and SSR apps with multiple routes, heavy rarely used features (editors, charts, maps, PDF export, admin panels). **Skip:** tiny apps (total JS < ~100 KB gzipped), modules used on every page.
- **Detect:** `React.lazy`, `lazy(() => import(...))`, `next/dynamic`, `defineAsyncComponent`, `loadChildren` (Angular), dynamic `import()`. The build output's chunk sizes (inventory, `next build` First Load JS, bundle analyzer). One giant `index-*.js` is a red flag.
- **✅ Done right:** route-level splitting (often automatic in Next.js, Nuxt, SvelteKit, Remix). Heavy libraries loaded only where used. No single chunk dominating the initial load.
- **Apply:** split by route first, then by heavy component. Use a bundle analyzer to find the big modules. Replace heavy libraries with lighter ones or native APIs where it's equivalent (`moment` → `date-fns`/`Intl`, full `lodash` → per-function imports).
- **Measure:** initial JS (gzipped), TBT/INP, LCP on mobile with 4× CPU.
- **Pitfalls:** splitting too fine creates request waterfalls. Lazy components need a loading state (see 1) and an error boundary.

### 5. SSR / Static Generation
- **What:** render HTML on the server (SSR) or at build time (SSG/ISR), so users see content before JavaScript runs.
- **Applies:** content and marketing pages, SEO-relevant pages, slow devices, first-visit performance. **Skip:** authenticated dashboards or internal tools where a client-side SPA is fine, apps where moving to SSR would mean a framework migration. Recommend that, don't do it unasked.
- **Detect:** the framework (Next.js, Nuxt, Remix, Astro, SvelteKit, Gatsby, Angular SSR), `getStaticProps`, `generateStaticParams`, `export const revalidate`, `prerender`, `output: 'export'`, `renderToString`. A plain CRA/Vite SPA with an empty `<div id="root">` is client-only.
- **✅ Done right:** static pages are statically generated, dynamic-but-cacheable pages use ISR or cache headers, and only truly per-request pages are SSR. Server components or islands minimize hydration.
- **Apply:** within the existing framework, change the rendering mode per page (static where data rarely changes, ISR with `revalidate` for semi-dynamic pages). In an SPA, pre-rendering key public routes may be a smaller step than migrating.
- **Measure:** TTFB, FCP and LCP on mobile with Slow 4G, server CPU.
- **Pitfalls:** SSR raises TTFB if the server does slow data fetching per request, so cache it. Watch for hydration mismatches. Never change the rendered output or the design.

### 6. Third-Party Scripts
- **What:** analytics, tag managers, chat widgets, A/B testing and ads often dominate main-thread time and bytes.
- **Applies:** any app that loads external scripts. **Skip:** none loaded.
- **Detect:** `googletagmanager`, `gtag(`, `fbq(`, `hotjar`, `intercom`, `clarity`, `segment`, `tiktok`, plus scripts from `unpkg`/`jsdelivr` in HTML, and `<script src=` without `async`/`defer`. `next/script` `strategy`. Partytown.
- **✅ Done right:** every third-party script is `async`/`defer` or loaded after interaction or idle (`next/script strategy="lazyOnload"`). There are no duplicates (GTM plus the same tags hardcoded), unused tags are removed, and heavy widgets load on intent (chat loads when the user clicks the chat button).
- **Apply:** inventory each script with its purpose and owner. Defer the non-critical ones. Use facades for chat and video. Consider a web worker (Partytown) for analytics. **Ask before removing** any tracking. That's a business decision.
- **Measure:** TBT/INP, main-thread time by origin (Lighthouse "Reduce the impact of third-party code"), transfer size.
- **Pitfalls:** deferring can change analytics accuracy or consent flows. Test that events still fire.

### 7. Font Optimization
- **What:** fonts that load fast without invisible text (FOIT) or layout shift.
- **Applies:** custom web fonts. **Skip:** system font stack only.
- **Detect:** `fonts.googleapis.com`, `@font-face`, `font-display`, `next/font`, `@fontsource/*`, `.ttf/.otf/.woff/.woff2` files (inventory), `<link rel="preload" as="font">`.
- **✅ Done right:** WOFF2, self-hosted or via `next/font` (no extra origin round-trip), `font-display: swap` (or `optional`), the critical font preloaded, subset to the needed scripts (Arabic plus Latin only if both are used), only the weights actually used, and a fallback font with metric adjustments (`size-adjust`, or `next/font` does it).
- **Apply:** convert TTF/OTF to WOFF2. Self-host or use the framework's font module. Drop unused weights and styles. Add `font-display: swap`. Preload only the 1–2 fonts used above the fold.
- **Measure:** CLS, FCP/LCP, font bytes.
- **Pitfalls:** preloading too many fonts competes with critical resources. Subsetting can drop glyphs. Test Arabic shaping and diacritics if relevant.

### 8. Unused Dependencies
- **What:** packages that are installed but unused, duplicated, or heavier than needed, inflating bundles, install time and attack surface.
- **Applies:** every project with a dependency manifest.
- **Detect:** the inventory's "possibly unused" list (a heuristic), then confirm with `npx knip` or `npx depcheck` (JS), `deptry` (Python), `cargo udeps` (Rust), `go mod tidy` (Go). Duplicates: `npm ls <pkg>`, `npx npm-dedupe`. Heavy imports: the bundle analyzer.
- **✅ Done right:** every dependency is used, dev-only tools are in devDependencies, no two libraries do the same job (two date libraries, two HTTP clients, two state managers), and imports are tree-shakeable.
- **Apply:** remove the confirmed-unused ones (one commit), move misplaced dev deps, and consolidate duplicates only when the swap is mechanical. Run the build and the full test suite after each removal.
- **Measure:** bundle size, install size, build time.
- **Pitfalls:** heuristics miss dynamic requires, CLI tools used only in scripts, peer dependencies, and plugins referenced by config strings. Verify before deleting.

## B. Runtime responsiveness

### 9. Debounce
- **What:** wait until input settles before doing expensive work (search requests, filtering, validation, autosave). Throttle limits the rate of continuous events (scroll, resize, mousemove).
- **Applies:** search-as-you-type, live filters, autosave, resize and scroll handlers that compute layout. **Skip:** discrete actions (button clicks, so disable the button while pending instead), cheap local updates.
- **Detect:** `debounce`, `throttle`, `useDebounce`, `useDeferredValue`, lodash/`use-debounce`. Counter-signal: `onChange` or `input` handlers that call `fetch`/`axios` directly.
- **✅ Done right:** ~200–400 ms debounce on search input, requests for stale queries cancelled (`AbortController`), and the input itself stays responsive (only the expensive part is debounced).
- **Apply:** use an existing utility if one is present (lodash, VueUse, `use-debounce`), or a tiny local helper. Cancel in-flight requests when a new one starts.
- **Measure:** requests per typed query, INP while typing.
- **Pitfalls:** debouncing the input value itself makes typing laggy. Forgetting cleanup on unmount causes leaks and state updates on unmounted components.

### 10. Optimistic UI
- **What:** update the UI immediately on user action, then reconcile with the server response, rolling back on failure.
- **Applies:** frequent, almost-always-successful actions (like, toggle, reorder, mark as read, add to cart, chat message). **Skip:** payments, irreversible or validation-heavy operations, anything where showing success before it happens would mislead.
- **Detect:** `onMutate` (React Query), `useOptimistic` (React 19), `optimisticResponse` (Apollo), manual pre-update patterns.
- **✅ Done right:** an instant update, rollback plus a clear error message on failure, and the server's state wins on success.
- **Apply:** use the data library already in the project. Keep rollback simple (snapshot the previous state).
- **Measure:** perceived latency per action (the time from click to visual feedback).
- **Pitfalls:** this changes visible behavior (feedback timing). Treat it as a UX change and confirm with the user if the current behavior is deliberate.

### 11. Virtualization
- **What:** render only the visible rows or items of long lists and tables (windowing).
- **Applies:** lists or tables with hundreds or thousands of rows rendered at once, chat histories, logs, large grids. **Skip:** short lists (< ~100 simple rows), paginated lists, content that must be fully in the DOM (print, Ctrl+F needs, SEO).
- **Detect:** `react-window`, `react-virtuoso`, `@tanstack/virtual`, `vue-virtual-scroller`, Angular CDK `cdk-virtual-scroll`. Mobile: `FlatList`/`FlashList` (RN), `ListView.builder` (Flutter), `RecyclerView`, `LazyColumn`. Counter-signal: `.map()` over large arrays in JSX without slicing, and `ScrollView` with many children in React Native.
- **✅ Done right:** a constant DOM size regardless of list length, stable keys, smooth scrolling, accessibility preserved.
- **Apply:** prefer pagination or infinite loading (19) when the user doesn't need all items. Otherwise virtualize with the lightest library that fits, or the platform's built-in list.
- **Measure:** DOM node count, INP and scroll FPS on 4× CPU, memory.
- **Pitfalls:** variable row heights need measurement support, it can break keyboard navigation, sticky headers and find-in-page, and the layout must look identical.

### 12. Unnecessary Re-renders
- **What:** components re-rendering when their output didn't change (new object/function props on every render, context that's too broad, state stored too high up).
- **Applies:** React, Vue or Angular apps with sluggish interactions. **Skip:** when the profiler shows no meaningful render cost.
- **Detect:** first **profile** (React DevTools Profiler "highlight updates", Vue DevTools, Angular DevTools). Code smells: inline objects or arrays passed to memoized children, one giant context with frequently changing values, derived state stored in state, `useEffect` that sets state on every render, a missing `key` or index keys on reorderable lists.
- **✅ Done right:** state colocated near where it's used, contexts split by update frequency, memoization (`React.memo`, `useMemo`, `useCallback`, `computed`, `OnPush`) **only** where the profiler showed a cost, stable keys.
- **Apply:** fix the cause first (move state down, split context, lift static values out of render). Then memoize the measured hot spots. React Compiler, if the project already uses it.
- **Measure:** profiler commit counts and durations for the interaction, INP on 4× CPU.
- **Pitfalls:** memoizing everything adds overhead and stale-closure bugs. Changing the state structure can change behavior, so test it.

### 13. AI Streaming
- **What:** stream LLM responses token by token (SSE, fetch streaming) so users see output in under a second instead of waiting for the full completion.
- **Applies:** any feature calling an LLM API for user-facing text (chat, summaries, generation). **Skip:** no AI features, outputs consumed only by code (structured JSON for a pipeline), very short responses.
- **Detect:** LLM SDK usage (`openai`, `@anthropic-ai/sdk`, `anthropic`, `@ai-sdk/*`, `langchain`, `generativeai`). Streaming signals: `stream: true`, `.stream(`, `streamText`, `text/event-stream`, `ReadableStream`, `EventSource`, `StreamingResponse`. A non-streaming call awaited, then returned whole, is ❌.
- **✅ Done right:** the server streams the tokens through to the client, the UI renders incrementally, cancellation is supported (abort on unmount or stop button), errors mid-stream are handled, and proxy buffering is disabled (`X-Accel-Buffering: no` on nginx).
- **Apply:** use the SDK's streaming mode and the framework's streaming response helpers. Keep the final rendered result identical.
- **Measure:** time to first token, total time, perceived latency.
- **Pitfalls:** proxies, CDNs and compression can buffer streams. Serverless timeouts. Markdown rendering of partial text may flicker, so render incrementally and safely.

## C. Network and delivery

### 14. CDN
- **What:** serve static assets (and cacheable pages) from edge locations near users.
- **Applies:** public web apps with users far from the origin, heavy static assets. **Skip:** internal tools on a LAN. ❓ often, because it's configured in infrastructure.
- **Detect:** hosting (Vercel, Netlify, Cloudflare Pages: CDN built in), `assetPrefix`, `CDN_URL`, CloudFront/Cloudflare/Fastly config, asset URLs on another domain. Response headers (`cf-cache-status`, `x-cache`, `age`, `via`) if a URL is available.
- **✅ Done right:** hashed static assets served from the CDN with long cache lifetimes, HTML cached where safe, a good hit ratio, and an image CDN for user content.
- **Apply:** **needs approval** (cost, DNS, infrastructure). In code you can prepare: hashed filenames, correct cache headers (16), and a configurable asset base URL.
- **Measure:** TTFB and asset download time from distant regions (WebPageTest locations), cache hit ratio.
- **Pitfalls:** caching personalized or authenticated responses. Stale deploys without hashed filenames.

### 15. Brotli / Gzip
- **What:** compress text responses (HTML, CSS, JS, JSON, SVG). Brotli is typically 15–25% smaller than gzip for static assets.
- **Applies:** all HTTP text responses. **Skip:** already-compressed formats (JPEG, PNG, WebP, video, zip). Compression is often already done by the host or CDN (❓ until checked).
- **Detect:** `compression()` (Express), `@fastify/compress`, `GZipMiddleware`, `django.middleware.gzip`, nginx `gzip on` / `brotli on` / `gzip_static`, build plugins (`vite-plugin-compression`, `compression-webpack-plugin`). Live check: `curl -sI -H 'Accept-Encoding: br,gzip' <url> | grep -i content-encoding`.
- **✅ Done right:** Brotli for static assets (pre-compressed at build time) and gzip or Brotli for dynamic responses, done **once** (at the CDN or proxy if one exists, otherwise in the app), with a minimum-size threshold.
- **Apply:** enable it at the outermost layer that the project controls. Pre-compress static builds if they're served by nginx.
- **Measure:** transferred vs. resource size for HTML, JS, CSS and JSON. Server CPU.
- **Pitfalls:** double compression, compressing tiny responses, a max Brotli level on dynamic responses (CPU-heavy), and buffering that breaks streaming (13).

### 16. Browser Caching
- **What:** HTTP cache headers so repeat visits and navigations don't re-download unchanged resources.
- **Applies:** every web app. **Skip:** never.
- **Detect:** `Cache-Control`, `max-age`, `immutable`, `ETag`, `Last-Modified`, the static file server config (`express.static` maxAge, nginx `expires`), headers in `vercel.json`/`netlify.toml`/`_headers`, service workers (`workbox`). Live: `curl -sI <asset-url>`.
- **✅ Done right:** fingerprinted assets (`app.3f9a1c.js`) get `Cache-Control: public, max-age=31536000, immutable`. HTML gets `no-cache` (revalidate) or a short max-age. API responses get explicit cache headers (`private`/`no-store` for user data, `s-maxage`/`stale-while-revalidate` for public data). ETags are used for revalidation.
- **Apply:** set headers by asset type, in the server, framework or host config. Make sure filenames are hashed before using long max-ages.
- **Measure:** repeat-view load time and bytes (Lighthouse or WebPageTest repeat view), 304 rate.
- **Pitfalls:** long caching of unhashed files means users get stuck on old versions. Caching user-specific responses publicly is a data leak.

### 17. Duplicate API Calls
- **What:** the same request fired several times: several components fetching the same data, effects re-running, StrictMode double calls treated as a bug, refetch on every mount.
- **Applies:** client apps that fetch data. **Skip:** server-rendered pages without client fetching.
- **Detect:** the Network tab (sort by URL, look for repeats on one page load). In code: files with `useEffect` plus `fetch`/`axios` (inventory co-occurrence), the same endpoint string in several components, effects with missing or unstable dependencies. Positive: React Query / TanStack Query, SWR, Apollo, RTK Query, `cache()` in React Server Components.
- **✅ Done right:** one fetch per resource per screen, deduplicated and cached by a data layer, with stale times set sensibly.
- **Apply:** if a data library exists, route the duplicate fetches through it (a shared query key). If not, lift the fetch to a common parent or a small shared hook. Only introduce a data library if duplication is widespread (needs approval, since it's a new dependency).
- **Measure:** request count per page load or interaction, LCP and INP.
- **Pitfalls:** caching changes freshness semantics. Keep data as fresh as the current behavior requires.

### 18. Parallel Requests
- **What:** run independent requests or queries concurrently instead of one after another (avoid waterfalls).
- **Applies:** sequential `await`s on independent calls, client request chains, server handlers that call several services. **Skip:** dependent calls (B needs A's result), rate-limited APIs.
- **Detect:** consecutive `await fetch`, `await db.` or `await service.` lines that don't use each other's results. The Network waterfall (a staircase pattern). Positive: `Promise.all`/`allSettled`, `asyncio.gather`, `errgroup`, `CompletableFuture.allOf`, `Task.WhenAll`.
- **✅ Done right:** independent work is started together, with partial-failure handling (`allSettled`) where one failure shouldn't kill the rest, and bounded concurrency for large fan-outs.
- **Apply:** group the independent awaits. Preload critical resources (`<link rel="preload">`, `preconnect` to API origins). For server-rendered pages, start the fetches in parallel at the top.
- **Measure:** endpoint or page latency (should approach the slowest call, not the sum).
- **Pitfalls:** unbounded parallelism can overwhelm the DB or a rate-limited API. Error semantics change (one rejection rejects `Promise.all`).

### 19. Pagination
- **What:** return and render data in pages or cursors instead of entire tables.
- **Applies:** any list endpoint or screen whose data can grow (orders, users, logs, products). **Skip:** small, bounded sets (a list of countries, settings).
- **Detect:** list endpoints and queries without `LIMIT`/`take`/`.limit()`/`paginate`. Positive: `cursor`, `offset`, `page_size`, `per_page`, `PageNumberPagination`, `.paginate(`, infinite query hooks.
- **✅ Done right:** a default and maximum page size enforced on the server, cursor (keyset) pagination for large or fast-changing tables, an index supporting the sort order (22), and the UI uses pages or infinite scroll.
- **Apply:** add server-side limits with a default that matches the current UI's needs. Keep the response shape backward compatible (add `next_cursor`, don't break existing fields). The UI change must be agreed if the visible behavior changes.
- **Measure:** response size and time, DB time, client memory and render time.
- **Pitfalls:** `OFFSET` gets slow on deep pages, so use keyset. Changing an API contract breaks clients, so version it or make it additive.

### 20. API Timeouts
- **What:** bound how long the app waits on any network call (HTTP, DB, cache, queue, LLM).
- **Applies:** every outbound call. **Skip:** never.
- **Detect:** `timeout`, `AbortController`/`AbortSignal.timeout`, `signal:`, `context.WithTimeout`, `statement_timeout`, `connectTimeout`, client config. Counter-signal: `fetch(` or `requests.get(` without a timeout. (Python `requests` has no default timeout. Many clients default to "wait forever".)
- **✅ Done right:** explicit connect and read timeouts suited to each dependency, a total request deadline below the upstream's (gateway, load balancer) timeout, retries only on idempotent calls with backoff and jitter, and a clear error or fallback for the user.
- **Apply:** add timeouts at the client-construction level (one place), not per call site. See `../../engineering-principles/references/robustness.md`.
- **Measure:** p99 latency under a slow-dependency simulation, error rate, worker and connection saturation.
- **Pitfalls:** timeouts too short for legitimately slow operations (large uploads, LLM calls). Retries without idempotency cause duplicates.

## D. Backend and data

### 21. N+1 Queries
- **What:** one query for a list, then one query per item for related data. Ten rows means 11 queries, a thousand rows means 1001.
- **Applies:** any ORM or data-access code that loops over results and touches relations. GraphQL resolvers. **Skip:** no relational data access.
- **Detect:** loops containing queries or lazy relation access (`for order in orders: order.customer.name`). ORM-specific: Django without `select_related`/`prefetch_related`, Rails without `includes`/`preload` (the Bullet gem detects it), Laravel without `with()`, Prisma `findMany` followed by per-item `findUnique`, SQLAlchemy lazy loading (use `selectinload`/`joinedload`), GraphQL without DataLoader. Best evidence: **count queries per request** (query logging, `assertNumQueries`, Debug Toolbar, Laravel Debugbar, Prisma `log: ['query']`).
- **✅ Done right:** a constant number of queries per request regardless of list size, eager loading or batching, DataLoader in GraphQL.
- **Apply:** add eager loading at the query. Add a test asserting the query count (it prevents regressions).
- **Measure:** queries per request, endpoint p95, DB time.
- **Pitfalls:** over-eager loading (joining huge relations you don't use) can be slower. Load only what's rendered (23). Large `JOIN`s can duplicate rows, so check the counts.

### 22. Database Indexes
- **What:** indexes on the columns used in `WHERE`, `JOIN`, `ORDER BY` and unique constraints, so queries don't scan whole tables.
- **Applies:** tables beyond a few thousand rows, slow queries. **Skip:** tiny tables, write-heavy tables where the extra index cost outweighs the read gain.
- **Detect:** migrations and schema (`CREATE INDEX`, `@@index`, `index=True`, `db_index=True`, `add_index`, `->index()`, `@Index`). Compare them against the query patterns in code (filters, joins, sorts, foreign keys). Postgres doesn't auto-index foreign keys. **Proof:** `EXPLAIN (ANALYZE, BUFFERS)` showing `Seq Scan` on a large table, plus the slow query log or `pg_stat_statements`.
- **✅ Done right:** indexes match the real query patterns (composite indexes in the right column order: equality columns first, then range or sort), foreign keys indexed, no unused or duplicate indexes.
- **Apply:** add the index in a migration, `CONCURRENTLY` on Postgres for big live tables. **Needs approval** for production schema changes. Verify with `EXPLAIN ANALYZE` before and after.
- **Measure:** query time and plan (index scan vs seq scan), endpoint p95, write latency (shouldn't regress meaningfully).
- **Pitfalls:** index bloat on write-heavy tables, locking during index creation, and wrong column order makes a composite index useless.

### 23. Required Columns Only
- **What:** select only the columns or fields the caller needs, not `SELECT *` or whole documents.
- **Applies:** wide tables (text/JSON/blob columns), list endpoints, API responses. **Skip:** narrow tables where every column is used.
- **Detect:** `SELECT *`, ORM calls returning full models for list views. Positive: `select: {}` (Prisma), `.only()`/`.values()` (Django), `.select()` (ActiveRecord, Knex, Mongoose), `attributes: []` (Sequelize), `load_only` (SQLAlchemy), projections, GraphQL field selection.
- **✅ Done right:** list queries fetch only the displayed fields, large columns are loaded on demand, and API responses are serialized from explicit field lists (also a security win).
- **Apply:** add projections on the hot list queries. Make sure every field the response or template uses is still selected. Tests or a response snapshot guard this.
- **Measure:** response payload size, query time, memory.
- **Pitfalls:** a missing field breaks the UI silently (undefined), so compare the responses before and after.

### 24. Connection Pooling
- **What:** reuse DB (and HTTP) connections instead of opening one per request.
- **Applies:** any server talking to a DB, especially serverless functions (where pool exhaustion is common). **Skip:** CLI scripts, SQLite.
- **Detect:** pool config (`pool`, `max`, `poolSize`, `maxPoolSize`, `connection_limit`, `CONN_MAX_AGE`, `pool_size`, HikariCP), PgBouncer, RDS Proxy, Prisma Accelerate or Data Proxy, Neon/Supabase poolers. Counter-signals: creating a new client per request (`new PrismaClient()` or `new Pool()` inside a handler), and serverless functions connecting straight to Postgres without a pooler. HTTP: keep-alive agents.
- **✅ Done right:** one pool per process, created at startup, sized for the DB's limits across all instances, and an external pooler for serverless. HTTP clients reuse connections (keep-alive).
- **Apply:** move client creation to module scope or a singleton, and configure the pool size. **Needs approval** for adding a pooler service.
- **Measure:** connection count on the DB, p95 under concurrency, connection errors.
- **Pitfalls:** too many instances × pool size exceeds the DB's `max_connections`. Transaction-mode poolers break session features (prepared statements, `SET`).

### 25. Redis Caching
- **What:** cache expensive computed or fetched results in a shared in-memory store (Redis, Memcached), or an in-process LRU for single-instance apps.
- **Applies:** expensive, frequently read, rarely changing data (config, catalog, aggregates, third-party API results), sessions and rate limits at scale. **Skip:** when the real fix is a query or index (21–23), when HTTP or CDN caching covers it (14, 16), and data that must always be fresh.
- **Detect:** `redis`, `ioredis`, `memcached`, `lru-cache`, `node-cache`, `@cache`, `cache_page`, `Rails.cache`, `Cache::remember`. What's cached, with which TTL and invalidation?
- **✅ Done right:** cache-aside with explicit TTLs, invalidation on writes, keys namespaced and versioned, stampede protection for hot keys, and the cache being down degrades to slower, not broken.
- **Apply:** if Redis or a cache already exists, use it for the measured hot path. Adding Redis **needs approval** (new infrastructure). An in-process LRU is a lighter first step for single-instance apps.
- **Measure:** hit ratio, endpoint p95, DB load.
- **Pitfalls:** stale or incorrect data, caching per-user data under shared keys (a data leak), and an unbounded memory footprint.

### 26. Background Job Queue
- **What:** move slow or non-critical work (emails, image processing, reports, webhooks, AI batch jobs, exports) out of the request into a worker.
- **Applies:** request handlers that do work the user doesn't need to wait for, or that risk timeouts. **Skip:** fast operations, and work whose result the user needs immediately.
- **Detect:** BullMQ/Bull, Celery, RQ, Dramatiq, Sidekiq, Resque, good_job, Laravel queues (`ShouldQueue`), SQS/PubSub, RabbitMQ, Kafka, Temporal, Inngest, pg-boss, graphile-worker. Counter-signal: `sendEmail`, image resizing, PDF generation, third-party calls, or big loops inside request handlers.
- **✅ Done right:** the request enqueues and responds fast (202 with a job ID, or the status shown in the UI), jobs are idempotent with retries and backoff, there's a dead-letter queue, and the queue depth is monitored.
- **Apply:** if a queue exists, move the slow step into a job. Adding a queue system **needs approval**. For small apps, a DB-backed queue (pg-boss, good_job, Laravel database driver) avoids new infrastructure.
- **Measure:** request p95, timeout rate, job latency.
- **Pitfalls:** this changes behavior (the result arrives later). The UI must communicate it, so agree with the user. Non-idempotent jobs duplicate side effects on retry.

### 27. Server / Database Proximity
- **What:** the app server and its DB in the same region (ideally the same zone or VPC). Each cross-region query adds tens to hundreds of ms.
- **Applies:** any app with a remote DB, and edge or serverless functions that call a central DB. **Skip:** both on the same host. ❓ usually: needs deploy and DB config.
- **Detect:** region settings in `vercel.json` (`regions`), `fly.toml` (`primary_region`), `serverless.yml`, `render.yaml`, Terraform, and the DB host in env examples (the region in the hostname). Edge runtime (`export const runtime = 'edge'`) talking to a single-region DB.
- **✅ Done right:** compute is pinned to the DB's region, edge functions only do work that doesn't need the DB (or use read replicas or edge caches), and chatty request paths make few round-trips.
- **Apply:** **needs approval** (deployment config). In code: reduce round-trips (batch queries, 21, 18) and avoid edge runtimes for DB-heavy routes.
- **Measure:** DB round-trip time (time a trivial `SELECT 1`), TTFB.
- **Pitfalls:** moving regions moves latency to users who are far away, so weigh where the users are.

### 28. Load Balancing
- **What:** distribute traffic across several instances or processes for throughput and availability.
- **Applies:** traffic exceeding one instance, high-availability needs, CPU-bound servers using a single core (Node without a cluster, Python with one worker). **Skip:** low-traffic apps where one instance has headroom. Often ❓ (in infrastructure).
- **Detect:** nginx `upstream`, HAProxy, cloud LB config, `replicas:` (Kubernetes, Compose), PM2 cluster mode, `cluster.fork`, gunicorn/uvicorn `--workers`, Puma workers, platform autoscaling. Statelessness check: in-memory sessions, local file uploads, and in-process caches all block horizontal scaling.
- **✅ Done right:** stateless instances (sessions in a DB or Redis, files in object storage), health checks, enough workers per instance for the available cores, autoscaling on real signals.
- **Apply:** first use all cores on one machine (workers or cluster). That's a config change. Multi-instance load balancing **needs approval** (infrastructure and cost) and requires statelessness first.
- **Measure:** throughput at the target p95, CPU per core, error rate under load (31).
- **Pitfalls:** sticky in-memory state breaks behind an LB, and WebSockets need sticky sessions or a pub/sub layer.

## E. Observability and testing

### 29. OpenTelemetry
- **What:** vendor-neutral tracing, metrics and logs, so you can see where time goes across services, DB and external calls in production.
- **Applies:** backend services, especially multi-service systems or where slow requests can't be reproduced locally. **Skip:** static sites, tiny apps with no production traffic yet (note as P3).
- **Detect:** `@opentelemetry/*`, `opentelemetry-*`, `otel` config, `OTEL_EXPORTER_*` env vars, or existing APM (Datadog `dd-trace`, New Relic, Honeycomb, Sentry performance, AWS X-Ray, Elastic APM).
- **✅ Done right:** auto-instrumentation for HTTP, DB and queue clients, trace context propagated between services, sampling configured, key spans with useful attributes, and dashboards for p95 by route.
- **Apply:** if an APM exists, use it. Don't add a second one. Adding OpenTelemetry plus an exporter or backend **needs approval** (vendor, cost, data policy). Keep personal data out of span attributes.
- **Measure:** it is the measurement. Check overhead (should be a few %) with sampling.
- **Pitfalls:** high-cardinality attributes (user IDs as metric labels) explode costs. Logging request bodies leaks data.

### 30. Real User Monitoring (RUM)
- **What:** collect performance from real users' devices and networks (Core Web Vitals at p75), not just from lab tests.
- **Applies:** any production web app with real users. **Skip:** pre-launch, internal tools (P3).
- **Detect:** `web-vitals` (`onLCP`, `onINP`, `onCLS`), `reportWebVitals` (Next.js), `@vercel/speed-insights`, Sentry browser performance, Datadog RUM, New Relic Browser, Cloudflare Web Analytics. CrUX data for public sites (PageSpeed Insights field data).
- **✅ Done right:** LCP, INP, CLS and TTFB reported with route and device or connection dimensions, dashboards on p75, and alerts on regressions.
- **Apply:** the lightest option is `web-vitals` sending to an existing analytics or logging endpoint, or the host's built-in feature. A new vendor **needs approval** (privacy and consent).
- **Measure:** it is the measurement. Compare field data with lab results.
- **Pitfalls:** consent and privacy laws (GDPR), and sampling bias. Lab numbers ≠ field numbers, and users experience the field ones.

### 31. Performance Testing
- **What:** repeatable load, stress and benchmark tests (and performance budgets in CI), so regressions are caught before users notice.
- **Applies:** APIs with meaningful traffic, critical user journeys, before launches or big changes. **Skip:** prototypes (P3).
- **Detect:** k6 scripts, Artillery, Locust, JMeter, Gatling, autocannon, `wrk`, Lighthouse CI (`lighthouserc`, `@lhci/cli`), `size-limit`/bundlesize budgets, `pytest-benchmark`, Go benchmarks (`func Benchmark`), `hyperfine`.
- **✅ Done right:** scripted scenarios with realistic data and concurrency, thresholds (p95 < X ms, error rate < 1%), run in CI or before release, a Lighthouse CI or bundle-size budget for the frontend.
- **Apply:** add a small k6 or autocannon script for the critical endpoints, and a Lighthouse CI or `size-limit` budget. Start with the scenarios this audit measured, so the baseline becomes a regression test.
- **Measure:** the trend over time, and fail the build on budget regressions.
- **Pitfalls:** load testing production without permission. Unrealistic data (empty DB) hides problems. Noisy CI runners give flaky thresholds, so leave margins.
