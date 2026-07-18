# UI_UX_GUIDELINES.md

# AI-ATS UI/UX Guidelines

## 1. Principles
- **Clarity over Cleverness**: Actionable buttons must be obvious.
- **Feedback Loop**: Every action (create, update, delete) must provide immediate feedback (Toast notification or inline error).
- **Graceful Degradation**: If the AI matching service is slow, the UI should not freeze. Show a skeleton loader for the AI score while rendering the rest of the candidate data.

## 2. Empty States
Always provide helpful empty states.
- *Bad*: "No jobs found."
- *Good*: "You haven't posted any jobs yet. [Create your first Job]"

## 3. Form Validation
- Validate on blur (when user leaves field).
- Display errors inline below the input field.
- Disable submit button while submitting to prevent double-posts.
- Use `Zod` schemas for all frontend form validation.

## 4. Accessibility (a11y)
- All interactive elements must be keyboard navigable.
- Ensure sufficient color contrast (WCAG AA).
- Use `aria-labels` for icon-only buttons.
