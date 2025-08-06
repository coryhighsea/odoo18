# Use the official Odoo 18.0 image as the base for our custom image
FROM odoo:18.0

# Switch to root to install packages
USER root

# Update package list and install any system dependencies if needed
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY ./addons/ai_agent_odoo/requirements.txt /tmp/requirements.txt

# Install Python packages for the AI agent addon
RUN pip3 install --break-system-packages -r /tmp/requirements.txt

# Verify the installation
RUN python3 -c "import openai; print(f'OpenAI version: {openai.__version__}')" || echo "OpenAI import failed"
RUN python3 -c "import httpx; print(f'httpx version: {httpx.__version__}')" || echo "httpx import failed"

# Clean up
RUN rm /tmp/requirements.txt

# Switch back to odoo user
USER odoo

# Set the working directory for the copy command
WORKDIR /mnt/extra-addons

# Copy the contents of our local 'addons' folder into the image.
# This bakes our custom module directly into the new image.
COPY ./addons .