# Nginx Dockerfile
FROM nginx:latest

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d
