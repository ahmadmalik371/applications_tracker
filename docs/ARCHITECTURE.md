# AI Assistant Architecture

## Overview

The AI Assistant is a service-layer orchestrator that powers six capabilities used
throughout the ATS platform. It is model-agnostic: each capability accepts domain
objects (Candidate, Job) and returns structured dictionaries, so the underlying
LLM provider can be swapped without changing call sites.

## Components

```
┌─────────────────────────────────────────────────┐
│                 API Layer (Routers)              │
│  /ai-assistant/*   /recommendations/*   /ml/*    │
└───────────────┬─────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────┐
│              AIAssistantService                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐      │
│  │ Search   │ │ Summarize│ │ JD Analysis  │      │
│  └──────────┘ └──────────┘ └──────────────┘      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────┐  │
│  │ Interview Qs │ │ Skill Gap    │ │ Compare  │  │
│  └──────────────┘ └──────────────┘ └──────────┘  │
└───────────────┬─────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────┐
│           Supporting Services                    │
│  EmbeddingService  FeatureExtractor  RankingSvc  │
│  SearchService     RecommendationEngine          │
└─────────────────────────────────────────────────┘
```

## Capabilities

| # | Capability | Method | Description |
|---|-----------|--------|-------------|
| 1 | Search | `search_candidates` | Natural-language candidate search via hybrid keyword + semantic matching |
| 2 | Summarization | `summarize_resume` | Structured resume summary with content-hash caching and manual regeneration |
| 3 | JD Analysis | `analyze_job_description` | Detects missing skills, duplicates, readability, biased language, missing experience/salary |
| 4 | Question Generation | `generate_interview_questions` | Technical, behavioral, leadership, problem-solving questions tailored to seniority |
| 5 | Skill Gap Analysis | `analyze_skill_gap` | Compares candidate skills vs job requirements; outputs readiness score |
| 6 | Comparison | `compare_candidates` | Side-by-side AI-assisted comparison with match scores |

## Design Principles

- **No external API dependency in tests**: All capabilities use deterministic heuristics
  so the full test suite runs without API keys. In production, each method delegates to
  an LLM provider.
- **Caching**: Resume summaries are cached by content hash; `force_regenerate=True`
  bypasses the cache.
- **Org isolation**: All queries are scoped by `organization_id`.

## ML Pipeline

See `docs/ML_PIPELINE.md` for the feedback loop, model versioning, evaluation, and
bias monitoring workflow.
