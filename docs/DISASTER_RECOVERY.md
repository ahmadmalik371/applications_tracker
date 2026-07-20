# Disaster Recovery Plan

## Overview

This document outlines the disaster recovery (DR) strategy for the AI-ATS platform. The plan covers backup procedures, recovery processes, and business continuity measures to ensure minimal downtime and data loss.

## Recovery Objectives

| Metric | Target | Description |
|--------|--------|-------------|
| RPO (Recovery Point Objective) | 1 hour | Maximum acceptable data loss |
| RTO (Recovery Time Objective) | 4 hours | Maximum acceptable downtime |
| RLO (Recovery Level Objective) | Full | Complete system restoration |

## Backup Strategy

### 1. Database Backups (PostgreSQL)

| Type | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| Full | Daily | 30 days | `pg_dump` custom format |
| WAL archiving | Continuous | 7 days | PostgreSQL WAL archiving |
| Logical | Weekly | 90 days | `pg_dump` with `--format=custom` |

### 2. File Backups

| Type | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| Uploads | Daily | 30 days | Filesystem copy to backup storage |
| Configs | On change | 90 days | Git-tracked + backup archive |

### 3. Backup Storage

- **Primary**: Local backup directory (`./backups/`)
- **Secondary**: S3-compatible object storage (MinIO/S3)
- **Tertiary**: Off-site cold storage (optional)

## Backup Commands

### Create a Full Backup
```bash
python scripts/backup.py create
```

### List Available Backups
```bash
python scripts/backup.py list
```

### Restore from Backup
```bash
python scripts/backup.py restore backups/backup_20240101_020000.tar.gz
```

### Schedule Automated Backups
```bash
python scripts/backup.py schedule --interval 24
```

## Recovery Procedures

### Scenario 1: Database Corruption

1. **Stop all services**:
   ```bash
   docker-compose down
   ```

2. **Restore database from latest backup**:
   ```bash
   python scripts/backup.py restore backups/backup_latest.tar.gz
   ```

3. **Verify database integrity**:
   ```bash
   docker-compose run --rm backend alembic upgrade head
   docker-compose run --rm backend python -c "from src.core.database import check_connection; print(check_connection())"
   ```

4. **Restart services**:
   ```bash
   docker-compose up -d
   ```

### Scenario 2: Complete Server Failure

1. **Provision new server** with required dependencies (Docker, Python, PostgreSQL).

2. **Restore from latest backup**:
   ```bash
   # Copy backup to new server
   scp backups/backup_latest.tar.gz user@new-server:/opt/ats/backups/
   
   # Restore
   cd /opt/ats
   python scripts/backup.py restore backups/backup_latest.tar.gz
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Verify all components**:
   - API health: `curl http://localhost:8000/health`
   - Frontend: Check `http://localhost:3000`
   - Worker: Check Celery status
   - Database: Verify data integrity

### Scenario 3: Data Center Outage

1. **Activate DR site** (if configured):
   ```bash
   # Update DNS to point to DR site
   # Restore from latest off-site backup
   ```

2. **Scale up DR infrastructure**:
   ```bash
   kubectl scale deployment backend --replicas=3 -n ai-ats
   kubectl scale deployment worker --replicas=2 -n ai-ats
   ```

3. **Verify failover**:
   - Run health checks
   - Verify data consistency
   - Monitor error rates

### Scenario 4: Security Breach

1. **Isolate affected systems**:
   ```bash
   # Revoke all access tokens
   # Rotate all secrets and API keys
   ```

2. **Restore from pre-breach backup**:
   ```bash
   python scripts/backup.py restore backups/backup_pre_breach.tar.gz
   ```

3. **Apply security patches** and audit changes.

4. **Rotate credentials**:
   - Update `.env` with new secrets
   - Update Kubernetes secrets
   - Regenerate API keys

## Monitoring & Alerting

### Health Checks

| Component | Endpoint | Interval |
|-----------|----------|----------|
| API | `/health` | 30s |
| Database | pg_isready | 5s |
| Redis | redis-cli ping | 5s |
| Celery | Flower API | 60s |

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| API response time | > 1s | > 5s | Scale up / investigate |
| Error rate | > 1% | > 5% | Rollback / investigate |
| Queue depth | > 100 | > 1000 | Scale workers |
| Disk usage | > 80% | > 90% | Clean up / expand |
| Memory usage | > 80% | > 95% | Scale up / investigate |

## Business Continuity

### Degraded Mode Operations

During partial outages, the system can operate in degraded mode:

1. **Read-only mode**: Allow viewing data but block modifications
2. **Queue-only mode**: Accept uploads but defer processing
3. **Cache-only mode**: Serve cached responses when DB is down

### Communication Plan

1. **Internal**: Notify team via Slack/email within 15 minutes
2. **External**: Update status page within 30 minutes
3. **Post-mortem**: Conduct within 48 hours of resolution

## Testing

### Recovery Drills

| Frequency | Type | Scope |
|-----------|------|-------|
| Monthly | Tabletop | Review procedures |
| Quarterly | Partial | Restore single component |
| Annually | Full | Complete DR failover |

### Validation Checklist

- [ ] Database restore completes without errors
- [ ] All API endpoints return correct data
- [ ] File uploads are accessible
- [ ] Background workers process tasks
- [ ] Frontend loads and functions correctly
- [ ] Monitoring and alerting are operational
- [ ] Security controls are intact

## Responsibilities

| Role | Responsibility |
|------|---------------|
| DevOps Engineer | Infrastructure recovery |
| Database Admin | Data restoration |
| Security Team | Breach response |
| Engineering Lead | Technical coordination |
| Product Manager | Stakeholder communication |

## Appendices

### A. Environment Variables for Recovery

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ats_db
POSTGRES_USER=ats_user
POSTGRES_PASSWORD=<password>

# Backup
BACKUP_DIR=./backups
UPLOADS_DIR=./uploads

# Storage (for off-site backups)
STORAGE_PROVIDER=s3
STORAGE_S3_BUCKET=ats-backups
STORAGE_S3_REGION=us-east-1
```

### B. Quick Recovery Commands

```bash
# Full recovery from latest backup
docker-compose down
python scripts/backup.py restore backups/backup_latest.tar.gz
docker-compose up -d

# Verify recovery
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health/db
```

### C. Contact Information

| Contact | Role | Phone | Email |
|---------|------|-------|-------|
| DevOps Lead | Infrastructure | N/A | devops@example.com |
| DB Admin | Database | N/A | dba@example.com |
| Security Lead | Security | N/A | security@example.com |