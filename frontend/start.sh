#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
npm install

# Install serve globally
npm install -g serve

# Serve the built application using serve
serve -s build -l $PORT 