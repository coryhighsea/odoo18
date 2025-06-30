# Use the official Odoo 18.0 image as the base for our custom image
FROM odoo:18.0

# Set the working directory for the copy command
WORKDIR /mnt/extra-addons

# Copy the contents of our local 'addons' folder into the image.
# This bakes our custom module directly into the new image.
COPY ./addons .