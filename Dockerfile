FROM python:3.11-slim

# Install optimized ffmpeg build + tzdata
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        tzdata \
        libx264-dev \
        libx265-dev \
        libvpx-dev \
        libfdk-aac-dev \
        libopus-dev \
        libass-dev \
        libfreetype6-dev \
        libvorbis-dev \
        libwebp-dev \
        libtheora-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m worker
USER worker

WORKDIR /app

# Copy worker
COPY --chown=worker:worker worker.py .

# Copy default settings
COPY --chown=worker:worker defaults/settings.json /defaults/settings.json

# Create mount points
RUN mkdir -p /timelapse /config

CMD ["python", "worker.py"]
