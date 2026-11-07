# Defense in Depth

When a bug was caused by invalid data, one validation check feels like
enough. But a single check can be bypassed by another code path, a
refactor, or a mock.

**Principle:** after fixing the root cause, validate at each layer the data
passes through, so the bug becomes *structurally impossible* rather than
merely fixed.

## The four layers

**1. Entry point:** reject obviously invalid input at the API or module boundary.
```typescript
function createProject(name: string, dir: string) {
  if (!dir?.trim()) throw new Error('dir cannot be empty');
  if (!existsSync(dir)) throw new Error(`dir does not exist: ${dir}`);
  if (!statSync(dir).isDirectory()) throw new Error(`not a directory: ${dir}`);
  // ...
}
```

**2. Business logic:** check that the data makes sense for *this* operation.
```typescript
function initWorkspace(projectDir: string) {
  if (!projectDir) throw new Error('projectDir required for workspace init');
}
```

**3. Environment guards:** refuse dangerous operations in the wrong context.
```typescript
if (process.env.NODE_ENV === 'test' && !resolve(dir).startsWith(resolve(tmpdir()))) {
  throw new Error(`Refusing git init outside temp dir during tests: ${dir}`);
}
```

**4. Debug instrumentation:** capture context for forensics when everything else fails.
```typescript
logger.debug('about to git init', { dir, cwd: process.cwd(), stack: new Error().stack });
```

## Applying it

1. Trace the data flow: where the bad value originates, and everywhere it's used.
2. List every checkpoint it passes through.
3. Add the right check at each one (not every layer needs all four).
4. Test each layer: bypass layer 1 and verify that layer 2 catches it.

## Keep it proportionate

Defense in depth is for data that can cause real damage: deleting or
writing files, money, permissions, data corruption, security boundaries.
For a cosmetic value, one check at the boundary is enough. Rule 6 still
holds: every line of code is a liability, so don't wrap everything in
redundant guards.

Validation errors should fail loudly, with a message that says what was
wrong and what was expected. Silent coercion (turning `''` into a default)
hides the next bug.
