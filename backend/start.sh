#!/usr/bin/env bash
# exit on error
set -o errexit

# Add the current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/opt/render/project/src/backend

# Start Gunicorn
exec gunicorn wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-file - 