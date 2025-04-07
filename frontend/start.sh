#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
npm install

# Install serve globally
npm install -g serve

# Ensure PORT is set
export PORT="${PORT:-3000}"

# Serve the built application using serve with config
serve -s build --config serve.json --listen $PORT 