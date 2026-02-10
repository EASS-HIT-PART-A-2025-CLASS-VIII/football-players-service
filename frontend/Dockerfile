# Build stage
FROM node:22-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Accept API URL as build arg (Vite embeds env vars at build time)
ARG VITE_API_LOCATION=http://localhost:8000
ENV VITE_API_LOCATION=$VITE_API_LOCATION

# Build the app
RUN npm run build

# Runtime stage
FROM node:22-alpine

WORKDIR /app

# Install serve to run the static app
RUN npm install -g serve

# Copy built app from build stage
COPY --from=build /app/dist ./dist

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start the app
CMD ["serve", "-s", "dist", "-l", "3000"]
