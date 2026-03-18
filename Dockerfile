FROM python:3.11-slim

# Install ffmpeg + tzdata
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m worker
USER worker

WORKDIR /app

COPY --chown=worker:worker worker.py .
COPY --chown=worker:worker defaults/settings.json /defaults/settings.json

CMD ["python", "worker.py"]
