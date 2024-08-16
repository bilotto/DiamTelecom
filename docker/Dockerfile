FROM python:3.10-alpine3.19

# Install pyyaml using pip
RUN pip install pyyaml requests

# Copy the project directories to the container
COPY diameter/src /app/diameter/src
COPY DiamTelecom/src /app/DiamTelecom/src
COPY provisioning_api/src /app/provisioning_api/src
COPY carrier/src /app/carrier/src

# Run dos2unix on the copied files
RUN find /app -type f -exec dos2unix {} \;

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=:/app/diameter/src:/app/DiamTelecom/src:/app/provisioning_api/src:/app/carrier/src

# Set the working directory to /app/carrier/src
WORKDIR /app/carrier/src