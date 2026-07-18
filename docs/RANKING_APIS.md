# Candidate Ranking APIs

Exposes the AI ranking engine over HTTP with re-ranking, history, comparison, filtering, export, and pagination.

Base path: `/api/v1/rankings`

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/candidates/{job_id}` | Rank candidates for a job |
| GET | `/jobs/{candidate_id}` | Rank jobs for a candidate |
| GET | `/explain/candidate/{candidate_id}/job/{job_id}` | Explainable AI breakdown |
| POST | `/candidates/re-rank/{job_id}` | Re-rank with custom weights (snapshot saved to history) |
| GET | `/history/{job_id}` | List ranking history snapshots (paginated) |
| POST | `/compare` | Compare 2+ candidates side by side for a job |
| GET | `/filter/{job_id}` | Rank then filter by score band / required skills |
| GET | `/export/{job_id}?fmt=csv\|json` | Download rankings as CSV or JSON |
| GET | `/candidates/paginated/{job_id}` | Paginated ranking with total count |

## Re-rank

`POST /candidates/re-rank/{job_id}` accepts:

```json
{ "embedding_weight": 0.4, "feature_weight": 0.6 }
```

Each re-rank persists a `RankingHistory` snapshot (top 50 results + weights + top score) so recruiters can audit how scores changed as weights move.

## Comparison

`POST /compare` accepts:

```json
{ "candidate_ids": ["uuid1", "uuid2"], "job_id": "uuid" }
```

Returns each candidate's match score, confidence, feature breakdown, skills, experience years, education, and location — sorted by score descending.

## Filtering

`GET /filter/{job_id}?min_score=60&max_score=95&required_skills=Python&required_skills=FastAPI`

Ranks first, then keeps only candidates inside the score band and possessing every required skill (case-insensitive).

## Export

`GET /export/{job_id}?fmt=csv` returns a CSV download (`text/csv` with `Content-Disposition`).
`GET /export/{job_id}?fmt=json` returns pretty-printed JSON.

## Pagination

`GET /candidates/paginated/{job_id}?skip=0&limit=50` returns:

```json
{ "items": [...], "total": 137, "skip": 0, "limit": 50 }
```

## Tests

`backend/tests/test_ranking_apis.py` covers CSV/JSON export, empty export, min-score filtering, and required-skills filtering.
