FROM python:3.11-slim

# Install ffmpeg + tzdata + common codec libs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        tzdata \
        libx264-163 \
        libx265-199 \
        libvpx7 \
        libopus0 \
        libass9 \
        libfreetype6 \
        libvorbis0a \
        libwebp7 \
        libtheora0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m worker
USER worker

WORKDIR /app

COPY --chown=worker:worker worker.py .
COPY --chown=worker:worker defaults/settings.json /defaults/settings.json

RUN mkdir -p /timelapse /config

CMD ["python", "worker.py"]
