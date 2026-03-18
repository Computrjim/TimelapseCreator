# Timelapse Worker for 3D Printer Frames
This container scans a /timelapse directory for completed 3D printer jobs, detects folders containing a metadata.json with "status": "completed", and automatically stitches captured image sequences into one or more timelapse videos.

The worker is designed for Unraid, but runs on any 64‑bit Linux system.

# Features
Automatically detects completed print jobs

Supports multiple timelapse modes per job

Layer‑based

Interval‑based

Every‑N‑layers

Any future mode your engine emits

Uses each mode’s filename pattern (e.g., layer_%04d.jpg, interval_%09d.jpg)

Produces one output video per mode

Deterministic filename format:
<file_name>_<YYYYMMDD-HHMMSSAM/PM>_<mode>_timelapse.mp4

Timezone conversion with 12‑hour timestamps

Optional deletion of frame images after stitching

Auto‑generated settings.json on first run

Writes a timelapse.json file listing all generated outputs

Zero external dependencies beyond ffmpeg

# Folder Structure
The worker expects the following directory layout:

    /timelapse/
        <printer_id>/
            <job_id>/
                metadata.json
                layer_0001.jpg
                layer_0002.jpg
                interval_000000001.jpg
                every_0001.jpg
...

Each job folder may contain multiple image sequences, one per timelapse mode.

# Metadata Format
Each job’s metadata.json may contain multiple timelapse modes.


```json
{
  "duration_seconds": 9528,
  "file_name": "pamlskovy-box-vicko.3mf",
  "first_layer": 2,
  "job_id": "pamlskovy-box-vicko.3mf",
  "last_layer": 498,
  "printer_id": "default",
  "status": "completed",
  "time_completed": "2026-03-18T04:05:02Z",
  "time_started": "2026-03-18T01:26:14Z",
  "timelapse": {
    "modes": [
      {
        "frames": 919,
        "pattern": "layer_%04d.jpg",
        "trigger": { "on_event": "layer_changed" },
        "type": "layer"
      },
      {
        "frames": 946,
        "pattern": "interval_%09d.jpg",
        "trigger": { "every_ms": 10000 },
        "type": "interval"
      },
      {
        "frames": 183,
        "pattern": "every_%04d.jpg",
        "trigger": { "every_n_layers": 5 },
        "type": "every_n_layers"
      }
    ]
  }
}
```
# Configuration

A default settings.json is copied into /config on first run.

Use this fenced code block syntax:

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

One timelapse video per mode

A timelapse.json file describing all outputs

Example output filenames:

pamlskovy-box-vicko.3mf_20260318-110502AM_layer_timelapse.mp4
pamlskovy-box-vicko.3mf_20260318-110502AM_interval_timelapse.mp4
pamlskovy-box-vicko.3mf_20260318-110502AM_every_n_layers_timelapse.mp4

Example timelapse.json (use fenced code block syntax):

```json
{
  "timelapse_created": true,
  "outputs": [
    {
      "type": "layer",
      "pattern": "layer_%04d.jpg",
      "output_file": "pamlskovy-box-vicko.3mf_20260318-110502AM_layer_timelapse.mp4"
    },
    {
      "type": "interval",
      "pattern": "interval_%09d.jpg",
      "output_file": "pamlskovy-box-vicko.3mf_20260318-110502AM_interval_timelapse.mp4"
    },
    {
      "type": "every_n_layers",
      "pattern": "every_%04d.jpg",
      "output_file": "pamlskovy-box-vicko.3mf_20260318-110502AM_every_n_layers_timelapse.mp4"
    }
  ],
  "created_at": "2026-03-18T11:05:02-05:00",
  "worker_version": "1.1.0"
}
```

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
