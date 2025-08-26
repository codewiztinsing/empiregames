# Use official Node.js LTS image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first
COPY package*.json ./

# Copy Prisma schema files before npm install
COPY prisma ./prisma

# Install dependencies (this will now work since prisma schema is available)
RUN npm install --legacy-peer-deps

# Copy the rest of the source code
COPY . .

# Install Prisma CLI globally
RUN npm install -g prisma

# reset database
RUN npx prisma migrate reset --force

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose app port
EXPOSE 5000

# Run the startup script
CMD ["/app/start.sh"]
