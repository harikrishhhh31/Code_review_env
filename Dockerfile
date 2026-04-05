FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements-server.txt /app/requirements-server.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements-server.txt

COPY . /app

ENV PYTHONPATH="/app"

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
