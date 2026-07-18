# AI_EVALUATION.md

# AI Model Evaluation

## Metrics

To ensure the ranking system is effective, we track offline and online metrics.

### Offline Metrics (During Training/Tuning)
- **NDCG (Normalized Discounted Cumulative Gain)**: Measures ranking quality. If the model ranks candidates that a human also ranked highly at the top, NDCG approaches 1.0.
- **Precision@K**: The percentage of the top K ranked candidates that were actually interviewed or hired in historical data.

### Online Metrics (Production)
- **Click-Through Rate (CTR)**: How often recruiters click into the profile of a top-5 ranked candidate.
- **Stage Progression Rate**: The correlation between a high AI match score and the likelihood of the candidate moving to the "Interview" stage.

## A/B Testing
When deploying a new version of the Ranker or updating the embedding model:
1. Route 10% of jobs to Model B.
2. Compare CTR and Stage Progression Rate after 2 weeks.
3. Promote to 100% if statistically significant improvement is observed.
