# CODING_STANDARDS.md

# AI-ATS Coding Standards

Version: 1.0

## Core Principles

1. **Clean Code**: Follow SOLID principles. Write code for humans first, machines second.
2. **Explicit over Implicit**: Avoid "magic" behavior. Use explicit configurations and clear variable names.
3. **DRY (Don't Repeat Yourself)**: Extract common logic, but do not prematurely abstract.
4. **KISS (Keep It Simple, Stupid)**: Avoid over-engineering.

---

## Backend (Python 3.11+)

### 1. Style & Formatting
- Code is formatted automatically using **Black** (line length 88).
- Linting is enforced via **Ruff**.
- Imports are sorted using `isort` (configured within Ruff).

### 2. Typing
- **Type Hints are Mandatory**: Every function, method, and variable (where ambiguous) must have type hints.
- Use `mypy` for static type checking in CI.

```python
# Correct
def calculate_score(match_data: dict[str, Any], weight: float = 1.0) -> float:
    return match_data.get("base_score", 0.0) * weight

# Incorrect
def calculate_score(match_data, weight=1.0):
    return match_data.get("base_score", 0.0) * weight
```

### 3. Naming Conventions
- Variables, functions, methods: `snake_case`
- Classes, exceptions: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Protected methods/variables: prefix with `_` (e.g., `_internal_method`)

### 4. Pydantic Models
- Use `BaseModel` from `pydantic` v2 for all request/response schemas.
- Provide descriptive `Field` definitions with constraints and examples.

### 5. Dependency Injection
- Use FastAPI's `Depends` for controllers.
- Pass dependencies explicitly in services (do not rely on global state).

---

## Frontend (Next.js 14+ / TypeScript)

### 1. Style & Formatting
- Code is formatted automatically using **Prettier**.
- Linting is enforced via **ESLint** (Strict Next.js configuration).

### 2. TypeScript
- **No `any`**: Do not use the `any` type. Define interfaces or types for all objects.
- Prefer `type` for unions/intersections, `interface` for object shapes.

### 3. Component Architecture
- Use **Functional Components** with Hooks.
- One component per file.
- File naming: `PascalCase.tsx` (e.g., `JobCard.tsx`).
- Extract reusable logic into custom hooks (`useCamelCase.ts`).

### 4. Styling
- Use **Tailwind CSS** for styling. Avoid custom CSS unless absolutely necessary.
- Use **Shadcn UI** for base components (buttons, dialogs, inputs).

### 5. Data Fetching
- Use **TanStack Query** (React Query) for client-side data fetching, caching, and mutations.
- Keep server actions in a dedicated `actions/` directory if using App Router.

---

## Git Workflow

1. **Branch Naming**:
   - Features: `feat/issue-123-short-desc`
   - Bug Fixes: `fix/issue-124-short-desc`
   - Chores: `chore/dependency-updates`
2. **Commit Messages**: Follow Conventional Commits format (`type(scope): description`).
   - Example: `feat(auth): implement JWT refresh rotation`
3. **Pull Requests**:
   - Must pass all CI checks (lint, test, build).
   - Require at least 1 approval from a code owner.
   - Squash and merge to `main`.
