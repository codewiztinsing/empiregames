# Use official Node.js LTS image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install --production

# Copy source code
COPY . .
COPY .env .env

# Expose app port
EXPOSE 5000

# Run app
CMD ["npm", "start"]
