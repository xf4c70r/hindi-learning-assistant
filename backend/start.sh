#!/bin/bash

# Apply database migrations
python manage.py migrate

# Start Gunicorn
gunicorn backend.wsgi:application --workers 4 --bind 0.0.0.0:$PORT 