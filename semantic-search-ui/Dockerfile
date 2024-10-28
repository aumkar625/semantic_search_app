# Dockerfile

# -----------------------------
# Stage 1: Build React Application
# -----------------------------
FROM node:16-alpine AS build

# Set environment variables
ENV NODE_ENV=production
ENV REACT_APP_API_URL=/api

# Set working directory
WORKDIR /app

# Create package.json using a heredoc to handle multi-line JSON
RUN cat <<EOF > package.json
{
  "name": "semantic-search-ui",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "axios": "^1.4.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
EOF

# Install dependencies
RUN npm install

# Copy all source files to the working directory
COPY . .

# Build the React app
RUN npm run build

# -----------------------------
# Stage 2: Serve with Nginx
# -----------------------------
FROM nginx:alpine

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d

# Copy the build output from Stage 1
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
