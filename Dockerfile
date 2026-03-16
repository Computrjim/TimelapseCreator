FROM python:3.11-slim

# Install ffmpeg + tzdata
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy worker
COPY worker.py .

# Copy default settings
COPY defaults/settings.json /defaults/settings.json

# Create mount points
RUN mkdir -p /timelapse /config

CMD ["python", "worker.py"]
