#!/usr/bin/env bash
cd backend
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application 