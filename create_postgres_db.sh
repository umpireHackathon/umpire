#!/bin/bash

# ============================================================================
# Script to create PostgreSQL database and tables using .env credentials
# ============================================================================

set -e

ENV_FILE=".env"
SQL_CREATE_DB="data/create_db.sql"
SQL_CREATE_TABLES="data/create_tables.sql"

# --- Load .env variables ---
if [[ ! -f "$ENV_FILE" ]]; then
  echo ".env file not found. Please create one with PGUSER, PGPASSWORD, PGHOST, and PGPORT."
  exit 1
fi

# Export each key=value in .env
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Validate required environment variables
REQUIRED_VARS=("PGUSER" "PGPASSWORD" "PGHOST" "PGPORT")
for VAR in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!VAR}" ]]; then
    echo "$VAR is missing in .env file."
    exit 1
  fi
done

# --- Function to run SQL file ---
run_sql_file() {
  local sql_file=$1
  local db_name=$2

  if [[ ! -f "$sql_file" ]]; then
    echo "SQL file not found: $sql_file"
    exit 1
  fi

  echo "Running script: $sql_file on database: $db_name ..."
  PGPASSWORD=$PGPASSWORD psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -d "$db_name" -f "$sql_file"
  echo "Successfully executed: $sql_file"
}

# --- Run SQL scripts ---
run_sql_file "$SQL_CREATE_DB" "postgres"
run_sql_file "$SQL_CREATE_TABLES" "umpire_db"

echo "All scripts executed successfully."