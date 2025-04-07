#!/usr/bin/env bash

# Ensure we're in the backend directory
cd backend

# Start Gunicorn
exec gunicorn wsgi:application --bind 0.0.0.0:$PORT 