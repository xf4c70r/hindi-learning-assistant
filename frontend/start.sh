#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
npm install

# Install serve globally
npm install -g serve

# Ensure PORT is set
export PORT="${PORT:-3000}"

# Copy serve.json to build directory
cp serve.json build/

# Serve the built application using serve with config
cd build && serve -s . --listen $PORT 