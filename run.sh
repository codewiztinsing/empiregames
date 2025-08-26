#!/bin/bash

# Navigate to the bingo directory
cd bingo

# Install dependencies
npm install

# Build the React application
npm run build

# Navigate to the app directory
cd ../app

# make sure templates/build directory exists
mkdir -p templates/build



# Remove all files from /templates/build directory
rm -rf templates/build/*

# Copy the new build files to /templates/build
cp -r ../bingo/build/* templates/build/

echo "Build completed"

# run pm2 restart all
pm2 restart all
