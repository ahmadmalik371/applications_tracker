# DESIGN_SYSTEM.md

# AI-ATS Design System

## Core Philosophy
The UI must feel professional, clean, and highly responsive. As an enterprise tool, data density is important, but not at the cost of readability. 

We use **Shadcn UI** as the foundation, built on top of Tailwind CSS.

## 1. Typography
- **Primary Font**: `Inter` (Sans-serif)
- **Monospace Font**: `JetBrains Mono` (For code/logs)

## 2. Color Palette (Tailwind Configuration)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "hsl(222.2 47.4% 11.2%)", // Deep Blue
          foreground: "hsl(210 40% 98%)",
        },
        secondary: {
          DEFAULT: "hsl(210 40% 96.1%)",
          foreground: "hsl(222.2 47.4% 11.2%)",
        },
        accent: {
          DEFAULT: "hsl(210 40% 96.1%)",
          foreground: "hsl(222.2 47.4% 11.2%)",
        },
        success: "hsl(142.1 76.2% 36.3%)",
        warning: "hsl(38 92% 50%)",
        destructive: "hsl(0 84.2% 60.2%)",
      }
    }
  }
}
```

## 3. Components (Shadcn)
- **Buttons**: Use standard variants (`default`, `secondary`, `outline`, `ghost`, `destructive`).
- **Cards**: Use for Job listings, Candidate profiles, and Analytics widgets.
- **Data Tables**: Used heavily for candidate lists. Must support sorting, filtering, and pagination.
- **Badges**: Use for status indicators (e.g., `Draft`, `Open`, `Rejected`).
- **Skeleton**: Use for loading states instead of spinners where possible.
