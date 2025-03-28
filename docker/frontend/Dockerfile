# Use Node.js 20 slim image
FROM node:20-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY frontend/ .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "run", "dev"] 