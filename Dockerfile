FROM python:3.11-slim

WORKDIR /app

COPY requirements-server.txt /app/requirements-server.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements-server.txt

COPY . /app

ENV PYTHONPATH="/app"
ENV PORT=7860

EXPOSE 7860

# Hugging Face Docker Spaces expect the app on 7860. Single worker avoids extra RAM on free tier.
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
