# src/video_analyzer.py — Extract frames from video and analyze each

import cv2
import tempfile
import os
from PIL import Image
from src.analyzer import analyze_image

def extract_frames(video_path: str, every_n: int = 5) -> list:
    """Extract every Nth frame from a video file."""
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % every_n == 0:
            # Convert BGR to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            timestamp = frame_count / fps if fps > 0 else frame_count
            frames.append({
                "frame_number": frame_count,
                "timestamp": round(timestamp, 2),
                "image": pil_img
            })
        frame_count += 1

    cap.release()
    return frames, total, fps

def analyze_video(video_bytes: bytes, api_key: str, every_n: int = 5,
                  location: str = "", progress_cb=None) -> list:
    """Analyze a video file frame by frame."""
    # Write to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    try:
        frames, total_frames, fps = extract_frames(tmp_path, every_n)
        results = []

        for i, frame_data in enumerate(frames):
            if progress_cb:
                progress_cb(i, len(frames), frame_data["timestamp"])

            try:
                result = analyze_image(frame_data["image"], api_key, location)
                result["timestamp"] = frame_data["timestamp"]
                result["frame_number"] = frame_data["frame_number"]
                result["frame_image"] = frame_data["image"]
                results.append(result)
            except Exception as e:
                results.append({
                    "timestamp": frame_data["timestamp"],
                    "frame_number": frame_data["frame_number"],
                    "error": str(e),
                    "severity_score": 0,
                    "severity_label": "Unknown",
                    "hazards_detected": [],
                    "frame_image": frame_data["image"]
                })

        return results
    finally:
        os.unlink(tmp_path)

def get_video_summary(results: list) -> dict:
    """Summarize video analysis results."""
    valid = [r for r in results if "error" not in r]
    if not valid:
        return {}

    scores = [r["severity_score"] for r in valid]
    all_hazards = []
    for r in valid:
        all_hazards.extend(r.get("hazards_detected", []))

    hazard_counts = {}
    for h in all_hazards:
        hazard_counts[h] = hazard_counts.get(h, 0) + 1

    worst = max(valid, key=lambda r: r["severity_score"])

    return {
        "total_frames_analyzed": len(results),
        "avg_severity": round(sum(scores) / len(scores), 2),
        "max_severity": round(max(scores), 2),
        "min_severity": round(min(scores), 2),
        "hazard_frequency": dict(sorted(hazard_counts.items(), key=lambda x: x[1], reverse=True)),
        "worst_moment": worst,
        "safe_pct": round(len([r for r in valid if r["severity_score"] < 3]) / len(valid) * 100),
        "critical_pct": round(len([r for r in valid if r["severity_score"] >= 7.5]) / len(valid) * 100),
    }
