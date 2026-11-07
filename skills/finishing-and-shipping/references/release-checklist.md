# Release Checklist

Scale it to the change. A copy fix needs the first section. A schema
migration needs all of it. Mark each item ✅, ➖ (not applicable) or ❌
(with what's missing).

## Before merge
- [ ] Full test suite, linter, type checker and build pass on the final commit
- [ ] Reviewed (`code-review-workflow`), with Critical and Important findings resolved
- [ ] No secrets, debug flags, `console.log`/`print` leftovers, or commented-out code
- [ ] Docs, README, API docs and changelog updated where behavior changed
- [ ] New environment variables and config documented, with safe defaults

## Database and data
- [ ] Migrations are **backward compatible** with the currently deployed code
  - Adding a column: nullable or with a default, and backfill separately
  - Renaming or removing: expand (add new) → deploy code that writes both → backfill → switch reads → contract (remove old) in a later release
- [ ] Migrations tested on a production-sized copy (lock time, duration)
- [ ] Large backfills run in batches, as background jobs, not in the migration
- [ ] New indexes created concurrently where the DB supports it (`CREATE INDEX CONCURRENTLY`)
- [ ] Down-migration or a documented manual rollback

## Rollout
- [ ] Risky behavior is behind a feature flag, defaulting to off
- [ ] Staged rollout (canary, percentage, internal users first) for high-risk changes
- [ ] Rollback procedure written down and fast (< 5 min): revert, flag off, or redeploy the previous artifact
- [ ] Dependent services and clients are compatible (API versioning, no breaking contract changes without notice)
- [ ] Cache invalidation planned if data shapes changed

## Observability
- [ ] Errors from the new code paths are logged with context (request ID, entity IDs)
- [ ] A metric or dashboard shows the change is working (success rate, latency, usage)
- [ ] Alerts exist for the failure modes that matter
- [ ] For performance-related changes: the before/after numbers are recorded (`performance-optimization`)

## After release
- [ ] Watch errors, latency and key metrics for the first hour or day
- [ ] Verify the feature works in production (smoke test the critical path)
- [ ] Remove the feature flag once it's stable (it's tech debt otherwise)
- [ ] Record follow-ups and known limitations in the issue tracker
- [ ] Close the issue, and notify the stakeholders
