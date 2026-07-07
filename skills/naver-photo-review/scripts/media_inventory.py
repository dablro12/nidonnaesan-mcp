#!/usr/bin/env python3
import argparse
import csv
import json
import mimetypes
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".gif", ".tif", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}


def run_command(args):
    try:
        return subprocess.run(args, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return None


def human_size(num_bytes):
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} GB"


def image_size_with_pillow(path):
    try:
        from PIL import Image

        with Image.open(path) as img:
            return img.size
    except Exception:
        return None


def image_size_with_sips(path):
    if shutil.which("sips") is None:
        return None
    result = run_command(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)])
    if result is None or result.returncode != 0:
        return None
    width = None
    height = None
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("pixelWidth:"):
            width = int(line.split(":", 1)[1].strip())
        elif line.startswith("pixelHeight:"):
            height = int(line.split(":", 1)[1].strip())
    if width and height:
        return width, height
    return None


def video_info_with_ffprobe(path):
    if shutil.which("ffprobe") is None:
        return {}
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height:format=duration",
            "-of",
            "json",
            str(path),
        ]
    )
    if result is None or result.returncode != 0:
        return {}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}
    stream = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}
    info = {}
    if stream.get("width"):
        info["width"] = int(stream["width"])
    if stream.get("height"):
        info["height"] = int(stream["height"])
    if fmt.get("duration"):
        try:
            info["duration_seconds"] = round(float(fmt["duration"]), 2)
        except ValueError:
            pass
    return info


def orientation(width, height):
    if not width or not height:
        return ""
    if width == height:
        return "square"
    return "vertical" if height > width else "horizontal"


def media_type(path):
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    guessed, _ = mimetypes.guess_type(str(path))
    if guessed and guessed.startswith("image/"):
        return "image"
    if guessed and guessed.startswith("video/"):
        return "video"
    return ""


def collect(folder):
    rows = []
    for path in sorted(Path(folder).expanduser().resolve().rglob("*")):
        if not path.is_file():
            continue
        kind = media_type(path)
        if not kind:
            continue

        stat = path.stat()
        row = {
            "type": kind,
            "filename": path.name,
            "path": str(path),
            "extension": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "size": human_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "width": "",
            "height": "",
            "duration_seconds": "",
            "orientation": "",
        }

        if kind == "image":
            size = image_size_with_pillow(path) or image_size_with_sips(path)
            if size:
                row["width"], row["height"] = size
                row["orientation"] = orientation(row["width"], row["height"])
        elif kind == "video":
            info = video_info_with_ffprobe(path)
            row.update(info)
            row["orientation"] = orientation(row.get("width"), row.get("height"))

        rows.append(row)
    return rows


def write_csv(rows, output):
    fields = [
        "type",
        "filename",
        "path",
        "extension",
        "size_bytes",
        "size",
        "modified",
        "width",
        "height",
        "duration_seconds",
        "orientation",
    ]
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def main():
    parser = argparse.ArgumentParser(description="Inventory images and videos for Naver review planning.")
    parser.add_argument("folder", help="Folder containing photos and videos")
    parser.add_argument("--output", help="JSON output path")
    parser.add_argument("--csv", help="CSV output path")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}")

    rows = collect(folder)
    summary = {
        "folder": str(folder),
        "total": len(rows),
        "images": sum(1 for row in rows if row["type"] == "image"),
        "videos": sum(1 for row in rows if row["type"] == "video"),
        "items": rows,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.csv:
        write_csv(rows, args.csv)

    print(f"media={summary['total']} images={summary['images']} videos={summary['videos']}")


if __name__ == "__main__":
    main()
