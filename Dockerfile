# Use the official Odoo 18.0 image as the base for our custom image
FROM odoo:18.0

# Switch to root to install packages
USER root

# Update package list and install any system dependencies if needed
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for the AI agent addon with system conflict handling
RUN pip3 install --break-system-packages --no-deps openai==1.99.1 || \
    pip3 install --break-system-packages --force-reinstall --no-deps openai==1.99.1

# Install httpx and its essential dependencies
RUN pip3 install --break-system-packages --no-deps httpcore anyio sniffio h11 || true
RUN pip3 install --break-system-packages --no-deps httpx==0.25.2 || \
    pip3 install --break-system-packages --force-reinstall --no-deps httpx==0.25.2

# Verify the installation
RUN python3 -c "import openai; print(f'OpenAI version: {openai.__version__}')" || echo "OpenAI import failed"
RUN python3 -c "import httpx; print(f'httpx version: {httpx.__version__}')" || echo "httpx import failed"

# Switch back to odoo user
USER odoo

# Set the working directory for the copy command
WORKDIR /mnt/extra-addons

# Copy the contents of our local 'addons' folder into the image.
# This bakes our custom module directly into the new image.
COPY ./addons .