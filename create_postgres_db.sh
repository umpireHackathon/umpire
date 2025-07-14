#!/bin/bash

# -----------------------------------------------------------------------------
# SYNOPSIS:
#     Creates PostgreSQL database, tables, and grants privileges using SQL scripts and credentials from .env.
#
# DESCRIPTION:
#     Loads PGUSER, PGPASSWORD, PGHOST, PGPORT from .env file.
#     Executes create_db.sql to create the database and user.
#     Executes create_tables.sql to initialize schema.
#     Executes grant_privileges.sql to ensure the user has correct access.
#
# NOTES:
#     Author: Umpire Team
#     Date: 2025-07
# -----------------------------------------------------------------------------

set -e  # Exit immediately on error

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
ENV_FILE=".env"
SQL_CREATE_DB="data/create_db.sql"
SQL_CREATE_TABLES="data/create_tables.sql"
SQL_GRANT_PRIVILEGES="data/grant_privileges.sql"

# -----------------------------------------------------------------------------
# Check .env file exists
# -----------------------------------------------------------------------------
if [ ! -f "$ENV_FILE" ]; then
  echo ".env file not found. Please create one with PGUSER, PGPASSWORD, PGHOST, and PGPORT."
  exit 1
fi

# -----------------------------------------------------------------------------
# Load environment variables
# -----------------------------------------------------------------------------
export $(grep -v '^#' "$ENV_FILE" | xargs)

# -----------------------------------------------------------------------------
# Check required variables
# -----------------------------------------------------------------------------
required_vars=(PGUSER PGPASSWORD PGHOST PGPORT)
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Environment variable $var is not set in .env"
    exit 1
  fi
done

# -----------------------------------------------------------------------------
# Helper function to run SQL
# -----------------------------------------------------------------------------
run_sql() {
  local sql_file="$1"
  local db="$2"

  if [ ! -f "$sql_file" ]; then
    echo "SQL file not found: $sql_file"
    exit 1
  fi

  echo "Running $sql_file on database: $db"
  PGPASSWORD="$PGPASSWORD" psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -d "$db" -f "$sql_file"
  echo "Finished $sql_file"
}

# -----------------------------------------------------------------------------
# Execute scripts
# -----------------------------------------------------------------------------
run_sql "$SQL_CREATE_DB" "postgres"
run_sql "$SQL_CREATE_TABLES" "umpire_db"
run_sql "$SQL_GRANT_PRIVILEGES" "umpire_db"

# -----------------------------------------------------------------------------
# Cleanup and done
# -----------------------------------------------------------------------------
unset PGPASSWORD
echo "Database setup complete. Tables created and privileges granted."
