# src/gps_extractor.py
import exifread
from io import BytesIO

def _convert_to_degrees(value) -> float:
    d, m, s = [float(x.num) / float(x.den) for x in value.values]
    return d + (m / 60.0) + (s / 3600.0)

def extract_gps(image_bytes: bytes) -> dict | None:
    try:
        tags = exifread.process_file(BytesIO(image_bytes), details=False)
        if "GPS GPSLatitude" not in tags or "GPS GPSLongitude" not in tags:
            return None
        lat = _convert_to_degrees(tags["GPS GPSLatitude"])
        lon = _convert_to_degrees(tags["GPS GPSLongitude"])
        if tags.get("GPS GPSLatitudeRef", "N").values[0] != "N": lat = -lat
        if tags.get("GPS GPSLongitudeRef", "E").values[0] != "E": lon = -lon
        return {"lat": lat, "lon": lon}
    except Exception:
        return None
