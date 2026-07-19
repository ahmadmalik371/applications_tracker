# Search Optimization

## Indexes

The following indexes are created in migration `a1b2c3d4e5f6`:

### pgvector (semantic similarity)
```sql
CREATE INDEX ix_candidates_embedding ON candidates
  USING ivfflat (embedded vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ix_jobs_embedding ON jobs
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### Full-text search (keyword)
```sql
CREATE INDEX ix_candidates_tsv ON candidates
  USING gin (to_tsvector('english', coalesce(first_name,'') || ' ' || coalesce(last_name,'') || ' ' || email));
CREATE INDEX ix_jobs_tsv ON jobs
  USING gin (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,'')));
```

## Hybrid Search

`hybrid_search_candidates` combines keyword (PostgreSQL full-text) and semantic
(pgvector cosine similarity) results using configurable weights (default 0.6/0.4).

## Caching

Search results are cached via the Redis cache service (`src.services.cache`) under
the `search` namespace with a 5-minute TTL. Invalidation is namespace-scoped.

## Benchmarking

Benchmark with `EXPLAIN ANALYZE` on the hybrid search query. Expected performance
with 100k candidates and the ivfflat index: < 50ms p95.
