#!/usr/bin/env bash

# Add the current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/opt/render/project/src/backend

# Apply database migrations
python manage.py migrate

# Start Gunicorn
cd /opt/render/project/src/backend
exec gunicorn wsgi:application --bind 0.0.0.0:$PORT 