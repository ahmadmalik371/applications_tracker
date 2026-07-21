# Contributing to AI-ATS

First off, thank you for considering contributing to AI-ATS. 

## Code of Conduct
By participating in this project, you are expected to uphold our Code of Conduct: be respectful, collaborative, and professional.

## How to Contribute

### 1. Find or Create an Issue
- Check the issue tracker for open tasks.
- If proposing a new feature, open an issue first to discuss it before writing code.

### 2. Branching Strategy
- Create a branch from `main`.
- Naming convention: `feat/issue-number-desc`, `fix/issue-number-desc`, or `docs/update-readme`.

### 3. Development Rules
- **Follow the Architecture**: Ensure your code respects the Modular Monolith boundaries (see `ARCHITECTURE.md`).
- **Follow Coding Standards**: See `CODING_STANDARDS.md` for Python/TypeScript rules.
- **Write Tests**: New features must include unit/integration tests.
- **Update Docs**: If you change an API or schema, update `API_SPEC.md` or `DATABASE.md`.

### 4. Pull Request Process
- Ensure all CI checks pass (lint, format, test).
- Request review from at least one code owner.
- Address review comments.
- Once approved, squash and merge to `main`.

## Local Setup
See `DEPLOYMENT.md` for instructions on setting up the local Docker Compose environment.
