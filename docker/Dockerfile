FROM python:3.10-alpine3.19

# Install git and other necessary dependencies
RUN apk add --no-cache git dos2unix

# Clone the required repositories
RUN git clone -b messages https://github.com/bilotto/diameter.git /app/diameter \
    && git clone https://github.com/bilotto/DiamTelecom.git /app/DiamTelecom

# Install Python dependencies
RUN pip install pyyaml requests

# Run dos2unix on the copied files
RUN find /app -type f -exec dos2unix {} \;

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app/diameter/src:/app/DiamTelecom/src

# Set the working directory
WORKDIR /app

# Default command
CMD ["/bin/sh"]
