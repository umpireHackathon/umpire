<#
.SYNOPSIS
    Creates PostgreSQL database and tables using SQL scripts and credentials from .env.

.DESCRIPTION
    Loads PGUSER, PGPASSWORD, PGHOST, PGPORT from .env file.
    Executes create_db.sql to create the database and user.
    Then executes create_tables.sql to initialize schema.

.NOTES
    Author: Your Name
    Date: 2025-07-12
#>

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
$envFile         = ".env"
$sqlCreateDb     = "data/create_db.sql"
$sqlCreateTables = "data/create_tables.sql"

# ---------------------------------------------------------------------------
# Verify .env exists
# ---------------------------------------------------------------------------
if (-not (Test-Path $envFile)) {
    Write-Error ".env file not found. Please create one with PGUSER, PGPASSWORD, PGHOST, and PGPORT."
    exit 1
}

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
        $key   = $matches[1].Trim()
        $value = $matches[2].Trim()
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# ---------------------------------------------------------------------------
# Ensure required variables are present
# ---------------------------------------------------------------------------
$requiredVars = @("PGUSER", "PGPASSWORD", "PGHOST", "PGPORT")
foreach ($var in $requiredVars) {
    if (-not [System.Environment]::GetEnvironmentVariable($var, "Process")) {
        Write-Error "$var is missing in .env file."
        exit 1
    }
}

# ---------------------------------------------------------------------------
# Helper: run a SQL script against a database
# ---------------------------------------------------------------------------
function Run-SqlScript {
    param (
        [string]$sqlFile,
        [string]$databaseName
    )

    if (-not (Test-Path $sqlFile)) {
        Write-Error "$sqlFile not found."
        exit 1
    }

    Write-Host "Running script: $sqlFile ..."
    try {
        psql -U $env:PGUSER -h $env:PGHOST -p $env:PGPORT -d $databaseName -f $sqlFile
        Write-Host "Successfully executed: $sqlFile"
    }
    catch {
        Write-Error "Error executing `${sqlFile}`: $_"
        exit 1
    }
}

# ---------------------------------------------------------------------------
# Execute scripts
# ---------------------------------------------------------------------------
Run-SqlScript -sqlFile $sqlCreateDb     -databaseName "postgres"
Run-SqlScript -sqlFile $sqlCreateTables -databaseName "umpire_db"

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
Write-Host "Database and tables created successfully."
