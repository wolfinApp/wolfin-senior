# Changelog

All notable changes to Wolfin Senior. Versions follow [Semantic Versioning](https://semver.org).

## 3.0.0 (2026-11-13)

The best ideas from Matt Pocock's skills and the most-used engineering skills
on aitmpl.com, folded into the existing chain instead of piled beside it.

### Added
- **`ui-engineering` skill:** reuse the project's components and tokens, design
  every state, accessibility from the platform up, right-to-left layouts, a
  deliberate look for new designs, and a browser check before "done".
  Ships `scripts/ui-check.mjs` (screenshots at 375 and 1280 px, console errors,
  overflow, unnamed controls, Tab order) and a full UI review checklist.
- **`architecture-review` skill:** finds hot spots in git history, applies the
  deletion test, ranks deepening candidates with before and after sketches,
  then designs the one you pick.
- **Five commands:** `/wolfin-senior:grill`, `review`, `audit`, `handoff`, `retro`.
- **Git guard hook:** force push, `reset --hard`, `clean -f`, `branch -D`,
  discarding changes, dropping stashes and history rewrites now ask you first,
  with what would be lost. Off with `WOLFIN_GIT_GUARD=off`.
- **Deep modules reference** (`engineering-principles`): module, interface,
  depth, seam, adapter, the deletion test, and "design it twice".
- **Domain language reference** (`requirements-and-design`): `GLOSSARY.md`
  and the three-part test for ADRs.
- **OWASP Top 10:2025** map, supply-chain and fail-safe sections in the
  security checklist.
- **Tests and CI:** behavior tests for every hook and structural checks for
  every skill, run on each push.

### Changed
- `requirements-and-design`: questions in rounds over a design tree, each with
  a recommended answer; facts are looked up, only decisions are asked;
  prototypes for questions talk can't settle; user stories and testing
  decisions in the design doc; shorter ADRs.
- `writing-plans`: vertical tracer-bullet tasks with "Blocked by" edges,
  prefactoring first, expand-migrate-contract for wide refactors.
- `test-driven-development`: agree the seams first, one slice at a time,
  mock only at system boundaries, tautological tests called out.
- `systematic-debugging`: build a command that goes red on the bug before
  any theory, minimise it, rank three to five falsifiable hypotheses, tag
  debug logs, clean up before "fixed".
- `code-review-workflow`: two axes (spec and standards), a bug hunt list, a
  code-smell baseline, every finding proven with a failure scenario, severity
  and a verdict first. Reviews never touch your checkout.
- `finishing-and-shipping`: pull requests carry a visual summary, before and
  after evidence, and the merge danger (one-way or two-way door).
- `project-memory`: handoff notes for a fresh session.

## 2.0.0 (2026-11-07)

- Renamed to Wolfin Senior (`wolfin-senior`).
- Strict mode: the router is binding, a reminder rides on every prompt, code
  edits wait for `docs-first` and `test-driven-development`, and a turn that
  changed code must verify and log before it ends.

## 1.0.0 (2026-11-05)

- First release: 13 skills mapped to the SDLC, the 19 rules, the 10 coding
  principles, a 31-point performance audit, docs-first version checks, and
  project memory.
