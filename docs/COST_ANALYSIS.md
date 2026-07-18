# COST_ANALYSIS.md

# AI-ATS Infrastructure & AI Cost Analysis

As a multi-tenant SaaS, unit economics are critical.

## 1. AI API Costs (per candidate)
Assuming a typical resume is 800 tokens.

- **Parsing (e.g., GPT-4o-mini)**: ~$0.00015 / input token + $0.0006 / output token. Estimated cost: **$0.0005 per resume**.
- **Embedding (e.g., text-embedding-3-small)**: ~$0.00002 / 1k tokens. Estimated cost: **$0.00002 per resume**.
- **Total AI Cost per Candidate**: **~$0.00052**

Processing 100,000 resumes costs approximately **$52.00** in LLM API fees.

## 2. Infrastructure Optimization
- **pgvector vs Managed Vector DB**: By using `pgvector` inside our existing Postgres instance, we eliminate the need for a $100+/mo Pinecone or Milvus cluster.
- **Tabular ML vs LLM Scoring**: Using XGBoost for ranking costs literally nothing (CPU time only) compared to passing 1,000 resumes into an LLM context window to rank them, which would cost hundreds of dollars per job.
