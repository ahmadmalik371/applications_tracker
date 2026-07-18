# AI_GUARDRAILS.md

# AI Guardrails & Ethics

## Principle: AI Assists, Humans Decide
The AI-ATS system is an assistive technology. It must never automatically reject a candidate or send an offer without human intervention.

## 1. Bias Detection & Mitigation
- **Blind Extraction**: During the resume parsing phase, explicit PII (Names, Addresses, Dates of Birth, Gender pronouns) should ideally be masked before generating embeddings, ensuring the vector space represents skills and experience rather than demographic indicators.
- **Fairness Testing**: The ML Ranker must be regularly tested against demographic datasets to ensure the score distribution is statistically similar across protected classes.

## 2. Hallucination Prevention (Parsing)
- We rely on `temperature=0` and strict JSON schemas for extraction.
- If the LLM generates a skill not present in the original text, it is considered a hallucination.
- **Verification step**: A lightweight script cross-references extracted text blocks against the raw PDF text to ensure fidelity.

## 3. Human Overrides
- Recruiters can manually adjust a candidate's stage regardless of the AI score.
- Recruiters can flag a score as "Inaccurate," which feeds back into the model evaluation pipeline.
