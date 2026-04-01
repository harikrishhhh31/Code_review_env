# =============================================================================
# Dockerfile for CodeReviewEnv
# =============================================================================
#
# This Dockerfile creates a container that runs the CodeReviewEnv server.
# It's used for:
# 1. Local testing with docker build && docker run
# 2. Deployment to Hugging Face Spaces
# 3. CI/CD validation
#
# LEARNING: Why Docker?
# Docker ensures the environment runs the same everywhere:
# - Your laptop
# - Judge's machine
# - Production servers
#
# It packages:
# - Python runtime
# - All dependencies
# - Your environment code
# - Start-up configuration
#
# =============================================================================

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
# This stage installs dependencies

# Start from Python 3.11 image
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY requirements.txt ./

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime
# -----------------------------------------------------------------------------
# This stage creates the final container

# Start from a clean Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency files first (for caching)
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Set up Python path
ENV PYTHONPATH="/app"

# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------
# Docker will periodically check if the server is healthy

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# -----------------------------------------------------------------------------
# Run the server
# -----------------------------------------------------------------------------

# Expose port (matches openenv.yaml config)
EXPOSE 8000

# Run uvicorn (ASGI server)
# --host 0.0.0.0: Listen on all interfaces
# --port 8000: Port to listen on
# uvicorn is an ASGI server that handles HTTP/WS connections
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
