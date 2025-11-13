#!/bin/sh
set -e

host="$1"
shift
cmd="$@"

echo "Waiting for postgres at $host..."
until pg_isready -h "$host" -p 5432 -U "$DB_USER" > /dev/null 2>&1; do
  echo "⏳ Waiting for PostgreSQL at $host:5432..."
  sleep 2
done

echo "✅ PostgreSQL is ready — starting app..."
exec $cmd
