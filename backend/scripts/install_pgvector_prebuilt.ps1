#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Install pre-built pgvector binaries for local PostgreSQL on Windows.

.DESCRIPTION
    Downloads community-built pgvector binaries (andreiramani/pgvector_pgsql_windows)
    and copies them into the PostgreSQL installation directory.

    After installation, run migrations from the backend directory:
      alembic upgrade head
#>
param(
    [string]$PgRoot = "C:\Program Files\PostgreSQL\18",
    [string]$PgVectorVersion = "0.8.3_18.4",
    [string]$ZipName = "vector.v0.8.3-pg18.zip"
)

$ErrorActionPreference = "Stop"

$downloadUrl = "https://github.com/andreiramani/pgvector_pgsql_windows/releases/download/$PgVectorVersion/$ZipName"
$zipPath = Join-Path $env:TEMP $ZipName
$extractPath = Join-Path $env:TEMP "pgvector-pg18-install"

Write-Host "Stopping PostgreSQL service..."
Get-Service -Name "postgresql-x64-18" -ErrorAction SilentlyContinue | Stop-Service -Force

Write-Host "Downloading pgvector from $downloadUrl ..."
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath

if (Test-Path $extractPath) {
    Remove-Item -Recurse -Force $extractPath
}
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

Write-Host "Installing pgvector into $PgRoot ..."
Copy-Item "$extractPath\lib\vector.dll" "$PgRoot\lib\" -Force
Copy-Item "$extractPath\share\extension\*" "$PgRoot\share\extension\" -Force
New-Item -ItemType Directory -Force -Path "$PgRoot\include\server\extension\vector" | Out-Null
Copy-Item "$extractPath\include\server\extension\vector\*" "$PgRoot\include\server\extension\vector\" -Force

$vectorControl = Join-Path $PgRoot "share\extension\vector.control"
if (-not (Test-Path $vectorControl)) {
    throw "vector.control not found after install; check PGROOT path."
}

Write-Host "Starting PostgreSQL service..."
Get-Service -Name "postgresql-x64-18" -ErrorAction SilentlyContinue | Start-Service

Write-Host "pgvector installed successfully." -ForegroundColor Green
Write-Host "Run 'alembic upgrade head' from the backend directory to enable the extension in your database."
