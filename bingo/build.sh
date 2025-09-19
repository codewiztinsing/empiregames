#!/bin/bash

# Exit on any error
set -e

echo "Building React app..."

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build the React app
echo "Running npm build..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "Build failed - build directory not found"
    exit 1
fi

echo "Build successful!"

# Copy files to production directory
echo "Copying files to /var/www/aker.bingo.com..."

# Create target directory if it doesn't exist
sudo mkdir -p /var/www/aker.bingo.com

# Copy build files to production directory
sudo cp -r build/* /var/www/aker.bingo.com/

# Set proper permissions
sudo chown -R www-data:www-data /var/www/aker.bingo.com
sudo chmod -R 755 /var/www/aker.bingo.com

echo "Files successfully copied to /var/www/aker.bingo.com"
echo "Deployment complete!"
