# Disaster Recovery Plan

## Overview

This document describes the backup strategy, recovery procedures, and disaster
recovery (DR) plan for the AI-ATS platform.

## Backup Strategy

### Scope
1. **PostgreSQL database** — full database dump (schema + data) in custom format
2. **Uploaded files** — resumes and attachments (local storage only)
3. **Configuration** — `.env`, `docker-compose.yml`, `alembic.ini`

### Schedule
- **Frequency**: Daily at 02:00 UTC
- **Retention**: 30 days of backups
- **Location**: `/backups` on the backup host (separate from application server)

### Scripts
- Backup: `backend/scripts/backup.sh`
- Restore: `backend/scripts/restore.sh`

### Cron Setup
```bash
# /etc/cron.d/ai-ats-backup
0 2 * * * /opt/ai-ats/backend/scripts/backup.sh /backups >> /var/log/ai-ats-backup.log 2>&1
```

## Recovery Procedures

### Database Recovery (Point-in-Time)

1. **Identify the backup** to restore from:
   ```bash
   ls -la /backups/
   ```

2. **Stop the application** to prevent writes during recovery:
   ```bash
   docker-compose stop backend worker beat
   ```

3. **Run the restore script**:
   ```bash
   ./backend/scripts/restore.sh /backups/20240115_020000
   ```

4. **Run pending migrations** (if the backup is from an older schema version):
   ```bash
   cd backend && alembic upgrade head
   ```

5. **Restart the application**:
   ```bash
   docker-compose up -d
   ```

### File Recovery

Uploaded files are restored as part of the restore script. If using S3/MinIO
storage, enable S3 versioning for point-in-time file recovery.

### Configuration Recovery

Configuration is included in the backup archive. Restore to the application
directory and restart services.

## Disaster Recovery

### RTO (Recovery Time Objective)
- **Target**: 4 hours
- **Procedure**: Provision new infrastructure from Terraform/K8s manifests,
  restore latest backup, update DNS.

### RPO (Recovery Point Objective)
- **Target**: 24 hours (daily backups)
- **For lower RPO**: Increase backup frequency or enable PostgreSQL streaming replication.

### Failover Procedure

1. **Detect failure**: Monitoring alerts (Prometheus/Grafana) or health check failures.
2. **Provision replacement**: Deploy to new infrastructure using K8s manifests.
3. **Restore data**: Run `restore.sh` with the latest backup.
4. **Update DNS**: Point traffic to the new infrastructure.
5. **Verify**: Run health checks and smoke tests.

## Testing

- Backup restore should be tested monthly in a staging environment.
- Full DR drill should be conducted quarterly.
- Document test results and update this plan as needed.
