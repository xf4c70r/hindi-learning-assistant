#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create static directory if it doesn't exist
mkdir -p staticfiles
mkdir -p static

# Collect static files
python manage.py collectstatic --no-input

# Output build success
echo "Backend build completed successfully!" 