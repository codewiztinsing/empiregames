#!/bin/bash

# Build the project
npm run build


# Copy the build files to the server
sudo mkdir -p /var/www/bingo.bilen.com
sudo cp -r build/* /var/www/bingo.bilen.com/
