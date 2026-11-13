# Deep Modules

Agents speed up coding, and with it software entropy: codebases grow
shallow, tangled and hard to test faster than ever. The cure is to care
about the shape of modules every day. This is the vocabulary for that,
from John Ousterhout's *A Philosophy of Software Design* and Michael
Feathers' *Working Effectively with Legacy Code*. Use these words exactly
when designing or reviewing structure, so the conversation stays precise.

## Vocabulary

- **Module:** anything with an interface and an implementation, at any
  scale: a function, a class, a package, a slice across tiers.
- **Interface:** everything a caller must know to use the module correctly.
  Not just the type signature: also invariants, ordering constraints, error
  modes, required configuration and performance characteristics.
- **Implementation:** the code inside the module.
- **Depth:** how much behavior a caller (or a test) gets per unit of
  interface they must learn. A **deep** module hides a lot behind a small
  interface. A **shallow** one has an interface nearly as complex as its
  implementation.
- **Seam:** a place where behavior can change without editing that place.
  It's where an interface lives. Where to put a seam is its own decision.
- **Adapter:** a concrete thing that satisfies an interface at a seam: the
  Postgres repository, the in-memory fake, the HTTP client.
- **Leverage:** what callers gain from depth: more capability per thing
  learned. One implementation pays back across every caller and test.
- **Locality:** what maintainers gain from depth: change, bugs and
  knowledge concentrate in one place. Fix once, fixed everywhere.

```
Deep                              Shallow
┌──────────────────────┐          ┌──────────────────────────────┐
│   small interface    │          │      large interface         │
├──────────────────────┤          ├──────────────────────────────┤
│                      │          │  thin implementation         │
│  rich implementation │          └──────────────────────────────┘
│                      │
└──────────────────────┘
```

## Principles

- **The deletion test.** Imagine deleting the module. If its complexity
  vanishes, it was a pass-through: inline it. If the complexity reappears in
  every caller, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same
  seam. If a test has to reach past the interface, the module is the wrong
  shape.
- **One adapter is a hypothetical seam. Two make a real one.** Don't add an
  interface, port or injection point until something actually varies across
  it (usually production plus test).
- **Depth lives in the interface, not the implementation.** A deep module
  can be built from small parts with their own internal seams and tests;
  they just aren't part of its interface.
- **Ask of every interface:** can it have fewer entry points, simpler
  parameters, more hidden inside?

## Designing for testability

1. **Accept dependencies, don't create them.**
   ```typescript
   // ✅ testable: the gateway is passed in
   function processOrder(order: Order, payments: PaymentGateway) {}
   // ❌ hard to test: the dependency is built inside
   function processOrder(order: Order) { const payments = new StripeGateway(); }
   ```
2. **Return results instead of producing side effects.** `calculateDiscount(cart): Discount`
   is easier to test than `applyDiscount(cart): void` that mutates the cart.
3. **Small surface.** Fewer methods and parameters mean fewer tests and
   simpler setup.

## Deepening a cluster of shallow modules

First classify what the cluster depends on. The category decides how the
deepened module is tested:

| Dependency | Example | How to test the deepened module |
|---|---|---|
| In-process | Pure logic, in-memory state | Merge the modules and test through the new interface. No adapter needed |
| Local stand-in exists | PGLite for Postgres, an in-memory file system | Run the stand-in in the test suite. The seam stays internal |
| Remote but yours | Your own services across the network | Define a port at the seam; an HTTP adapter in production, an in-memory adapter in tests |
| Truly external | Stripe, Twilio, a partner API | Inject it as a port; tests use a fake adapter |

**Replace tests, don't layer them.** Once tests exist at the deepened
module's interface, delete the old unit tests on the shallow pieces. Tests
that must change whenever the implementation changes are testing past the
interface.

## Design it twice

Your first interface is rarely the best. For a module that matters, have
three or more fresh subagents each design a radically different interface
in parallel, each under a different constraint:

1. Minimize the interface: one to three entry points, maximum leverage each.
2. Maximize flexibility: many use cases and extension points.
3. Optimize for the most common caller: make the default case trivial.
4. (When it crosses a network or a third party) design around ports and adapters.

Each returns the interface (types, invariants, error modes), a usage
example, what it hides, its dependency strategy, and its trade-offs. Compare
them on depth, locality and seam placement, then recommend one, or a
hybrid, and say why. Be opinionated: the user wants a strong read, not a menu.
