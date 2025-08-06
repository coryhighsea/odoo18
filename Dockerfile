# Use the official Odoo 18.0 image as the base for our custom image
FROM odoo:18.0

# Switch to root to install packages
USER root

# Install OpenAI package for the AI agent addon
RUN pip3 install --break-system-packages --force-reinstall --no-deps openai>=1.0.0

# Switch back to odoo user
USER odoo

# Set the working directory for the copy command
WORKDIR /mnt/extra-addons

# Copy the contents of our local 'addons' folder into the image.
# This bakes our custom module directly into the new image.
COPY ./addons .