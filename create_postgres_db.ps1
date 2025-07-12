<#
.SYNOPSIS
    Creates PostgreSQL database and user by running SQL from create_db.sql using credentials in .env.

.DESCRIPTION
    Loads PGUSER, PGPASSWORD, PGHOST, PGPORT from .env file and executes create_db.sql using psql.
    Safely handles missing variables and cleans up password after execution.

.NOTES
    Author: Your Name
    Date: 2025-07-12
#>

# Set the path to the .env file and SQL file
$envFile = ".env"
$sqlFile = "data/create_db.sql"

# Ensure .env exists
if (-not (Test-Path $envFile)) {
    Write-Error ".env file not found. Please create one with PGUSER, PGPASSWORD, PGHOST, and PGPORT."
    exit 1
}

# Load environment variables from .env
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Ensure required variables are loaded
$requiredVars = @("PGUSER", "PGPASSWORD", "PGHOST", "PGPORT")
foreach ($var in $requiredVars) {
    if (-not [System.Environment]::GetEnvironmentVariable($var, "Process")) {
        Write-Error "$var is missing in .env file."
        exit 1
    }
}

# Check if SQL file exists
if (-not (Test-Path $sqlFile)) {
    Write-Error "$sqlFile not found. Please ensure the SQL file is present in the current directory."
    exit 1
}

# Run the SQL file using psql
try {
    psql -U $env:PGUSER -h $env:PGHOST -p $env:PGPORT -f $sqlFile
    Write-Host "✅ Database creation script executed successfully."
} catch {
    Write-Error "❌ Error running SQL script: $_"
} finally {
    # Remove sensitive environment variable
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}
