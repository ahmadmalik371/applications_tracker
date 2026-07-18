# Business Rule Engine

The rule engine screens candidates against configurable, organization-scoped rules before they enter the ranking pipeline.

## Rule Model (`src/models/rules.py`)

Each `Rule` belongs to an organization and is evaluated against a candidate/job pair.

| Field | Type | Description |
|---|---|---|
| `rule_type` | `experience`, `skills`, `education`, `location`, `seniority`, `custom` | What the rule checks |
| `operator` | `equals`, `not_equals`, `greater_than`, `less_than`, `contains`, `not_contains`, `in`, `not_in` | Comparison operator |
| `condition_value` | JSON | Type-specific payload (e.g. `{"years": 5}`, `{"skills": ["Python"]}`) |
| `score_impact` | int | Score added when the rule passes |
| `is_blocking` | bool | If true, failing the rule fails the whole evaluation |
| `priority` | int | Execution order (lower runs first) |
| `is_active` | bool | Soft-disable a rule without deleting it |

## Evaluation (`src/services/rules.py`)

`RuleEvaluationService.evaluate_candidate_against_job(session, candidate, job, organization_id)` runs every active rule for the organization and returns:

```json
{
  "overall_passed": true,
  "blocking_rules_failed": [],
  "total_score_impact": 25,
  "rules_passed": 2,
  "rules_failed": 0,
  "details": [
    {
      "rule_id": "...",
      "rule_name": "Minimum 3 years experience",
      "passed": true,
      "reason": "Rule 'Minimum 3 years experience' passed for candidate ...",
      "score_impact": 10,
      "is_blocking": false
    }
  ]
}
```

Each evaluation is persisted as a `RuleEvaluation` row for auditability.

### Supported rule types

- **experience** — compares total years parsed from the resume against `condition_value.years`.
- **skills** — `contains` (any), `in` (all), `not_contains` (none) against `condition_value.skills`.
- **education** — substring match on the candidate's education entries.
- **location** — compares candidate location to `condition_value.location` (or the job location).
- **seniority** — infers seniority from years of experience and compares to `condition_value.seniority` (junior/mid/senior/lead/principal).

## API (`src/api/v1/routers/rules.py`)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/rules` | Create a rule (admin/recruiter) |
| GET | `/api/v1/rules` | List rules for the organization |
| GET | `/api/v1/rules/{rule_id}` | Get a rule |
| PUT | `/api/v1/rules/{rule_id}` | Update a rule |
| DELETE | `/api/v1/rules/{rule_id}` | Delete a rule |
| POST | `/api/v1/rules/evaluate/candidate/{candidate_id}/job/{job_id}` | Evaluate all rules |

## Tests

`backend/tests/test_rules.py` covers experience (greater_than), skills (contains pass), and skills (missing skill fail).
