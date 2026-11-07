---
name: project-memory
description: Persistent memory and work journal so nothing is forgotten between sessions or after context compaction. Use at the start of work to recall what was decided and where things stand, after every meaningful step to log what was done and how it was verified, whenever the user states a preference, corrects you, or a decision or hard-won lesson emerges, and before ending a turn that changed files. Also use when the user says "remember", "don't forget", "what did we do", "where did we stop", "continue", "pick up where we left off".
---

# Project Memory

Your context window is temporary. It gets compacted, sessions end, and a new
session starts knowing nothing. Files on disk are permanent. This skill moves
everything worth keeping out of your head and into files, in three layers:

| Layer | File | What it holds | How it changes |
|---|---|---|---|
| **Now** | `NOW.md` | The resume point: active task, progress, next step, blockers | Rewritten to stay current |
| **Journal** | `journal/YYYY-MM-DD.md` | The step log: what was asked, done, verified, decided | Append-only |
| **Knowledge** | `<topic>.md` + the `MEMORY.md` index | Durable facts: preferences, decisions, conventions, lessons | Updated in place, never duplicated |

## Where it lives

- **Project memory:** `<repo root>/.wolfin-senior/memory/`. In a git worktree,
  that's the *main* checkout's root, so every worktree shares one memory.
  The session-start hook prints the resolved absolute path. Use that path.
  If it's missing, resolve it yourself:
  `cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && pwd`
  (or the current directory outside git).
- **User memory** (preferences that hold across all projects):
  `~/.claude/wolfin-senior/memory/`, same format, with no NOW or journal.

On first use, create the directory and add `.wolfin-senior/` to
`.git/info/exclude`. That keeps it out of commits without touching the
project's `.gitignore`. Commit memory only if the user asks for it to be
shared with the team.

If your harness already has its own memory system, keep each fact in exactly
one place. Before saving, check both, and update the existing entry rather
than adding a second one.

## At the start: recall

The session-start hook injects `MEMORY.md`, `NOW.md`, the tail of the latest
journal, and the user memory index. Read them before you respond:

1. **NOW.md has an active task?** Pick it up from its "Next" line, unless the
   user asked for something else. In that case, update NOW.md first so the old
   task isn't lost (move it to "Paused").
2. **Before a decision, search memory** for the topic: `grep -ril "<keyword>" <memory dir>`.
   A recorded decision or user preference beats your default.
3. **Memories go stale.** If one names a file, function, flag or version,
   check that it still exists before relying on it. Fix or delete stale ones.

No injected memory (hook not installed, or a new project)? Read
`<memory dir>/NOW.md` and `MEMORY.md` yourself if they exist.

## During work: the journal

Append to `journal/YYYY-MM-DD.md` (today's date; create the file if needed)
**at each milestone,** not at the end of the day:
- a step finished and verified
- a decision made, with its reason
- a fix that failed (so it isn't retried blindly later)
- a commit, merge, PR, or deploy
- before ending a turn that changed files

Entry format, short and factual:

```markdown
## 14:32 · Fix N+1 on /api/orders
- Asked: orders page slow (user)
- Did: eager-loaded items in `orders/service.ts:55`; added query-count test
- Verified: `npm test` → 48/48 pass; p95 820 → 140 ms (autocannon -c 50)
- Decided: no Redis yet; index + eager load were enough
- Next: WebP for hero images
```

Rules: commands with their real results (never "should pass"), file paths
for what changed, and the *why* for decisions. One entry per milestone, a
few lines each. The journal is a log, not an essay.

**Commands to rerun beat descriptions.** "Verified: `pytest tests/api -q`
→ 31 passed" lets a future session re-check it in one step.

## Keep NOW.md current

Rewrite it whenever the task, progress, or next step changes. It's the
first thing a fresh session reads, so it must be true *right now*:

```markdown
# Now
Updated: 2026-11-04 14:32

## Active task
Speed up the products and orders pages (perf audit: `docs/performance/2026-11-04-audit.md`)

## Done
- [x] Baseline measured (mobile LCP 4.8 s)
- [x] N+1 on /api/orders fixed (commit a1b2c3d)

## Next
1. Convert `public/hero.png` to AVIF/WebP with srcset
2. Lazy-load gallery images

## Blockers / waiting on user
- Approval for Redis (cost)

## Paused
- (none)

## Key files
`orders/service.ts`, `src/app/products/page.tsx`, ledger `.wolfin-senior/plans/perf/progress.md`
```

When a task is finished, clear it from NOW.md and leave the outcome in the
journal.

## Knowledge: what to save

One fact or topic per file, named in kebab-case, with frontmatter:

```markdown
---
name: orders-use-keyset-pagination
description: Orders API paginates by (created_at, id) cursor, never OFFSET
type: decision
updated: 2026-11-04
---
Orders list uses keyset pagination on (created_at DESC, id DESC).
**Why:** OFFSET took 2.3 s at page 400 (measured 2026-11-04).
**How to apply:** new list endpoints on large tables use the same cursor helper `lib/cursor.ts`.
Related: [[orders-indexes]]
```

Then add one line to `MEMORY.md`, the index loaded every session:
`- [orders-use-keyset-pagination](orders-use-keyset-pagination.md): Orders API paginates by cursor, never OFFSET`

| Type | Save when | Example |
|---|---|---|
| `user` | The user's role, skills, language, or working preferences become clear | "Prefers replies in Iraqi Arabic, code in English" |
| `feedback` | The user corrects you or confirms an approach. Include the why. | "Don't add dependencies without asking (got burned by bundle size)" |
| `decision` | A choice was made that the code alone won't explain | "Postgres full-text search over Elasticsearch: < 1M rows, fewer services" |
| `convention` | A project rule not enforced by tooling | "API errors always return `{ error: { code, message } }`" |
| `lesson` | A non-obvious root cause or gotcha you learned the hard way | "Tests fail in CI only: timezone is UTC there; use fixed TZ in tests" |
| `reference` | Where something lives outside the code | "Staging logs: Grafana → dashboard 'api-staging'" |
| `project` | Goals, deadlines, constraints, stakeholders. Use absolute dates. | "Launch freeze from 2026-12-01" |

User-level facts (`user` type, and `feedback` that applies everywhere) go
in the user memory. Everything else goes in project memory.

## Knowledge: what NOT to save

- **Secrets:** passwords, tokens, API keys, private keys, personal data. Save
  *where* a secret lives ("in 1Password vault X"), never the secret itself.
- **Anything the repo already records:** code structure, what a function
  does, git history, the contents of README or CLAUDE.md. Memory is for what
  is *not* derivable.
- **Guesses.** Save verified facts. If something is unconfirmed, say so in the entry.
- **Conversation trivia** that won't matter in the next session.

When asked to "remember" something that falls in this list, ask what was
non-obvious about it and save that instead.

## Maintenance

- **Update, don't duplicate.** Before creating a file, grep for an existing
  one on the topic and edit it.
- **Delete what's wrong.** A wrong memory is worse than none, because it gets obeyed.
- **Keep MEMORY.md short:** one line per memory, under about 150 lines. When it
  grows past that, merge related memories into one topic file.
- **Journal housekeeping:** when the journal directory has more than about 30
  daily files, summarize the old month into `journal/YYYY-MM-summary.md`
  (decisions, outcomes, lessons) and delete the daily files it covers.

## The stop check

If the plugin's Stop hook is installed, it checks at the end of each turn:
if you edited files or committed, and neither `NOW.md` nor today's journal
was updated during that turn, it asks you to log before finishing. When it
fires, write the journal entry and refresh NOW.md, then end. That's the whole
response. The user can turn it off with `WOLFIN_MEMORY_GATE=off`.

## Red flags

| Thought | Reality |
|---|---|
| "I'll remember this" | You won't survive compaction. Write it down. |
| "I'll log everything at the end" | The end may come as a compaction. Log at each milestone. |
| "It's in the conversation already" | The next session can't see the conversation. |
| "NOW.md is roughly right" | A stale resume point sends the next session the wrong way. Rewrite it. |
| "I'll save the token so we don't lose it" | Never. Save where it's stored. |
| "This memory says X, so X" | Memories age. Verify file, function and flag names before acting on them. |
