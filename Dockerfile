# syntax=docker/dockerfile:1
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3.11-dev python3-pip git && \
    rm -rf /var/lib/apt/lists/*

# Set python3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Use venv for all future commands
ENV PATH="/opt/venv/bin:$PATH"

# Expose API port
EXPOSE 8000

# Entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
