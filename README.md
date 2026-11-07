# Wolfin Senior plugin

**English** · [العربية](README.ar.md)

A Claude Code plugin that makes the agent work like a senior engineer, not just someone who writes code: it understands the problem first, checks the docs for the versions you actually run, writes the test first, proves every claim, and keeps a memory that survives between sessions. And it follows all of this literally, because hooks enforce it.

These skills are the result of a Bachelor's degree in Computer Science, a Master's degree in Artificial Intelligence, more than six years of work with the banking sector and payment companies, and training more than 240 students around the world.

Plugin id: `wolfin-senior`. Skills appear as `wolfin-senior:<skill>`.

> **Full guide with diagrams:** [docs/how-it-works.en.md](docs/how-it-works.en.md) · [بالعربي](docs/how-it-works.md) · Articles on [wolfin.app](https://wolfin.app/blog?post=wolfin-senior-plugin)

## Install

```bash
claude plugin marketplace add wolfinApp/wolfin-senior
claude plugin install wolfin-senior@wolfin-senior-marketplace
```

Open a new session, then ask: "What's the project memory path?" If it answers with a `.wolfin-senior/memory` path, the plugin is running.

Try it for one session, without installing:

```bash
claude --plugin-url https://wolfin.app/downloads/wolfin-senior.zip
```

Update later with `claude plugin marketplace update wolfin-senior-marketplace`. You need Claude Code and Python 3. The hooks run on macOS and Linux; on Windows, use WSL.

## The skills

| SDLC phase | Skill | What it does |
|---|---|---|
| Every phase | `using-wolfin-senior` | The router: picks the right skill before any work, and turns the 19 rules of software engineering into behaviors |
| 01 Requirements, 02 Design | `requirements-and-design` | One question at a time, 2 to 3 approaches with trade-offs, a design doc and ADRs. No code before you approve |
| 03 Development | `docs-first` | Before any code: installed vs latest versions, then the official docs and changelog for the exact APIs |
| 03 Development | `writing-plans` | Turns the design into small tasks with files, signatures, tests, commands and expected output |
| 03 Development | `executing-plans` | Runs the plan inline, with a fresh subagent per task plus review, or in parallel, with a ledger that survives compaction |
| 03 Development | `test-driven-development` | Failing test first, watch it fail, minimal code, refactor |
| 03 Development, 06 Maintenance | `engineering-principles` | The 10 coding principles: standards, documentation, robustness, SOLID, testability, moderate abstraction, design patterns, fewer global dependencies, continuous refactoring, security |
| 04 Testing | `systematic-debugging` | No fix before the root cause. After 3 failed fixes, stop and question the design |
| 04 Testing | `verification-before-completion` | Never says "done" without running the check and reading the output |
| 04 Testing | `code-review-workflow` | Self-review, a fresh reviewer subagent, useful reviews, and feedback without flattery |
| 05 Deployment, 06 Maintenance | `finishing-and-shipping` | Meaningful commits, merge or PR, release checklist (migrations, rollback, monitoring) |
| 06 Maintenance | `performance-optimization` | Inspects and measures first, reports 31 techniques with priority and impact, applies only what fits, one at a time |
| Every phase | `project-memory` | NOW.md, a daily journal and durable facts, so nothing is forgotten. Never stores secrets |

## Strict mode: followed literally

Any agent with this plugin treats the skills as binding instructions:
- It loads every skill that applies before responding, announces it, and follows every step in order, with no skipping, merging or "adapting".
- Only you can waive a step, explicitly. If a step can't be done, it says so.
- When it dispatches a subagent to write code, it passes the same rules on.

Four hooks enforce the most important rules:

| Hook | Runs | Enforces |
|---|---|---|
| `session-start` | Session start, resume, clear, after compaction | Loads the router as binding instructions, plus the project memory |
| `prompt-reminder` | Every message | A short reminder of the rules (about 100 tokens) |
| `code-gate.py` | Before every code edit | Refused until `docs-first` and `test-driven-development` are loaded (lets edits through after 3 refusals, so it can't trap a session) |
| `stop-gate.py` | End of every turn | Code changed after the last test run: run the tests. Anything changed: log it to the memory |

Turn any check off on its own: `WOLFIN_CODE_GATE=off`, `WOLFIN_VERIFY_GATE=off`, `WOLFIN_MEMORY_GATE=off`, `WOLFIN_REMINDER=off`.

## Memory

Each project gets `.wolfin-senior/memory/` at the repo root, shared by all git worktrees:

```
.wolfin-senior/memory/
├── NOW.md               where the work stands: current task, done, next step, blockers
├── MEMORY.md            index: one line per saved fact
├── journal/2026-11-07.md   step log: asked, done, verified (command and result), decided
└── <topic>.md           a durable fact: decision, preference, convention, lesson
```

Preferences that apply to every project live in `~/.claude/wolfin-senior/memory/`. The folder is added to `.git/info/exclude` automatically, so it never ends up in a commit. Passwords, tokens and keys are never stored, only where they live.

## Layout

```
.claude-plugin/          plugin.json + marketplace.json
hooks/session-start      injects the binding router and memory at session start and after compaction
hooks/prompt-reminder    short reminder of the rules on every message
hooks/code-gate.py       refuses code edits until docs-first and TDD are loaded
hooks/stop-gate.py       end of turn: tested after the last code edit, work logged
skills/<name>/SKILL.md   the skill itself
skills/<name>/references/   references read only when needed
skills/docs-first/scripts/versions.py   installed vs latest versions, with doc links
skills/performance-optimization/scripts/inventory.py   performance evidence for the 31 techniques
```

## Credits and license

MIT. Parts of the workflow skills (planning, test-driven development, debugging, review) are adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT, © 2025 Jesse Vincent). See [LICENSE](LICENSE).
