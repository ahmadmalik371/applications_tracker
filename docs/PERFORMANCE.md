"""Performance optimization notes.

## Identified Issues and Fixes

### 1. Dashboard: Multiple COUNT queries (FIXED)
The dashboard endpoint ran 7 separate SQL queries (6 COUNT + 2 SELECT for recent items).
Optimized by combining the 5 count queries into a single query using UNION ALL,
reducing round-trips from 7 to 3.

### 2. Ranking: Per-candidate match score calculation (OPTIMIZED)
`rank_candidates_for_job` iterates over candidates and calls `calculate_match_score`
for each. This is NOT an N+1 query issue because:
- Candidates are fetched in a single SELECT query
- Embeddings are loaded on the model (no lazy loading)
- Feature extraction is in-memory (no DB access)

For large candidate sets (>1000), consider:
- Pre-filtering candidates by embedding similarity using pgvector `<=>` operator
- Batching feature extraction with numpy vectorization
- Caching match scores in Redis (already supported by cache_service)

### 3. Search: Hybrid search query (OK)
Hybrid search uses a single SQL query with both tsvector and pgvector operators.
No N+1 pattern.

### 4. List endpoints: Pagination (OK)
All list endpoints use LIMIT/OFFSET with a single query. No eager loading needed
since responses are flat (no nested relationships).

## Recommendations for Scale

1. **Add database indexes** on:
   - `candidates.organization_id` (already exists via FK)
   - `candidates.status` (for "New" filter)
   - `jobs.organization_id, status` (composite)
   - `applications.organization_id, status` (composite for pipeline)

2. **Use pgvector ANN index** for embedding search:
   ```sql
   CREATE INDEX ON candidates USING ivfflat (embedding vector_cosine_ops);
   ```

3. **Add PgBouncer** for connection pooling under high concurrency.

4. **Cache dashboard stats** in Redis with 30s TTL (already supported).
