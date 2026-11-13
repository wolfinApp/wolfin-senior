---
name: ui-engineering
description: Use whenever you build, change or review user interface code, including small UI tweaks and when the user is in a hurry — pages, components, forms, lists, tables, dialogs, navigation, layout or styling in React, Next.js, Vue, Svelte, Angular, Astro or plain HTML, CSS and Tailwind. Reuses the project's own components and design tokens, designs every state (loading, empty, error, long content), works with a keyboard, a screen reader, right-to-left text and at phone width, gives new designs a deliberate look instead of a template, and checks the result in a real browser before calling it done. Triggers on "build a page", "add a form", "fix the layout", "make it responsive", "style this", "landing page", "dashboard UI".
---

# UI Engineering

A senior frontend engineer isn't faster at typing markup. They read the
codebase before writing, design the states nobody asked for, try what they
built with the keyboard, and look at it in a browser before they say it
works. This skill is that habit, written down.

**The UI isn't done until you've seen it work in a browser, unhappy paths
included.** A passing type check says nothing about whether the button can
be reached with Tab, or whether a long name breaks the layout on a phone.

Say at the start: "Using ui-engineering to build <what>."

## 1. Read the project before you write

Find and use:
- **The stack and its versions** (`docs-first`): framework, router, React 18
  or 19 (it changes `forwardRef`, `use` and actions), TypeScript strictness.
- **The existing components:** if there's a `Button`, `Input`, `Dialog` or a
  design-system package, use it. Never hand-roll a second button.
- **The tokens:** colors, spacing, radius and type scale (CSS variables, the
  Tailwind theme, a theme object). A new hex value or magic pixel number in a
  project that has tokens is a bug.
- **The data layer:** the API helpers, the query library (TanStack Query,
  SWR, server components, loaders) and how errors are already handled.
- **The scripts:** `dev`, `typecheck`, `lint`, `test`, `build`. You'll run them.
- **A sibling page** that does something similar. Match its structure and naming.

Ask before adding a dependency (a UI kit, an icon set, a state or date
library). The platform and the project usually have what you need (rule 10).

## 2. List the states before you build

Everything that shows data or takes input has more states than the happy
path. Write them down for the feature, then build each one:

| State | What the user must see |
|---|---|
| Loading | A placeholder or skeleton with `aria-busy`, and no layout jump when data arrives |
| Empty | Why it's empty and what to do ("No members match "zz". Clear the search.") |
| Error | What failed, in plain words, and a way out (Retry, or a link). Never a blank area or a console-only error |
| Pending action | The control shows progress and is disabled only while the request runs. No double submit |
| Success | Confirmation that it happened, announced to screen readers |
| Long and odd content | Long names, emails and words wrap or truncate. 0, 1 and 500 items all look right |
| Partial failure | One row's action failing doesn't break the rest of the list |
| No permission | The control is hidden or explained, never a click that silently fails |

Find a way to force the failures (a mock flag, a query parameter, offline
mode in devtools) so you can see the error state yourself.

## 3. Build with the platform first

Semantic HTML gives you keyboard support, focus and screen-reader names for
free. Reach for ARIA only when no element does the job.

- `<button>` for actions, `<a href>` (or the router's `Link`) for navigation. Never `<div onClick>`.
- Every input has a visible `<label>`, the right `type` (`email`, `tel`, `url`, `search`), a `name` and `autocomplete`.
- Inputs that submit live in a `<form>` with `onSubmit`, so Enter works.
- Icon-only buttons have a name that says what and which: `aria-label="Remove Ada Lovelace"`, not "Delete" twelve times. The icon gets `aria-hidden="true"`.
- One `<h1>` per page, headings in order, lists as `<ul>`/`<ol>`, tables with `<th scope>`.
- Async results go in a `role="status"` region, blocking errors in `role="alert"`.
- Visible focus on everything interactive (`:focus-visible`). Never remove an outline without a replacement.
- Dialogs move focus in, trap it, close on Escape, and return focus to what opened them.
- Destructive actions get a confirmation or an undo window. After removing a row, move focus somewhere sensible, not to `<body>`.
- Text contrast at least 4.5:1, and never color alone to carry meaning.

The full checklist (forms, motion, images, i18n and RTL, theming, touch,
hydration): `references/ui-checklist.md`. Use it when reviewing UI code.

## 4. State and data: keep it boring

- **Derive, don't sync.** A filtered list is `items.filter(...)` during
  render, not a second state variable kept in step by an effect.
- **Effects are for the outside world** (fetching, subscriptions, timers),
  not for reacting to your own state. Event logic goes in the event handler.
- **Fetching in an effect needs cleanup:** ignore stale responses or abort
  them. If the project has a query library or server components, use those.
- **Never define a component inside another component.** It remounts on
  every render and loses its state and focus.
- **Composition over boolean props.** When a component grows `isCompact`,
  `showHeader` and `withFooter`, split it into variants or compound parts.
- **URL state lives in the URL** when people expect to share or reload it:
  the search query, the tab, the page, the filters.
- **Don't optimize blind.** Memoize, virtualize or split code when a
  measurement or an obvious size calls for it (`performance-optimization`).

## 5. Layout that survives real content

- Design at **375 px wide** first, then widen. The page never scrolls sideways.
- Flex and grid children that hold text need `min-width: 0`. Long strings
  need `overflow-wrap: anywhere`, or a deliberate truncation with the full
  value available elsewhere.
- Touch targets at least 24×24 CSS px, 44 px for primary mobile actions.
- **Right-to-left:** if the product serves Arabic, Hebrew, Persian or Urdu,
  use logical properties (`margin-inline-start`, `inset-inline-end`,
  `text-align: start`), mirror directional icons, and check the page with
  `dir="rtl"`.
- Respect `prefers-reduced-motion`. Animate `transform` and `opacity`, and
  never `transition: all`.
- If the product has a dark theme, check both themes.

## 6. Give new designs a point of view

When there's no design system to extend (a new landing page, a new product),
the default look an AI produces is recognizable and forgettable. Make
deliberate choices instead:

- **Start from the subject.** Who uses it, and what does their world look
  like? A tool for financial analysts and a toy for eight-year-olds should
  share nothing. The subject's materials, vocabulary and conventions are
  where distinctive choices come from.
- **Typography carries the personality.** One or two families, chosen for
  this project, a clear type scale, and line lengths under about 80
  characters.
- **Structure is information.** Numbers only for real sequences; borders,
  labels and dividers only when they encode something.
- **Motion with a purpose.** One orchestrated moment lands better than
  fade-ins on every section. Motion that answers the user's action (opening,
  expanding, confirming) is welcome.
- **Real copy.** Write the actual words, never lorem ipsum or "Unlock the
  power of".
- **Avoid the generated look:** a big number with a gradient accent as the
  hero, fade-up entrances everywhere, cream backgrounds with a terracotta
  accent, purple-to-blue gradients, emoji as icons, all-caps labels on
  everything.

In an existing product, its design system wins. Consistency beats novelty.

## 7. Verify in a real browser

Run in this order, and read the output:

1. The project's `typecheck`, `lint` and `test`, then `build`.
2. **Open the page in a real browser.** Start the dev server and run the
   bundled checker against your own page only:
   ```bash
   node "${CLAUDE_SKILL_DIR}/scripts/ui-check.mjs" http://localhost:5173/settings --out .ui-check
   ```
   (`${CLAUDE_SKILL_DIR}` is this skill's folder.) It loads the page at
   375 px and 1280 px, saves full-page screenshots, and reports console and
   network errors, sideways overflow and its widest culprits, controls with
   no accessible name, clickable `div`s, images without alt text or size, a
   missing `lang`, and the Tab order with any stop that has no visible
   focus. It uses Playwright from the project (`npm i -D playwright-core`
   drives the installed Chrome). If the session has a browser tool, you can
   use that instead, covering the same checks.
3. **Look at the screenshots.** Read them; don't just confirm they exist.
4. **Walk the unhappy paths:** force the error state, search for nothing,
   remove the last item, submit an invalid value, use only the keyboard.
5. Delete the output folder when done, or keep it out of git.

If you can't run a browser here, say exactly what you couldn't verify. "It
builds" is not "it works" (`verification-before-completion`).

## 8. Report

- What you built, and which existing components and tokens you reused.
- The states you handled.
- What you verified and how (commands, checker output, screenshots looked
  at), and what you couldn't verify.
- Follow-ups you deliberately left out.

## Red flags: stop and fix

| Thought or sign | Reality |
|---|---|
| A new button style in a project that has a `Button` | Use the component. Two buttons become ten. |
| The API error only reaches `console.error` | The user sees a blank area. Show the error state. |
| Every row's icon button is named "Delete" | A screen-reader user hears twelve identical buttons. Name the row. |
| A `div` or `li` with `onClick` | Unreachable by keyboard. Use a `button`. |
| An effect that copies props into state | Derive it during render. |
| "It's just a small UI tweak, no need to look" | Small tweaks break layouts. Open the page. |
| "Done", and the page was never opened | Not done. Run step 7. |
