import os
import json
import subprocess
import time
import shutil
from datetime import datetime
import zoneinfo

BASE = "/timelapse"
CONFIG_PATH = "/config/settings.json"
DEFAULTS_PATH = "/defaults/settings.json"
DONE_FILE = "timelapse.json"

DEFAULT_CONFIG = {
    "delete_frames_after_stitch": False,
    "default_fps": 30,
    "scan_interval_seconds": 10,
    "output_format": "mp4",
    "timezone": None
}


def ensure_settings_file():
    """Copy default settings.json into /config if missing."""
    if not os.path.exists(CONFIG_PATH):
        print("[config] No settings.json found, copying defaults...")
        try:
            shutil.copy(DEFAULTS_PATH, CONFIG_PATH)
        except Exception as e:
            print(f"[config] Failed to copy default settings.json: {e}")


def load_config():
    """Load settings.json with fallback to defaults."""
    if not os.path.exists(CONFIG_PATH):
        print("[config] settings.json missing, using defaults")
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH) as f:
            user_cfg = json.load(f)
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(user_cfg)
        return cfg
    except Exception as e:
        print(f"[config] Failed to load settings.json: {e}, using defaults")
        return DEFAULT_CONFIG.copy()


def resolve_timezone(config):
    """Resolve timezone from config or system."""
    tz_name = config.get("timezone")
    if tz_name:
        try:
            return zoneinfo.ZoneInfo(tz_name)
        except Exception as e:
            print(f"[time] Invalid timezone '{tz_name}', falling back to UTC: {e}")
            return zoneinfo.ZoneInfo("UTC")

    # Fallback: system timezone
    try:
        with open("/etc/timezone") as f:
            sys_tz_name = f.read().strip()
        return zoneinfo.ZoneInfo(sys_tz_name)
    except Exception:
        print("[time] Could not determine system timezone, using UTC")
        return zoneinfo.ZoneInfo("UTC")


def build_output_filename(meta, config, tz):
    """Build deterministic output filename."""
    base = meta.get("file_name") or meta.get("job_id") or "timelapse"

    try:
        dt_utc = datetime.fromisoformat(meta["time_completed"].replace("Z", "+00:00"))
        dt_local = dt_utc.astimezone(tz)
        timestamp = dt_local.strftime("%Y%m%d-%I%M%S%p")  # 12-hour format
    except Exception as e:
        print(f"[naming] Failed to parse time_completed, using 'unknown': {e}")
        timestamp = "unknown"

    ext = config["output_format"]
    return f"{base}_{timestamp}_timelapse.{ext}"


def compute_fps(config):
    """Timelapse FPS is always from config, never metadata."""
    return config["default_fps"]


def write_done_file(job_path, output_name, tz):
    """Write timelapse.json to mark job as processed."""
    done_path = os.path.join(job_path, DONE_FILE)
    data = {
        "timelapse_created": True,
        "output_file": output_name,
        "created_at": datetime.now(tz).isoformat(),
        "worker_version": "1.0.0"
    }
    try:
        with open(done_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[done] Wrote {DONE_FILE}")
    except Exception as e:
        print(f"[done] Failed to write {DONE_FILE}: {e}")


def process_job(job_path, config, tz):
    # Skip if already processed
    if os.path.exists(os.path.join(job_path, DONE_FILE)):
        return

    metadata_path = os.path.join(job_path, "metadata.json")
    if not os.path.exists(metadata_path):
        return

    try:
        with open(metadata_path) as f:
            meta = json.load(f)
    except Exception as e:
        print(f"[job] Failed to read metadata.json in {job_path}: {e}")
        return

    if meta.get("status") != "completed":
        return

    output_name = build_output_filename(meta, config, tz)
    output_file = os.path.join(job_path, output_name)

    fps = compute_fps(config)
    print(f"[job] Stitching timelapse for {job_path} at {fps} fps -> {output_file}")

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate", str(fps),
        "-i", os.path.join(job_path, "layer_%04d.jpg"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_file,
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ffmpeg] Failed for {job_path}: {e}")
        return

    if config["delete_frames_after_stitch"]:
        deleted = 0
        for f in os.listdir(job_path):
            if f.startswith("layer_") and f.endswith(".jpg"):
                try:
                    os.remove(os.path.join(job_path, f))
                    deleted += 1
                except Exception as e:
                    print(f"[cleanup] Failed to delete {f}: {e}")
        print(f"[cleanup] Deleted {deleted} frame images in {job_path}")

    write_done_file(job_path, output_name, tz)
    print(f"[job] Completed timelapse: {output_file}")


def scan_all(config, tz):
    if not os.path.exists(BASE):
        print(f"[scan] Base path does not exist: {BASE}")
        return

    for printer in os.listdir(BASE):
        printer_path = os.path.join(BASE, printer)
        if not os.path.isdir(printer_path):
            continue

        for job in os.listdir(printer_path):
            job_path = os.path.join(printer_path, job)
            if os.path.isdir(job_path):
                process_job(job_path, config, tz)


if __name__ == "__main__":
    ensure_settings_file()
    print("[worker] Timelapse worker started. Watching for completed jobs...")

    while True:
        config = load_config()
        tz = resolve_timezone(config)
        scan_all(config, tz)
        time.sleep(config["scan_interval_seconds"])
