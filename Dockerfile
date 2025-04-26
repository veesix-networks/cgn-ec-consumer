# Set python version
ARG BASE_CONTAINER=python:3.12.3-slim

# Set the base image 
FROM --platform=linux/amd64 $BASE_CONTAINER

# Adds metadata to image.
LABEL maintainer="cgn-ec@veesix-networks.co.uk"

# dont write pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# dont buffer to stdout/stderr
ENV PYTHONUNBUFFERED=1
# Prometheus multiprocess directory
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc

# Make a directory for app
WORKDIR /app

# Create prometheus multiprocess directory
RUN mkdir -p /tmp/prometheus_multiproc && chmod 777 /tmp/prometheus_multiproc

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
# RUN pip install --no-cache-dir --user -r /req.txt

# Copy source code
COPY . .

# Expose prometheus metrics port
EXPOSE 4499

# Run the application
CMD ["python", "-m", "app_multi_process"]