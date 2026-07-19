# ML Pipeline

## Feedback Loop

Recruiters rate AI recommendations (good / bad / false_positive / false_negative)
via `POST /api/v1/ml/feedback`. Feedback is persisted in `ai_recommendation_feedback`
and aggregated via `GET /api/v1/ml/feedback/summary` for future model retraining.

```
Ranking → Recruiter reviews → Feedback recorded → Retraining dataset → New model version
```

## Model Version Management

- `POST /api/v1/ml/models` — register a new model version
- `POST /api/v1/ml/models/{id}/deploy` — activate a version (deactivates all others)
- `POST /api/v1/ml/models/{id}/rollback` — rollback to a previous version

Only one model version can be active at a time. Deploying or rolling back
atomically flips the `is_active` flag.

## Evaluation Metrics

Each evaluation records: precision, recall, F1, ROC AUC, MAP@K, NDCG, latency (ms).

- `POST /api/v1/ml/models/{id}/evaluations` — add evaluation metrics
- `GET /api/v1/ml/models/{id}/evaluations` — list evaluations

## Bias Monitoring

Fairness metrics are computed and stored in `bias_reports`:

- **Demographic parity**: |P(hired|A) - P(hired|B)|; flagged when > threshold (default 0.1)
- **Disparate impact**: min(p_a, p_b) / max(p_a, p_b); flagged when < threshold (default 0.8)

Flagged reports surface warnings to recruiters and admins.
