#!/usr/bin/env bash
# PostgreSQL recovery script for AI-ATS
# Usage: ./restore.sh <backup_dir>
# Example: ./restore.sh /tmp/ai-ats-backups/20240115_020000

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup_dir>"
    echo "Example: $0 /tmp/ai-ats-backups/20240115_020000"
    exit 1
fi

BACKUP_PATH="$1"

if [ ! -d "${BACKUP_PATH}" ]; then
    echo "Error: Backup directory not found: ${BACKUP_PATH}"
    exit 1
fi

# Load environment
POSTGRES_USER="${POSTGRES_USER:-ats_user}"
POSTGRES_DB="${POSTGRES_DB:-ats_db}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "[$(date)] Starting recovery from ${BACKUP_PATH}"

# 1. Verify checksums
if [ -f "${BACKUP_PATH}/checksums.sha256" ]; then
    echo "Verifying checksums..."
    (cd "${BACKUP_PATH}" && sha256sum -c checksums.sha256)
fi

# 2. Restore PostgreSQL database
DB_DUMP="${BACKUP_PATH}/database.dump"
if [ -f "${DB_DUMP}" ]; then
    echo "Restoring PostgreSQL database..."
    PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_restore \
        -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" \
        -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -v --clean --if-exists "${DB_DUMP}"
else
    echo "Warning: database.dump not found, skipping DB restore"
fi

# 3. Restore uploads
UPLOADS_ARCHIVE="${BACKUP_PATH}/uploads.tar.gz"
if [ -f "${UPLOADS_ARCHIVE}" ]; then
    echo "Restoring uploads..."
    UPLOADS_DIR="${UPLOADS_DIR:-./uploads}"
    UPLOADS_PARENT="$(dirname "${UPLOADS_DIR}")"
    tar xzf "${UPLOADS_ARCHIVE}" -C "${UPLOADS_PARENT}"
fi

# 4. Restore config
CONFIG_ARCHIVE="${BACKUP_PATH}/config.tar.gz"
if [ -f "${CONFIG_ARCHIVE}" ]; then
    echo "Restoring configuration..."
    tar xzf "${CONFIG_ARCHIVE}" -C "$(dirname "$0")/.."
fi

echo "[$(date)] Recovery completed from ${BACKUP_PATH}"
