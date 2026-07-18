# FEATURE_SPECIFICATIONS.md

# AI-ATS Feature Specifications

## 1. Authentication & Multi-Tenancy

**Description**: Secure access to the platform ensuring data isolation between organizations.

**Acceptance Criteria**:
- [ ] User can register a new organization and become `Org Admin`.
- [ ] User can invite other users to their organization.
- [ ] Users can only view data (Jobs, Candidates, Applications) associated with their `organization_id`.
- [ ] JWT tokens expire after 15 minutes. Refresh tokens are HTTP-only cookies.
- [ ] API endpoints reject requests without a valid token.
- [ ] API endpoints reject requests if the user lacks the required role.

## 2. Job Management

**Description**: The ability for recruiters and hiring managers to create and manage job postings.

**Acceptance Criteria**:
- [ ] Recruiter can create a job with a title, description, location, and employment type.
- [ ] Recruiter can define a list of required and preferred skills.
- [ ] Job status can be toggled between Draft, Open, Paused, and Closed.
- [ ] When a job is created/updated, a vector embedding of its requirements is generated asynchronously.

## 3. Resume Parsing

**Description**: Automatic extraction of structured data from candidate resumes using LLMs.

**Acceptance Criteria**:
- [ ] Candidate uploads PDF or DOCX (max 5MB).
- [ ] System returns 202 Accepted immediately.
- [ ] Background worker extracts text.
- [ ] Background worker calls LLM to extract JSON (Experience, Education, Skills).
- [ ] System saves parsed JSON to `candidates` table.
- [ ] System handles parsing failures gracefully and allows manual entry.

## 4. Semantic AI Matching

**Description**: Finding the best candidates for a job using vector similarity and ML ranking.

**Acceptance Criteria**:
- [ ] Job embeddings and Candidate embeddings are stored in `pgvector`.
- [ ] Recruiter views a job's candidate pool and sees candidates ranked by match score.
- [ ] Match score calculation considers both semantic similarity (vector distance) and hard business rules (e.g., years of experience).
- [ ] Recruiter can view an "Explanation" for the score (Strengths, Weaknesses, Missing Skills).
- [ ] The matching algorithm executes in under 2 seconds for a pool of 1,000 candidates.

## 5. Application Pipeline (Kanban)

**Description**: Visual management of candidates moving through the hiring process.

**Acceptance Criteria**:
- [ ] Applications are displayed in a Kanban board grouped by Stage.
- [ ] Recruiter can drag and drop a candidate card to a new stage.
- [ ] Moving to "Rejected" requires selecting a rejection reason.
- [ ] Board can be filtered by AI Match Score (e.g., "Show only > 80%").
