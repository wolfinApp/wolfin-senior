---
name: docs-first
description: Use before writing or changing any code that touches a language feature, framework, library, SDK, CLI, config format or external API, before adding or upgrading a dependency, and before scaffolding a new project. Checks the versions the project actually uses against the latest releases, then reads the official, current documentation, changelog and migration notes for exactly the APIs about to be used, instead of trusting memory. Triggers on any coding task, and on "check the docs", "latest version", "راجع الدوكيومنتيشن", "آخر تحديث", "آخر إصدار".
---

# Docs First

Your knowledge of APIs has a cutoff, and frameworks keep moving. Defaults
change, functions get renamed, config formats get replaced, and the pattern
everyone used last year is deprecated today. Code written from memory
compiles against the version in your head, not the one in the project.
Rule 19: you'll never stop learning. This skill makes "check the docs" a
step you take, not a thing you mean to do.

Say at the start: "Using docs-first: checking <stack> docs before coding."

## The rule

```
NO CODE AGAINST AN API YOU HAVEN'T CHECKED FOR THE VERSION IN USE
```

That means checking the **installed** version's documentation for every
framework, library, SDK, CLI or config format you're about to use, plus
what changed up to the **latest** release.

What doesn't need a lookup: core language basics that haven't changed in
years (loops, string slicing), and APIs you already checked this session
or that the project memory records as checked recently, for the same
version (see "Cache it" below).

## Step 1: Pin down the versions

Read what the project actually uses. Don't guess from memory or the README.

| Ecosystem | Declared | Actually installed / locked |
|---|---|---|
| Node | `package.json` (+ `engines`, `.nvmrc`) | `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`, `npm ls <pkg>` |
| Python | `pyproject.toml`, `requirements*.txt`, `.python-version` | `poetry.lock` / `uv.lock`, `pip show <pkg>` |
| Go | `go.mod` (`go` directive) | `go list -m all` |
| Rust | `Cargo.toml`, `rust-toolchain.toml` | `Cargo.lock` |
| Ruby | `Gemfile`, `.ruby-version` | `Gemfile.lock` |
| PHP | `composer.json` | `composer.lock`, `composer show <pkg>` |
| Dart/Flutter | `pubspec.yaml` | `pubspec.lock` |
| JVM / .NET | `pom.xml`, `build.gradle`, `*.csproj` | `mvn dependency:tree`, `dotnet list package` |
| Containers | `Dockerfile` `FROM` tags | the image actually built |

Then get the latest releases in one go with the bundled script:

```bash
python3 <this-skill-dir>/scripts/versions.py <repo-path>            # direct deps + runtimes vs latest
python3 <this-skill-dir>/scripts/versions.py <repo-path> --only next,react,prisma
```

It reads the manifests and lockfiles, asks the public registries (npm, PyPI,
Go proxy, crates.io, RubyGems, Packagist, pub.dev) and endoflife.date for
the latest stable versions, and prints a table that marks anything a major
version behind. Use `--offline` to skip the network. Native alternatives:
`npm outdated`, `pip list --outdated`, `go list -m -u all`,
`composer outdated`, `bundle outdated`, `flutter pub outdated`,
`dotnet list package --outdated`.

Package names are sent to the public registries. For private or internal
packages, use `--only` to restrict the check to public ones.

## Step 2: Read the right documentation

For each library or framework the change will use, read only the topics
you're about to use, in this order of trust:

1. **The official docs for the installed major version.** Most doc sites have
   version switchers or versioned URLs. Make sure you're reading the right
   one. The latest docs can describe APIs your version doesn't have.
2. **The changelog, release notes and migration guides** between the
   installed version and the latest. Look for breaking changes,
   deprecations, and new recommended patterns.
3. **The installed source itself,** which is the ground truth for this
   project: type definitions (`node_modules/<pkg>/**/*.d.ts`), the package
   README, docstrings (`python -c "import pkg; help(pkg.fn)"`), `go doc`,
   and `<cli> --help`.
4. **Official examples and starter templates** from the same maintainers.

Blog posts, Q&A answers and tutorials come last, only to locate something,
then confirm it in the official docs. They're often written for an older
version.

**Tools,** whichever the harness offers: a documentation MCP server (such as
Context7) if one is connected, web fetch and search, a web-fetch subagent,
`gh` (`gh release view --repo owner/repo`, `gh api repos/{owner}/{repo}/releases/latest`),
or `curl` against the registry APIs. Offline, rely on step 3 and say so.

## Step 3: Decide which version to code against

- **Existing project:** code against the **installed** version. Never use an
  API that only exists in a newer release. If the project is behind (a major
  version, a deprecated API in use, a security advisory, an end-of-life
  runtime), *tell the user* and recommend an upgrade with its migration
  cost. Don't upgrade on your own. An upgrade is its own task, with its own
  plan and tests.
- **New project or new dependency:** use the **latest stable** release (not
  beta, RC or canary unless the user asks), and check that it's compatible
  with the runtime and the other dependencies. Prefer what the official docs
  currently recommend (the current router, the current config format, the
  current project generator).
- **Deprecated in the installed version:** don't write new code with a
  deprecated API when the replacement already exists in that version.

## Step 4: Report it briefly, then code

Tell the user in two or three lines before coding, in their language:

> Checked the docs: Next.js installed 16.1.2 (latest 16.4.5, same major). Route handlers and
> `cookies()` follow the 16.x docs. Prisma 5.22 is two majors behind (7.x), so I'm coding against 5.x;
> I recommend a separate upgrade task.

Then build the change following what the docs say, not what you remember.

## Step 5: Cache it in memory

Save what you checked so the next task doesn't repeat it, and so nothing
you learned is lost (`project-memory`):
- **Journal entry:** `Docs check: next@16.1.2 (latest 16.4.5), topics: route handlers, cookies; sources: <urls>`.
- **A `reference` memory per key library** (update it, don't duplicate):
  installed version, latest version, the date checked, doc URLs, and gotchas
  found ("`cookies()` is async in this version").

**Re-check when** the installed version changes, the check is older than
about 30 days, you're about to use an API or topic not covered by the last
check, or something behaves differently from what the docs said.

## Examples of why memory isn't enough

Breaking changes that code written from memory routinely gets wrong. These
are past examples. The current state is whatever today's docs say.
- ESLint moved to flat config (`eslint.config.js`) as the default in v9.
- Tailwind CSS v4 moved configuration into CSS (`@import "tailwindcss"`, `@theme`).
- Pydantic v2 renamed core methods (`.dict()` became `.model_dump()`, `@validator` became `@field_validator`).
- SQLAlchemy 2.0 made `select()`-style queries the standard over the legacy `Query` API.
- React 19 lets function components take `ref` as a prop, and renamed `useFormState` to `useActionState`.
- Next.js 15 made `params`, `cookies()` and `headers()` async, and stopped caching `fetch` by default.
- Python 3.12 removed `distutils`.

## Red flags

| Thought | Reality |
|---|---|
| "I know this API well" | You know the version you trained on. Check the installed one. |
| "The docs check slows me down" | Debugging a removed API, or a wrong default, is slower. |
| "Latest docs are fine" | Not if the project is a major version behind. Read the matching version. |
| "This tutorial shows how" | Tutorials age fast. Confirm in the official docs. |
| "I'll upgrade the package while I'm here" | Upgrades are their own task. Recommend it, don't sneak it in. |
| "I checked this last month for another version" | Version changed, so re-check. |
