#!/usr/bin/env bash
# Render build script

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python backend/manage.py collectstatic --no-input

# Run migrations
python backend/manage.py migrate
