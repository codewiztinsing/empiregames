# Use official Node.js LTS image for building
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files first (better caching)
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm install --legacy-peer-deps


# Copy source code
COPY . .

# Build the React app for production
RUN npm run build

# Production stage - use nginx to serve static files
FROM nginx:alpine

# Copy built React app from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration if needed (optional)
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

