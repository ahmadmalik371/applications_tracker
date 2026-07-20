"""Backup and recovery script for PostgreSQL, files, and configuration.

Usage:
    python scripts/backup.py create          # Create a full backup
    python scripts/backup.py restore <file>   # Restore from a backup
    python scripts/backup.py list             # List available backups
    python scripts/backup.py schedule         # Schedule periodic backups
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", "./backups"))
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

DB_NAME = os.environ.get("POSTGRES_DB", "ats_db")
DB_USER = os.environ.get("POSTGRES_USER", "ats_user")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "ats_password")
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")

UPLOADS_DIR = Path(os.environ.get("UPLOADS_DIR", "./uploads"))
CONFIG_FILES = [
    Path(".env"),
    Path("docker-compose.yml"),
    Path("docker-compose.prod.yml"),
    Path("k8s/manifests.yaml"),
]


def _timestamp() -> str:
    return datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def _backup_path(name: str) -> Path:
    return BACKUP_DIR / name


def create_backup() -> str:
    """Create a full backup: database dump + files + config."""
    timestamp = _timestamp()
    backup_name = f"backup_{timestamp}"
    backup_path = _backup_path(backup_name)
    backup_path.mkdir(parents=True, exist_ok=True)

    # 1. Database dump
    logger.info("Backing up database...")
    db_dump_file = backup_path / "database.sql"
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    result = subprocess.run(
        [
            "pg_dump",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-d", DB_NAME,
            "--format=custom",
            "--file", str(db_dump_file),
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("Database backup failed: %s", result.stderr)
        shutil.rmtree(backup_path)
        raise RuntimeError(f"Database backup failed: {result.stderr}")

    # 2. Uploaded files
    if UPLOADS_DIR.exists():
        logger.info("Backing up uploaded files...")
        files_backup = backup_path / "uploads"
        shutil.copytree(str(UPLOADS_DIR), str(files_backup))

    # 3. Configuration files
    logger.info("Backing up configuration files...")
    config_backup = backup_path / "config"
    config_backup.mkdir(exist_ok=True)
    for config_file in CONFIG_FILES:
        if config_file.exists():
            shutil.copy2(str(config_file), str(config_backup / config_file.name))

    # 4. Backup metadata
    metadata = {
        "name": backup_name,
        "timestamp": timestamp,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "size_bytes": sum(
            f.stat().st_size for f in backup_path.rglob("*") if f.is_file()
        ),
        "components": {
            "database": db_dump_file.exists(),
            "uploads": (backup_path / "uploads").exists(),
            "config": (backup_path / "config").exists(),
        },
    }
    with open(backup_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Create compressed archive
    archive_name = f"{backup_name}.tar.gz"
    archive_path = _backup_path(archive_name)
    result = subprocess.run(
        ["tar", "-czf", str(archive_path), "-C", str(BACKUP_DIR), backup_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("Archive creation failed: %s", result.stderr)
    else:
        shutil.rmtree(backup_path)  # Remove uncompressed directory

    logger.info("Backup created: %s", archive_path)
    return str(archive_path)


def restore_backup(backup_file: str) -> None:
    """Restore from a backup archive."""
    backup_path = Path(backup_file)
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    logger.info("Restoring from backup: %s", backup_file)

    # Extract archive
    extract_dir = BACKUP_DIR / "restore_temp"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True)

    result = subprocess.run(
        ["tar", "-xzf", str(backup_path), "-C", str(extract_dir)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        shutil.rmtree(extract_dir)
        raise RuntimeError(f"Extraction failed: {result.stderr}")

    # Find the backup directory
    backup_dirs = list(extract_dir.iterdir())
    if not backup_dirs:
        shutil.rmtree(extract_dir)
        raise RuntimeError("No backup directory found in archive")
    backup_content = backup_dirs[0]

    # Restore database
    db_dump = backup_content / "database.sql"
    if db_dump.exists():
        logger.info("Restoring database...")
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD
        result = subprocess.run(
            [
                "pg_restore",
                "-h", DB_HOST,
                "-p", DB_PORT,
                "-U", DB_USER,
                "-d", DB_NAME,
                "--clean",
                "--if-exists",
                str(db_dump),
            ],
            env=env,
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            logger.warning("Database restore had warnings: %s", result.stderr)
        else:
            logger.info("Database restored successfully")

    # Restore uploaded files
    uploads_backup = backup_content / "uploads"
    if uploads_backup.exists():
        logger.info("Restoring uploaded files...")
        if UPLOADS_DIR.exists():
            shutil.rmtree(UPLOADS_DIR)
        shutil.copytree(str(uploads_backup), str(UPLOADS_DIR))

    # Restore config files
    config_backup = backup_content / "config"
    if config_backup.exists():
        logger.info("Restoring configuration files...")
        for config_file in config_backup.iterdir():
            dest = Path(config_file.name)
            shutil.copy2(str(config_file), str(dest))

    shutil.rmtree(extract_dir)
    logger.info("Restore completed successfully")


def list_backups() -> list[dict]:
    """List all available backups with metadata."""
    backups = []
    for f in sorted(BACKUP_DIR.glob("backup_*.tar.gz"), reverse=True):
        size_mb = f.stat().st_size / (1024 * 1024)
        backups.append({
            "name": f.name,
            "size_mb": round(size_mb, 2),
            "created": datetime.datetime.fromtimestamp(
                f.stat().st_mtime
            ).isoformat(),
        })
    return backups


def schedule_backups(interval_hours: int = 24) -> None:
    """Create a scheduled backup task (cron entry or Windows task)."""
    if sys.platform == "win32":
        # Create a scheduled task on Windows
        script_path = Path(__file__).resolve()
        task_name = "AIATS_Backup"
        cmd = [
            "schtasks", "/Create", "/F",
            "/TN", task_name,
            "/TR", f"python {script_path} create",
            "/SC", "DAILY",
            "/ST", "02:00",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Scheduled task '%s' created (daily at 02:00)", task_name)
        else:
            logger.warning("Failed to create scheduled task: %s", result.stderr)
    else:
        # Create a cron job on Unix
        script_path = Path(__file__).resolve()
        cron_line = f"0 2 * * * cd {script_path.parent.parent} && python {script_path} create\n"
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True,
        )
        existing = result.stdout if result.returncode == 0 else ""
        if cron_line not in existing:
            new_cron = existing + cron_line
            result = subprocess.run(
                ["crontab"],
                input=new_cron, capture_output=True, text=True,
            )
            if result.returncode == 0:
                logger.info("Cron job added (daily at 02:00)")
            else:
                logger.warning("Failed to add cron job: %s", result.stderr)


def main():
    parser = argparse.ArgumentParser(description="Backup and recovery tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("create", help="Create a full backup")
    restore_parser = subparsers.add_parser("restore", help="Restore from a backup")
    restore_parser.add_argument("file", help="Backup file to restore from")
    subparsers.add_parser("list", help="List available backups")
    schedule_parser = subparsers.add_parser("schedule", help="Schedule periodic backups")
    schedule_parser.add_argument(
        "--interval", type=int, default=24,
        help="Backup interval in hours (default: 24)",
    )

    args = parser.parse_args()

    if args.command == "create":
        create_backup()
    elif args.command == "restore":
        restore_backup(args.file)
    elif args.command == "list":
        backups = list_backups()
        if backups:
            print(f"{'Name':<50} {'Size (MB)':<15} {'Created':<30}")
            print("-" * 95)
            for b in backups:
                print(f"{b['name']:<50} {b['size_mb']:<15} {b['created']:<30}")
        else:
            print("No backups found.")
    elif args.command == "schedule":
        schedule_backups(args.interval)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()