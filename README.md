# Timelapse Worker for 3D Printer Frames
This container scans a /timelapse directory for completed 3D printer jobs, detects folders containing a metadata.json with "status": "completed", and automatically stitches all layer_####.jpg images into a timelapse video.

The worker is designed for Unraid, but runs on any 64‑bit Linux system.

# Features
Automatically detects completed print jobs

Stitches layer_####.jpg frames into an MP4 timelapse

Deterministic filename format:
<file_name>_<YYYYMMDD-HHMMSSAM/PM>_timelapse.mp4

Timezone conversion with 12‑hour timestamps

Optional deletion of frame images after stitching

Auto‑generated settings.json on first run

Writes a timelapse.json file to mark jobs as processed

Zero external dependencies beyond ffmpeg

# Folder Structure
    /timelapse/
        <printer_id>/
            <job_id>/
                metadata.json
                layer_0001.jpg
                layer_0002.jpg
                ...



# Configuration
A default settings.json is copied into /config on first run:

```json
{
  "delete_frames_after_stitch": false,
  "default_fps": 30,
  "scan_interval_seconds": 10,
  "output_format": "mp4",
  "timezone": "America/Chicago"
}
```


You may edit this file at any time.

# Output
Each completed job produces:

A timelapse video

A timelapse.json file indicating the job has been processed

Example output filename:

debug_job_1773688647_20260316-021730PM_timelapse.mp4

# Docker Usage (Unraid or CLI)
Mount two volumes:

/timelapse → your printer timelapse folder

/config → persistent settings

Example:

docker run -d \
-v /mnt/user/timelapse:/timelapse \
-v /mnt/user/appdata/timelapse-worker:/config \
ghcr.io/computrjim/timelapse-worker:latest

# GitHub Container Registry
Images are published automatically to:

ghcr.io/computrjim/timelapse-worker:latest

# License
MIT
