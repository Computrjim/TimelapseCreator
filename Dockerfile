FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# No external Python deps right now; everything is stdlib + ffmpeg
COPY worker.py .

# Create mount points (for clarity)
RUN mkdir -p /timelapse /config

# Default command
CMD ["python", "worker.py"]
