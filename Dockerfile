# Odoo 19 Dockerfile
FROM odoo:19

# Set working directory
WORKDIR /var/lib/odoo

# Install additional system dependencies if needed
USER root

# Install any additional Python packages if required
# RUN pip3 install --no-cache-dir <package-name>

# Switch back to odoo user
USER odoo

# Copy custom addons (will be mounted as volume in docker-compose)
# The addons will be mounted from the host

