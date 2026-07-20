#!/usr/bin/env bash
# PostgreSQL backup script for AI-ATS
# Usage: ./backup.sh [backup_dir]
# Cron: 0 2 * * * /opt/ai-ats/scripts/backup.sh /backups

set -euo pipefail

BACKUP_DIR="${1:-/tmp/ai-ats-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"
mkdir -p "${BACKUP_PATH}"

# Load environment
POSTGRES_USER="${POSTGRES_USER:-ats_user}"
POSTGRES_DB="${POSTGRES_DB:-ats_db}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "[$(date)] Starting backup to ${BACKUP_PATH}"

# 1. PostgreSQL dump (schema + data, custom format for parallel restore)
echo "Backing up PostgreSQL database..."
PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
    -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
    -F c -v -f "${BACKUP_PATH}/database.dump"

# 2. Uploads directory (if using local storage)
UPLOADS_DIR="${UPLOADS_DIR:-./uploads}"
if [ -d "${UPLOADS_DIR}" ]; then
    echo "Backing up uploads directory..."
    tar czf "${BACKUP_PATH}/uploads.tar.gz" -C "$(dirname "${UPLOADS_DIR}")" "$(basename "${UPLOADS_DIR}")"
fi

# 3. Configuration files
echo "Backing up configuration..."
tar czf "${BACKUP_PATH}/config.tar.gz" \
    -C "$(dirname "$0")/.." \
    .env docker-compose.yml backend/alembic.ini 2>/dev/null || true

# 4. Compute checksum
echo "Generating checksum..."
sha256sum "${BACKUP_PATH}"/* > "${BACKUP_PATH}/checksums.sha256"

# 5. Retention: keep last 30 days
echo "Cleaning old backups (keeping last 30 days)..."
find "${BACKUP_DIR}" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true

echo "[$(date)] Backup completed: ${BACKUP_PATH}"
