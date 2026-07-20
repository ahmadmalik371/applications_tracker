# Accessibility (a11y) Guidelines

## Standard: WCAG 2.1 AA

The AI-ATS frontend targets WCAG 2.1 Level AA compliance.

## Implemented Features

### Keyboard Navigation
- Skip-to-main-content link (visible on focus) in `layout.tsx`
- All interactive elements are keyboard-accessible via tab navigation
- Focus states are visible on all components

### Screen Reader Support
- Semantic HTML: `<main>`, `<header>`, `<nav>` landmarks used throughout
- `id="main-content"` anchor for skip link
- `aria-label` attributes on icon-only buttons
- `role` attributes where semantic HTML is insufficient

### ARIA Labels
- Form inputs have associated `<label>` elements
- Loading states use `aria-busy` and `aria-live="polite"`
- Status badges use `role="status"`
- Error messages use `role="alert"`

### Color Contrast
- Body text uses `text-zinc-900` on `bg-zinc-50` (contrast ratio > 7:1)
- Muted text uses `text-zinc-500` (contrast ratio > 4.5:1)
- Interactive elements maintain visible focus indicators

### Responsive Design
- Mobile-first breakpoints (sm, md, lg)
- Touch targets minimum 44x44px
- No horizontal scroll on mobile viewports

## Testing

- Manual keyboard navigation testing on all pages
- Screen reader testing with NVDA and VoiceOver
- Automated contrast checking via axe-core (recommended for CI)
- Lighthouse accessibility audit (target score: 90+)
