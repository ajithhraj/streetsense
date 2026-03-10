# src/analyzer.py
import base64, json, requests
from PIL import Image
from io import BytesIO
from src.hazard_taxonomy import HAZARDS, get_severity_label

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.thumbnail((1024, 1024), Image.LANCZOS)
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_image(image: Image.Image, api_key: str, location_name: str = "") -> dict:
    hazard_list = "\n".join([
        f"- {name}: {info['description']}"
        for name, info in HAZARDS.items() if name != "no_hazard"
    ])
    location_ctx = f"This image is from: {location_name}." if location_name else ""

    prompt = f"""You are an expert road safety inspector analyzing Indian road conditions.
{location_ctx}

Analyze this road image and return ONLY a JSON object:
{{
  "hazards_detected": ["pothole"],
  "primary_hazard": "pothole",
  "severity_score": 7.5,
  "confidence": 0.85,
  "location_in_frame": "center-left",
  "road_condition": "Poor",
  "immediate_action": "Reduce speed. Avoid pothole on left.",
  "civic_report": "Large pothole detected spanning 1 meter at center-left. Immediate repair required.",
  "affected_area_percent": 25,
  "passable": true
}}

Available hazard types:
{hazard_list}

Rules:
- hazards_detected: list of hazards visible, or ["no_hazard"] if safe
- severity_score: 0.0 (safe) to 10.0 (critical)
- confidence: 0.0 to 1.0
- road_condition: Excellent / Good / Fair / Poor / Critical
- civic_report: formal 2-sentence report for municipal authorities
- Return ONLY valid JSON"""

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_to_base64(image)}"}},
                {"type": "text", "text": prompt}
            ]
        }],
        "temperature": 0.1,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(GROQ_API_URL, json=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        timeout=30)

    if not response.ok:
        raise Exception(f"Groq API error {response.status_code}: {response.text[:200]}")

    result = json.loads(response.json()["choices"][0]["message"]["content"])
    result["severity_label"], result["severity_color"] = get_severity_label(result["severity_score"])
    result["hazard_details"] = {h: HAZARDS[h] for h in result.get("hazards_detected", []) if h in HAZARDS}
    return result
