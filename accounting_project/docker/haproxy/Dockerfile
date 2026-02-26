# /home/ubuntu/accounting_project/docker/haproxy/Dockerfile

# Use the official HAProxy image
FROM haproxy:2.8-alpine

# Copy the custom HAProxy configuration file
# The configuration file needs to be created separately
COPY ./docker/haproxy/haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

# Expose the port HAProxy will listen on (e.g., 80 or a custom port if Nginx handles 80)
# Assuming HAProxy listens internally and Nginx forwards to it.
# If HAProxy is the main entry point, expose 80/443.
# For this setup (Nginx -> HAProxy -> Django), HAProxy doesn't need external exposure directly.

# Command to run HAProxy
CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]

