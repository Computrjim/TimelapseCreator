# Timelapse Worker for 3D Printer Frames

This container scans a `/timelapse` directory for completed 3D printer jobs,
detects folders containing a `metadata.json` with `"status": "completed"`,
and automatically stitches all `layer_####.jpg` images into a timelapse video.

The worker is designed for Unraid, but runs on any 64‑bit Linux system.

---

## Features

- Automatically detects completed print jobs
- Stitches `layer_####.jpg` frames into an MP4 timelapse
- Deterministic filename format:
