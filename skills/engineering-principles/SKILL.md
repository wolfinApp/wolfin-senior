---
name: engineering-principles
description: Use whenever writing, designing, refactoring, or judging code quality — applies the 10 good coding principles (coding standards, documentation, robustness, SOLID, testability, moderate abstraction, design patterns, fewer global dependencies, continuous refactoring, security) plus maintainability and dependency discipline. Use when adding a module, class, API or dependency, when code feels messy or hard to change, when asked "is this good code?", "clean code", "refactor", "SOLID", "design pattern", "secure this", "نظّف الكود", "رتّب الكود", "هل الكود زين؟".
---

# Engineering Principles

Good code is code the next person (often you, six months later, or someone
on call at 3 a.m.) can understand, change and trust. Customers don't care
about your code (rule 4), but they feel every bug, slowdown and outage it
causes. These principles are how you keep those away.

Everything is a trade-off (rule 12). A principle is a default, not a law.
When you deviate, do it on purpose and say why.

## Before writing code

1. **Read the surroundings.** Match the project's structure, naming, error
   handling and test style. Consistency beats your personal preference (rules 15 and 17).
2. **Find the standards.** Look for `.editorconfig`, the ESLint/Prettier,
   Ruff/Black/Flake8, golangci, Checkstyle, rustfmt or SwiftLint config, and
   `CONTRIBUTING.md`. Run the formatter and linter the project uses.
3. **Smallest change that solves it.** Every line you add is a line someone
   must read, test, secure and maintain (rule 6).

## The 10 principles

### 1. Coding standards
Standards make code consistent and readable, and they end style arguments
(rule 15). Follow the project's config first, then the language's community
standard: PEP 8 for Python, Google Java Style or the project's Checkstyle for
Java, Effective Go and `gofmt` for Go, the Airbnb/Standard config or the
project's ESLint for JavaScript/TypeScript, `rustfmt` and Clippy for Rust.
Let tools enforce style, so reviews can focus on substance.

### 2. Documentation and annotations
Comment **why**, not **what**. The code says what. Explain complex logic,
the reason one approach was chosen over another, non-obvious constraints
("API returns max 100 items, so we paginate"), and workarounds (with the
issue link). Keep docs clear, concise, and updated in the same commit as
the code. A wrong comment is worse than none. Public APIs get docstrings
(parameters, returns, errors, an example). Hard-to-reverse decisions get
an ADR (`requirements-and-design`).

### 3. Robustness
Assume everything outside your function will fail eventually: **input
errors, disk failure, network overload, intentional attack.** Validate at
the boundaries, set timeouts on every network call, retry only idempotent
operations (with backoff and jitter), degrade gracefully, and fail loudly
with useful messages instead of failing silently. Details and code:
`references/robustness.md`.

### 4. SOLID
- **S**ingle responsibility: one reason to change per module or class.
- **O**pen/closed: extend behavior by adding code, not by editing stable code.
- **L**iskov substitution: subtypes must honor the parent's contract.
- **I**nterface segregation: small, focused interfaces rather than fat ones.
- **D**ependency inversion: depend on abstractions, and inject dependencies.
Smells and fixes for each: `references/solid-and-patterns.md`.

### 5. Easy to test
Testable code has **low complexity, automated tests, low cost to run, and
fast feedback.** Keep core logic pure (input → output). Push I/O (DB,
network, clock, randomness) to the edges and inject it. If a unit is hard to
test, the design is telling you something. See `test-driven-development`.

### 6. Moderate abstraction
With no abstraction, low-level code is complex and hard to maintain. Too
much abstraction means indirection nobody can follow. Aim for the middle:
extract the core logic, expose small public classes and methods, and hide
the details. Rule of three: duplicate once, abstract on the third
occurrence, when you can see the real shape. Don't build frameworks for one
use case.

### 7. Design patterns
Use a pattern when it solves a problem you actually have, never as
decoration.
- **Creational:** Factory (construction varies by type or config). Singleton
  sparingly, because it's global state in disguise.
- **Structural:** Adapter (wrap a third-party API behind your own
  interface), Proxy (add caching, lazy loading or access control
  transparently).
- **Behavioral:** Strategy (swap algorithms, replacing `if/else` chains on a
  type), Observer (decoupled notifications).
When and when not: `references/solid-and-patterns.md`.

### 8. Reduce global dependencies
Global mutable state couples every function that touches it, so behavior
depends on call order and tests interfere with each other. Prefer local
state, pass dependencies explicitly (parameters, constructor injection),
keep configuration read once at startup into an immutable object, and keep
module-level singletons stateless.

### 9. Continuous refactoring
Improve the design of existing code in small steps, always under green tests:
- Leave code a little better than you found it, *within the scope of your task*.
- Refactor in commits separate from behavior changes, so reviews stay readable and reverts stay safe.
- Common moves: extract function, rename, inline a needless abstraction, replace a conditional with polymorphism or a lookup table, delete dead code.
- Large restructures get their own plan, not a drive-by.

### 10. Security assurance
Treat all input as hostile. Watch for **SQL injection** (always use
parameterized queries), **cross-site scripting** (escape output, use CSP,
never inject raw HTML from users), and **data leakage** (no secrets in code
or logs, minimal data in responses, authorization on every request). Full
checklist: `references/security.md`.

## Maintainability and complexity (rules 2, 6, 16)

- **Names** say what something is or does: `unpaidInvoices`, not `list2`. Booleans read as questions: `isExpired`, `hasAccess`.
- **Functions** do one thing at one level of abstraction. If you need "and" to describe it, split it.
- **Nesting:** use early returns and guard clauses. More than 3 levels deep is a smell.
- **Magic values** become named constants that carry their reason.
- **Dead code** gets deleted. Git remembers it.
- **The on-call test:** could someone debug this from logs and error messages alone at 3 a.m.? If not, add context to errors and log the key decisions.
- **Boring beats clever.** Cleverness has to be paid back every time someone reads the code.

## Adding a dependency (rule 10)

Before adding a package, check in order:
1. Can the standard library or an existing dependency do it?
2. Is it a few lines you can write and test yourself?
3. If you do add it: is it maintained (recent releases, open issues
   handled)? Popular? What's its license? Its size and its transitive
   dependencies? Any known vulnerabilities (`npm audit`, `pip-audit`,
   `cargo audit`)?
4. Use the latest stable version, and read its current docs before using it (`docs-first`).
5. Say why it earned its place, in the commit or PR.

## Quick self-check before you hand in code

- [ ] Follows the project's style, and the formatter and linter pass
- [ ] Each unit has one responsibility, and names say what it does
- [ ] Inputs validated at the boundaries, errors handled and informative
- [ ] Network calls have timeouts, and resources are cleaned up
- [ ] No secrets, no injection paths, authorization checked
- [ ] No new global mutable state, and dependencies are injected
- [ ] No speculative abstraction or options nobody asked for
- [ ] Tests cover the behavior, and are fast and deterministic
- [ ] Comments explain why, and docs are updated with the code
- [ ] No new dependency without justification
