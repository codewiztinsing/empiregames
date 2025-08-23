# Use official Node.js LTS image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .
COPY .env .env

# Install Prisma CLI globally
RUN npm install -g prisma

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose app port
EXPOSE 5000

# Run the startup script
CMD ["/app/start.sh"]
