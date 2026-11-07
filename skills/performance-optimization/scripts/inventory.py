#!/usr/bin/env python3
"""Performance inventory: facts and leads for the 31-criterion audit.

Usage: python3 inventory.py [repo_path] [--examples N]

Prints Markdown. Everything here is a hint for where to read, never a
verdict: a match may be a comment, and a missing match may mean the feature
lives in infrastructure outside the repo. Standard library only.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", "out", ".nuxt", ".output",
    ".svelte-kit", ".astro", "vendor", "venv", ".venv", "env", "__pycache__",
    "target", "coverage", ".turbo", ".cache", ".parcel-cache", "Pods", ".gradle",
    ".idea", ".vscode", ".dart_tool", ".expo", "bower_components", ".wolfin-senior",
    ".terraform", "tmp", "storage",
}
BUILD_DIRS = ["dist", "build", ".next/static", "out", ".output/public", "public/build"]
LOCK_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "poetry.lock",
    "Pipfile.lock", "Gemfile.lock", "composer.lock", "Cargo.lock", "go.sum", "uv.lock",
}
TEXT_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro",
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".py", ".rb", ".php",
    ".go", ".java", ".kt", ".kts", ".scala", ".cs", ".rs", ".swift", ".dart",
    ".ex", ".exs", ".sql", ".prisma", ".graphql", ".gql", ".yml", ".yaml",
    ".toml", ".json", ".conf", ".tf", ".ini", ".cfg", ".xml", ".gradle", ".env",
    ".example", ".erb", ".twig", ".liquid", ".hbs", ".ejs", ".pug",
}
TEXT_NAMES = {"Dockerfile", "Procfile", "nginx.conf", "Caddyfile", "Makefile", "_headers", ".htaccess"}
RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}
MODERN = {".webp", ".avif"}
FONTS = {".ttf", ".otf", ".woff", ".woff2", ".eot"}
MAX_TEXT_BYTES = 1_000_000

MANIFESTS = {
    "package.json": "Node/JS", "requirements.txt": "Python", "pyproject.toml": "Python",
    "Pipfile": "Python", "go.mod": "Go", "Gemfile": "Ruby", "composer.json": "PHP",
    "pom.xml": "Java (Maven)", "build.gradle": "JVM (Gradle)", "build.gradle.kts": "JVM (Gradle)",
    "Cargo.toml": "Rust", "pubspec.yaml": "Dart/Flutter", "mix.exs": "Elixir",
    "Package.swift": "Swift", "angular.json": "Angular",
}
DEPLOY_FILES = {
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yaml", "fly.toml",
    "vercel.json", "netlify.toml", "render.yaml", "app.yaml", "serverless.yml",
    "wrangler.toml", "Procfile", "nginx.conf", "Caddyfile", "_headers", "railway.json",
    "amplify.yml", "firebase.json", "Chart.yaml", "skaffold.yaml",
}
JS_FRAMEWORKS = [
    "next", "nuxt", "@remix-run/react", "astro", "@sveltejs/kit", "gatsby", "react", "vue",
    "svelte", "@angular/core", "solid-js", "preact", "react-native", "expo", "electron",
    "express", "fastify", "@nestjs/core", "koa", "hono", "@hapi/hapi",
    "prisma", "@prisma/client", "drizzle-orm", "typeorm", "sequelize", "mongoose", "knex",
    "@tanstack/react-query", "swr", "@apollo/client", "redux", "@reduxjs/toolkit", "zustand",
    "vite", "webpack", "tailwindcss",
]

# Packages used without being imported (peer or runtime deps of a framework).
IMPLICIT_DEPS = {
    "react-dom", "typescript", "tslib", "@babel/runtime", "core-js", "regenerator-runtime",
    "sharp", "server-only", "client-only", "@next/font",
}

# criterion number -> (label, [(signal name, regex)])
I = re.IGNORECASE
SIGNALS = {
    1: ("Skeleton Loading", [
        ("skeleton/shimmer", re.compile(r"skeleton|shimmer|animate-pulse|placeholder-glow", I)),
        ("spinner/loading text (counter-signal)", re.compile(r"spinner|CircularProgress|<Spin\b|ActivityIndicator|Loading\.\.\.", I)),
    ]),
    2: ("WebP / AVIF", [
        ("image pipeline", re.compile(r"next/image|@nuxt/image|gatsby-plugin-image|<picture|image/(avif|webp)|\bsharp\b|imagemin|vite-imagetools|cloudinary|imgix", I)),
    ]),
    3: ("Lazy Loading", [
        ("lazy media", re.compile(r"loading=[\"']lazy|IntersectionObserver|lazysizes|react-lazyload|v-lazy", I)),
        ("high fetch priority", re.compile(r"fetchpriority|priority\b(?=[\s=}])", I)),
    ]),
    4: ("Code Splitting", [
        ("dynamic import / lazy components", re.compile(r"React\.lazy|\blazy\(\s*\(\)\s*=>|next/dynamic|defineAsyncComponent|loadChildren|import\(\s*[\"'`]", I)),
    ]),
    5: ("SSR / Static Generation", [
        ("rendering mode", re.compile(r"getStaticProps|getServerSideProps|generateStaticParams|export const (revalidate|dynamic)|prerender|renderToString|renderToPipeableStream|output:\s*[\"']export|use server|ssr:\s*(true|false)", I)),
    ]),
    6: ("Third-Party Scripts", [
        ("third-party tags", re.compile(r"googletagmanager|google-analytics|gtag\(|fbq\(|connect\.facebook\.net|hotjar|intercom|clarity\.ms|segment\.(com|io)|analytics\.tiktok|snap\.licdn|crisp\.chat|tawk\.to|cdn\.jsdelivr|unpkg\.com", I)),
        ("script loading strategy", re.compile(r"<script[^>]+\b(async|defer)\b|strategy=[\"'](lazyOnload|afterInteractive|worker)|partytown", I)),
    ]),
    7: ("Font Optimization", [
        ("font loading", re.compile(r"fonts\.googleapis|@font-face|font-display|next/font|@fontsource|as=[\"']font", I)),
    ]),
    9: ("Debounce", [
        ("debounce/throttle", re.compile(r"debounce|throttle|useDeferredValue|useDebounce", I)),
    ]),
    10: ("Optimistic UI", [
        ("optimistic updates", re.compile(r"optimistic|onMutate|useOptimistic", I)),
    ]),
    11: ("Virtualization", [
        ("virtual lists", re.compile(r"react-window|react-virtualized|@tanstack/(react-)?virtual|react-virtuoso|vue-virtual-scroller|cdk-virtual-scroll|FlashList|ListView\.builder|RecyclerView|LazyColumn", I)),
        ("ScrollView with mapped children (RN counter-signal)", re.compile(r"<ScrollView", 0)),
    ]),
    12: ("Unnecessary Re-renders", [
        ("memoization", re.compile(r"React\.memo|\buseMemo\b|\buseCallback\b|\bmemo\(|shallowRef|ChangeDetectionStrategy\.OnPush|why-did-you-render", 0)),
        ("context providers", re.compile(r"createContext\(|\.Provider\b", 0)),
    ]),
    13: ("AI Streaming", [
        ("LLM SDK usage", re.compile(r"openai|@anthropic-ai|\banthropic\b|@ai-sdk|langchain|generativeai|google-genai|ollama|chat\.completions|messages\.create|responses\.create", I)),
        ("streaming", re.compile(r"text/event-stream|ReadableStream|stream\s*[:=]\s*(true|True)|streamText|streamObject|EventSource|StreamingResponse|toDataStreamResponse|toTextStreamResponse|\.stream\(", 0)),
    ]),
    14: ("CDN", [
        ("CDN / edge hosting", re.compile(r"cloudfront|cloudflare|fastly|akamai|bunnycdn|assetPrefix|CDN_URL|cdn_url|\bcdn\.", I)),
    ]),
    15: ("Brotli / Gzip", [
        ("compression", re.compile(r"\bcompression\(|@fastify/compress|brotli|gzip_static|gzip\s+on|GZipMiddleware|django\.middleware\.gzip|vite-plugin-compression|compression-webpack-plugin|Rack::Deflater|UseResponseCompression", I)),
    ]),
    16: ("Browser Caching", [
        ("cache headers / SW", re.compile(r"Cache-Control|max-age|immutable|\bETag\b|Last-Modified|\bexpires\s+\d|maxAge|serviceWorker|workbox", I)),
    ]),
    17: ("Duplicate API Calls", [
        ("data-fetching/dedupe layer", re.compile(r"@tanstack/(react|vue|svelte)-query|react-query|\buseSWR\b|from [\"']swr[\"']|@apollo/client|urql|createApi\(|\bcache\(\s*async", 0)),
    ]),
    18: ("Parallel Requests", [
        ("concurrency helpers", re.compile(r"Promise\.all|Promise\.allSettled|asyncio\.gather|errgroup|CompletableFuture\.allOf|sync\.WaitGroup|Task\.WhenAll", 0)),
        ("preconnect/preload", re.compile(r"rel=[\"'](preconnect|preload|dns-prefetch)", I)),
    ]),
    19: ("Pagination", [
        ("pagination", re.compile(r"paginat|per_page|perPage|pageSize|page_size|next_cursor|nextCursor|\bcursor\b|\boffset\b|\.take\(|\btake:\s|\bskip:\s|\bLIMIT\s+[\d$:?]|\.limit\(|keyset|useInfiniteQuery", I)),
    ]),
    20: ("API Timeouts", [
        ("timeouts", re.compile(r"timeout|AbortController|AbortSignal|context\.WithTimeout|statement_timeout|connectTimeout|deadline", I)),
    ]),
    21: ("N+1 Queries", [
        ("eager loading / batching", re.compile(r"select_related|prefetch_related|\binclude:\s*\{|joinedload|selectinload|subqueryload|\.with\(\s*[\[\"']|eager_load|\.includes\(|\.preload\(|DataLoader|\bJOIN\b", 0)),
    ]),
    22: ("Database Indexes", [
        ("index definitions", re.compile(r"CREATE\s+(UNIQUE\s+)?INDEX|@@index|@@unique|@index\b|index=True|db_index=True|add_index|->index\(|\.index\(\s*[\[\"'{]|Index\(\s*[\"']|createIndex|@Index\(", I)),
    ]),
    23: ("Required Columns Only", [
        ("SELECT * (counter-signal)", re.compile(r"SELECT\s+\*", I)),
        ("projections", re.compile(r"\bselect:\s*\{|\.only\(|\.values\(|\.values_list\(|attributes:\s*\[|load_only|\.pluck\(|projection", 0)),
    ]),
    24: ("Connection Pooling", [
        ("pool config", re.compile(r"\bpool\b|Pool\(|pgbouncer|connection_limit|poolSize|maxPoolSize|pool_size|CONN_MAX_AGE|HikariCP|createPool|keepAlive", I)),
        ("client created per call (check scope)", re.compile(r"new PrismaClient\(|new Pool\(|createConnection\(|psycopg2?\.connect\(|mysql\.connector\.connect\(", 0)),
    ]),
    25: ("Redis Caching", [
        ("cache stores", re.compile(r"\bredis\b|ioredis|memcache|lru-cache|node-cache|@cache\b|cache_page|Rails\.cache|Cache::remember|functools\.lru_cache|@lru_cache|unstable_cache", I)),
    ]),
    26: ("Background Job Queue", [
        ("queues / workers", re.compile(r"bullmq|\bbull\b|bee-queue|agenda|celery|\brq\b|dramatiq|sidekiq|resque|delayed_job|good_job|ShouldQueue|\bSQS\b|pubsub|rabbitmq|amqplib|kafkajs|temporal|inngest|trigger\.dev|graphile-worker|pg-boss|BackgroundTasks", I)),
    ]),
    27: ("Server / Database Proximity", [
        ("region settings", re.compile(r"\bregions?[\"']?\s*[:=]|primary_region|AWS_REGION|runtime\s*=\s*[\"']edge", I)),
    ]),
    28: ("Load Balancing", [
        ("scaling / workers", re.compile(r"\bupstream\s+\w+\s*\{|haproxy|load.?balanc|\breplicas:|cluster\.fork|exec_mode\s*[:=]\s*[\"']cluster|--workers|workers\s*=|WEB_CONCURRENCY|\bingress\b|autoscal", I)),
    ]),
    29: ("OpenTelemetry", [
        ("tracing / APM", re.compile(r"opentelemetry|\botel\b|OTEL_|jaeger|zipkin|dd-trace|ddtrace|newrelic|honeycomb|aws-xray|elastic-apm|@sentry/(node|nextjs)|sentry_sdk", I)),
    ]),
    30: ("Real User Monitoring", [
        ("RUM / web-vitals", re.compile(r"web-vitals|\bonLCP\b|\bonINP\b|\bonCLS\b|reportWebVitals|speed-insights|@vercel/analytics|@sentry/(browser|react|vue|nextjs)|datadog-rum|browser-rum|PerformanceObserver", I)),
    ]),
    31: ("Performance Testing", [
        ("load/bench tooling", re.compile(r"\bk6\b|from [\"']k6|artillery|locust|autocannon|jmeter|gatling|lighthouserc|@lhci|size-limit|bundlesize|pytest-benchmark|func Benchmark|hyperfine|\bwrk\b", I)),
    ]),
}

IMPORT_STRING = re.compile(r"""(?:from\s+|require\(\s*|import\(\s*|import\s+)["']([^"'\s]+)["']""")
ANY_STRING = re.compile(r"""["'`](@?[a-zA-Z0-9][\w.\-]*(?:/[\w.\-]+)*)["'`]""")


def pkg_name(spec):
    if spec.startswith((".", "/", "~", "#")) or ":" in spec:
        return None
    parts = spec.split("/")
    return "/".join(parts[:2]) if spec.startswith("@") else parts[0]


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def is_text(name, ext):
    return (ext in TEXT_EXT or name in TEXT_NAMES or name.startswith(".env")) and name not in LOCK_FILES and not name.endswith((".min.js", ".min.css", ".map"))


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for f in filenames:
            yield os.path.join(dirpath, f)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--examples", type=int, default=3, help="example matches per signal")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.exit(f"not a directory: {root}")

    manifests, deploy, images, fonts = [], [], defaultdict(lambda: [0, 0]), defaultdict(int)
    big_images, package_jsons = [], []
    hits = defaultdict(list)  # (crit, signal) -> [(rel, line, text)]
    hit_files = defaultdict(set)
    import_names, string_names = set(), set()
    effect_fetch_files = []
    text_files = 0

    for path in walk(root):
        rel = os.path.relpath(path, root)
        name = os.path.basename(path)
        ext = os.path.splitext(name)[1].lower()
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        if name in MANIFESTS:
            manifests.append((rel, MANIFESTS[name]))
            if name == "package.json":
                package_jsons.append(path)
        if name in DEPLOY_FILES or rel.startswith((".github/workflows", "k8s", "helm", "terraform", "infra")):
            deploy.append(rel)
        if ext in RASTER or ext in MODERN or ext == ".svg":
            kind = "modern (webp/avif)" if ext in MODERN else "vector (svg)" if ext == ".svg" else "raster (png/jpg/gif...)"
            images[kind][0] += 1
            images[kind][1] += size
            if ext in RASTER and size > 150 * 1024:
                big_images.append((size, rel))
            continue
        if ext in FONTS:
            fonts[ext] += 1
            continue
        if not is_text(name, ext) or size > MAX_TEXT_BYTES:
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except OSError:
            continue
        text_files += 1
        lines = None
        for crit, (_, sigs) in SIGNALS.items():
            for sig_name, rx in sigs:
                m = rx.search(content)
                if not m:
                    continue
                hit_files[(crit, sig_name)].add(rel)
                if len(hits[(crit, sig_name)]) < args.examples:
                    if lines is None:
                        lines = content.splitlines()
                    line_no = content.count("\n", 0, m.start()) + 1
                    snippet = lines[line_no - 1].strip()[:110] if line_no - 1 < len(lines) else ""
                    hits[(crit, sig_name)].append((rel, line_no, snippet))
        if ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro"}:
            for spec in IMPORT_STRING.findall(content):
                n = pkg_name(spec)
                if n:
                    import_names.add(n)
            if "useEffect" in content and ("fetch(" in content or "axios" in content):
                effect_fetch_files.append(rel)
        if name != "package.json":  # its own keys would mark every dependency as used
            for spec in ANY_STRING.findall(content):
                n = pkg_name(spec)
                if n:
                    string_names.add(n)

    out = []
    w = out.append
    w(f"# Performance inventory: `{root}`\n")
    w("> Leads, not verdicts. Read the files before classifying any criterion. "
      "No match can mean the feature lives in infrastructure outside the repo (mark ❓).\n")
    w(f"Scanned {text_files} text files (skipping node_modules, build output, lock files).\n")

    w("## Stack")
    for rel, kind in sorted(manifests):
        w(f"- `{rel}`: {kind}")
    if not manifests:
        w("- No known manifest found.")
    deps_report = []
    for pj in package_jsons:
        try:
            with open(pj, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        deps = data.get("dependencies", {}) or {}
        dev = data.get("devDependencies", {}) or {}
        allp = {**dev, **deps}
        fw = [f"{k}@{allp[k]}" for k in JS_FRAMEWORKS if k in allp]
        rel = os.path.relpath(pj, root)
        if fw:
            w(f"- `{rel}` key packages: {', '.join(fw)}")
        scripts = " ".join(str(v) for v in (data.get("scripts") or {}).values())
        unused = []
        for d in deps:
            if d.startswith("@types/") or d in IMPLICIT_DEPS or d in import_names or d in string_names:
                continue
            bare = d.split("/")[-1]
            if re.search(rf"(?<![\w-]){re.escape(bare)}(?![\w-])", scripts):
                continue
            unused.append(d)
        deps_report.append((rel, len(deps), len(dev), unused))
    w("")

    w("## Deployment / infrastructure files")
    w("\n".join(f"- `{d}`" for d in sorted(deploy)[:25]) or "- None found (hosting/CDN/LB/region likely ❓).")
    w("")

    w("## Images (criteria 2, 3)")
    if images:
        w("| Kind | Files | Total size |\n|---|---|---|")
        for kind, (count, total) in sorted(images.items()):
            w(f"| {kind} | {count} | {human(total)} |")
        if big_images:
            w("\nLargest raster images (> 150 KB):")
            for size, rel in sorted(big_images, reverse=True)[:10]:
                w(f"- `{rel}`: {human(size)}")
    else:
        w("- No image files in the repo (images may come from a CMS/CDN/uploads).")
    w("")

    w("## Fonts (criterion 7)")
    w(", ".join(f"{ext}: {n}" for ext, n in sorted(fonts.items())) or "- No font files (system fonts or remote fonts; check CSS for fonts.googleapis).")
    if fonts and not fonts.get(".woff2") and (fonts.get(".ttf") or fonts.get(".otf")):
        w("- ⚠️ TTF/OTF present without WOFF2.")
    w("")

    w("## Build output (criterion 4), if a build exists locally")
    found_build = False
    for bd in BUILD_DIRS:
        p = os.path.join(root, bd)
        if not os.path.isdir(p):
            continue
        assets = []
        for dp, _, fs in os.walk(p):
            for f in fs:
                if f.endswith((".js", ".css")) and not f.endswith(".map"):
                    fp = os.path.join(dp, f)
                    assets.append((os.path.getsize(fp), os.path.relpath(fp, root)))
        if assets:
            found_build = True
            total_js = sum(s for s, r in assets if r.endswith(".js"))
            w(f"- `{bd}`: {len(assets)} JS/CSS files, JS total {human(total_js)} (raw, not gzipped). Largest:")
            for size, rel in sorted(assets, reverse=True)[:8]:
                w(f"  - `{rel}`: {human(size)}")
    if not found_build:
        w("- No build output found. Run the production build to measure bundle sizes.")
    w("")

    w("## Dependencies (criterion 8)")
    for rel, nd, ndev, unused in deps_report:
        w(f"- `{rel}`: {nd} dependencies, {ndev} devDependencies.")
        if unused:
            w(f"  - Possibly unused (no import/string reference found, framework peer deps excluded; confirm with `npx knip` or `npx depcheck`): {', '.join(sorted(unused))}")
    if not deps_report:
        w("- No package.json. For Python use `deptry`, Go `go mod tidy`, Rust `cargo udeps`.")
    w("")

    w("## Signals by criterion")
    w("Format: signal → files matched · examples `path:line`.\n")
    for crit, (label, sigs) in SIGNALS.items():
        w(f"### {crit}. {label}")
        for sig_name, _ in sigs:
            files = hit_files.get((crit, sig_name), set())
            if not files:
                w(f"- {sig_name}: none")
                continue
            w(f"- {sig_name}: {len(files)} file(s)")
            for rel, line_no, snippet in hits[(crit, sig_name)]:
                w(f"  - `{rel}:{line_no}`: `{snippet.replace('`', '')}`")
        if crit == 17:
            if effect_fetch_files:
                w(f"- useEffect + fetch/axios in the same file (check for duplicates and missing cancellation): {len(effect_fetch_files)} file(s)")
                for rel in effect_fetch_files[: args.examples]:
                    w(f"  - `{rel}`")
            else:
                w("- useEffect + fetch/axios co-occurrence: none")
        w("")
    w("### 8. Unused Dependencies: see the Dependencies section above.")
    print("\n".join(out))


if __name__ == "__main__":
    main()
