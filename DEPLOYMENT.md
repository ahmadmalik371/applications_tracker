# DEPLOYMENT.md

# AI-ATS Deployment Guide

## Architecture Topology

The production architecture consists of:
- Load Balancer (Nginx/Traefik or Cloud LB)
- Application Servers (FastAPI running via Uvicorn/Gunicorn)
- Frontend Servers (Next.js Node server or static CDN + Edge functions)
- PostgreSQL (Primary/Replica) with `pgvector`
- Redis (Session cache & Celery message broker)
- Celery Workers (Asynchronous processing)
- Object Storage (S3 for resumes and avatars)

---

## Local Development (Docker Compose)

For local development, we use Docker Compose to spin up all necessary infrastructure.

1. Copy `.env.example` to `.env` and fill in required values.
2. Run `make docker-up` (or `docker-compose up -d`).
3. Run database migrations: `make migrate`.
4. Access the API at `http://localhost:8000`.
5. Access the Frontend at `http://localhost:3000`.

---

## Production Deployment Strategies

### 1. VM / Bare Metal (Docker Compose)
Suitable for early-stage production or staging.
- Deploy the updated code to the VM.
- Pull latest Docker images.
- Run `docker-compose -f docker-compose.prod.yml up -d`.

### 2. Cloud Native (AWS / GCP) - Recommended
- **Compute**: AWS ECS (Fargate) or GCP Cloud Run for API and Frontend.
- **Database**: Amazon RDS for PostgreSQL or Google Cloud SQL (Ensure pgvector is supported/enabled).
- **Cache**: Amazon ElastiCache or GCP Memorystore (Redis).
- **Storage**: Amazon S3 or Google Cloud Storage.
- **Workers**: ECS Fargate tasks running the Celery worker image.

### 3. Kubernetes (Future Scale)
For massive scale, the platform is designed to be deployed via Helm charts to a Kubernetes cluster.
- Ingress Controller for routing.
- HPA (Horizontal Pod Autoscalers) on the FastAPI API deployments.
- KEDA for autoscaling Celery workers based on Redis queue length.

---

## CI/CD Pipeline

We use GitHub Actions for Continuous Integration and Deployment.

### 1. Pull Request (CI)
- Triggered on PR open/update.
- Runs Python Black/Ruff linters.
- Runs Next.js ESLint.
- Runs Pytest (unit & integration tests against a temporary Postgres container).
- Blocks merge if tests fail or coverage drops.

### 2. Merge to Main (CD / Staging)
- Builds Docker images (`ai-ats-api`, `ai-ats-web`, `ai-ats-worker`).
- Tags images with Git SHA.
- Pushes to Container Registry (ECR/GCR).
- Deploys to Staging environment.
- Runs Alembic migrations automatically.

### 3. Release (Production)
- Triggered on GitHub Release creation.
- Promotes Staging images to Production tags.
- Deploys to Production cluster.
- Monitors health check endpoints (`/api/v1/health`) before routing traffic.
