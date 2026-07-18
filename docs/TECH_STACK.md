# TECH_STACK.md

# AI-ATS Technology Stack

## 1. Backend

| Technology | Purpose | Justification |
|------------|---------|---------------|
| **Python 3.11+** | Core Language | Industry standard for AI/ML integration. |
| **FastAPI** | API Framework | High performance, async support, auto-generated OpenAPI docs, built-in validation via Pydantic. |
| **SQLAlchemy 2.0** | ORM | Mature, secure ORM supporting complex queries and relationships. |
| **Alembic** | Database Migrations | Standard migration tool for SQLAlchemy. |
| **Pydantic v2** | Data Validation | Fast Rust-based validation, deep integration with FastAPI. |
| **Celery** | Task Queue | Reliable background processing for long-running AI tasks. |
| **Passlib / Argon2** | Password Hashing | Secure, modern hashing algorithms protecting user credentials. |
| **PyJWT** | Authentication | Stateless authentication suitable for distributed systems. |

## 2. Frontend

| Technology | Purpose | Justification |
|------------|---------|---------------|
| **Next.js 14+** | React Framework | App Router, SSR/SSG capabilities, excellent developer experience. |
| **TypeScript** | Core Language | Type safety, fewer runtime errors, better IDE support. |
| **Tailwind CSS** | Styling | Utility-first CSS, highly customizable, fast iteration. |
| **Shadcn UI** | UI Components | Accessible, unstyled components that we own and can customize fully. |
| **TanStack Query** | Data Fetching | Handles caching, background updates, and loading states seamlessly. |
| **React Hook Form** | Form State | Performant form validation without unnecessary re-renders. |
| **Zod** | Schema Validation | Type-safe schema validation, pairs perfectly with React Hook Form. |

## 3. Database & Infrastructure

| Technology | Purpose | Justification |
|------------|---------|---------------|
| **PostgreSQL 16+** | Primary DB | ACID compliant, reliable, supports JSONB. |
| **pgvector** | Vector Store | Allows storing embeddings directly in Postgres alongside relational data. Eliminates need for a separate vector database. |
| **Redis 7+** | Cache / Broker | High performance in-memory store for Celery message brokering and API caching. |
| **Docker** | Containerization | Ensures consistent environments across dev, staging, and prod. |

## 4. AI & ML

| Technology | Purpose | Justification |
|------------|---------|---------------|
| **OpenAI / Anthropic** | LLM Provider | Used for structured data extraction from resumes (parsing). |
| **text-embedding-3-small** | Embeddings | Fast, cheap, high-quality vector embeddings. |
| **XGBoost / LightGBM** | ML Ranking | Tabular ML models for fast, explainable candidate ranking. |
| **SHAP** | Explainability | Provides mathematically sound feature importance scores for explainable AI. |
| **PyMuPDF** | PDF Parsing | Fast text extraction from uploaded resumes. |
