#!/usr/bin/env bash
# build.sh

set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Change to backend directory
cd backend

echo "Current environment variables:"
echo "DATABASE_URL is set: $([ -n "$DATABASE_URL" ] && echo "YES" || echo "NO")"
echo "RENDER environment: ${RENDER:-Not set}"

# Test database connection before collecting static files
echo "Testing database connection..."
python manage.py test_db

# Run Django system checks
echo "Running Django system checks..."
python manage.py check --database default

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running migrations..."
python manage.py migrate --no-input

echo "Build completed successfully!"