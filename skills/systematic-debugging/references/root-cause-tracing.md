# Root Cause Tracing

Bugs often surface deep in the call stack: a file created in the wrong
directory, a DB opened with the wrong path, a `null` three layers down. The
instinct is to fix where the error appears. That's treating the symptom.

**Principle:** trace backwards through the call chain until you find the
original trigger, then fix it at the source.

## Process

1. **Observe the symptom.** `Error: git init failed in ~/project/packages/core`
2. **Find the immediate cause**, the line that directly does it:
   `execFile('git', ['init'], { cwd: projectDir })`
3. **Ask what called this, and with what value?**
   ```
   WorktreeManager.create(projectDir)    ← projectDir = ''  (!)
     ← Session.initializeWorkspace()
     ← Session.create()
     ← test: Project.create('name', context.tempDir)
   ```
   An empty `cwd` resolves to `process.cwd()`, which is the source directory.
4. **Keep tracing up** until you reach where the bad value was *born*:
   `setupTest()` returns `{ tempDir: '' }` until `beforeEach` runs, and the
   test read it at module load time.
5. **Fix at the source:** make `tempDir` a getter that throws if it's read
   before setup. Then consider defense in depth (`defense-in-depth.md`).

## When you can't trace by reading: instrument

Log the inputs and the stack right before the failing operation:

```typescript
console.error('DEBUG gitInit', { directory, cwd: process.cwd(), env: process.env.NODE_ENV, stack: new Error().stack });
```

```python
import traceback, sys
print("DEBUG save_file", path, file=sys.stderr); traceback.print_stack()
```

Run it and filter: `npm test 2>&1 | grep 'DEBUG gitInit'`. Look for the test
file names, the triggering line, and the pattern (same test? same
parameter?). In tests, use stderr or `console.error`, because the app logger
may be silenced.

Remove the instrumentation once you've found the cause, or convert it into
proper debug-level logging if it would help next time.

## Finding a polluting test

When something appears during the suite (a stray file, changed global
state) but not when tests run alone, bisect:

1. Run the suspect test files one at a time (or halves of the list).
2. After each one, check for the pollution (the file exists, the state changed).
3. The first test after which the pollution appears is the polluter.

```bash
for f in $(ls tests/**/*.test.ts); do
  npx vitest run "$f" >/dev/null 2>&1
  if [ -e .git-stray ]; then echo "POLLUTER: $f"; break; fi
done
```

Common causes: shared module-level state, a missing cleanup in
`afterEach`, tests writing to real paths instead of temp directories, and
leaked timers or mocks.

## Key principle

```
symptom → immediate cause → caller → caller → … → origin
                                                    ↑ fix here
                                     then add validation at the layers in between
```

Fixing where the error appears leaves the origin free to cause the next bug
through a different path.
