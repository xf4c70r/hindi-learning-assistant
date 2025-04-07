#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Create static directories
mkdir -p static staticfiles

# Run Django migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input 