# SOLID and Design Patterns: Smells and Fixes

## SOLID

### S: Single Responsibility
**Smell:** a class or module changes for unrelated reasons. `UserService`
handles validation, SQL, emails and PDF reports. Its name needs "and" or
"Manager".
**Fix:** split by reason to change: `UserValidator`, `UserRepository`,
`WelcomeMailer`. The original becomes a thin coordinator, or disappears.

```python
# ❌
class Report:
    def compute(self): ...
    def to_pdf(self): ...
    def email(self, to): ...
# ✅
class Report:            # data + computation only
    def compute(self): ...
def render_pdf(report: Report) -> bytes: ...
def send_report(report: Report, to: str, mailer: Mailer) -> None: ...
```

### O: Open/Closed
**Smell:** every new variant means editing a growing `if/elif` or `switch` on a type.
**Fix:** a lookup table or polymorphism. New variants add code without
touching stable code.

```typescript
// ❌
function price(kind: string, base: number) {
  if (kind === 'student') return base * 0.5;
  if (kind === 'senior') return base * 0.7;
  return base;
}
// ✅
const discounts: Record<string, number> = { student: 0.5, senior: 0.7 };
const price = (kind: string, base: number) => base * (discounts[kind] ?? 1);
```

Don't pre-build extension points for variants that don't exist yet (YAGNI).
Refactor toward open/closed when the second or third variant arrives.

### L: Liskov Substitution
**Smell:** a subclass throws `NotImplemented` for a parent method, narrows
the accepted inputs, or callers check `isinstance` before calling.
Classic: `Square extends Rectangle` breaks `setWidth`.
**Fix:** model the actual capabilities. Use composition or a smaller shared
interface instead of forcing inheritance.

### I: Interface Segregation
**Smell:** implementers stub out half an interface. Clients depend on
methods they never call.
**Fix:** split it into role interfaces: `Readable`, `Writable`, `Closable`.
Clients ask only for what they use.

### D: Dependency Inversion
**Smell:** business logic constructs its own DB client, HTTP client or
clock (`new PostgresClient()` inside `OrderService`), so you can't test it
without the real thing.
**Fix:** depend on an interface and inject the implementation.

```typescript
interface PaymentGateway { charge(cents: number, token: string): Promise<ChargeResult> }
class Checkout {
  constructor(private gateway: PaymentGateway, private clock: () => Date) {}
}
// prod: new Checkout(new StripeGateway(key), () => new Date())
// test: new Checkout(fakeGateway, () => new Date('2026-01-01'))
```

## Design patterns: when they help, when they hurt

| Pattern | Use when | Don't use when |
|---|---|---|
| **Factory** | Construction varies by type or config, or is complex (many steps, validation) | A plain constructor works |
| **Builder** | Many optional parameters, step-by-step construction | 2–3 parameters (use named args or an options object) |
| **Singleton** | Truly one stateless resource (a logger) | Anything with mutable state. It's a global variable, hard to test. Prefer injecting one instance. |
| **Adapter** | Wrapping a third-party or legacy API behind your own interface, so you can swap or mock it | You control both sides |
| **Proxy / Decorator** | Adding caching, logging, retries, auth or lazy loading without changing the wrapped object | One call site. Just call the thing. |
| **Facade** | Giving a simple entry point to a messy subsystem | The subsystem is already simple |
| **Strategy** | Swappable algorithms (pricing rules, sort orders, export formats) | Exactly one algorithm |
| **Observer / Events** | Decoupled reactions (order placed → email, analytics, stock) | The flow must be traced step by step, or the order matters |
| **Repository** | Isolating data access from business logic | A tiny script |

**Rule of thumb:** if you can't name the concrete problem the pattern solves
*in this codebase today*, don't add it. Pattern-heavy code with one
implementation per interface is moderate-abstraction failure (principle 6).

## Refactoring moves (always under green tests)

| Smell | Move |
|---|---|
| Long function | Extract function, named for intent |
| Duplicate code (3rd time) | Extract a shared helper |
| Long parameter list | Introduce a parameter object |
| Type-switch repeated in several places | Replace the conditional with polymorphism or a map |
| Feature envy (method uses another object's data more than its own) | Move the method |
| Primitive obsession (`string email` everywhere) | Introduce a value type |
| Shotgun surgery (one change touches 10 files) | Gather the responsibility into one module |
| Speculative generality | Inline the abstraction, delete unused hooks |
| Comments explaining confusing code | Rename and extract until the comment is unnecessary |
