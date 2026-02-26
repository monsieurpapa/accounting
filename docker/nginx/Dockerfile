# /home/ubuntu/accounting_project/docker/nginx/Dockerfile

# Use the official Nginx image
FROM nginx:1.25-alpine

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy the custom Nginx configuration
COPY ./docker/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Command to run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]

