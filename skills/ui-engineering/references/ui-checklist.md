# UI Review Checklist

Read this when reviewing interface code, or before calling a UI done. Each
line is a check you can answer yes or no by looking at the code or the page.

## Keyboard and focus
- [ ] Every action works with the keyboard alone: Tab to reach, Enter or Space to act, Escape to close
- [ ] Tab order follows the visual order; no positive `tabindex`
- [ ] Every focusable element shows a visible focus style (`:focus-visible`)
- [ ] Dialogs and menus move focus in, keep it inside, and return it on close
- [ ] After an item is removed or a view changes, focus lands somewhere sensible
- [ ] A "skip to content" link exists on pages with long navigation

## Names and semantics
- [ ] Every control has an accessible name that says what and which ("Remove Ada", not "Remove")
- [ ] Buttons are `<button>`, links are `<a href>`; no clickable `div`, `span` or `li`
- [ ] Headings form an outline (one `h1`, no skipped levels)
- [ ] Lists, tables and forms use their real elements
- [ ] Status messages use `role="status"`; blocking errors use `role="alert"`
- [ ] Icons that carry no meaning are `aria-hidden="true"`
- [ ] `<html lang>` is set, and changes for content in another language

## Forms
- [ ] Every input has a visible label (placeholder is not a label)
- [ ] Correct `type`, `name`, `autocomplete` and `inputmode`
- [ ] Errors appear next to the field, in words, linked with `aria-describedby`, and focus moves to the first error on submit
- [ ] Required fields are marked in text, not only with color or an asterisk
- [ ] Submitting is disabled only while the request runs; double submit is impossible
- [ ] Typed input survives an error (the form doesn't reset)

## Content and layout
- [ ] Works at 375 px with no sideways scroll, and up to wide desktop
- [ ] Long names, emails, URLs and words wrap or truncate on purpose
- [ ] 0, 1, many and very many items all look right
- [ ] Text contrast at least 4.5:1 (3:1 for large text and UI parts)
- [ ] Meaning never depends on color alone
- [ ] Line length under about 80 characters for reading text

## Images and media
- [ ] Every `img` has `alt` (empty for decoration) and explicit `width` and `height`
- [ ] Below-the-fold images use `loading="lazy"`; the hero image doesn't
- [ ] Modern formats (WebP or AVIF) with sensible sizes (`srcset`, `sizes`)
- [ ] Video has captions; nothing autoplays with sound

## Motion
- [ ] `prefers-reduced-motion` turns off non-essential animation
- [ ] Only `transform` and `opacity` are animated; no `transition: all`
- [ ] Nothing flashes more than three times a second

## Touch
- [ ] Targets at least 24×24 CSS px, 44 px for primary mobile actions, with space between them
- [ ] Nothing depends on hover alone

## Theming
- [ ] Colors and spacing come from the project's tokens, not new literals
- [ ] Dark theme (if supported) checked: contrast, images, borders, focus rings
- [ ] `color-scheme` is set so form controls and scrollbars match the theme

## Language and direction
- [ ] All user-facing text goes through the project's translation system, if it has one
- [ ] Dates, numbers and currency use `Intl` formatting for the user's locale
- [ ] For right-to-left languages: logical CSS properties, mirrored directional icons, checked with `dir="rtl"`
- [ ] Layout survives text 30% longer than English

## Navigation and URLs
- [ ] Shareable state (tab, filters, search, page) is in the URL
- [ ] Back and forward buttons work as people expect
- [ ] Links that open new tabs say so; external links use `rel="noopener"`
- [ ] The page title changes with the view

## Server rendering and hydration
- [ ] No hydration mismatch: dates, random values and `window` reads happen on the client only
- [ ] The page is usable, or at least readable, before JavaScript finishes loading
