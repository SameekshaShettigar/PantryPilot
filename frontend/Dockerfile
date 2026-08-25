# Stage 1: Build React SPA bundle using Node.js
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests
COPY package.json ./

# Install npm dependencies
RUN npm install

# Copy frontend source code
COPY . ./

# Build production bundle (/app/dist)
RUN npm run build

# Stage 2: Serve static production assets with Nginx
FROM nginx:alpine

# Copy built dist files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
