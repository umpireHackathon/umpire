#!/bin/bash

# ------------------------------------------------------------------------------
# DESCRIPTION:
#   Creates PostgreSQL database and user by running SQL from create_db.sql 
#   using credentials defined in a .env file.
# AUTHOR:
#   Your Name
# DATE:
#   2025-07-12
# ------------------------------------------------------------------------------

# Define file paths
ENV_FILE=".env"
CREATE_DB_SQL="data/create_db.sql"
PRIVILEGES_SQL="data/create_user_privileges.sql"

# Exit immediately on error
set -e

# Check if .env file exists
if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ .env file not found. Please create one with PGUSER, PGPASSWORD, PGHOST, and PGPORT."
  exit 1
fi

# Load environment variables from .env
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Check required variables
for var in PGUSER PGPASSWORD PGHOST PGPORT; do
  if [[ -z "${!var}" ]]; then
    echo "❌ Missing $var in .env file."
    exit 1
  fi
done

# Check if SQL files exist
if [[ ! -f "$CREATE_DB_SQL" ]]; then
  echo "❌ $CREATE_DB_SQL not found."
  exit 1
fi

if [[ ! -f "$PRIVILEGES_SQL" ]]; then
  echo "❌ $PRIVILEGES_SQL not found."
  exit 1
fi

# Step 1: Create database (will fail silently if it already exists)
echo "📦 Creating database (ignore error if it already exists)..."
psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -f "$CREATE_DB_SQL" || echo "⚠️ Database may already exist."

# Step 2: Create user and grant privileges
echo "🔐 Creating user and assigning privileges..."
psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -d umpire_db -f "$PRIVILEGES_SQL"

# Done
echo "✅ PostgreSQL database and user setup complete."
