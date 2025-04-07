#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
npm install

# Build the application
npm run build

# Create serve.json in the build directory
cat > build/serve.json << EOL
{
  "rewrites": [
    { "source": "/healthz", "destination": "/index.html" },
    { "source": "/**", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/healthz",
      "headers": [
        { "key": "Content-Type", "value": "text/plain" }
      ]
    }
  ]
}
EOL

# Output build success
echo "Frontend build completed successfully!" 