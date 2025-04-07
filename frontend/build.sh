#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
npm install

# Build the application
npm run build

# Output build success
echo "Frontend build completed successfully!" 