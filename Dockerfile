# FROM python:3.9-slim-buster
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY main.py .
# EXPOSE 5000
# CMD ["python", "main.py"]

# Use a Python base image. 
FROM --platform=linux/amd64 python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container.
WORKDIR /app

# Copy  application files into the container.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

# Expose the port your application will listen on 
EXPOSE 8000

# Set the command to run your application.
CMD ["python", "main.py"]
