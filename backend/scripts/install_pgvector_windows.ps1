#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Build and install the pgvector extension for local PostgreSQL on Windows.

.DESCRIPTION
    pgvector is not bundled with PostgreSQL on Windows.

    Preferred: run install_pgvector_prebuilt.ps1 (downloads pre-built binaries).
    This script builds from source when you have Visual Studio C++ Build Tools.

    After installation, run migrations from the backend directory:
      alembic upgrade head
#>
param(
    [string]$PgRoot = "C:\Program Files\PostgreSQL\18",
    [string]$PgVectorVersion = "v0.8.5"
)

$ErrorActionPreference = "Stop"

function Find-Nmake {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\*\bin\Hostx64\x64\nmake.exe",
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\*\bin\Hostx64\x64\nmake.exe",
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\*\bin\Hostx64\x64\nmake.exe",
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\*\bin\Hostx64\x64\nmake.exe"
    )
    foreach ($pattern in $candidates) {
        $match = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($match) { return $match.FullName }
    }
    return $null
}

$nmake = Find-Nmake
if (-not $nmake) {
    Write-Host "nmake not found. Install Visual Studio 2022 Build Tools with C++ workload:" -ForegroundColor Yellow
    Write-Host "  winget install -e --id Microsoft.VisualStudio.2022.BuildTools" -ForegroundColor Cyan
    Write-Host "Then open 'x64 Native Tools Command Prompt for VS 2022' and run:" -ForegroundColor Yellow
    Write-Host @"

  set `"PGROOT=$PgRoot`"
  cd %TEMP%
  git clone --branch $PgVectorVersion https://github.com/pgvector/pgvector.git
  cd pgvector
  nmake /F Makefile.win
  nmake /F Makefile.win install

"@ -ForegroundColor White
    exit 1
}

$buildDir = Join-Path $env:TEMP "pgvector-build"
if (Test-Path $buildDir) {
    Remove-Item -Recurse -Force $buildDir
}

Write-Host "Cloning pgvector $PgVectorVersion..."
git clone --branch $PgVectorVersion --depth 1 https://github.com/pgvector/pgvector.git $buildDir

Push-Location $buildDir
$env:PGROOT = $PgRoot

Write-Host "Building pgvector..."
& $nmake /F Makefile.win
if ($LASTEXITCODE -ne 0) { throw "pgvector build failed" }

Write-Host "Installing pgvector into $PgRoot..."
& $nmake /F Makefile.win install
if ($LASTEXITCODE -ne 0) { throw "pgvector install failed" }

Pop-Location
Write-Host "pgvector installed successfully." -ForegroundColor Green

$vectorControl = Join-Path $PgRoot "share\extension\vector.control"
if (-not (Test-Path $vectorControl)) {
    throw "vector.control not found after install; check PGROOT path."
}

Write-Host "Run 'alembic upgrade head' from the backend directory to enable the extension in your database."
